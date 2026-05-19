from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SCENE = ROOT / "scenes" / "regions" / "region_home_area.tscn"
REPORT = ROOT / ".codex" / "reports" / "home_area_object_inventory_2026-05-18.md"

LOCAL_FOREGROUND_OCCLUDERS = (
    "ForegroundStatic/LocalPlantOccluders/HouseFrontBushOccluder",
    "ForegroundStatic/LocalPlantOccluders/MailboxGrassOccluder",
    "ForegroundStatic/LocalPlantOccluders/BenchFlowerOccluder",
    "ForegroundStatic/LocalPlantOccluders/SouthEdgeFlowerOccluder",
)


@dataclass(frozen=True)
class ObjectContract:
    object_id: str
    category: str
    visual_nodes: tuple[str, ...]
    blocker_nodes: tuple[str, ...]
    interaction_nodes: tuple[str, ...]
    layering_rule: str
    interaction_rule: str


OBJECTS = (
    ObjectContract(
        "house_and_veranda",
        "structure",
        ("YSortWorld/Houses/CloudHouse/HouseBodyArtV007", "TileMapLayer_Detail/VerandaFloorArtV007", "ForegroundStatic/Occluders/HouseRoofOccluderArtV007"),
        ("YSortWorld/Houses/CloudHouse/HouseBlocker",),
        ("YSortWorld/Interactables/HouseDoorEntrance",),
        "House body, veranda floor, and roof occluder are separate layers; veranda/front path remains walkable.",
        "Door uses its own Area2D hotspot; house wall/base blocker must not cover steps or front path.",
    ),
    ObjectContract(
        "mailbox",
        "interactable_prop",
        ("YSortWorld/Props/Mailbox/MailboxArt",),
        ("YSortWorld/Props/Mailbox/PropBlocker",),
        ("YSortWorld/Interactables/MailboxInteract",),
        "Mailbox art is independent from bush/house layers.",
        "Mailbox has a front-side Area2D hotspot and a small post/base blocker.",
    ),
    ObjectContract(
        "well",
        "interactable_prop",
        ("YSortWorld/Props/Well/WellArt",),
        ("YSortWorld/Props/Well/PropBlocker",),
        ("YSortWorld/Interactables/WellInteract",),
        "Well art is independent from paths and grass; roof is not a walking blocker by itself.",
        "Well has a south/front Area2D hotspot and a blocker around the stone base.",
    ),
    ObjectContract(
        "bench",
        "interactable_prop",
        ("YSortWorld/Props/Bench/BenchArt",),
        ("YSortWorld/Props/Bench/PropBlocker",),
        ("YSortWorld/Interactables/BenchRestInteract",),
        "Bench is separate from fence/ground; player can stand in front while the seat/base blocks movement.",
        "Bench rest uses its own Area2D hotspot; rest anchor remains separate from visual prop origin.",
    ),
    ObjectContract(
        "road_sign",
        "interactable_prop",
        ("YSortWorld/Props/RoadSign/RoadSignArt",),
        ("YSortWorld/Props/RoadSign/PropBlocker",),
        ("YSortWorld/Interactables/RoadSignInteract",),
        "Road sign is separate from back-farm path and fence.",
        "Road sign has a small front-side hotspot and base blocker.",
    ),
    ObjectContract(
        "trees",
        "occluding_nature",
        ("YSortWorld/Trees/BigShadeTree/TreeLeftTrunkArtV007", "YSortWorld/Trees/PersimmonTree/TreeRightTrunkArtV007", "ForegroundStatic/Occluders/TreeLeftCanopyOccluderArtV007", "ForegroundStatic/Occluders/TreeRightCanopyOccluderArtV007"),
        ("YSortWorld/Trees/BigShadeTree/BigShadeRootBlocker", "YSortWorld/Trees/BigShadeTree/TreeBlocker", "YSortWorld/Trees/PersimmonTree/PersimmonRootBlocker", "YSortWorld/Trees/PersimmonTree/TreeBlocker", "YSortWorld/Trees/SmallLeftTree/TreeBlocker"),
        (),
        "Trunks/roots are YSort world objects; canopies are visual occluders only.",
        "No generic tree interaction in this pass; blockers are root/trunk only.",
    ),
    ObjectContract(
        "fences_and_back_rail",
        "barrier",
        ("YSortWorld/Barriers/FenceLeft/FenceLeftGuide", "YSortWorld/Barriers/FenceRight/FenceRightGuide", "YSortWorld/Barriers/BackFarmRail/BackFarmRailGuide"),
        ("YSortWorld/Barriers/FenceLeft/FenceLeftBlocker", "YSortWorld/Barriers/FenceRight/FenceRightBlocker", "YSortWorld/Barriers/BackFarmRail/BackFarmRailBlocker"),
        (),
        "Fence/rail visuals are separate from trees, paths, and benches.",
        "No interaction; they are directional walking barriers only.",
    ),
    ObjectContract(
        "foreground_plants",
        "foreground_occlusion",
        ("ForegroundStatic/ForegroundGrassArtV007",) + LOCAL_FOREGROUND_OCCLUDERS,
        (),
        (),
        "Broad full-scene plate is disabled; local plant occlusion is split into small independent cutouts.",
        "No interaction; visual occlusion only, with no broad full-width coverage over the player path.",
    ),
    ObjectContract(
        "region_exits",
        "navigation",
        (),
        (),
        ("YSortWorld/Interactables/BackyardFarmEntrance", "YSortWorld/Interactables/PlayerYardEntrance"),
        "Region exits are not props and must not be merged into prop art layers.",
        "Each exit has its own Area2D hotspot and target scene/region contract.",
    ),
)


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def node_block(scene_text: str, node_path: str) -> str:
    parts = node_path.split("/")
    name = parts[-1]
    parent = "/".join(parts[:-1])
    if parent:
        pattern = rf'\[node name="{re.escape(name)}" [^\]]*parent="{re.escape(parent)}"[^\]]*\]'
    else:
        pattern = rf'\[node name="{re.escape(name)}" [^\]]*\]'
    match = re.search(pattern + r".*?(?=\n\[node |\n\[connection |\Z)", scene_text, re.S)
    if match is None:
        fail(f"missing node for object inventory: {node_path}")
    return match.group(0)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)



def require_sparse_cutout(node_path: str, block: str) -> None:
    match = re.search(r'texture_path = "res://([^"]+)"', block)
    require(match is not None, f"{node_path} must declare texture_path")
    asset_path = ROOT / match.group(1)
    require(asset_path.exists(), f"{node_path} missing cutout PNG: {asset_path}")
    image = Image.open(asset_path).convert("RGBA")
    alpha_values = list(image.getchannel("A").getdata())
    pixel_count = max(1, len(alpha_values))
    coverage = sum(1 for value in alpha_values if value > 12) / pixel_count
    average_alpha = sum(alpha_values) / pixel_count
    max_alpha = max(alpha_values) if alpha_values else 0
    require(image.width <= 1800 and image.height <= 1100, f"{node_path} cutout is too large: {image.width}x{image.height}")
    require(coverage <= 0.78, f"{node_path} cutout alpha is too broad: coverage={coverage:.3f}")
    require(average_alpha <= 65.0, f"{node_path} cutout alpha is too opaque: avg={average_alpha:.1f}")
    require(max_alpha <= 120, f"{node_path} cutout max alpha is too high: max={max_alpha}")

def main() -> None:
    scene_text = SCENE.read_text(encoding="utf-8")
    lines: list[str] = [
        "# HomeArea Object Inventory",
        "",
        "Updated: 2026-05-18",
        "",
        "Purpose: keep HomeArea runtime objects separated so visual layers, blockers, and interaction logic do not collapse back into broad mixed rectangles.",
        "",
        "| Object | Category | Visual Layers | Blockers | Interactions | Layering Rule | Interaction Rule |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]

    for contract in OBJECTS:
        for node_path in contract.visual_nodes + contract.blocker_nodes + contract.interaction_nodes:
            block = node_block(scene_text, node_path)
            if node_path.endswith("ForegroundGrassArtV007"):
                require("visible = false" in block, "broad foreground grass plate must stay disabled")
            if node_path in LOCAL_FOREGROUND_OCCLUDERS:
                require("Sprite2D" in block, f"{node_path} must be a small Sprite2D cutout")
                require('texture_path = "res://production/assets/regions/home_area_formal/v001/layers/foreground_cutouts/' in block, f"{node_path} must load a dedicated foreground cutout PNG")
                require('metadata/occluder_scope = "local_plant_cutout"' in block, f"{node_path} must declare local plant cutout scope")
                require_sparse_cutout(node_path, block)
            if node_path in contract.interaction_nodes:
                shape_path = f"{node_path}/CollisionShape2D"
                shape_block = node_block(scene_text, shape_path)
                require("RectangleShape2D_hotspot" in shape_block, f"{node_path} must have a real hotspot shape")
        lines.append(
            "| {object_id} | {category} | {visuals} | {blockers} | {interactions} | {layering_rule} | {interaction_rule} |".format(
                object_id=contract.object_id,
                category=contract.category,
                visuals="<br>".join(contract.visual_nodes) if contract.visual_nodes else "none",
                blockers="<br>".join(contract.blocker_nodes) if contract.blocker_nodes else "none",
                interactions="<br>".join(contract.interaction_nodes) if contract.interaction_nodes else "none",
                layering_rule=contract.layering_rule,
                interaction_rule=contract.interaction_rule,
            )
        )

    lines.extend([
        "",
        "## Visual QA Points",
        "",
        "- House/front steps: player must stand on grass, lower step, and front path without being blocked by the house body blocker.",
        "- Mailbox: player stands in front/under nearby bush cover; mailbox post/base blocks, bush does not become an interaction target.",
        "- Bench: player stands at the front of the bench; bench base blocks, bench interaction hotspot is separate from fence/tree layers.",
        "- Well: player can approach the south/front edge; the stone base blocks but the roof art is visual only.",
        "- Trees/fences: trunks, roots, and fences block; canopies are visual occluders only.",
        "- Foreground plants: broad full-width occluder is disabled until replaced by local cutouts.",
    ])

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"OK: HomeArea object inventory written to {REPORT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()