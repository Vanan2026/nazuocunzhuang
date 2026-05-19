# home_area_art removed

Date: 2026-05-19
Status: removed intentionally.

Reason:
- production/assets/regions/home_area_art/v001..v007 were historical wrong-path HomeArea art attempts.
- They are not the current canonical source for scene reconstruction.
- Keeping them caused repeated reuse of invalid assets and stale layer/interact/blocker work.

Replacement:
- Use production/assets/regions/home_area_world2d/v001 for the restarted workflow.
- Correct pipeline: 3D blockout -> source image -> same-canvas base/foreground structural layers -> Godot interactions.

Policy:
- Do not recreate home_area_art for HomeArea production unless the pipeline owner explicitly reopens it.
- Historical docs may still mention home_area_art; treat those references as obsolete unless updated to home_area_world2d/v001.
