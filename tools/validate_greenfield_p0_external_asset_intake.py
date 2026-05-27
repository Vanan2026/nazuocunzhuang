from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
HANDOFF = ROOT / "production" / "assets" / "external_gpt_handoff" / "greenfield_p0" / "v001"
REQUEST = HANDOFF / "asset_request_manifest.json"
INCOMING = HANDOFF / "incoming"


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def load_request(manifest_path: Path) -> dict:
    require(manifest_path.exists(), f"missing request manifest: {manifest_path}")
    return json.loads(manifest_path.read_text(encoding="utf-8"))


def flatten_assets(request: dict) -> list[dict]:
    assets = request.get("assets", [])
    if assets:
        return assets
    result: list[dict] = []
    for batch in request.get("batches", []):
        result.extend(batch.get("assets", []))
    return result


def resolve_incoming_root(manifest_path: Path, request: dict) -> Path:
    raw_root = str(request.get("incoming_root", "")).strip()
    if raw_root:
        incoming_root = Path(raw_root)
        if not incoming_root.is_absolute():
            incoming_root = ROOT / incoming_root
        return incoming_root
    return manifest_path.parent / "incoming"


def validate_png(path: Path, asset: dict) -> list[str]:
    errors = []
    try:
        with Image.open(path) as image:
            if image.format != "PNG":
                errors.append("not PNG")
            expected_size = tuple(asset["expected_size"])
            if image.size != expected_size:
                errors.append(f"wrong size {image.size}, expected {expected_size}")
            if image.mode != "RGBA":
                errors.append(f"wrong mode {image.mode}, expected RGBA")
            if image.mode == "RGBA":
                alpha = image.getchannel("A")
                min_alpha, max_alpha = alpha.getextrema()
                if asset["transparent"]:
                    if min_alpha == 255 and max_alpha == 255:
                        errors.append("expected transparent-capable asset but alpha is fully opaque")
                    if max_alpha == 0:
                        errors.append("alpha is fully transparent")
                else:
                    if min_alpha != 255 or max_alpha != 255:
                        errors.append(f"expected fully opaque alpha, got {min_alpha}-{max_alpha}")
    except Exception as exc:  # pragma: no cover - diagnostic path
        errors.append(f"cannot open PNG: {exc}")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--allow-partial", action="store_true", help="allow missing assets and validate only files already dropped into incoming")
    parser.add_argument("--manifest", default=str(REQUEST), help="request manifest to validate")
    args = parser.parse_args()

    manifest_path = Path(args.manifest)
    if not manifest_path.is_absolute():
        manifest_path = ROOT / manifest_path
    request = load_request(manifest_path)
    assets = flatten_assets(request)
    require(assets, "request manifest has no assets")
    incoming_root = resolve_incoming_root(manifest_path, request)

    present = 0
    missing = []
    invalid = []
    for asset in assets:
        path = incoming_root / asset["incoming_path"]
        if not path.exists():
            missing.append(asset["incoming_path"])
            continue
        present += 1
        errors = validate_png(path, asset)
        if errors:
            invalid.append({"path": asset["incoming_path"], "errors": errors})

    if invalid:
        for item in invalid[:20]:
            print(f"INVALID: {item['path']}: {', '.join(item['errors'])}")
        if len(invalid) > 20:
            print(f"... {len(invalid) - 20} more invalid files")
        fail(f"{len(invalid)} incoming assets failed validation")

    if missing and not args.allow_partial:
        for path in missing[:20]:
            print(f"MISSING: {path}")
        if len(missing) > 20:
            print(f"... {len(missing) - 20} more missing files")
        fail(f"{len(missing)} requested incoming assets are missing")

    print(
        "OK: greenfield P0 external asset intake validates "
        f"present={present} missing={len(missing)} allow_partial={args.allow_partial}"
    )


if __name__ == "__main__":
    main()
