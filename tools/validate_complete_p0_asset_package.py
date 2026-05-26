from __future__ import annotations

import json
import struct
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
ITEMS = ROOT / "game/data/items.json"
ITEM_MANIFEST = ROOT / "production/assets/items/p0_item_icons/v001/p0_item_icons_manifest.json"
NPC_MANIFEST = ROOT / "production/assets/characters/p0_npc_complete_runtime/v001/p0_npc_complete_runtime_manifest.json"
P0_NPCS = {"aoi", "gen", "mika", "hana"}
DIRS = {"down", "up", "left", "right"}
EXPRS = {"neutral", "happy", "thinking"}


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def read_json(path: Path) -> Any:
    require(path.exists(), f"missing {path.relative_to(ROOT).as_posix()}")
    return json.loads(path.read_text(encoding="utf-8-sig"))


def png_size(path: Path) -> tuple[int, int]:
    require(path.exists(), f"missing png {path.relative_to(ROOT).as_posix()}")
    with path.open("rb") as handle:
        data = handle.read(24)
    require(data[:8] == b"\x89PNG\r\n\x1a\n", f"not png: {path.relative_to(ROOT).as_posix()}")
    return struct.unpack(">II", data[16:24])


def validate_items() -> None:
    items = read_json(ITEMS)
    manifest = read_json(ITEM_MANIFEST)
    require(manifest.get("package_id") == "p0_item_icons_v001", "item manifest package_id mismatch")
    require(manifest.get("status") == "usable", "item package must be usable")
    require(manifest.get("launch_quality_approved") is False, "item package must not claim launch approval")
    records = manifest.get("runtime_exports", [])
    require(len(records) == len(items), "item manifest must cover every item data row")
    records_by_id = {record.get("item_id"): record for record in records if isinstance(record, dict)}
    for item in items:
        item_id = item["item_id"]
        require(item_id in records_by_id, f"item manifest missing {item_id}")
        runtime = ROOT / item["icon"].removeprefix("res://")
        require(png_size(runtime) == (64, 64), f"item icon must be 64x64: {runtime.relative_to(ROOT).as_posix()}")
        require(records_by_id[item_id].get("runtime_file") == runtime.relative_to(ROOT).as_posix(), f"item runtime_file mismatch for {item_id}")


def validate_npcs() -> None:
    manifest = read_json(NPC_MANIFEST)
    require(manifest.get("package_id") == "p0_npc_complete_runtime_v001", "NPC manifest package_id mismatch")
    require(set(manifest.get("required_npc_ids", [])) == P0_NPCS, "NPC manifest P0 ids mismatch")
    require(set(manifest.get("required_idle_directions", [])) == DIRS, "NPC idle directions mismatch")
    require(set(manifest.get("required_walk_directions", [])) == DIRS, "NPC walk directions mismatch")
    require(set(manifest.get("required_portrait_expressions", [])) == EXPRS, "NPC portrait expressions mismatch")
    require(manifest.get("status") == "usable", "NPC package must be usable")
    require(manifest.get("launch_quality_approved") is False, "NPC package must not claim launch approval")
    records = manifest.get("runtime_exports", [])
    require(len(records) == 44, "NPC manifest must contain 44 runtime records")
    for npc_id in sorted(P0_NPCS):
        for direction in sorted(DIRS):
            idle = ROOT / f"assets/art/characters/npc/npc_{npc_id}_idle_{direction}_128.png"
            walk = ROOT / f"assets/art/characters/npc/npc_{npc_id}_walk_{direction}_4x128.png"
            require(png_size(idle) == (128, 128), f"idle size mismatch: {idle.relative_to(ROOT).as_posix()}")
            require(png_size(walk) == (512, 128), f"walk sheet size mismatch: {walk.relative_to(ROOT).as_posix()}")
        for expr in sorted(EXPRS):
            portrait = ROOT / f"assets/art/portraits/npc_{npc_id}_portrait_{expr}_512.png"
            require(png_size(portrait) == (512, 512), f"portrait size mismatch: {portrait.relative_to(ROOT).as_posix()}")


def main() -> None:
    validate_items()
    validate_npcs()
    print("OK: complete P0 item icon and NPC runtime asset package validates")


if __name__ == "__main__":
    main()