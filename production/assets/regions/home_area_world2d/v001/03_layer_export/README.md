# 03_layer_export

This folder receives approved source-derived outputs only.

Do not put rough review crops, local stickers, manual patch screenshots, or rejected plate extractions here.

Required sequence:
1. Approve 02_source_generation/source_full.png.
2. Export base_clean.png as opaque full canvas.
3. Export structural foreground PNGs as transparent full canvas.
4. Export independent prop crops only with props_pivot_manifest.json.
5. Run human visual review before Godot integration.
