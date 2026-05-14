#!/usr/bin/env python3
"""Scan project text files for encoding risks and write a fix checklist.

The scanner is intentionally read-only for project files. It reports files that
should be reviewed or converted, but never rewrites the scanned content.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Iterable


TEXT_EXTENSIONS = {
    ".cfg",
    ".csv",
    ".gd",
    ".gdshader",
    ".godot",
    ".html",
    ".ini",
    ".json",
    ".md",
    ".py",
    ".ps1",
    ".shader",
    ".toml",
    ".tres",
    ".tscn",
    ".txt",
    ".xml",
    ".yaml",
    ".yml",
}

BINARY_EXTENSIONS = {
    ".blend",
    ".dll",
    ".exe",
    ".glb",
    ".gltf",
    ".ico",
    ".jpg",
    ".jpeg",
    ".ogg",
    ".pck",
    ".png",
    ".pyc",
    ".uid",
    ".wav",
    ".webp",
    ".zip",
}

DEFAULT_SKIP_DIRS = {
    ".git",
    ".godot",
    ".vs",
    ".vscode",
    "__pycache__",
    "export",
    "node_modules",
}

DEFAULT_SKIP_SUFFIXES = {
    ".import",
}

DEFAULT_SKIP_RELATIVE_PATHS = {
    "tools/scan_text_encoding.py",
    "tools/test_scan_text_encoding.py",
}

MOJIBAKE_MARKERS = [
    "锟斤拷",
    "ï¿½",
    "�",
    "Ã",
    "Â",
    "Ð",
    "Ñ",
    "鈥",
    "鈮",
    "鉁",
    "鉂",
    "鎺",
    "绋",
    "褰",
    "骞",
    "涓",
    "浠",
    "鍓",
    "鐘",
    "宸",
    "楠",
    "闃",
]


def is_probably_binary(data: bytes) -> bool:
    if not data:
        return False
    if b"\x00" in data[:4096]:
        return True
    control = sum(1 for byte in data[:4096] if byte < 9 or 13 < byte < 32)
    return control / min(len(data), 4096) > 0.08


def find_mojibake_markers(text: str) -> list[str]:
    return [marker for marker in MOJIBAKE_MARKERS if marker in text]


def _decode_candidate(data: bytes, encoding: str) -> tuple[bool, str]:
    try:
        return True, data.decode(encoding)
    except UnicodeDecodeError:
        return False, ""


def _cjk_score(text: str) -> int:
    return sum(1 for char in text if "\u4e00" <= char <= "\u9fff")


def _suspicious_legacy_utf8_score(text: str) -> int:
    ranges = (
        ("\u0300", "\u036f"),  # combining marks often produced by accidental legacy-byte UTF-8 decode
        ("\u0400", "\u04ff"),  # Cyrillic is uncommon in this project and common in mojibake
        ("\u0080", "\u00ff"),  # Latin-1 supplement
    )
    return sum(1 for char in text for start, end in ranges if start <= char <= end)


def classify_bytes(path: Path, data: bytes) -> dict[str, object]:
    rel_path = path.as_posix()
    result: dict[str, object] = {
        "path": rel_path,
        "bytes": len(data),
        "status": "ok",
        "encoding": "utf-8",
        "needs_fix": False,
        "markers": [],
        "recommendation": "No action.",
    }

    if not data:
        result["recommendation"] = "Empty text file; no encoding action."
        return result

    if is_probably_binary(data):
        result.update(
            {
                "status": "binary",
                "encoding": "binary",
                "needs_fix": True,
                "recommendation": "Unexpected binary-looking content in a scanned text path; review extension or exclude rule.",
            }
        )
        return result

    bom_map = [
        (b"\xef\xbb\xbf", "utf-8-sig"),
        (b"\xff\xfe", "utf-16-le"),
        (b"\xfe\xff", "utf-16-be"),
    ]
    for bom, encoding in bom_map:
        if data.startswith(bom):
            ok, text = _decode_candidate(data, encoding)
            markers = find_mojibake_markers(text) if ok else []
            result.update(
                {
                    "status": "bom",
                    "encoding": encoding,
                    "needs_fix": encoding != "utf-8-sig" or bool(markers),
                    "markers": markers,
                    "recommendation": "Convert to UTF-8 without BOM after review."
                    if encoding != "utf-8-sig"
                    else "Optional: normalize to UTF-8 without BOM if the file is hand-edited.",
                }
            )
            if markers:
                result["status"] = "mojibake"
                result["needs_fix"] = True
                result["recommendation"] = "Review original source encoding; do not blind-convert until text is confirmed."
            return result

    ok, text = _decode_candidate(data, "utf-8")
    if ok:
        legacy_ok, legacy_text = _decode_candidate(data, "gb18030")
        if legacy_ok and _cjk_score(legacy_text) > _cjk_score(text) and _suspicious_legacy_utf8_score(text) > 0:
            result.update(
                {
                    "status": "non_utf8",
                    "encoding": "gb18030",
                    "needs_fix": True,
                    "markers": find_mojibake_markers(text),
                    "recommendation": "UTF-8 decoding succeeds but looks like legacy-byte mojibake; review GB18030 decode, then convert targeted files to UTF-8.",
                }
            )
            return result
        markers = find_mojibake_markers(text)
        if markers:
            result.update(
                {
                    "status": "mojibake",
                    "markers": markers,
                    "needs_fix": True,
                    "recommendation": "File is valid UTF-8 but contains mojibake markers; restore from source or manually repair text.",
                }
            )
        return result

    for encoding in ("gb18030", "cp1252", "latin-1"):
        ok, text = _decode_candidate(data, encoding)
        if ok:
            markers = find_mojibake_markers(text)
            result.update(
                {
                    "status": "non_utf8",
                    "encoding": encoding,
                    "needs_fix": True,
                    "markers": markers,
                    "recommendation": f"Review decoded text, then convert from {encoding} to UTF-8 in a targeted batch.",
                }
            )
            return result

    result.update(
        {
            "status": "undecodable",
            "encoding": "unknown",
            "needs_fix": True,
            "recommendation": "Could not decode as UTF-8, GB18030, CP1252, or Latin-1; inspect manually before conversion.",
        }
    )
    return result


def should_scan(path: Path, root: Path, include_hidden: bool, include_extensions: set[str]) -> bool:
    relative = path.relative_to(root)
    relative_key = relative.as_posix()
    if relative_key in DEFAULT_SKIP_RELATIVE_PATHS:
        return False
    parts = relative.parts
    if not include_hidden and any(part.startswith(".") for part in parts):
        return False
    if any(part in DEFAULT_SKIP_DIRS for part in parts[:-1]):
        return False
    if any(path.name.endswith(suffix) for suffix in DEFAULT_SKIP_SUFFIXES):
        return False
    suffix = path.suffix.lower()
    if suffix in BINARY_EXTENSIONS:
        return False
    return suffix in include_extensions


def iter_scan_files(root: Path, include_hidden: bool, include_extensions: set[str]) -> Iterable[Path]:
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        try:
            if should_scan(path, root, include_hidden, include_extensions):
                yield path
        except (OSError, ValueError):
            continue


def build_markdown(root: Path, results: list[dict[str, object]]) -> str:
    counts = Counter(str(item["status"]) for item in results)
    needs_fix = [item for item in results if item["needs_fix"]]
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        "# Encoding Scan Report",
        "",
        f"- Generated: {generated_at}",
        f"- Root: `{root}`",
        f"- Scanned text files: {len(results)}",
        f"- Needs review/fix: {len(needs_fix)}",
        "",
        "## Status Summary",
        "",
    ]
    for status, count in sorted(counts.items()):
        lines.append(f"- `{status}`: {count}")

    lines.extend(
        [
            "",
            "## Batch Fix Checklist",
            "",
            "This is a detection-only plan. Do not run global replacement. Fix in small batches and review diffs after each batch.",
            "",
        ]
    )

    if not needs_fix:
        lines.append("- No encoding fixes currently recommended.")
    else:
        for item in sorted(needs_fix, key=lambda row: (str(row["status"]), str(row["path"]))):
            markers = ", ".join(item.get("markers", [])) or "-"
            lines.extend(
                [
                    f"### {item['path']}",
                    f"- Status: `{item['status']}`",
                    f"- Detected encoding: `{item['encoding']}`",
                    f"- Markers: {markers}",
                    f"- Action: {item['recommendation']}",
                    "",
                ]
            )

    lines.extend(
        [
            "## Suggested Safe Workflow",
            "",
            "1. Open one checklist group at a time.",
            "2. Confirm the intended source encoding or original text.",
            "3. Convert only confirmed files to UTF-8.",
            "4. Review `git diff` and run project validation before the next group.",
        ]
    )
    return "\n".join(lines) + "\n"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Read-only project text encoding scanner.")
    parser.add_argument("--root", default=".", help="Project root to scan.")
    parser.add_argument(
        "--report",
        default=".codex/reports/encoding_scan.md",
        help="Markdown report path.",
    )
    parser.add_argument(
        "--json",
        default=".codex/reports/encoding_scan.json",
        help="JSON report path.",
    )
    parser.add_argument("--include-hidden", action="store_true", help="Include hidden directories such as .codex.")
    parser.add_argument("--max-size", type=int, default=2_000_000, help="Skip text candidates larger than this many bytes.")
    parser.add_argument(
        "--ext",
        action="append",
        default=[],
        help="Additional extension to scan, for example --ext .log. Can be repeated.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    root = Path(args.root).resolve()
    include_extensions = set(TEXT_EXTENSIONS)
    include_extensions.update(ext if ext.startswith(".") else f".{ext}" for ext in args.ext)

    results: list[dict[str, object]] = []
    skipped_large: list[str] = []
    unreadable: list[dict[str, str]] = []

    for path in iter_scan_files(root, args.include_hidden, include_extensions):
        try:
            if path.stat().st_size > args.max_size:
                skipped_large.append(path.relative_to(root).as_posix())
                continue
            data = path.read_bytes()
        except OSError as exc:
            unreadable.append({"path": path.relative_to(root).as_posix(), "error": str(exc)})
            continue
        result = classify_bytes(path.relative_to(root), data)
        results.append(result)

    report_path = (root / args.report).resolve()
    json_path = (root / args.json).resolve()
    report_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "root": str(root),
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "scanned_files": len(results),
        "needs_fix": sum(1 for item in results if item["needs_fix"]),
        "skipped_large": skipped_large,
        "unreadable": unreadable,
        "results": results,
    }
    report_path.write_text(build_markdown(root, results), encoding="utf-8", newline="\n")
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")

    counts = Counter(str(item["status"]) for item in results)
    print(f"Scanned {len(results)} text files under {root}")
    print(f"Needs review/fix: {payload['needs_fix']}")
    print(f"Markdown report: {report_path}")
    print(f"JSON report: {json_path}")
    for status, count in sorted(counts.items()):
        print(f"{status}: {count}")
    if unreadable:
        print(f"Unreadable files: {len(unreadable)}")
    if skipped_large:
        print(f"Skipped large files: {len(skipped_large)}")
    return 1 if unreadable else 0


if __name__ == "__main__":
    raise SystemExit(main())
