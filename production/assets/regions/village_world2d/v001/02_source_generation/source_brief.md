# Village Plaza Source Brief

## Target

Create one full-canvas source image for `Region_Village / VillagePlaza`.

Correction: the current generated file at `village_painted_source.png` is only a structure/layout draft. A true storybook candidate has been generated after referencing the parent OutdoorWorld seamless master package:

- `production/assets/outdoor_world_world2d/v001/`
- `true_source_candidates/village_true_painted_source_candidate_v001.png`

- File target: `village_painted_source.png`
- Canvas: `1800x1200`
- Alpha: fully opaque source PNG
- Perspective: fixed top-down 3/4 2D
- Runtime scale reference: Godot places generated region layers at scale `0.18`

## Required gameplay anchors

- `VillageNotice`: a small village notice object near the central social route.
- `SeedStallProxy`: a modest non-economic seed advice stall near Aoi's late-morning standing point.
- `OldMapleClue`: an old tree or small unlabelled plaque that can quietly suggest a secret without explaining it.
- `VillageReturnPath`: a west-side path that reads as the way back to PlayerYard.
- `AoiVillageStandLateMorning`: a clear standing pocket beside the seed stall, not inside road clutter.
- `BenchRestProp`: a resting bench below the plaza path.

## Composition

The image should read as a small village plaza node, not a complete town. Keep roads and doorstep approaches clear. Houses, stall props, trees, and benches must sit outside the primary lane so player movement and interaction prompts remain readable.

The west, north, east, and south seam connectors must read as connected road exits in the source image. Use the connector spines from `layout_lock.json` as soft road guides, not as pixel-perfect painted edges.

The approved final source must not look like an engineering diagram. It should remove labels, rectangles, marker dots, and schematic road rendering while preserving the same readable spatial relationships.

## Hidden discovery policy

Use environmental hints only: tree age, small plaque silhouette, worn path curve, or gentle lighting. Do not put readable task text, arrows, labels, UI, or explicit old-well instructions into the art.

## Style

Warm low-saturation rural storybook art, soft hand-painted texture, clear silhouettes, clean outlines, cozy countryside life simulation mood.

## Negative content

Do not include combat, weapons, monsters, horror, harsh neon, photorealism, copied franchise style, watermark, UI, characters, readable task text, or text baked into gameplay art.
