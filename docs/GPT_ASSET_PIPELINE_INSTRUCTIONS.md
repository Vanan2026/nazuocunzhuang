# GPT Asset Pipeline Instructions

This document is the entry point for an external GPT or image-production agent that will create art assets for the Godot project.

The goal is not to redesign the game. The goal is to replace existing placeholder PNG files with approved Greenfield-style production art while keeping every runtime path stable unless an asset request manifest explicitly moves a group to a component-based workflow.

## Project Target

- Game: `那座村庄`
- Engine: Godot 4.x
- Genre: cozy rural life simulation
- Camera: fixed 3/4 top-down 2D
- Tone: slow life, repair, seasons, relationships, gentle exploration
- Forbidden content: combat, monsters, weapons, armor, HP bars, loot drops, horror, sci-fi HUD, copied named game/anime/movie styles

## Required Reading Order

Read these files in this order:

1. `docs/ART_BIBLE.md`
2. `docs/ASSET_MANIFEST.md`
3. `docs/MISSING_ASSETS_REPORT.md`
4. `production/assets/external_gpt_handoff/greenfield_p0/v002/README.md`
5. `production/assets/external_gpt_handoff/greenfield_p0/v002/asset_request_manifest.json`
6. `production/assets/external_gpt_handoff/greenfield_p0/v002/prompt_briefs.md`

Use the style reference at:

```text
production/assets/references/style_mother/greenfield_p0_style_mother_2026-05-27.jpg
```

This image is an art bible and experience target. Do not copy it pixel-for-pixel. Use its visual language: warm low-saturation storybook color, paper/wood UI, soft foliage, 3/4 top-down cozy rural scenes, readable hand-painted icons, and simple rounded characters.

## Output Rule

Generate PNG files only.

Each generated file must match the `incoming_path`, `final_runtime_path`, `expected_size`, and `transparent` fields in:

```text
production/assets/external_gpt_handoff/greenfield_p0/v002/asset_request_manifest.json
```

Do not rename files. Do not create alternate names. Do not change paths.

Use this workflow:

1. Generate one batch at a time.
2. Put outputs in the matching `incoming_path` under:

```text
production/assets/external_gpt_handoff/greenfield_p0/v002/incoming/
```

3. After review, approved files are copied over the exact `final_runtime_path`.
4. No Godot code should be edited just to replace UI, icon, portrait, or sprite art.
5. HomeArea is now component-based; Godot placement metadata may be authored after visual approval.

## Batch Order

Produce assets in this order:

1. `batch_01_ui_kit_core`
2. `batch_02_ui_icons_map_settings`
3. `batch_03_home_area_component_pack`
4. `batch_04_p0_portraits`
5. `batch_05_runtime_walk_sprites`
6. `batch_06_item_icons_core`

Do not produce all batches in one request. Keep every batch reviewable.

## Registration Rules

For UI icons, item icons, portraits, and walk sprites:

- Match the exact pixel size.
- Keep transparent background when `transparent=true`.
- Keep silhouettes readable at in-game scale.
- Do not bake text into icons or buttons.

For HomeArea component assets:

- Do not use the deprecated full-canvas base/foreground/collision layer workflow.
- Generate isolated transparent components for Godot assembly.
- Every component must match the exact `expected_size`.
- Every component with `transparent=true` must be a true RGBA/alpha PNG.
- Do not bake checkerboard, white, gray, preview, or studio backgrounds into transparent assets.
- Use the same fixed 3/4 top-down game perspective across all components.
- Keep visual scale consistent across the component pack.
- Do not include ground, shadow plates, or unrelated surrounding scene pixels unless the component description explicitly asks for them.
- House body and house roof must be separate components.
- Components are assembled later through Godot placement metadata, such as `home_area_component_manifest.json` and `home_area_godot_placement.json`.

Deprecated HomeArea full-canvas targets must not be generated for v002:

- `scene_home_area_base.png`
- `scene_home_area_foreground_occlusion.png`
- `scene_home_area_collision_mask.png`
- `scene_home_area_review_contact.png`

## Visual Quality Rules

Use:

- warm low-saturation palette
- hand-painted storybook texture
- readable silhouettes
- soft rural light
- paper/wood UI motifs
- simple 3.5 to 4-head character proportions
- cozy village details: cottage, dirt paths, fields, flowers, trees, well, mailbox, fence, river/pond where applicable

Avoid:

- photorealism
- hard neon colors
- heavy black outlines
- noisy over-detail
- flat vector UI
- copied named IP styles
- readable text baked into UI panels, map, buttons, icons, or world art
- combat or danger language

## Validation Commands

After placing generated files in `incoming/`, run:

```powershell
python tools\validate_greenfield_p0_external_asset_intake.py --manifest production\assets\external_gpt_handoff\greenfield_p0\v002\asset_request_manifest.json --allow-partial
```

After approved files replace their `final_runtime_path`, run the relevant checks:

```powershell
python tools\validate_greenfield_replaceable_asset_pipeline.py
python tools\validate_greenfield_p0_ui_kit.py
python tools\validate_greenfield_p0_settings_screen.py
python tools\validate_greenfield_p0_map_screen.py
```

Godot runtime checks for the current P0 shell:

```powershell
C:\Users\23732\AppData\Local\Programs\Godot\4.6.1\Godot_v4.6.1-stable_win64_console.exe --headless --path . --script tools\validate_greenfield_p0_settings_screen.gd
```

## Current Status

Formal runtime paths currently have placeholder or review files. This means the Godot project can load them. It does not mean final art is approved.

HomeArea full-canvas layer assets are legacy review placeholders until the component pack is generated and integrated.

Use `docs/MISSING_ASSETS_REPORT.md` as the current list of art still requiring final generation and visual approval.

## Delivery Format For GPT Responses

When returning generated assets or an asset plan, include:

- batch id
- asset id
- incoming path
- final runtime path
- expected size
- transparent or opaque
- short production note
- any risk that might require a repaint

Do not include broad redesign suggestions unless a listed asset cannot be produced under the existing manifest.
