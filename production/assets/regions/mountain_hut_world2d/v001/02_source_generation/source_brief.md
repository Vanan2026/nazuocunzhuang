# MountainHut Source Brief v001

Status: ready_for_source_request_after_package_review

## Intent

Create one warm low-saturation fixed 3/4 top-down 2D storybook source image for MountainHut that visually continues from the accepted Village east edge. The place should feel like a quiet recovery/discovery stop at the edge of the village, not a combat or danger scene.

## Required Inputs

- OutdoorWorld master package: `production/assets/outdoor_world_world2d/v001/`
- MountainHut layout lock: `production/assets/regions/mountain_hut_world2d/v001/01_layout_lock/layout_lock.json`
- Seam brief: `production/assets/seams/village_to_mountain_hut/v001/seam_brief.md`
- Village reference package: `production/assets/regions/village_world2d/v001/`

## Source Output

- Output id: `mountain_hut_painted_source`
- Canvas: `1800x1200`
- Alpha: opaque
- Composition: one shared full-canvas scene
- Registration target: registration-perfect layer alignment, not pixel-perfect brush tracing

## Must Show

- West road entering from the Village seam and curving gently toward the hut.
- Small hut exterior, door, porch edge, soft roof shadow, herb shelf, and woodpile.
- Compatible grass, road material, detail density, and perspective with Village.
- Clear standing/inspection space near the hut door.

## Must Avoid

- Combat, monsters, damage cues, weapons, hard survival danger, or failure pressure.
- Readable task text baked into the image.
- Independent layer compositions.
- Cropped transparent layer planning.
