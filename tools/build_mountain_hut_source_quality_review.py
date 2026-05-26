from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps, ImageStat


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_DIR = ROOT / "production/assets/regions/mountain_hut_world2d/v001"
SOURCE_DIR = PACKAGE_DIR / "02_source_generation"
REVIEW_DIR = PACKAGE_DIR / "05_review_and_qa"
WORKFLOW = PACKAGE_DIR / "workflow_manifest.json"
LAYER_CONTRACT = PACKAGE_DIR / "03_layer_export/layer_contract.json"
ACCEPTANCE = SOURCE_DIR / "source_acceptance.json"
SOURCE_REVIEW = REVIEW_DIR / "source_candidate_review.md"
REVIEW_GATE = REVIEW_DIR / "review_gate.md"
PROJECT_MANIFEST = ROOT / "production/assets/project_art_production_manifest_2026-05-19.json"
VILLAGE_SOURCE = ROOT / "production/assets/regions/village_world2d/v001/02_source_generation/village_painted_source.png"
MOUNTAIN_HUT_SOURCE = SOURCE_DIR / "mountain_hut_painted_source.png"
REVIEW_OVERLAY = REVIEW_DIR / "mountain_hut_painted_source_review_overlay_v001.png"
QUALITY_JSON = REVIEW_DIR / "source_quality_review_v001.json"
QUALITY_MD = ROOT / ".codex/reports/mountain_hut_source_quality_review_2026-05-24.md"
REFERENCE_BOARD = REVIEW_DIR / "mountain_hut_repaint_v002_reference_board.png"
REPAINT_BRIEF = SOURCE_DIR / "mountain_hut_repaint_v002_brief.md"

CANVAS = (1800, 1200)
DETAIL_RATIO_MIN = 0.65
SEAM_DELTA_MAX = 24.0
STATUS = "needs_repaint_before_layer_export"


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def load_source(path: Path) -> Image.Image:
    image = Image.open(path).convert("RGB")
    if image.size != CANVAS:
        raise SystemExit(f"{rel(path)} size mismatch: {image.size}")
    return image


def edge_detail_score(image: Image.Image) -> float:
    gray = ImageOps.grayscale(image)
    edges = gray.filter(ImageFilter.FIND_EDGES)
    return float(ImageStat.Stat(edges).mean[0])


def gray_variance(image: Image.Image) -> float:
    gray = ImageOps.grayscale(image)
    return float(ImageStat.Stat(gray).var[0])


def rgb_mean(image: Image.Image) -> tuple[float, float, float]:
    return tuple(float(v) for v in ImageStat.Stat(image).mean)


def crop_village_east(image: Image.Image) -> Image.Image:
    return image.crop((CANVAS[0] - 520, 380, CANVAS[0], 900))


def crop_hut_west(image: Image.Image) -> Image.Image:
    return image.crop((0, 420, 520, 940))


def edge_average(image: Image.Image, side: str) -> tuple[float, float, float]:
    if side == "right":
        crop = image.crop((image.width - 40, 0, image.width, image.height))
    else:
        crop = image.crop((0, 0, 40, image.height))
    return tuple(float(v) for v in ImageStat.Stat(crop).mean)


def color_delta(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
    return sum(abs(a[index] - b[index]) for index in range(3)) / 3.0


def font(size: int) -> ImageFont.ImageFont:
    for name in ["arial.ttf", "segoeui.ttf"]:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def draw_wrapped(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, *, width: int, fill: tuple[int, int, int], font_obj: ImageFont.ImageFont, line_gap: int = 6) -> int:
    x, y = xy
    line = ""
    for word in text.split():
        test = f"{line} {word}".strip()
        bbox = draw.textbbox((0, 0), test, font=font_obj)
        if bbox[2] - bbox[0] <= width or not line:
            line = test
        else:
            draw.text((x, y), line, fill=fill, font=font_obj)
            y += (bbox[3] - bbox[1]) + line_gap
            line = word
    if line:
        bbox = draw.textbbox((0, 0), line, font=font_obj)
        draw.text((x, y), line, fill=fill, font=font_obj)
        y += (bbox[3] - bbox[1]) + line_gap
    return y


def make_card(board: Image.Image, title: str, image: Image.Image, xy: tuple[int, int], size: tuple[int, int]) -> None:
    draw = ImageDraw.Draw(board)
    x, y = xy
    w, h = size
    draw.rounded_rectangle((x - 12, y - 54, x + w + 12, y + h + 18), radius=10, fill=(242, 232, 207), outline=(128, 103, 71), width=2)
    draw.text((x, y - 42), title, fill=(50, 42, 31), font=font(24))
    board.paste(ImageOps.fit(image, size, method=Image.Resampling.LANCZOS), xy)


def build_reference_board(village: Image.Image, hut: Image.Image, metrics: dict[str, Any]) -> None:
    REFERENCE_BOARD.parent.mkdir(parents=True, exist_ok=True)
    board = Image.new("RGB", (1800, 1500), (232, 220, 192))
    draw = ImageDraw.Draw(board)
    title_font = font(34)
    body_font = font(22)
    small_font = font(18)

    draw.text((34, 28), "MountainHut v002 repaint reference board", fill=(45, 36, 25), font=title_font)
    draw.text((36, 72), "Use the Village source as the painterly quality target; keep MountainHut layout and seam registration stable.", fill=(70, 56, 38), font=body_font)

    make_card(board, "Accepted Village source target", village, (34, 150), (840, 560))
    make_card(board, "Current MountainHut candidate: needs repaint", hut, (926, 150), (840, 560))

    village_crop = crop_village_east(village)
    hut_crop = crop_hut_west(hut)
    make_card(board, "Village east seam crop", village_crop, (34, 820), (520, 520))
    make_card(board, "MountainHut west seam crop", hut_crop, (594, 820), (520, 520))

    panel_x = 1160
    panel_y = 816
    draw.rounded_rectangle((panel_x, panel_y, 1766, 1358), radius=10, fill=(246, 238, 217), outline=(128, 103, 71), width=2)
    draw.text((panel_x + 24, panel_y + 20), "Repaint blockers", fill=(51, 39, 27), font=font(26))
    y = panel_y + 64
    bullets = [
        f"Detail ratio vs Village: {metrics['detail_ratio']:.2f}; target for review readiness is at least {DETAIL_RATIO_MIN:.2f}.",
        "Foliage reads as flat symbolic blobs/dots; repaint with clustered leaves, grasses, small flowers, rocks, and soft depth.",
        "Road edges are too banded/graphic; match the Village road's softened dirt, stone scatter, and blended grass transition.",
        "Hut roof/walls need Village-level material texture, shadow, and scale coherence while preserving the door approach.",
        "Do not export runtime layers from this candidate. Repaint one full opaque source first; later layers derive from that accepted source.",
    ]
    for bullet in bullets:
        y = draw_wrapped(draw, (panel_x + 28, y), f"- {bullet}", width=556, fill=(62, 49, 35), font_obj=small_font, line_gap=6) + 10

    draw.line((34, 1410, 1766, 1410), fill=(112, 91, 64), width=2)
    footer = "Registration target: shared 1800x1200 source canvas, west seam at x=0 y~667, road width ~76px, no combat/danger cues, no independent layer compositions."
    draw_wrapped(draw, (38, 1430), footer, width=1700, fill=(66, 53, 37), font_obj=body_font)
    board.save(REFERENCE_BOARD)


def build_metrics(village: Image.Image, hut: Image.Image) -> dict[str, Any]:
    village_detail = edge_detail_score(village)
    hut_detail = edge_detail_score(hut)
    village_variance = gray_variance(village)
    hut_variance = gray_variance(hut)
    village_edge = edge_average(crop_village_east(village), "right")
    hut_edge = edge_average(crop_hut_west(hut), "left")
    seam_delta = color_delta(village_edge, hut_edge)
    return {
        "village_detail_edge_mean": round(village_detail, 4),
        "mountain_hut_detail_edge_mean": round(hut_detail, 4),
        "detail_ratio": round(hut_detail / village_detail, 4),
        "minimum_detail_ratio_for_repaint_ready": DETAIL_RATIO_MIN,
        "village_gray_variance": round(village_variance, 4),
        "mountain_hut_gray_variance": round(hut_variance, 4),
        "variance_ratio": round(hut_variance / village_variance, 4),
        "village_rgb_mean": [round(v, 4) for v in rgb_mean(village)],
        "mountain_hut_rgb_mean": [round(v, 4) for v in rgb_mean(hut)],
        "village_east_edge_rgb_mean": [round(v, 4) for v in village_edge],
        "mountain_hut_west_edge_rgb_mean": [round(v, 4) for v in hut_edge],
        "seam_edge_average_channel_delta": round(seam_delta, 4),
        "maximum_preferred_seam_delta_for_precheck": SEAM_DELTA_MAX,
        "seam_color_precheck_passed": seam_delta <= SEAM_DELTA_MAX,
    }


def write_quality_artifacts(metrics: dict[str, Any]) -> dict[str, Any]:
    data = {
        "review_id": "mountain_hut_source_quality_review_v001",
        "status": STATUS,
        "reviewed_at": "2026-05-24",
        "source_candidate": rel(MOUNTAIN_HUT_SOURCE),
        "quality_reference_source": rel(VILLAGE_SOURCE),
        "reference_board": rel(REFERENCE_BOARD),
        "repaint_brief": rel(REPAINT_BRIEF),
        "source_candidate_review": rel(SOURCE_REVIEW),
        "metrics": metrics,
        "producer_verdict": "The current MountainHut candidate is useful as a layout/seam reference, but it is not ready for layer export or runtime replacement.",
        "blocking_findings": [
            "Detail density is materially below the accepted Village source.",
            "Foliage and flower detail still read as programmatic marks instead of finished storybook painting.",
            "The road color seam is improved, but the road edge treatment and integrated stone/grass texture do not yet match the Village source.",
            "Hut material, roof detail, and foreground tree treatment need a stronger painterly pass before semantic layers are worth exporting.",
        ],
        "required_next_step": "Create a v002 full-canvas repaint using the reference board, then run human/art review before layer export.",
        "hard_approval_flags": {
            "human_visual_approval": False,
            "layer_export_approved": False,
            "runtime_replacement": False,
            "launch_quality_approved": False,
        },
    }
    write_json(QUALITY_JSON, data)
    QUALITY_MD.parent.mkdir(parents=True, exist_ok=True)
    QUALITY_MD.write_text(
        f"""# MountainHut Source Quality Review - 2026-05-24

## Verdict

Status: `{STATUS}`.

The current MountainHut source candidate should stay blocked from layer export and runtime replacement. It is a useful layout/seam reference, but it is visibly lower-detail and less painterly than the accepted Village source.

## Evidence

- Quality JSON: `{rel(QUALITY_JSON)}`
- Repaint reference board: `{rel(REFERENCE_BOARD)}`
- v002 repaint brief: `{rel(REPAINT_BRIEF)}`
- MountainHut candidate: `{rel(MOUNTAIN_HUT_SOURCE)}`
- Village quality target: `{rel(VILLAGE_SOURCE)}`

## Metrics

- Village detail edge mean: `{metrics['village_detail_edge_mean']}`
- MountainHut detail edge mean: `{metrics['mountain_hut_detail_edge_mean']}`
- Detail ratio: `{metrics['detail_ratio']}`; target before review readiness: `{DETAIL_RATIO_MIN}`
- Village gray variance: `{metrics['village_gray_variance']}`
- MountainHut gray variance: `{metrics['mountain_hut_gray_variance']}`
- Seam edge average channel delta: `{metrics['seam_edge_average_channel_delta']}`; color precheck passed: `{metrics['seam_color_precheck_passed']}`

## Producer Notes

- The seam color pass is useful and should be preserved as a reference.
- The current source still has simplified trees, dotted flowers, banded road edges, and lower hut material detail.
- A v002 repaint should keep the full `1800x1200` shared canvas and west seam registration, but increase painterly foliage/road/building detail to match Village.
- Do not export runtime layers until a source is explicitly accepted.
""",
        encoding="utf-8",
    )
    return data


def write_repaint_brief(metrics: dict[str, Any]) -> None:
    REPAINT_BRIEF.write_text(
        f"""# MountainHut Repaint v002 Brief

Status: v002_repaint_required_before_layer_export

## Purpose

Produce a stronger full-canvas `mountain_hut_painted_source` candidate that can be reviewed against the accepted Village source. The current candidate remains a structural/seam reference only.

## Required Inputs

- Repaint reference board: `{rel(REFERENCE_BOARD)}`
- Accepted Village quality target: `{rel(VILLAGE_SOURCE)}`
- Current MountainHut candidate: `{rel(MOUNTAIN_HUT_SOURCE)}`
- Layout lock: `production/assets/regions/mountain_hut_world2d/v001/01_layout_lock/layout_lock.json`
- Seam brief: `production/assets/seams/village_to_mountain_hut/v001/seam_brief.md`

## Output Target

- Produce one opaque full-canvas source candidate at `1800x1200`.
- Preserve the west seam entry at source x=0, y about 667, road width about 76px.
- Keep the hut door and standing pocket readable.
- Keep one shared composition; do not make independent runtime layers yet.

## Repaint Targets

- Match Village-level painterly detail density. Current detail ratio is `{metrics['detail_ratio']}`, below the `{DETAIL_RATIO_MIN}` review-readiness target.
- Replace symbolic tree blobs and flower dots with clustered leaves, grasses, small flowers, rocks, and soft layered vegetation.
- Soften the road edges to match the accepted Village road: dirt variation, small stones, subtle wheel/foot wear, and blended grass transition.
- Improve hut roof, wall, porch, door, herb shelf, and woodpile material texture while keeping simple readable silhouettes.
- Preserve calm cozy rural life-sim mood.

## Must Avoid

- Combat, monsters, weapons, danger signs, blood, damage, hard survival pressure, countdowns, or failure cues.
- Baked quest text or UI text.
- Cropped transparent layers or independently recomposed layer images.
- Pixel-perfect brush tracing to layout coordinates; the target is registration-perfect layer alignment with natural painted variation.

## Acceptance Before Layer Export

- Human/art review explicitly accepts the source.
- Source remains a full `1800x1200` opaque shared canvas.
- West seam road, ground color, perspective, and detail density match the Village east edge.
- All later runtime layers derive from the accepted source on the full canvas.
""",
        encoding="utf-8",
    )


def ensure_section(path: Path, heading: str, body: str) -> None:
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    marker = f"\n## {heading}\n"
    if marker.strip() in text:
        text = text.split(marker.strip(), 1)[0].rstrip() + marker + body.strip() + "\n"
    else:
        text = text.rstrip() + marker + body.strip() + "\n"
    path.write_text(text, encoding="utf-8")


def update_workflow_records(review: dict[str, Any]) -> None:
    acceptance = load_json(ACCEPTANCE)
    acceptance["codex_source_quality_review"] = {
        "status": STATUS,
        "review_record": rel(QUALITY_JSON),
        "reference_board": rel(REFERENCE_BOARD),
        "repaint_brief": rel(REPAINT_BRIEF),
        "not_human_visual_approval": True,
        "layer_export_blocked_reason": "Current source is below accepted Village painterly detail and needs v002 repaint or explicit human override.",
    }
    write_json(ACCEPTANCE, acceptance)

    workflow = load_json(WORKFLOW)
    workflow.setdefault("validation", {})["source_quality_gate"] = "tools/validate_mountain_hut_source_quality_gate.py"
    workflow.setdefault("phase_status", {})["02_source_quality_review"] = STATUS
    source_candidate = workflow.setdefault("source_candidate", {})
    source_candidate["quality_review_status"] = STATUS
    source_candidate["quality_review_record"] = rel(QUALITY_JSON)
    source_candidate["repaint_reference_board"] = rel(REFERENCE_BOARD)
    source_candidate["v002_repaint_brief"] = rel(REPAINT_BRIEF)
    workflow["next_art_step"] = "Use the v002 repaint brief/reference board to produce a stronger full-canvas source before layer export."
    write_json(WORKFLOW, workflow)

    contract = load_json(LAYER_CONTRACT)
    source = contract.setdefault("source_image", {})
    source["quality_review_status"] = STATUS
    source["quality_review_record"] = rel(QUALITY_JSON)
    source["v002_repaint_brief"] = rel(REPAINT_BRIEF)
    source["required_next_step"] = "Create or receive a v002 full-canvas repaint, then human-review the accepted source before layer export."
    contract["layer_export_status"] = "blocked_until_v002_source_quality_acceptance"
    write_json(LAYER_CONTRACT, contract)

    project = load_json(PROJECT_MANIFEST)
    for region in project.get("current_runtime_regions", []):
        if isinstance(region, dict) and region.get("region_id") == "Region_MountainHut":
            region["phase"] = "mountain_hut_source_candidate_needs_repaint"
            region["active_source_quality_review"] = rel(QUALITY_JSON)
            region["active_repaint_reference_board"] = rel(REFERENCE_BOARD)
            region["active_repaint_brief"] = rel(REPAINT_BRIEF)
            region["next_art_step"] = "Use the v002 repaint reference board/brief to create a higher-quality full-canvas source before any layer export or runtime replacement."
    write_json(PROJECT_MANIFEST, project)

    ensure_section(
        SOURCE_REVIEW,
        "Source Quality Gate",
        f"""- Quality status: `{STATUS}`.
- Quality review record: `{rel(QUALITY_JSON)}`.
- v002 repaint reference board: `{rel(REFERENCE_BOARD)}`.
- v002 repaint brief: `{rel(REPAINT_BRIEF)}`.
- Layer export remains blocked until a stronger full-canvas source is accepted by human/art review.
""",
    )
    ensure_section(
        REVIEW_GATE,
        "Source Quality Gate Extension",
        f"""- The current source candidate is marked `{STATUS}` by `{rel(QUALITY_JSON)}`.
- A passing structural validator is not enough to export layers.
- Before layer export, the team must either accept a source explicitly in human/art review or produce a v002 repaint from `{rel(REFERENCE_BOARD)}` and `{rel(REPAINT_BRIEF)}`.
- Runtime layers still must derive from one accepted full-canvas `painted_source`.
""",
    )


def main() -> None:
    village = load_source(VILLAGE_SOURCE)
    hut = load_source(MOUNTAIN_HUT_SOURCE)
    metrics = build_metrics(village, hut)
    build_reference_board(village, hut, metrics)
    write_repaint_brief(metrics)
    review = write_quality_artifacts(metrics)
    update_workflow_records(review)
    print(f"OK: wrote {rel(QUALITY_JSON)}")
    print(f"OK: wrote {rel(REFERENCE_BOARD)}")
    print(f"OK: wrote {rel(REPAINT_BRIEF)}")


if __name__ == "__main__":
    main()
