# GPT Asset Pipeline Instructions

This document is the entry point for an external GPT or image-production agent that will create art assets for the Godot project.

The goal is not to redesign the game. The goal is to replace existing placeholder PNG files with approved Greenfield-style production art while keeping every runtime path stable.

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

Each generated file must match the `final_runtime_path`, `expected_size`, and `transparent` fields in:

```text
production/assets/external_gpt_handoff/greenfield_p0/v002/asset_request_manifest.json
```

Do not rename files. Do not create alternate names. Do not change paths. The game code expects these exact paths.

Use this workflow:

1. Generate one batch at a time.
2. Put outputs in the matching `incoming_path` under:

```text
production/assets/external_gpt_handoff/greenfield_p0/v002/incoming/
```

3. After review, approved files are copied over the exact `final_runtime_path`.
4. No Godot code should be edited just to replace art.

## Batch Order

Produce assets in this order:

1. `batch_01_ui_kit_core`
2. `batch_02_ui_icons_map_settings`
3. `batch_03_home_area_full_canvas`
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

For HomeArea scene assets:

- `scene_home_area_mother.png`, `scene_home_area_base.png`, `scene_home_area_foreground_occlusion.png`, and `scene_home_area_collision_mask.png` must all be `1920x1080`.
- Keep the same canvas, origin, perspective, scale, and composition across all HomeArea layers.
- Do not crop transparent layers to object bounds.
- Treat `scene_home_area_mother.png` as the single composition source.
- Derive runtime layers from that same composition. Do not independently regenerate base and foreground as different scenes.
- `scene_home_area_base.png` must contain the playable background without foreground occluders blocking the character.
- `scene_home_area_foreground_occlusion.png` must contain only pixels that should visually pass in front of the player, with transparency elsewhere.
- `scene_home_area_collision_mask.png` is a production aid and must align with the same full canvas.

The target is registration-perfect layer alignment, not pixel-perfect tracing of manifest coordinates. Natural brush variation is allowed in grass, flowers, stones, leaves, and texture details as long as the layers align.

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
python tools\validate_greenfield_p0_home_area_scene.py
python tools\validate_greenfield_p0_settings_screen.py
python tools\validate_greenfield_p0_map_screen.py
```

Godot runtime checks for the current P0 shell:

```powershell
C:\Users\23732\AppData\Local\Programs\Godot\4.6.1\Godot_v4.6.1-stable_win64_console.exe --headless --path . --script tools\validate_greenfield_p0_settings_screen.gd
C:\Users\23732\AppData\Local\Programs\Godot\4.6.1\Godot_v4.6.1-stable_win64_console.exe --headless --path . --script tools\validate_greenfield_p0_home_area_scene.gd
```

## Current Status

All formal runtime paths currently have placeholder or current review files. This means the Godot project can load them. It does not mean final art is approved.

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
