# Greenfield P0 GPT Asset Production Brief

Use this document when asking GPT to produce replacement art for the Godot project. The project already has working placeholder assets and scenes; new art should replace the exact runtime paths rather than changing code.

## Current Handoff

Use this small-batch request package:

```text
production/assets/external_gpt_handoff/greenfield_p0/v002/
```

Copy prompts from:

```text
production/assets/external_gpt_handoff/greenfield_p0/v002/prompt_briefs.md
```

Drop generated PNGs into:

```text
production/assets/external_gpt_handoff/greenfield_p0/v002/incoming/
```

Then validate with:

```powershell
py -3.12 tools\validate_greenfield_p0_external_asset_intake.py --manifest production\assets\external_gpt_handoff\greenfield_p0\v002\asset_request_manifest.json --allow-partial
```

## Non-Negotiable Rules

- Generate PNG only.
- Preserve exact filename, relative path, canvas size, and alpha requirement.
- Do not bake UI text into reusable panels, buttons, slots, tabs, icons, or maps.
- Do not copy any existing game, anime, movie, artist, map, or named style.
- Do not include combat, weapons, monsters, armor, HP bars, loot, horror, sci-fi HUD, or watermark.
- Treat generated output as `review_ready`, not final approved art.

## Region Layer Rule

For HomeArea and future region work:

- Start from one `painted_source` / mother composition.
- Export runtime layers from that same composition.
- Keep exact same full canvas size, origin, perspective, scale, rotation, and composition.
- Do not crop transparent foreground layers to object bounds.
- Registration-perfect layer alignment matters more than pixel-tracing manifest coordinates.

## Current Batches

| Batch | Count | Purpose |
|---|---:|---|
| `batch_01_ui_kit_core` | 12 | Replace paper/wood panels, buttons, slots, tabs, checkbox, scrollbar. |
| `batch_02_ui_icons_map_settings` | 9 | Replace HUD icons, map icon, settings icon, paper map, settings preview. |
| `batch_03_home_area_full_canvas` | 5 | Replace HomeArea mother/base/foreground/collision/review sheet as one aligned set. |
| `batch_04_p0_portraits` | 11 | Replace player and core NPC portraits. |
| `batch_05_runtime_walk_sprites` | 8 | Replace player walk strips and core NPC walk-down strips. |
| `batch_06_item_icons_core` | 11 | Replace core resource, gift, food, and key item icons. |

Each batch stays under 12 assets so GPT generation remains executable and reviewable.

## Replacement Contract

The v002 manifest records `final_runtime_path` for each asset. After intake validation and review, accepted assets should be copied from `incoming/` to those runtime paths:

```text
assets/ui/...
assets/scenes/home_area/...
assets/art/portraits/...
assets/art/characters/...
assets/art/items/...
```

Godot scenes and data files already point at these stable locations. Replacing art should not require changing scripts.

## What To Send GPT First

Start with `Batch 01 UI Kit Core`. It has the most impact because HUD, Inventory, Dialogue, Map, and Settings all reuse the same Greenfield theme.

After Batch 01 is accepted, generate:

1. `Batch 02 UI Icons Map Settings`
2. `Batch 03 HomeArea Full Canvas`
3. `Batch 04 P0 Portraits`
4. `Batch 05 Runtime Walk Sprites`
5. `Batch 06 Item Icons Core`

Do not ask GPT for all batches at once.
