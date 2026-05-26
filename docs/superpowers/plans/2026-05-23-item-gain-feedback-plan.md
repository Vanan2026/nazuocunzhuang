# Item Gain Feedback Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make resource pickup and crop harvest results visible through compact player-facing feedback.

**Architecture:** Reuse the existing compact `DialogueBox` instead of adding a new UI layer. `ResourcePickup` owns immediate pickup feedback because it already knows the gained item/count. `PlayerYard` owns crop-harvest feedback by listening to `FarmPlot.crop_harvested` and resolving item display names through `DataRegistry`.

**Tech Stack:** Godot 4.6.1, GDScript, Python static validators, Godot headless runtime validators.

---

### Task 1: Add Item Gain Feedback Validators

**Files:**
- Create: `tools/validate_item_gain_feedback.py`
- Create: `tools/validate_item_gain_feedback.gd`

- [ ] **Step 1: Write the static validator**

The validator should require:
- `ResourcePickup.gd` contains `_show_gain_feedback()` and `_get_dialogue_box()`.
- `PlayerYard.gd` connects `crop_harvested` and has `_on_farm_plot_harvested()`.
- The runtime validator file exists.

- [ ] **Step 2: Run static validator to verify RED**

Run: `python tools\validate_item_gain_feedback.py`

Expected: fail because production code has no item-gain feedback hooks yet.

- [ ] **Step 3: Write the Godot runtime validator**

The runtime validator should instantiate `PlayerYard`, then:
- interact with `WoodPile`;
- assert `DialogueBox` is visible and text includes `获得`;
- mature and harvest `FarmPlot0`;
- assert `DialogueBox` is visible and text includes `收获` plus `crop_turnip` gain behavior.

- [ ] **Step 4: Run runtime validator to verify RED**

Run: `D:\Godot\Godot_v4.6.1-stable_win64_console.exe --headless --path . --script res://tools/validate_item_gain_feedback.gd`

Expected: fail on missing feedback after pickup or harvest.

### Task 2: Implement Minimal Feedback

**Files:**
- Modify: `game/entities/interactable/ResourcePickup.gd`
- Modify: `game/scenes/world/PlayerYard.gd`

- [ ] **Step 1: Resource pickup feedback**

Add `_show_gain_feedback(item_id, count)` to `ResourcePickup.gd`, resolving `DialogueBox` and showing one line:

```gdscript
"获得：%s x%d，已经放进背包。"
```

- [ ] **Step 2: Harvest feedback**

In `PlayerYard.gd`, connect each farm plot `crop_harvested` signal and show:

```gdscript
"收获：%s x%d，已经放进背包。"
```

- [ ] **Step 3: Run focused validators**

Run:
- `python tools\validate_item_gain_feedback.py`
- `D:\Godot\Godot_v4.6.1-stable_win64_console.exe --headless --path . --script res://tools/validate_item_gain_feedback.gd`

Expected: both pass.

### Task 3: Regression And Memory

**Files:**
- Modify: `.codex/status.md`
- Modify: `.codex/context/project_state.md`
- Modify: `.codex/context/roadmap.md`
- Modify: `.codex/context/decisions.md`
- Modify: `.codex/learnings/improvements.md`
- Create: `.codex/tasks/done/2026-05-23-item-gain-feedback.md`

- [ ] **Step 1: Run related regressions**

Run static and Godot runtime validators for item gain feedback, resource pickup persistence, crop sleep/harvest, yard readability, and main-flow playable.

- [ ] **Step 2: Update project memory**

Record the completed slice, verification results, risks, and next task.

- [ ] **Step 3: Final diff check**

Run: `git diff --check`

Expected: no whitespace errors; CRLF normalization warnings are acceptable if exit code is 0.
