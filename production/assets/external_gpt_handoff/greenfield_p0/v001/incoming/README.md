# Greenfield P0 Incoming Asset Staging

This folder is the formal external asset intake and audit area for Greenfield P0.
It is not the final Godot runtime asset directory.

## Current Contract

The active scene-layer contract is the three-image structure below:

```text
01_scene_mothers/regions/{region}/{region}_scene_mother.png
02_scene_base/regions/{region}/{region}_base.png
03_foreground_occlusion/regions/{region}/{region}_foreground_occlusion.png
04_audit/scene_mother_layers.json
04_audit/previews/scene_layer_preview_contact.png
```

Rules:

- `scene_mother` and `base` are fully opaque PNGs.
- `foreground_occlusion` is full-canvas RGBA with transparent background.
- The three region images must share the exact same size, origin, and composition.
- `04_audit/scene_mother_layers.json` records the foreground occlusion pixel regions.

## Removed Legacy Intake

The older full-manifest intake shape was removed from this active intake folder after the three-image contract became the current source of truth:

```text
01_mother_images/
02_runtime_exports/
```

Those files were evidence/source history only and were not part of the active three-image scene-layer contract. Use Git history if a rollback or comparison is needed.
