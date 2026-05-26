from __future__ import annotations

from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
OUTDOOR_GD = ROOT / "game" / "scenes" / "world" / "OutdoorWorld.gd"
VILLAGE_CAPTURE_GD = ROOT / "tools" / "capture_village_v002_semantic_layer_godot_review.gd"
MOUNTAIN_CAPTURE_GD = ROOT / "tools" / "capture_mountain_hut_semantic_layer_godot_review.gd"
VILLAGE_REPORT = ROOT / ".codex" / "reports" / "village_v002_semantic_layer_godot_review_2026-05-26.md"
MOUNTAIN_REPORT = ROOT / ".codex" / "reports" / "mountain_hut_semantic_layer_godot_review_2026-05-26.md"
SOCKET_TEXTURE = ROOT / "assets" / "art" / "greenfield_p0" / "world" / "socket_bridges" / "village_mountain_hut_socket_bridge.png"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read(path: Path) -> str:
    require(path.exists(), f"missing required file: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8")


def main() -> None:
    outdoor_text = read(OUTDOOR_GD)
    village_capture_text = read(VILLAGE_CAPTURE_GD)
    mountain_capture_text = read(MOUNTAIN_CAPTURE_GD)
    village_report_text = read(VILLAGE_REPORT)
    mountain_report_text = read(MOUNTAIN_REPORT)
    require(SOCKET_TEXTURE.exists(), f"missing socket bridge texture: {SOCKET_TEXTURE.relative_to(ROOT)}")
    require(SOCKET_TEXTURE.stat().st_size > 1_000, "socket bridge texture is unexpectedly small")
    with Image.open(SOCKET_TEXTURE) as socket_image:
        require(socket_image.width >= 72, "socket bridge texture should be wide enough to overlap both region edges")
        require(socket_image.height >= 220, "socket bridge texture should cover the full Village/MountainHut seam height")
    require("sprite.z_index = -29" in outdoor_text, "socket bridge sprite should render above BaseGround but below detail layers")

    required_outdoor_tokens = [
        "VILLAGE_MOUNTAIN_HUT_SOCKET_BRIDGE_NODE",
        "VILLAGE_MOUNTAIN_HUT_SOCKET_TEXTURE_PATH",
        "VILLAGE_MOUNTAIN_HUT_SOCKET_TEXTURE_POSITION",
        "VILLAGE_MOUNTAIN_HUT_SOCKET_POINTS",
        "func _compose_world_socket_bridges",
        "func _add_village_mountain_hut_socket_bridge",
        "func _load_socket_bridge_texture",
        "VillageMountainHutSocketBridge",
        "PaintedSocketBridge",
        "socket_bridge",
        "village_to_mountain_hut",
        "Sprite2D",
        "village_mountain_hut_socket_bridge.png",
    ]
    for token in required_outdoor_tokens:
        require(token in outdoor_text, f"OutdoorWorld socket bridge missing token: {token}")
    require(
        outdoor_text.find("_compose_world_ground_fill()") < outdoor_text.find("_compose_world_socket_bridges()"),
        "OutdoorWorld should compose socket bridges after the world fill exists",
    )

    required_village_tokens = [
        "MOUNTAIN_HUT_LAYER_MANIFEST_PATH",
        "MountainHutSemanticLayerReference",
        "v004_semantic_layers_exported_pending_review",
        "_load_mountain_hut_reference_manifest",
        '_install_semantic_layers(mountain_hut_section, mountain_hut_manifest, "MountainHutSemanticLayerReference")',
    ]
    for token in required_village_tokens:
        require(token in village_capture_text, f"Village review should install current MountainHut reference: {token}")

    required_mountain_tokens = [
        "VILLAGE_V002_LAYER_MANIFEST_PATH",
        "VillageV002SemanticLayerReference",
        "v002_semantic_layers_exported_pending_review",
        "_load_village_v002_reference_manifest",
        '_install_semantic_layers(village_section, village_manifest, "VillageV002SemanticLayerReference")',
    ]
    for token in required_mountain_tokens:
        require(token in mountain_capture_text, f"MountainHut review should install current Village v002 reference: {token}")

    required_report_tokens = [
        "socket bridge",
        "review-only",
        "runtime_replacement=false",
        "launch_quality_approved=false",
    ]
    for token in required_report_tokens:
        require(token in village_report_text, f"Village report missing socket bridge note: {token}")
        require(token in mountain_report_text, f"MountainHut report missing socket bridge note: {token}")

    print("OK: Village-to-MountainHut socket bridge static validation passed")


if __name__ == "__main__":
    main()
