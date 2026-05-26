# MountainHut Repaint v002 Brief

Status: v002_repaint_required_before_layer_export

## Purpose

Produce a stronger full-canvas `mountain_hut_painted_source` candidate that can be reviewed against the accepted Village source. The current candidate remains a structural/seam reference only.

## Required Inputs

- Repaint reference board: `production/assets/regions/mountain_hut_world2d/v001/05_review_and_qa/mountain_hut_repaint_v002_reference_board.png`
- Accepted Village quality target: `production/assets/regions/village_world2d/v001/02_source_generation/village_painted_source.png`
- Current MountainHut candidate: `production/assets/regions/mountain_hut_world2d/v001/02_source_generation/mountain_hut_painted_source.png`
- Layout lock: `production/assets/regions/mountain_hut_world2d/v001/01_layout_lock/layout_lock.json`
- Seam brief: `production/assets/seams/village_to_mountain_hut/v001/seam_brief.md`

## Output Target

- Produce one opaque full-canvas source candidate at `1800x1200`.
- Preserve the west seam entry at source x=0, y about 667, road width about 76px.
- Keep the hut door and standing pocket readable.
- Keep one shared composition; do not make independent runtime layers yet.

## Repaint Targets

- Match Village-level painterly detail density. Current detail ratio is `0.5323`, below the `0.65` review-readiness target.
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
