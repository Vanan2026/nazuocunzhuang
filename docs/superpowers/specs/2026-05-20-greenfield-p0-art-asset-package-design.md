# Greenfield P0 Art Asset Package Design

Date: 2026-05-20
Project: 《那座村庄》
Status: design approved in chat, awaiting written-spec review

## Goal

Rebuild the art production direction from zero. Existing HomeArea image assets, layer splits, pasted patches, and old scene-specific fixes are historical evidence only. They must not be used as source material for the new asset package.

The new direction is asset-package first: produce a coherent P0 art system before rebuilding scenes. This includes source mother images, refined runtime layers, Godot review scenes, validation gates, and explicit approval states.

## Scope

P0 includes both the playable base asset package and seasonal environment variants.

P0 also includes all 10 currently registered runtime regions because their layout and visual design affect asset scale, traversal, UI density, and the full village identity:

- `Region_HomeArea`
- `Region_Village`
- `Region_BackFarm`
- `Region_ForestEdge`
- `Region_Orchard`
- `Region_Pond`
- `Region_MountainPath`
- `Region_MountainHut`
- `Region_Mountain`
- `Region_CliffView`

Each region must produce:

- layout mother image
- painted source image
- refined runtime layers
- Godot review scene integration
- capture review evidence
- manifest with source, layer, anchor, validation, and approval state

Execution may be batched, but the P0 acceptance scope does not shrink. This is art production work, so refined runtime layers are required for all P0 regions.

## Non-Goals

- Do not use old HomeArea images, historical layer splits, or local patch assets as source material.
- Do not call any generated or structurally valid asset launch-quality without user visual approval.
- Do not build combat, damage, enemies, weapons, loot drops, or high-pressure failure content.
- Do not solve visual problems by patching Godot scene nodes over weak source art.
- Do not make UI a late skin pass; UI has its own mother board and runtime asset outputs.

## Source Mother Image System

All runtime assets must trace back to a source mother image or mother board with a manifest. A runtime export without a mother manifest is not allowed into the new package.

Mother image types:

- Style mother image: palette, line weight, brush texture, lighting, season mood, softness, saturation, and fixed 3/4 top-down language.
- Character motion mother sheets: protagonist and P0 NPC proportions, 8-direction poses, animation timing, foot anchors, and portrait language.
- Prop mother boards: house modules, mailbox, well, bench, road signs, fences, doors, storage, farm props, trees, rocks, and harvest props.
- Tile and terrain mother boards: grass, dirt, paths, tilled fields, water edges, slopes/steps where needed, and seasonal variants.
- UI layout mother board: HUD, inventory, dialogue box, calendar/weather, journal/tasks, interaction prompt, and shared frame/button/icon style.
- Region scene mother images: one per P0 region, defining spatial layout, traversal, entrances, exits, interactions, occlusion, seasonal replacement zones, and region-specific prop needs.

Each mother manifest must record:

- canvas size
- coordinate system
- grid/tile size where applicable
- object list
- export rects or full-canvas layer references
- pivot and foot/base anchors
- collision and interaction recommendations
- season variant mapping
- Godot destination paths
- validation commands
- status: `draft`, `usable`, `approved`, `rejected`, or `archived`

## Character Package

The protagonist uses 8 directions because the game is fixed 3/4 top-down and the animation needs to read cleanly across diagonal movement.

Protagonist P0 runtime package:

- idle: 8 directions
- walk: 8 directions
- interact: 8 directions
- water: 8 directions
- pickup: 8 directions

P0 NPC package for Aoi, Gen, Mika, and Hana:

- idle: 8 directions
- walk: 8 directions
- portraits: neutral, happy, thinking

Character standards:

- 3.5 to 4 head proportion target
- foot origin at bottom center
- consistent visible height across directions
- simple readable silhouette
- no illustration-only proportions that break gameplay scale

## Region Runtime Layer Standard

Each P0 region must output refined runtime layers. At minimum:

- base ground
- terrain/path details
- behind-player structures
- YSort structures and props
- foreground occlusion
- shadow overlay
- light/weather overlay
- season variant mapping

Layers must be same-source and either coordinate-stable full-canvas layers or explicitly documented with pivot/offset data. Flattened review plates are not runtime layers. Mask-derived stickers are not acceptable final runtime layers.

Godot scene integration responsibilities:

- place layers
- wire YSort
- configure camera bounds
- add walkable zones and blockers
- add interaction areas
- add entrances/exits
- capture review screenshots

Godot must not be used to hide weak art with local patch sprites.

## Seasonal System

Seasonal variants are P0 for environment assets because seasons are a core pillar.

Seasonal variants apply to:

- terrain tiles
- grass and dirt color/state
- field states
- paths and water edge variants where useful
- crops and harvested states
- trees, shrubs, leaves, snow or rain overlays
- ambient FX such as rain, snow, leaf drift, warm light, mist

Seasonal variants do not apply by default to:

- character animation sets
- NPC portraits
- item icons
- base UI frames

Those can receive later variants only if a specific gameplay or presentation need is approved.

## UI Package

UI requires a layout mother board before runtime image export.

P0 UI surfaces:

- HUD: date, time, weather, money/energy if active
- inventory panel
- dialogue box and portrait frame
- calendar/weather panel
- journal/tasks panel
- interaction prompt
- basic modal/confirmation frame

Style target:

- notebook, paper, wood sign, and gentle countryside UI language
- readable and compact for repeated play
- not sci-fi HUD
- consistent icon stroke, padding, and frame materials

Runtime UI exports include panel frames, buttons, selectors, icons, prompt markers, and basic weather/season icons.

## Package Structure

New production package root:

```text
production/assets/base_asset_pack/v001/
  00_brief/
  01_mother_images/
    style/
    characters/
    props/
    tiles/
    ui/
    regions/
  02_runtime_exports/
    characters/
    portraits/
    props/
    tiles/
    crops/
    items/
    ui/
    fx/
    regions/
  03_contact_sheets/
  04_godot_gallery/
  workflow_manifest.json
```

Runtime copies for Godot references live under `assets/art/`, not directly under `production/assets/`.

## Godot Review Flow

The first Godot target is an asset gallery scene, not a final scene:

- show protagonist and NPC animation strips
- show 8-direction pose checks
- show prop scale next to player
- show seasonal tile sets
- show crop stages
- show UI layout samples
- show each region's runtime layer stack and capture points

After the gallery passes structural validation, regions are integrated into review scenes in batches. The P0 batch scope remains all 10 regions, but implementation can proceed in a controlled order.

Recommended first execution batch:

1. Global style, UI, tile, character, and prop mother boards
2. Region mother images for all 10 regions
3. Refined runtime layers for HomeArea, Village, and BackFarm
4. Godot gallery and first three region review scenes
5. Remaining region refined layers and review scenes

## Validation Gates

Every production pass must run structural validation before visual review:

- manifest schema validation
- file existence and naming validation
- PNG dimensions and alpha validation
- animation direction/frame-count validation
- pivot/anchor validation
- season variant coverage validation
- no old HomeArea image/source reference validation
- Godot load validation
- Godot gallery capture validation
- region capture validation

Visual approval remains separate. Automated validation can mark assets `usable`; only user review can mark assets `approved`.

## Failure and Rework Rules

If an asset group fails visual review:

- return to its mother image or template
- regenerate or repaint the full affected group
- rerun exports and validation
- update manifest state and review notes

Do not:

- paste local patches into Godot scenes
- reuse rejected HomeArea images
- mix independent source styles inside one region
- promote a structurally valid but visually rejected package

## Acceptance Criteria

This design is complete when:

- the base asset package structure is created
- mother image manifests exist for all required categories
- P0 character, region, seasonal, prop, crop, item, FX, and UI asset lists are explicit
- each of the 10 regions has a mother-image plan and refined runtime layer requirement
- validation scripts prevent old-route HomeArea references from entering the new package
- Godot gallery and region review plan are documented

Implementation is not complete until the generated/refined assets, Godot gallery, region scenes, captures, and validation gates exist and pass.
