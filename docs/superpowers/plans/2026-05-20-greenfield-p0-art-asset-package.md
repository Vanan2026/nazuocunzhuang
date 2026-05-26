# Greenfield P0 Art Asset Package Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce the first greenfield P0 art asset package from source mother boards through runtime exports, 10-region refined layers, Godot gallery review, and validation gates.

**Architecture:** Add a deterministic production script that creates all source mother boards, runtime PNG exports, manifests, contact sheets, and a Godot review gallery under a new `base_asset_pack/v001` package. Add validators that reject missing outputs, missing manifests, old HomeArea source references, invalid PNG dimensions, missing 8-direction character coverage, missing seasonal variants, and missing 10-region runtime layers.

**Tech Stack:** Python 3 + Pillow for PNG generation and validation, Godot 4.6 headless CLI for gallery loading, existing `.codex` memory/status files for recovery.

---

## File Structure

- Create `tools/generate_greenfield_p0_art_pack.py`: owns all generated P0 source mother boards, runtime exports, contact sheets, workflow manifest, and Godot gallery scene.
- Create `tools/validate_greenfield_p0_art_pack.py`: validates the package structure, manifest, runtime PNGs, 8-direction characters, seasonal coverage, 10-region layers, and old-route bans.
- Create `tools/validate_greenfield_p0_gallery.gd`: loads the generated Godot gallery and checks that major sections and representative sprites exist.
- Create `scenes/dev/greenfield_p0_asset_gallery.tscn`: generated review scene containing the package overview, character samples, seasonal tile samples, UI samples, prop samples, and region layer previews.
- Create `production/assets/base_asset_pack/v001/`: source mother boards, runtime exports, manifests, and contact sheets.
- Create `assets/art/greenfield_p0/`: stable runtime copies used by the generated gallery.
- Modify `.codex/status.md`: track production progress.
- Modify `.codex/context/project_state.md`, `.codex/context/roadmap.md`, `.codex/context/decisions.md`, `.codex/learnings/improvements.md`: record the new greenfield production line after validation.

## Task 1: Create Package Generator

**Files:**
- Create: `tools/generate_greenfield_p0_art_pack.py`
- Create by script: `production/assets/base_asset_pack/v001/workflow_manifest.json`
- Create by script: `assets/art/greenfield_p0/**`
- Create by script: `scenes/dev/greenfield_p0_asset_gallery.tscn`

- [x] **Step 1: Write the generator script**

Create a script with these concrete sections:

```python
SEASONS = ["spring", "summer", "autumn", "winter"]
DIRECTIONS = ["down", "down_right", "right", "up_right", "up", "up_left", "left", "down_left"]
REGIONS = ["home_area", "village", "back_farm", "forest_edge", "orchard", "pond", "mountain_path", "mountain_hut", "mountain", "cliff_view"]
```

It must generate source mother boards, runtime exports, contact sheets, a workflow manifest, and `scenes/dev/greenfield_p0_asset_gallery.tscn`.

- [x] **Step 2: Run generator**

Run:

```powershell
python tools\generate_greenfield_p0_art_pack.py
```

Expected:

```text
OK: generated greenfield P0 art package
```

## Task 2: Create Package Validator

**Files:**
- Create: `tools/validate_greenfield_p0_art_pack.py`

- [x] **Step 1: Write validator**

Validator checks:

```text
workflow_manifest.json exists
status is usable
source_first is true
launch_quality_approved is false
10 region packages exist
each region has layout_mother, painted_source, and runtime layer PNGs
4 seasons exist for tiles and region overlays
protagonist has 8 directions for idle/walk/interact/water/pickup
P0 NPCs have 8 directions for idle/walk and three portraits
UI mother board and runtime UI exports exist
old HomeArea route strings are absent from manifest and gallery
```

- [x] **Step 2: Run validator**

Run:

```powershell
python tools\validate_greenfield_p0_art_pack.py
```

Expected:

```text
OK: greenfield P0 art package validates
```

## Task 3: Create Godot Gallery Validator

**Files:**
- Create: `tools/validate_greenfield_p0_gallery.gd`
- Validate: `scenes/dev/greenfield_p0_asset_gallery.tscn`

- [x] **Step 1: Write Godot validator**

Validator loads the gallery scene and checks nodes named:

```text
GreenfieldP0AssetGallery
CharacterSamples
SeasonTileSamples
UISamples
PropSamples
RegionSamples
```

It also verifies representative Sprite2D nodes have non-null textures.

- [x] **Step 2: Run Godot validator**

Run:

```powershell
D:\Godot\Godot_v4.6.1-stable_win64_console.exe --headless --path . --script tools\validate_greenfield_p0_gallery.gd
```

Expected:

```text
OK: greenfield P0 asset gallery validates
```

## Task 4: Run Baseline Integration Checks

**Files:**
- Validate: `project.godot`
- Validate: `scenes/dev/greenfield_p0_asset_gallery.tscn`
- Validate: generated PNG package

- [x] **Step 1: Run Python validators**

Run:

```powershell
python tools\validate_greenfield_p0_art_pack.py
python tools\validate_project_art_production_landing.py
```

Expected: both commands print `OK`.

- [x] **Step 2: Run Godot load checks**

Run:

```powershell
D:\Godot\Godot_v4.6.1-stable_win64_console.exe --headless --path . --script tools\load_scene.gd -- res://scenes/dev/greenfield_p0_asset_gallery.tscn
D:\Godot\Godot_v4.6.1-stable_win64_console.exe --headless --path . --script tools\validate_greenfield_p0_gallery.gd
```

Expected: both commands print `OK`.

## Task 5: Update Project Memory

**Files:**
- Modify: `.codex/status.md`
- Modify: `.codex/context/project_state.md`
- Modify: `.codex/context/roadmap.md`
- Modify: `.codex/context/decisions.md`
- Modify: `.codex/learnings/improvements.md`
- Create: `.codex/tasks/done/2026-05-20-greenfield-p0-art-asset-package.md`

- [x] **Step 1: Update status and memory**

Record:

```text
Greenfield P0 art package v001 generated
10 region mother/source/runtime layer packages exist
8-direction protagonist and NPC coverage exists
P0 UI mother board and runtime UI samples exist
Godot gallery validates
launch_quality_approved remains false
human visual approval remains required
```

- [x] **Step 2: Run final text checks**

Run:

```powershell
git diff --check -- tools\generate_greenfield_p0_art_pack.py tools\validate_greenfield_p0_art_pack.py tools\validate_greenfield_p0_gallery.gd docs\superpowers\plans\2026-05-20-greenfield-p0-art-asset-package.md
```

Expected: no errors.

## Self-Review

- Spec coverage: plan covers mother images, 8-direction characters, seasonal variants, UI layout mother board, all 10 regions, refined runtime layers, Godot gallery, validation, and memory updates.
- Placeholder scan: no TBD/TODO placeholders are used.
- Type consistency: region, direction, season, and status names are consistent with the design spec.
