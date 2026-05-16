# 10 — Codex 任务清单

版本：v1.0  
用途：直接复制给 Codex 分阶段执行。

---

## 0. 总原则

不要一次执行全部任务。每次只执行一个任务包。执行前阅读 `AGENTS.md` 和相关 docs。

每个任务完成后必须输出：

```text
Changed files:
Test steps:
Expected result:
Known limitations:
Next suggested task:
```

---

## Task 001 — 读取文档并生成项目结构

### Prompt

```text
Read AGENTS.md, 00_README_FOR_CODEX.md, docs/01_PROJECT_DESIGN_GDD.md, docs/07_GODOT_IMPLEMENTATION_SPEC.md, and docs/11_ACCEPTANCE_CHECKLIST.md.

Create the recommended Godot project folder structure if it does not exist. Do not add combat-related systems. Add placeholder README notes in empty folders so the structure is committed. Create an initial Main.tscn / WorldRoot.tscn if the repository is a Godot project. If Godot project files do not exist, create a docs-only implementation plan and do not fabricate engine files that cannot be validated.

Return changed files and test steps.
```

---

## Task 002 — 建立 Autoload 管理器骨架

```text
Implement autoload manager script skeletons according to docs/07_GODOT_IMPLEMENTATION_SPEC.md:
GameState, EventBus, TimeManager, SeasonManager, WeatherManager, DataRegistry, InventoryManager, RelationshipManager, QuestManager, DialogueManager, SaveManager, SceneRouter.

Use typed GDScript where practical. Do not implement full logic yet, but include signals, basic properties, and comments explaining responsibility. Do not add combat, HP, damage, weapons, or monster-related fields.
```

---

## Task 003 — 数据表导入与 DataRegistry

```text
Using docs/08_CONTENT_DATA_SCHEMA.md and data/*.csv as source references, create JSON data files under game/data/: items.json, crops.json, npcs.json, dialogues.json, recipes.json, restoration_targets.json.

Implement DataRegistry loading and validation:
- unique IDs
- required fields
- reference checks for crop seed/harvest items
- no combat-related forbidden fields

Print validation summary on startup.
```

---

## Task 004 — 玩家移动与交互基类

```text
Implement Player.tscn and Player.gd with 2D top-down movement for Godot 4.x. Add input actions if missing: move_up, move_down, move_left, move_right, interact, use_tool, open_inventory, open_journal, cancel.

Implement Interactable.gd base class and InteractionArea detection. Create a simple test scene PlayerYard.tscn with at least three interactables: mailbox, bed, signboard.

No combat mechanics.
```

---

## Task 005 — 时间、日期、天气、睡觉

```text
Implement TimeManager and WeatherManager MVP logic:
- 4 seasons, 28 days each
- day starts at 06:00
- time block changes
- sleep interaction advances to next day
- tomorrow weather generated on sleep
- HUD displays season/day/time/weather

Rainy weather should set a flag that farming can use for auto-watering.
```

---

## Task 006 — 农田系统 MVP

```text
Implement FarmPlot system:
- empty, tilled, planted, watered, ready states
- plant seeds from inventory
- water plot
- day-end growth
- rainy day auto watering
- harvest adds item to inventory

Use crop data from game/data/crops.json. Create 6 test plots in PlayerYard.tscn. Use placeholder sprites if final art does not exist.
```

---

## Task 007 — 背包系统与 UI

```text
Implement InventoryManager and InventoryUI MVP:
- add/remove/has/count
- display item grid
- selected item name and description
- show seed and crop counts
- support using selected seed on FarmPlot through current interaction

Use docs/08_CONTENT_DATA_SCHEMA.md for item fields.
```

---

## Task 008 — NPC 与对话系统 MVP

```text
Implement NPC.tscn, NPC.gd, DialogueManager, and DialogueBox UI.

Create three NPCs using game/data/npcs.json: aoi, gen, mika.

Dialogue selection priority:
event > relationship > weather > seasonal > daily > fallback.

Add daily first-talk relationship increase. Store whether player talked to each NPC today. Reset on new day.
```

---

## Task 009 — 送礼与关系

```text
Implement gift giving:
- Player can choose an inventory item when interacting with NPC.
- NPC likes/dislikes use item tags from item data.
- RelationshipManager updates relationship value.
- Birthday gift multiplier exists but can be MVP placeholder.
- Show simple response dialogue.

Do not make relationship a romance-only system. Keep it village relationship oriented.
```

---

## Task 010 — 修复系统：旧水井

```text
Implement RestorationTarget using restoration_targets.json.

Create old_well in PlayerYard:
- show requirements
- check inventory and money
- on repair, deduct resources
- set GameState flag
- switch visual state
- unlock yard water source flag
- emit restoration_completed
- persist in save file
```

---

## Task 011 — 保存读取 MVP

```text
Implement SaveManager:
- save to user://save_slot_01.json
- load from same file
- save time/weather/player/inventory/relationships/flags/farm plots/restoration states
- support default values for missing fields

Add Save and Load buttons to a debug menu or keyboard shortcuts for MVP.
```

---

## Task 012 — 传闻系统 MVP

```text
Implement daily rumor system:
- Load rumors from data.
- Choose 1-3 rumors each day based on season/weather/flags.
- Show via mailbox, bulletin board, or NPC dialogue.
- Add one mysterious bell rumor after old_well is repaired.
```

---

## Task 013 — 美术占位资产生成

```text
Using docs/04_ART_DIRECTION_BIBLE.md, docs/05_ART_ASSET_BIBLE.md, docs/06_AI_ASSET_PROMPT_LIBRARY.md, and data/style_palette.json, generate simple placeholder SVG or PNG assets for MVP:
- player placeholder
- 3 NPC placeholders
- 8 crop icons/stages
- mailbox, bed, old well broken/repaired, signboard
- HUD icons for sunny/cloudy/rainy

Use warm low-saturation palette and clear silhouettes. Do not create combat items.
```

---

## Task 014 — UI 风格包

```text
Create UI theme resources and placeholder art consistent with the art bible:
- paper panel
- wood button
- dialogue box
- inventory slot
- calendar icon
- weather icons

Apply them to HUD, InventoryUI, DialogueBox.
```

---

## Task 015 — 垂直切片整合

```text
Create a playable vertical slice flow:
1. Start in player house.
2. Leave to yard.
3. Read mailbox/weather.
4. Plant and water crops.
5. Visit village path.
6. Talk to Aoi and Gen.
7. Collect wood/stone placeholders.
8. Repair old well.
9. Sleep.
10. See next day state persisted.
11. Trigger bell rumor after repair.

Fix blockers only. Do not expand scope.
```

---

## Task 016 — 验收检查

```text
Run through docs/11_ACCEPTANCE_CHECKLIST.md. Create a report listing:
- passed checks
- failed checks
- missing assets
- missing systems
- suggested next tasks

Do not implement new features during this task unless required to fix a blocking issue.
```
