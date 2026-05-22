from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HANDOFF = ROOT / "production" / "assets" / "external_gpt_handoff" / "greenfield_p0" / "v001"
REQUEST_MANIFEST = HANDOFF / "asset_request_manifest.json"
WORKFLOW_MANIFEST = ROOT / "production" / "assets" / "base_asset_pack" / "v001" / "workflow_manifest.json"
INCOMING = HANDOFF / "incoming"


BATCH_TITLES = {
    "batch_b_regions": "Batch B - Region Mother Images And Runtime Layers Request",
}


REGION_SPACE_BRIEFS = {
    "home_area": (
        "Private home yard plus public front lane. The house must sit above its yard paths, never on the road. "
        "Mailbox and bench sit beside the public lane, and the well stays inside the private yard with a narrow side footpath."
    ),
    "village": (
        "Small lived-in village center with through lanes, a modest plaza edge, doorstep paths, and a small landmark. "
        "Houses must be set back from roads with readable door approaches, not pasted into the lane."
    ),
    "back_farm": (
        "Working farm area with a lower access lane, central service lane, clear shed approach, and field blocks on either side. "
        "Field plots must leave visible service gaps and must not cover or interrupt the roads."
    ),
    "forest_edge": (
        "Loose forest border with a broken moss trail, forage spur, and orchard link. Keep tree masses organic but leave the path readable."
    ),
    "orchard": (
        "Orchard with diagonal service path and cart gap through tree rows. Rows may be rhythmic but should not become a perfect grid."
    ),
    "pond": (
        "Pond bank with a crescent walking path, small dock/rest point, south rest spur, and north arrival path. Water edge and bank path must be distinct."
    ),
    "mountain_path": (
        "Stone switchback trail with clear elevation rhythm. The path should feel climbable and continuous, not a decorative zigzag over cliffs."
    ),
    "mountain_hut": (
        "Quiet hut workyard with curved arrival path, porch, herb patch, woodpile side path, and ridge link. The hut should not block the access path."
    ),
    "mountain": (
        "Rocky trail and stream crossing with a clearing spur and hut descent. Rocks frame the path while preserving traversable continuity."
    ),
    "cliff_view": (
        "Cliff overlook with contour ledge path and rest/view spur. The walking area must read as safe ground, with the vista beyond it."
    ),
}


LAYER_BRIEFS = {
    "painted_source": (
        "complete region source/review mother; fully painted composite for judging layout, mood, object placement, and seam readiness"
    ),
    "base_ground": (
        "opaque base layer only: terrain, roads, water/soil/stone base, and walkable ground shapes; no tall props or foreground occluders"
    ),
    "terrain_details": (
        "transparent detail layer: grass tufts, soil accents, small stones, leaves, and local texture variation; no blocking objects"
    ),
    "behind_player_structures": (
        "transparent back/depth layer: walls, upper structures, distant tree masses, slopes, and forms that should render behind the player"
    ),
    "ysort_props_structures": (
        "transparent interactive/depth layer: readable props, structures, crops, benches, wells, doors, rocks, or trees with bottom anchors for Y-sort"
    ),
    "foreground_occlusion": (
        "transparent foreground layer: sparse canopy, front eaves, tall grass, rails, or ledge fronts that may pass in front of the player"
    ),
    "shadow_overlay": (
        "transparent soft shadow layer: contact shadows and grounding shadows only; avoid heavy black shadows"
    ),
    "light_weather_overlay_spring": (
        "transparent spring overlay: subtle warm light, fresh foliage hints, soft pollen or blossom accents"
    ),
    "light_weather_overlay_summer": (
        "transparent summer overlay: gentle warmer light, fuller foliage accents, soft humid atmosphere"
    ),
    "light_weather_overlay_autumn": (
        "transparent autumn overlay: low-saturation fallen leaves and mellow golden light"
    ),
    "light_weather_overlay_winter": (
        "transparent winter overlay: light snow dusting or cool seasonal tint while preserving path readability"
    ),
}


def load_json(path: Path) -> dict:
    if not path.exists():
        raise SystemExit(f"missing required file: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def region_id_for_asset(asset_id: str, region_ids: list[str]) -> str:
    for region_id in sorted(region_ids, key=len, reverse=True):
        if asset_id == f"{region_id}_painted_source" or asset_id.startswith(f"{region_id}_"):
            return region_id
    return ""


def layer_id_for_asset(asset_id: str, region_id: str) -> str:
    prefix = f"{region_id}_"
    if asset_id == f"{region_id}_painted_source":
        return "painted_source"
    return asset_id.removeprefix(prefix)


def format_points(points: list[list[int]]) -> str:
    return ", ".join(f"({point[0]}, {point[1]})" for point in points)


def road_summary(layout_profile: dict) -> list[str]:
    lines = []
    for road in layout_profile.get("road_paths", []):
        points = road.get("pixel_points", [])
        role = road.get("role", "road")
        road_id = road.get("id", "road")
        width = road.get("width_px", "?")
        lines.append(f"- `{road_id}` / role `{role}` / width `{width}px` / points: {format_points(points)}")
    return lines


def object_zone_summary(layout_profile: dict) -> list[str]:
    zones = layout_profile.get("object_zones", [])
    if not zones:
        return ["- No required object-zone rectangles in manifest; preserve the road motif and leave walkable gaps around major props."]
    lines = []
    for zone in zones:
        rect = zone.get("rect", [])
        lines.append(
            f"- `{zone.get('id')}` / role `{zone.get('role')}` / rect `{rect}` / relation: {zone.get('relation')}"
        )
    return lines


def group_batch_assets(request_manifest: dict, workflow_manifest: dict, priority: str) -> dict[str, list[dict]]:
    region_ids = [region["region_id"] for region in workflow_manifest["regions"]]
    grouped: dict[str, list[dict]] = defaultdict(list)
    for asset in request_manifest["assets"]:
        if asset["priority"] != priority:
            continue
        region_id = region_id_for_asset(asset["asset_id"], region_ids)
        if not region_id:
            raise SystemExit(f"could not infer region for asset: {asset['asset_id']}")
        grouped[region_id].append(asset)
    return grouped


def sort_assets_for_region(region_id: str, assets: list[dict]) -> list[dict]:
    order = [
        f"{region_id}_painted_source",
        f"{region_id}_base_ground",
        f"{region_id}_terrain_details",
        f"{region_id}_behind_player_structures",
        f"{region_id}_ysort_props_structures",
        f"{region_id}_foreground_occlusion",
        f"{region_id}_shadow_overlay",
        f"{region_id}_light_weather_overlay_spring",
        f"{region_id}_light_weather_overlay_summer",
        f"{region_id}_light_weather_overlay_autumn",
        f"{region_id}_light_weather_overlay_winter",
    ]
    index = {asset_id: i for i, asset_id in enumerate(order)}
    return sorted(assets, key=lambda asset: index.get(asset["asset_id"], 999))


def write_region_assets_section(
    lines: list[str],
    *,
    request_manifest: dict,
    region: dict,
    assets: list[dict],
    scene_number: int,
) -> None:
    region_id = region["region_id"]
    layout_profile = region["layout_profile"]
    connectors = layout_profile.get("seam_connectors", {})
    lines.extend([
        f"## Scene {scene_number:02d}: {region_id} / {region.get('display_name', region_id)}",
        "",
        f"- Canvas: `{region['canvas_size'][0]}x{region['canvas_size'][1]}`",
        "- Registration blueprint: 外部 GPT 先按本文件 `GPT Blueprint Requirement` 绘制/确认，不由 Codex 预先生图。",
        f"- Incoming root: `{INCOMING.relative_to(ROOT).as_posix()}`",
        f"- Road motif: `{layout_profile.get('road_motif')}`",
        f"- Road signature: `{layout_profile.get('road_signature')}`",
        f"- Composition focal point: `{layout_profile.get('composition_focal_point')}`",
        f"- Seam connectors: `{connectors}`",
        f"- Space brief: {REGION_SPACE_BRIEFS.get(region_id, 'Preserve a believable rural region layout with readable paths and usable object placement.')}",
        "",
        "### Production Flow",
        "",
        "1. Generate and confirm `painted_source` first.",
        "2. Treat `painted_source` as the only composition source.",
        "3. Split/mask/paint `base_ground` and transparent runtime layers from that same composition.",
        "4. Export every PNG at the full canvas size. Do not crop, resize, rotate, or auto-trim transparent layers.",
        "5. In Godot, every layer will be placed at position `(0, 0)`, scale `1`, rotation `0`, under the same parent.",
        "",
        "### Registration Contract",
        "",
        "- Required: same canvas size, origin, perspective, composition, coordinate system, pivot, scale, and rotation across all 11 PNGs.",
        "- Required: transparent layers keep full canvas alpha outside painted pixels.",
        "- Required: houses, shrine, bench, doors, roads, shadows, and foreground occlusion must align when stacked.",
        "- Guide: manifest road points, road widths, object rectangles, and seam connectors define spatial logic.",
        "- Allowed: natural hand-painted variation on road edges, grass, flowers, pebbles, leaves, and texture marks.",
        "",
        "### GPT Blueprint Requirement",
        "",
        "- 在生成 `painted_source` 之前，请先由外部 GPT 绘制一张 registration blueprint / engineering diagram。",
        f"- Blueprint 画布也是 `{region['canvas_size'][0]}x{region['canvas_size'][1]}`，用来确认构图注册，不作为 Godot runtime asset。",
        "- Blueprint 应清楚标注：canvas 边界、主路/支路、road role、road width、object-zone rect、seam connector、composition focal point、完整画布导出规则。",
        "- Blueprint 可以比 Codex 程序图更美观，但必须表达同一个空间逻辑：房子退到路外、门口可达、bench 不在路中心、shrine 有窄入口、道路不断裂。",
        "- Blueprint 确认后，再生成 `village_painted_source`；所有 runtime layers 从该母图拆层/遮罩/补绘。",
        "",
        "### Road Contract",
        "",
    ])
    lines.extend(road_summary(layout_profile))
    lines.extend(["", "### Object-Zone Contract", ""])
    lines.extend(object_zone_summary(layout_profile))
    lines.extend(["", "### Runtime Layer Order For Godot", ""])
    layer_order = [
        ("base_ground", "z_index 0; opaque bottom terrain/roads"),
        ("terrain_details", "z_index 1; transparent terrain accents"),
        ("behind_player_structures", "z_index 2; structures/trees behind player"),
        ("ysort_props_structures", "z_index 3 or later split into independent props for exact Y-sort"),
        ("shadow_overlay", "z_index 4; soft transparent shadow layer"),
        ("foreground_occlusion", "above player; foreground canopy/eaves/occluders"),
        ("light_weather_overlay_*", "seasonal overlay enabled one at a time"),
    ]
    for layer_name, note in layer_order:
        lines.append(f"- `{layer_name}`: {note}.")
    lines.extend(["", "### Asset Requests", ""])

    if len(assets) != 11:
        raise SystemExit(f"{region_id} expected 11 assets, got {len(assets)}")
    for number, asset in enumerate(assets, start=1):
        size = asset["expected_size"]
        layer_id = layer_id_for_asset(asset["asset_id"], region_id)
        layer_brief = LAYER_BRIEFS.get(layer_id, "region runtime layer")
        alpha_rule = "transparent PNG with clean alpha; full canvas, no crop" if asset["transparent"] else "fully opaque PNG"
        full_path = (INCOMING / asset["incoming_path"]).relative_to(ROOT)
        if layer_id == "painted_source":
            prompt = (
                f"{request_manifest['style_lock']} Create the confirmed painted_source mother image for {region_id}; "
                f"exact canvas {size[0]}x{size[1]} px; fully opaque PNG. First create/confirm a registration blueprint from this request, then use it as the spatial guide. "
                f"{REGION_SPACE_BRIEFS.get(region_id, '')} Keep roads, object zones, seam connectors, and composition readable. "
                "This image becomes the only composition source for all runtime layers."
            )
        else:
            prompt = (
                f"{request_manifest['style_lock']} Create {layer_id} for {region_id}; exact canvas {size[0]}x{size[1]} px; "
                f"{alpha_rule}. Derive/split/mask/paint this layer from the confirmed {region_id}_painted_source composition, "
                "not as a newly composed scene. Keep registration-perfect alignment: same full canvas, origin, scale, rotation, perspective, and composition. "
                f"Layer requirement: {layer_brief}."
            )
        lines.extend([
            f"#### {number}. {asset['asset_id']}",
            "",
            "- 文件路径：",
            "```text",
            asset["incoming_path"],
            "```",
            "",
            "- 完整放置路径：",
            "```text",
            full_path.as_posix(),
            "```",
            "",
            f"- 尺寸：`{size[0]}x{size[1]}`",
            f"- Alpha：`{alpha_rule}`",
            f"- Layer brief: {layer_brief}.",
            "- Prompt:",
            "",
            "```text",
            prompt,
            "```",
            "",
            "- Negative:",
            "",
            "```text",
            asset["negative_prompt"],
            "```",
            "",
        ])


def write_batch_b_region_request(region_id: str) -> Path:
    request_manifest = load_json(REQUEST_MANIFEST)
    workflow_manifest = load_json(WORKFLOW_MANIFEST)
    grouped = group_batch_assets(request_manifest, workflow_manifest, "batch_b_regions")
    regions = workflow_manifest["regions"]
    region_by_id = {region["region_id"]: region for region in regions}
    if region_id not in region_by_id:
        raise SystemExit(f"unknown region: {region_id}")
    scene_number = [region["region_id"] for region in regions].index(region_id) + 1
    region = region_by_id[region_id]
    assets = sort_assets_for_region(region_id, grouped[region_id])
    output = HANDOFF / f"batch_02_scene_{scene_number:02d}_{region_id}_request.md"

    lines = [
        f"# Batch 02 / Scene {scene_number:02d} - {region.get('display_name', region_id)} Registration-Perfect Region Request",
        "",
        "用途：这是第 2 批区域资产中的单场景执行文件。它替代 110 张大批文件作为本次外部生产输入。",
        "",
        "核心标准：`registration-perfect` 图层注册一致；不是按 manifest 坐标逐像素描摹美术笔触。",
        "",
        "验收命令：",
        "",
        "```powershell",
        "py -3.12 tools\\validate_greenfield_p0_external_asset_intake.py --allow-partial",
        "```",
        "",
        "## Global Style Lock",
        "",
        request_manifest["style_lock"],
        "",
        "## Global Negative Prompt",
        "",
        request_manifest["negative_prompt"],
        "",
    ]
    write_region_assets_section(
        lines,
        request_manifest=request_manifest,
        region=region,
        assets=assets,
        scene_number=scene_number,
    )
    lines.extend([
        "## 本子批验收标准",
        "",
        "- 共 11 张 PNG，全都按上方路径放入 `incoming/`。",
        "- 11 张 PNG 全部为 `1800x1200`。",
        "- `village_painted_source` 与 `village_base_ground` 必须完全不透明。",
        "- 其他 9 张 runtime layers 必须透明背景、完整画布、不裁切、不缩放、不旋转。",
        "- 所有 layers 叠加时必须对齐：房屋、shrine、bench、门口、道路、阴影、前景遮挡不能漂移。",
        "- 道路/对象/seam 参考 blueprint 和 manifest，保持空间逻辑；手绘边缘和细节允许自然浮动。",
        "- 不得出现房屋压路、道路穿房、bench 在路中心、shrine 堵路、路径被装饰截断、UI 文本、水印、战斗元素或科幻 HUD。",
    ])
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output


def write_batch_b_request() -> Path:
    request_manifest = load_json(REQUEST_MANIFEST)
    workflow_manifest = load_json(WORKFLOW_MANIFEST)
    grouped = group_batch_assets(request_manifest, workflow_manifest, "batch_b_regions")
    regions = workflow_manifest["regions"]

    lines = [
        f"# {BATCH_TITLES['batch_b_regions']}",
        "",
        "用途：生产 Greenfield P0 的 10 个区域母图、精绘源图和 Godot runtime layers。",
        "",
        "交付方式：请在外部生成 PNG 后，按每个条目的相对路径放入 `incoming/` 目录。",
        "",
        "Incoming 根目录：",
        "",
        "```text",
        str(INCOMING.relative_to(ROOT)).replace("\\", "/"),
        "```",
        "",
        "验收命令：",
        "",
        "```powershell",
        "py -3.12 tools\\validate_greenfield_p0_external_asset_intake.py --allow-partial",
        "```",
        "",
        "## 全局风格锁定",
        "",
        request_manifest["style_lock"],
        "",
        "## 全局负面要求",
        "",
        request_manifest["negative_prompt"],
        "",
        "## 第二批总体要求",
        "",
        "- 本批共 `110` 张 PNG：10 个区域，每个区域 11 张。",
        "- 每个区域先做并确认 `painted_source` 完整精绘母图；runtime layers 必须从同一张母图拆层/遮罩/补绘生成，不要分别重新生成新构图。",
        "- 目标是 `registration-perfect`：同一区域 11 张图必须完全同尺寸、同原点、同透视、同构图、同坐标系；叠加后应复原 painted_source 的主要空间关系。",
        "- Manifest 坐标是工程蓝图和空间逻辑约束，不要求每个手绘边缘、草花石头笔触逐像素复刻坐标表。",
        "- `painted_source` 与 `base_ground` 必须完全不透明；其他 layers 必须透明背景并保留干净 alpha。",
        "- 透明 layers 必须导出完整区域画布，不能裁切到物体 bounding box，不能自动贴边。",
        "- 道路、房屋、水井、田地、树、池塘、山路等必须遵守生活逻辑：物件在路边或可到达位置，不得压在路中心；田块不得覆盖路；建筑不得堵死入口。",
        "- 构图不能过分工整或十区域套同一模板；每个区域必须有自己的道路节奏、功能重心和自然边界。",
        "- 边缘 seam/socket 必须留出可连接空间，后续会用于无缝地图拼装。",
        "- 不要把 UI、文字、水印、角色、战斗元素、怪物、武器画进区域图。",
        "",
        "## Runtime Layer 规则",
        "",
    ]
    for layer_id, brief in LAYER_BRIEFS.items():
        lines.append(f"- `{layer_id}`: {brief}.")
    lines.append("")

    for region in regions:
        region_id = region["region_id"]
        assets = sort_assets_for_region(region_id, grouped[region_id])
        layout_profile = region["layout_profile"]
        connectors = layout_profile.get("seam_connectors", {})
        lines.extend([
            f"## Region: {region_id} / {region.get('display_name', region_id)}",
            "",
            f"- Canvas: `{region['canvas_size'][0]}x{region['canvas_size'][1]}`",
            f"- Road motif: `{layout_profile.get('road_motif')}`",
            f"- Road signature: `{layout_profile.get('road_signature')}`",
            f"- Composition focal point: `{layout_profile.get('composition_focal_point')}`",
            f"- Seam connectors: `{connectors}`",
            f"- Space brief: {REGION_SPACE_BRIEFS.get(region_id, 'Preserve a believable rural region layout with readable paths and usable object placement.')}",
            "",
            "### Road contract",
            "",
        ])
        lines.extend(road_summary(layout_profile))
        lines.extend(["", "### Object-zone contract", ""])
        lines.extend(object_zone_summary(layout_profile))
        lines.extend([
            "",
            "### Registration contract",
            "",
            "- `painted_source` is the only composition source for this region.",
            "- All runtime layers must keep the full canvas, origin `(0, 0)`, scale `1`, rotation `0`, and the same 3/4 perspective as `painted_source`.",
            "- Roads and object zones should follow the manifest structure and remain spatially readable; natural hand-painted edge variation is allowed.",
            "- Details such as grass, flowers, pebbles, leaves, and brush texture do not need pixel-perfect correspondence to manifest points.",
        ])
        lines.extend(["", "### Asset requests", ""])

        if len(assets) != 11:
            raise SystemExit(f"{region_id} expected 11 assets, got {len(assets)}")
        for number, asset in enumerate(assets, start=1):
            size = asset["expected_size"]
            layer_id = layer_id_for_asset(asset["asset_id"], region_id)
            layer_brief = LAYER_BRIEFS.get(layer_id, "region runtime layer")
            alpha_rule = "transparent PNG with clean alpha" if asset["transparent"] else "fully opaque PNG"
            full_path = (INCOMING / asset["incoming_path"]).relative_to(ROOT)
            prompt = (
                f"{asset['prompt']} Region-specific requirement: {REGION_SPACE_BRIEFS.get(region_id, '')} "
                f"Layer requirement: {layer_brief}. Preserve road contract, object-zone logic, seam connector readability, "
                "and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. "
                "Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels."
            )
            lines.extend([
                f"#### {number}. {asset['asset_id']}",
                "",
                "- 文件路径：",
                "```text",
                asset["incoming_path"],
                "```",
                "",
                "- 完整放置路径：",
                "```text",
                str(full_path).replace("\\", "/"),
                "```",
                "",
                f"- 尺寸：`{size[0]}x{size[1]}`",
                f"- Alpha：`{alpha_rule}`",
                f"- Layer brief: {layer_brief}.",
                "- Prompt:",
                "",
                "```text",
                prompt,
                "```",
                "",
                "- Negative:",
                "",
                "```text",
                asset["negative_prompt"],
                "```",
                "",
            ])

    lines.extend([
        "## 本批验收标准",
        "",
        "- 110 张 PNG 全部按路径放入 `incoming/`。",
        "- 文件尺寸必须与条目完全一致。",
        "- `painted_source` 和 `base_ground` 不透明；其他 runtime layers 保持透明背景。",
        "- 所有透明 layers 必须保留完整区域画布，不裁切、不缩放、不自动贴边。",
        "- 同一区域所有 layers 必须 registration-perfect：像素级同画布、同原点、同透视、同坐标系，不能出现单层偏移、缩放、旋转或透视变化。",
        "- 道路中心线建议严格跟随 manifest 的结构和功能关系，但手绘边缘允许自然浮动；草、花、石头等细节不做像素级锁死。",
        "- 每个区域的道路和对象关系必须符合本文件的 road/object-zone contract，且 runtime layers 必须从确认后的母图构图拆出。",
        "- 不得出现房子压路、水井隔十字路口、田地压路、路径被装饰物截断、过度工整中心构图、十区域同模板等问题。",
        "- 不得包含水印、模型签名、乱码文字、UI 文本、战斗元素、科幻 HUD 或命名 IP 风格复刻。",
    ])

    output = HANDOFF / "batch_b_regions_request.md"
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch", choices=["batch_b_regions"], default="batch_b_regions")
    parser.add_argument("--region", help="Write a single-region Batch B subbatch request, for example: village.")
    args = parser.parse_args()
    if args.batch == "batch_b_regions" and args.region:
        output = write_batch_b_region_request(args.region)
    elif args.batch == "batch_b_regions":
        output = write_batch_b_request()
    else:  # pragma: no cover - argparse prevents this
        raise SystemExit(f"unsupported batch: {args.batch}")
    print(f"OK: wrote {output.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
