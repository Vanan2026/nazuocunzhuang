from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

EXPECTED_RUNTIME_PROPS = [
    "assets/art/props/region_home_area_prop_mailbox_v001.png",
    "assets/art/props/region_home_area_prop_road_sign_v001.png",
    "assets/art/props/region_home_area_prop_well_broken_v001.png",
    "assets/art/props/region_home_area_prop_bench_v001.png",
    "assets/art/props/prop_well_old_broken_256.png",
]

EXPECTED_SCENE_SNIPPETS = [
    "res://game/entities/visual/RuntimeTextureSprite.gd",
    '[node name="MailboxArt" type="Sprite2D" parent="Mailbox"]',
    '[node name="SignboardArt" type="Sprite2D" parent="Signboard"]',
    '[node name="OldWell" type="Area2D" parent="."',
    '[node name="OldWellArt" type="Sprite2D" parent="OldWell"]',
    '[node name="Bench" type="Area2D" parent="."',
    '[node name="BenchArt" type="Sprite2D" parent="Bench"]',
    "region_home_area_prop_mailbox_v001.png",
    "region_home_area_prop_road_sign_v001.png",
    "prop_well_old_broken_256.png",
    "region_home_area_prop_bench_v001.png",
]

FORBIDDEN = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in [
        r"\bcombat\b",
        r"\bmonster\b",
        r"\bdamage\b",
        r"\bweapon\b",
        r"\bhp\b",
        r"\bkill\b",
        r"\bloot\b",
    ]
]


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    sys.exit(1)


def main() -> None:
    for relative_path in EXPECTED_RUNTIME_PROPS:
        path = ROOT / relative_path
        if not path.is_file():
            fail(f"missing runtime prop: {relative_path}")
        if path.stat().st_size <= 0:
            fail(f"empty runtime prop: {relative_path}")

    scene_path = ROOT / "game" / "scenes" / "world" / "PlayerYard.tscn"
    scene_text = scene_path.read_text(encoding="utf-8")
    for snippet in EXPECTED_SCENE_SNIPPETS:
        if snippet not in scene_text:
            fail(f"PlayerYard missing art landing snippet: {snippet}")
    for pattern in FORBIDDEN:
        if pattern.search(scene_text):
            fail(f"PlayerYard contains forbidden gameplay term: {pattern.pattern}")

    manifest_path = ROOT / "production" / "assets" / "final_art" / "runtime_landing_pass1" / "art_landing_pass1_manifest.json"
    if not manifest_path.is_file():
        fail("missing art landing manifest")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if len(manifest.get("assets", [])) != 4:
        fail("art landing manifest should contain 4 runtime props")

    print("OK: validated Art Landing Pass 1 file and scene contract")


if __name__ == "__main__":
    main()
