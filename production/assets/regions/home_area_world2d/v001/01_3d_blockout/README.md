# 01_3d_blockout

Purpose: hold the locked structure authority for the HomeArea scene art.

Inputs:
- Godot/dev blockout scene may be used as reference if it preserves the same camera, composition, exits, and object layout.
- camera_lock.json is the production contract for source generation.
- object_mask_lock.json is the production contract for object and layer identity.

Output expected before source approval:
- blockout_render_full.png at 6144x4096 or a documented scale-equivalent render.
- blockout_mask_overlay.png showing object ids from object_mask_lock.json.

Do not add final paint, interactions, or blockers in this phase.
