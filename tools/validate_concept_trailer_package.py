#!/usr/bin/env python3
"""Validate the 2D slice concept trailer prep package."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "docs" / "trailer" / "concept_trailer_2d_slice_2026-05-14.json"
DOCUMENT = ROOT / "docs" / "trailer" / "concept_trailer_2d_slice_2026-05-14.md"
CAPTURE_SCRIPT = ROOT / "tools" / "capture_concept_trailer_frames.gd"


def _failures() -> list[str]:
    failures: list[str] = []

    for path in (MANIFEST, DOCUMENT, CAPTURE_SCRIPT):
        if not path.exists():
            failures.append(f"missing required package file: {path.relative_to(ROOT)}")

    if failures:
        return failures

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    document = DOCUMENT.read_text(encoding="utf-8")

    target_duration = float(manifest.get("target_duration_seconds", 0.0))
    if not 15.0 <= target_duration <= 20.0:
        failures.append(f"target_duration_seconds is {target_duration}, expected 15-20")

    shots = manifest.get("shots", [])
    if not isinstance(shots, list) or not shots:
        failures.append("manifest shots must be a non-empty list")
        return failures

    total_duration = sum(float(shot.get("duration_seconds", 0.0)) for shot in shots)
    if abs(total_duration - target_duration) > 0.01:
        failures.append(f"shot duration total {total_duration} does not match target {target_duration}")
    if not 15.0 <= total_duration <= 20.0:
        failures.append(f"shot duration total is {total_duration}, expected 15-20")

    shot_ids: set[str] = set()
    capture_files: set[str] = set()
    regions: set[str] = set()
    poses: set[str] = set()

    for index, shot in enumerate(shots, start=1):
        shot_id = str(shot.get("id", ""))
        if not re.fullmatch(r"shot_\d{2}_[a-z0-9_]+", shot_id):
            failures.append(f"shot {index} has invalid id: {shot_id!r}")
        if shot_id in shot_ids:
            failures.append(f"duplicate shot id: {shot_id}")
        shot_ids.add(shot_id)

        if shot_id and shot_id not in document:
            failures.append(f"document does not mention shot id: {shot_id}")

        capture_file = str(shot.get("capture_file", ""))
        if not re.fullmatch(r"\d{2}_[a-z0-9_]+\.png", capture_file):
            failures.append(f"{shot_id} has invalid capture_file: {capture_file!r}")
        if capture_file in capture_files:
            failures.append(f"duplicate capture_file: {capture_file}")
        capture_files.add(capture_file)

        if float(shot.get("duration_seconds", 0.0)) <= 0.0:
            failures.append(f"{shot_id} duration must be positive")
        if len(shot.get("resolution", manifest.get("resolution", []))) != 2:
            failures.append(f"{shot_id} resolution must be width/height when provided")

        regions.add(str(shot.get("region_id", "")))
        poses.add(str(shot.get("pose", "")))

    required_regions = {"Region_HomeArea", "Region_BackFarm"}
    missing_regions = required_regions - regions
    if missing_regions:
        failures.append(f"manifest missing required regions: {sorted(missing_regions)}")

    if "veranda_rest" not in poses:
        failures.append("manifest missing veranda_rest pose")
    if not any(pose.startswith("farm_") for pose in poses):
        failures.append("manifest missing BackFarm farm interaction pose")
    if "walk" not in poses:
        failures.append("manifest missing protagonist walk pose")

    for source in manifest.get("source_files", []):
        path = ROOT / source
        if not path.exists():
            failures.append(f"manifest source file does not exist: {source}")

    required_headings = ["## 15-20 秒镜头脚本", "## 场景捕捉顺序", "## HeyGen 输入文案"]
    for heading in required_headings:
        if heading not in document:
            failures.append(f"document missing heading: {heading}")

    return failures


def main() -> int:
    failures = _failures()
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}", file=sys.stderr)
        return 1

    print("OK: concept trailer package validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
