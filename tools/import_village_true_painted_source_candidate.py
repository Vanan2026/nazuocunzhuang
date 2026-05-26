from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageStat


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_DIR = ROOT / "production" / "assets" / "regions" / "village_world2d" / "v001"
CANDIDATE_DIR = PACKAGE_DIR / "02_source_generation" / "true_source_candidates"
CANDIDATE_ID = "village_true_painted_source_candidate_v001"
TARGET_SIZE = (1800, 1200)

PROMPT = """Use case: stylized-concept
Asset type: 2D game environment painted source candidate for a seamless countryside life-sim world
Primary request: Create a true storybook painted source image for the Village Plaza region of a seamless fixed 3/4 top-down 2D rural world. Use the visible OutdoorWorld master blueprint and visible Village structure draft only as spatial references. Transform the diagrammatic draft into finished warm countryside scene art, not an engineering diagram.
Scene/backdrop: A compact village entry plaza in a gentle countryside: grass, soft dirt roads, two small set-back village houses, a modest notice board near the west/center path, a small seed advice stall near the east side, an old maple tree clue area in the lower-right, a quiet bench below the plaza path, and visible road exits west, north, east, and south that can connect to adjacent seamless world chunks.
Subject: Environment only; no characters. Leave a readable empty standing pocket near the seed stall for Aoi. Keep all gameplay anchors recognizable but natural.
Style/medium: Warm low-saturation hand-painted storybook 2D game art, fixed 3/4 top-down perspective, cozy rural life simulation mood, soft painterly texture, clean readable silhouettes, gentle outlines, no hard vector-diagram look.
Composition/framing: Wide region source composition. Preserve spatial relationships from the reference draft: west return path enters from left, central social plaza, notice board left-center, seed stall right-center, old maple lower-right, bench lower-left/below plaza, road exits north/east/south remain visible. Roads should curve naturally and continue to canvas edges without looking like isolated markers.
Lighting/mood: Calm spring morning, soft diffuse light, no harsh shadows, no dramatic contrast.
Color palette: Muted fresh greens, warm dirt-road ochres, soft browns, faded red/brown roofs, gentle cream house walls, subtle flower accents. Keep colors compatible with seamless adjacent outdoor regions.
Materials/textures: Painted grass with varied brush texture, worn dirt paths, wooden notice board, simple wooden seed stall, old maple bark and soft canopy, small stones and flowers. Natural variation is allowed; do not trace guide coordinates mechanically.
Text: No readable text. Notice board may have small unreadable marks only.
Constraints: fully opaque PNG-style scene source; no UI, no labels, no overlay rectangles, no debug markers, no arrows, no characters, no readable quest text, no watermark. Preserve roads/anchors clearly enough for later layer splitting. Do not copy any named game, anime, movie, or artist style. No combat, weapons, monsters, horror, or pressure imagery.
Avoid: photorealism, isometric 3D render, flat vector diagram, map labels, grid lines, thick schematic roads, giant empty grass, random crop, cropped objects, disconnected exits, props sitting in walk lanes, Aoi standing pocket filled with decoration.
"""


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def validate_image(image: Image.Image, label: str) -> None:
    if image.mode not in {"RGB", "RGBA"}:
        fail(f"{label} must be RGB/RGBA, got {image.mode}")
    rgb = image.convert("RGB")
    ranges = [high - low for low, high in rgb.getextrema()]
    stat = ImageStat.Stat(rgb)
    if max(ranges) < 90:
        fail(f"{label} has too little value/color range")
    if sum(stat.var) < 1000:
        fail(f"{label} appears too flat for a painted source candidate")


def write_metadata(source_path: Path, original_size: tuple[int, int]) -> None:
    payload = {
        "candidate_id": CANDIDATE_ID,
        "status": "true_painted_source_candidate_pending_human_visual_review",
        "candidate_type": "true_storybook_painted_source_candidate",
        "source_generator": "codex_builtin_image_gen",
        "original_generated_source": str(source_path),
        "original_image": str((CANDIDATE_DIR / f"{CANDIDATE_ID}_original.png").relative_to(ROOT)).replace("\\", "/"),
        "normalized_image": str((CANDIDATE_DIR / f"{CANDIDATE_ID}.png").relative_to(ROOT)).replace("\\", "/"),
        "prompt_file": str((CANDIDATE_DIR / f"{CANDIDATE_ID}_prompt.md").relative_to(ROOT)).replace("\\", "/"),
        "original_size": list(original_size),
        "normalized_size": [TARGET_SIZE[0], TARGET_SIZE[1]],
        "alpha": "opaque",
        "human_visual_approval": False,
        "layer_export_approved": False,
        "runtime_replacement": False,
        "launch_quality_approved": False,
        "references": {
            "outdoor_world_master": "production/assets/outdoor_world_world2d/v001/workflow_manifest.json",
            "village_layout_lock": "production/assets/regions/village_world2d/v001/01_layout_lock/layout_lock.json",
            "layout_structure_draft": "production/assets/regions/village_world2d/v001/02_source_generation/village_painted_source.png"
        },
        "notes": [
            "This candidate is saved for human visual review only.",
            "Do not split runtime layers until the user explicitly accepts this source.",
            "Do not replace runtime art from this candidate in the current task."
        ]
    }
    (CANDIDATE_DIR / f"{CANDIDATE_ID}.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, help="Generated image path from the built-in image generator.")
    args = parser.parse_args()

    source_path = Path(args.source).resolve()
    if not source_path.is_file():
        fail(f"missing generated source image: {source_path}")

    CANDIDATE_DIR.mkdir(parents=True, exist_ok=True)
    image = Image.open(source_path)
    validate_image(image, "original generated image")
    original_size = image.size

    original_out = CANDIDATE_DIR / f"{CANDIDATE_ID}_original.png"
    normalized_out = CANDIDATE_DIR / f"{CANDIDATE_ID}.png"
    prompt_out = CANDIDATE_DIR / f"{CANDIDATE_ID}_prompt.md"

    image.convert("RGB").save(original_out)
    normalized = image.convert("RGB").resize(TARGET_SIZE, Image.Resampling.LANCZOS)
    validate_image(normalized, "normalized candidate image")
    normalized.save(normalized_out)
    prompt_out.write_text("# Village true painted source candidate prompt\n\n```text\n" + PROMPT.strip() + "\n```\n", encoding="utf-8")
    write_metadata(source_path, original_size)

    print(f"OK: wrote {original_out.relative_to(ROOT)}")
    print(f"OK: wrote {normalized_out.relative_to(ROOT)}")
    print(f"OK: wrote {CANDIDATE_DIR / (CANDIDATE_ID + '.json')}")


if __name__ == "__main__":
    main()
