# HomeArea source image brief v001

Goal: produce one full-canvas approved source image for the HomeArea seamless 2D world scene.

Canvas:
- 6144x4096 PNG.
- Top-left origin, same coordinate space as camera_lock.json and object_mask_lock.json.

Scene content:
- Warm countryside home yard in fixed 3/4 top-down view.
- Small repaired-or-repairable rural house in upper center.
- Clear central playable yard and readable dirt paths.
- Village/forest path toward upper right.
- Back farm path toward lower right or southeast.
- Left foreground tree and lower foreground grass used for depth only, not broad rectangle occlusion.
- Well, mailbox, bench, road sign, flower bushes, fences, shrubs as clear prop candidates.

Hard constraints:
- No character, NPC, UI, combat object, weapon, monster, damage sign, or loot icon baked into the environment.
- No copied franchise style or named-game imitation.
- Maintain object positions from the locked blockout.
- Preserve enough negative space for player navigation and later interaction polygons.

Approval gate:
- Source image must be approved before base/foreground layer export starts.
