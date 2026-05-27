from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HANDOFF = ROOT / "production" / "assets" / "external_gpt_handoff" / "greenfield_p0" / "v002"
MANIFEST = HANDOFF / "asset_request_manifest.json"
PROMPTS = HANDOFF / "prompt_briefs.md"
README = HANDOFF / "README.md"
DOC = ROOT / "docs" / "GREENFIELD_P0_GPT_ASSET_PRODUCTION_BRIEF.md"

FORBIDDEN = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in [
        r"\bcombat\b",
        r"\bmonster\b",
        r"\bweapon\b",
        r"\barmor\b",
        r"\bhp\b",
        r"\bloot\b",
    ]
]

REQUIRED_BATCHES = {
    "batch_01_ui_kit_core",
    "batch_02_ui_icons_map_settings",
    "batch_03_home_area_full_canvas",
    "batch_04_p0_portraits",
    "batch_05_runtime_walk_sprites",
    "batch_06_item_icons_core",
}

REQUIRED_PROMPT_HEADINGS = {
    "batch_01_ui_kit_core": "Batch 01 UI Kit Core",
    "batch_02_ui_icons_map_settings": "Batch 02 UI Icons Map Settings",
    "batch_03_home_area_full_canvas": "Batch 03 HomeArea Full Canvas",
    "batch_04_p0_portraits": "Batch 04 P0 Portraits",
    "batch_05_runtime_walk_sprites": "Batch 05 Runtime Walk Sprites",
    "batch_06_item_icons_core": "Batch 06 Item Icons Core",
}


def fail(message: str) -> None:
    raise AssertionError(message)


def read(path: Path) -> str:
    if not path.exists():
        fail(f"missing file: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8")


def validate_manifest() -> None:
    request = json.loads(read(MANIFEST))
    if request.get("package_id") != "greenfield_p0_external_gpt_asset_request_v002":
        fail("manifest package_id should identify v002")
    if "greenfield_p0_style_mother_2026-05-27.jpg" not in str(request.get("style_reference", "")):
        fail("manifest should reference the current style mother")
    if int(request.get("rules", {}).get("max_assets_per_batch", 0)) != 12:
        fail("manifest should cap batches at 12 assets")
    if "painted_source" not in request.get("rules", {}).get("region_layers", ""):
        fail("manifest should preserve source-first region layer rules")

    batch_ids = {batch.get("batch_id", "") for batch in request.get("batches", [])}
    if not REQUIRED_BATCHES <= batch_ids:
        fail(f"manifest missing required batches: {sorted(REQUIRED_BATCHES - batch_ids)}")

    seen_incoming: set[str] = set()
    seen_runtime: set[str] = set()
    for batch in request.get("batches", []):
        batch_id = str(batch.get("batch_id", ""))
        assets = batch.get("assets", [])
        if len(assets) > 12:
            fail(f"{batch_id} has {len(assets)} assets; max is 12")
        if not assets:
            fail(f"{batch_id} has no assets")
        if batch_id == "batch_03_home_area_full_canvas" and len(assets) != 5:
            fail("HomeArea full-canvas batch should stay small and coordinated")
        for asset in assets:
            for field in ["asset_id", "category", "incoming_path", "final_runtime_path", "expected_size", "transparent", "prompt"]:
                if field not in asset:
                    fail(f"{batch_id} asset missing field: {field}")
            incoming = str(asset["incoming_path"])
            runtime = str(asset["final_runtime_path"])
            if incoming in seen_incoming:
                fail(f"duplicate incoming path: {incoming}")
            if runtime in seen_runtime:
                fail(f"duplicate runtime path: {runtime}")
            seen_incoming.add(incoming)
            seen_runtime.add(runtime)
            expected_size = asset["expected_size"]
            if not isinstance(expected_size, list) or len(expected_size) != 2:
                fail(f"{incoming} expected_size should be [w, h]")
            if int(expected_size[0]) <= 0 or int(expected_size[1]) <= 0:
                fail(f"{incoming} expected_size should be positive")
            prompt = str(asset["prompt"])
            for pattern in FORBIDDEN:
                if pattern.search(prompt):
                    fail(f"{incoming} prompt contains forbidden term: {pattern.pattern}")
        if batch_id == "batch_03_home_area_full_canvas":
            sizes = {tuple(asset["expected_size"]) for asset in assets}
            if sizes != {(1920, 1080)}:
                fail("HomeArea full-canvas batch must use one shared 1920x1080 canvas")


def validate_docs() -> None:
    prompt_text = read(PROMPTS)
    readme_text = read(README)
    doc_text = read(DOC)
    for batch_id, heading in REQUIRED_PROMPT_HEADINGS.items():
        if heading not in prompt_text and batch_id not in prompt_text:
            fail(f"prompt_briefs missing batch: {batch_id}")
    for token in [
        "Do not ask GPT for all batches at once",
        "Registration-perfect layer alignment",
        "Batch 01 UI Kit Core",
        "production/assets/external_gpt_handoff/greenfield_p0/v002",
    ]:
        if token not in doc_text:
            fail(f"production brief missing token: {token}")
    readme_lower = readme_text.lower()
    for token in ["v002", "small-batch", "incoming/", "human visual approval"]:
        if token not in readme_lower:
            fail(f"README missing token: {token}")


def main() -> None:
    validate_manifest()
    validate_docs()
    print("OK: Greenfield P0 GPT asset handoff v002 validates")


if __name__ == "__main__":
    main()
