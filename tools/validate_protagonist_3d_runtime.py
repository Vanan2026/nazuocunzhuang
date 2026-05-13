from __future__ import annotations

import json
import struct
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GLB_PATH = ROOT / "assets" / "3d" / "processed" / "protagonist_3d" / "protagonist_rigged_anim_v002_real.glb"
CHARACTER_SCENE = ROOT / "scenes" / "3d" / "protagonist_3d_character.tscn"
PLAYTEST_SCENE = ROOT / "scenes" / "dev" / "hunyuan_scene_001_protagonist_3d_playtest.tscn"
CHARACTER_SCRIPT = ROOT / "scripts" / "world" / "protagonist_3d_controller.gd"

REQUIRED_CLIPS = {"idle", "walk", "interact", "sit_down", "sit_idle", "stand_up"}
GLB_MAGIC = 0x46546C67
JSON_CHUNK = 0x4E4F534A


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def read_glb_json(path: Path) -> dict:
    data = path.read_bytes()
    require(len(data) >= 20, f"glb too short: {path}")
    magic, _version, total_len = struct.unpack_from("<III", data, 0)
    require(magic == GLB_MAGIC, "invalid glb magic")
    require(total_len == len(data), "invalid glb total length")

    offset = 12
    while offset + 8 <= len(data):
        chunk_len, chunk_type = struct.unpack_from("<II", data, offset)
        offset += 8
        chunk = data[offset : offset + chunk_len]
        offset += chunk_len
        if chunk_type == JSON_CHUNK:
            return json.loads(chunk.decode("utf-8"))
    fail("missing json chunk")


def validate_glb() -> None:
    require(GLB_PATH.exists(), f"missing glb: {GLB_PATH}")
    gltf = read_glb_json(GLB_PATH)

    clips = {a.get("name", "") for a in gltf.get("animations", [])}
    missing = sorted(REQUIRED_CLIPS - clips)
    require(not missing, f"missing clips: {', '.join(missing)}")

    require(len(gltf.get("skins", [])) >= 1, "missing skin rig")
    require(len(gltf.get("meshes", [])) >= 1, "missing mesh")


def validate_scene_contract() -> None:
    for path in (CHARACTER_SCENE, PLAYTEST_SCENE, CHARACTER_SCRIPT):
        require(path.exists(), f"missing file: {path}")

    character_scene_text = CHARACTER_SCENE.read_text(encoding="utf-8")
    require("protagonist_rigged_anim_v002_real.glb" in character_scene_text, "character scene must instance processed glb")
    require("protagonist_3d_controller.gd" in character_scene_text, "character scene must attach controller script")

    playtest_text = PLAYTEST_SCENE.read_text(encoding="utf-8")
    require("hunyuan_scene_001_preview.tscn" in playtest_text, "playtest must include preview world")
    require("protagonist_3d_character.tscn" in playtest_text, "playtest must include protagonist scene")


def main() -> None:
    validate_glb()
    validate_scene_contract()
    print("OK: protagonist 3d runtime contract validated")


if __name__ == "__main__":
    main()
