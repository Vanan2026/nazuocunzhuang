# Persistent Main Flow Router Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the `game/` main route keep inventory, flags, time, relationships, quests, current scene, and player spawn state across `PlayerHouse`, `PlayerYard`, and `ForestEdge`.

**Architecture:** `Main.gd` becomes the persistent state owner and scene router host. Existing scene-local managers remain for compatibility; `Main` syncs shared state into them on scene entry and harvests state from them on scene exit or key state-change signals. `SceneTravel` requests `SceneRouter` transitions with scene ids and spawn ids instead of directly changing files.

**Tech Stack:** Godot 4.6 GDScript, existing `game/autoload` managers, headless Godot validation scripts, Python static validators.

---

### Task 1: Persistent Flow Validation

**Files:**
- Create: `tools/validate_persistent_main_flow.py`
- Create: `tools/validate_persistent_main_flow.gd`

- [x] Write a Python file/data validator that requires `Main.gd`, spawn-aware `SceneTravel`, first-week `QuestManager`, NPC rumor hooks, cross-scene schedules, and spawn points.
- [x] Run `py -3.12 tools\validate_persistent_main_flow.py` and verify it fails on missing `Main.gd`.
- [x] Write a Godot runtime validator that instantiates `Main.tscn`, routes house -> yard -> forest -> yard, verifies shared inventory/flags/time/quest state, NPC forest assignment, NPC rumor display, and return spawn.
- [x] Run the Godot validator and verify it fails on the current direct scene-change implementation.

### Task 2: Main Scene Router And Shared State

**Files:**
- Create: `game/scenes/Main.gd`
- Modify: `game/scenes/Main.tscn`
- Modify: `game/autoload/SceneRouter.gd`
- Modify: `game/autoload/SaveManager.gd`

- [x] Add persistent manager nodes under `Main`.
- [x] Add a scene registry for `player_house`, `player_yard`, and `forest_edge`.
- [x] Implement `change_scene(scene_id, spawn_id)` with state harvest, scene load, state apply, spawn placement, and `SceneRouter.set_current_scene(...)`.
- [x] Extend save data with `scene` and `quests`, keeping old scene validators compatible.

### Task 3: Spawn-Aware Travel

**Files:**
- Create: `game/systems/scene/SpawnPoint.gd`
- Modify: `game/entities/interactable/SceneTravel.gd`
- Modify: `game/scenes/home/PlayerHouse.tscn`
- Modify: `game/scenes/world/PlayerYard.tscn`
- Modify: `game/scenes/world/ForestEdge.tscn`

- [x] Add `target_scene_id` and `target_spawn_id` to `SceneTravel`.
- [x] Route through `SceneRouter.request_scene_change(...)` when a router is available.
- [x] Add spawn markers to all three main-flow scenes.
- [x] Keep `target_scene` fallback for direct scene loads and old tests.

### Task 4: NPC Schedules And Rumor Trigger

**Files:**
- Modify: `game/data/npc_schedules.json`
- Modify: `game/data/rumors.json`
- Modify: `game/entities/npc/NPC.gd`
- Modify: `game/systems/npc/NpcScheduleDirector.gd`
- Modify: `game/scenes/world/ForestEdge.tscn`

- [x] Add real non-yard schedule entries such as `forest_edge`, `village_shop`, `carpenter_yard`, and `post_route`.
- [x] Hide NPCs that are not assigned to the current scene/time block.
- [x] Add `RumorManager` lookup to NPC interaction and show one `npc` rumor before fallback dialogue when available.
- [x] Add ForestEdge NPC instances and schedule director so at least Mika can appear there in the afternoon.

### Task 5: First-Week Quest Chain

**Files:**
- Modify: `game/autoload/QuestManager.gd`
- Modify: `game/scenes/world/PlayerYard.gd`
- Modify: `game/entities/interactable/RumorBoard.gd`
- Modify: `game/autoload/SaveManager.gd`

- [x] Add `first_week_restore_path` objective state to `QuestManager`.
- [x] Track mailbox read, bulletin read, old well repaired, bench repaired, sign repaired, forest notice heard, and forest edge visited.
- [x] Persist quest state through save data.
- [x] Update quest progress from `Main` after state sync.

### Task 6: Regression And Commit

**Files:**
- Modify project memory under `.codex/`

- [x] Run Python Task 002-012, Task 015, main-flow, and persistent-flow validators.
- [x] Run Godot Task 002-012 runtime validators where present, Task 015, main-flow, and persistent-flow validators.
- [x] Load `Main.tscn`, `PlayerHouse.tscn`, `PlayerYard.tscn`, `ForestEdge.tscn`, old `world.tscn`, HomeArea, and BackFarm headlessly.
- [x] Run legacy HomeArea route validators that must still pass.
- [x] Update `.codex/status.md`, project state, roadmap, decisions, improvements/errors as needed.
- [ ] Commit with a focused message after validation is green.
