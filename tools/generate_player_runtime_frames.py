from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ASSET_DIR = ROOT / "assets" / "art" / "greenfield_p0" / "characters" / "player"
OUTPUT = ROOT / "game" / "entities" / "player" / "PlayerRuntimeFrames.tres"
FRAME_SIZE = 128

SUFFIXES = [
    "down",
    "down_left",
    "left",
    "up_left",
    "up",
    "up_right",
    "right",
    "down_right",
]


@dataclass(frozen=True)
class AnimationSpec:
    state: str
    frame_count: int
    loop: bool
    speed: float


SPECS = [
    AnimationSpec("idle", 1, True, 1.0),
    AnimationSpec("walk", 4, True, 6.0),
    AnimationSpec("interact", 4, False, 8.0),
    AnimationSpec("pickup", 4, False, 8.0),
    AnimationSpec("water", 4, False, 7.0),
]


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def file_name(spec: AnimationSpec, suffix: str) -> str:
    if spec.frame_count == 1:
        return f"chr_player_base_{spec.state}_{suffix}_128.png"
    return f"chr_player_base_{spec.state}_{suffix}_4x128.png"


def relative_asset_path(spec: AnimationSpec, suffix: str) -> str:
    path = ASSET_DIR / file_name(spec, suffix)
    if not path.is_file():
        fail(f"missing runtime player asset: {path.relative_to(ROOT)}")
    return path.relative_to(ROOT).as_posix()


def build_resource_text() -> str:
    ext_resources: list[str] = []
    ext_ids: dict[str, str] = {}
    sub_resources: list[str] = []
    animations: list[str] = []

    ext_index = 1
    sub_index = 1

    def ensure_ext(path: str) -> str:
        nonlocal ext_index
        if path in ext_ids:
            return ext_ids[path]
        ext_id = f"tex_{ext_index}"
        ext_index += 1
        ext_ids[path] = ext_id
        ext_resources.append(f'[ext_resource type="Texture2D" path="res://{path}" id="{ext_id}"]')
        return ext_id

    for spec in SPECS:
        for suffix in SUFFIXES:
            asset_path = relative_asset_path(spec, suffix)
            ext_id = ensure_ext(asset_path)
            frame_refs: list[str] = []

            if spec.frame_count == 1:
                frame_refs.append(f'{{\n"duration": 1.0,\n"texture": ExtResource("{ext_id}")\n}}')
            else:
                for frame_index in range(spec.frame_count):
                    sub_id = f"AtlasTexture_{sub_index}"
                    sub_index += 1
                    sub_resources.append(
                        f'[sub_resource type="AtlasTexture" id="{sub_id}"]\n'
                        f'atlas = ExtResource("{ext_id}")\n'
                        f"region = Rect2({frame_index * FRAME_SIZE}, 0, {FRAME_SIZE}, {FRAME_SIZE})\n"
                    )
                    frame_refs.append(f'{{\n"duration": 1.0,\n"texture": SubResource("{sub_id}")\n}}')

            animation_name = f"player_{spec.state}_{suffix}"
            animations.append(
                '{\n"frames": [%s],\n"loop": %s,\n"name": &"%s",\n"speed": %.1f\n}'
                % (", ".join(frame_refs), "true" if spec.loop else "false", animation_name, spec.speed)
            )

    load_steps = len(ext_resources) + len(sub_resources) + 1
    sections = [f"[gd_resource type=\"SpriteFrames\" load_steps={load_steps} format=3]", ""]
    sections.extend(ext_resources)
    if sub_resources:
        sections.append("")
        sections.extend(sub_resources)
    sections.append("")
    sections.append("[resource]")
    sections.append(f"animations = [{', '.join(animations)}]")
    sections.append("")
    return "\n".join(sections)


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(build_resource_text(), encoding="utf-8")
    print(f"OK: wrote runtime SpriteFrames -> {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
