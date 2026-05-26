# Branch Audit Cleanup Merge Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reduce the current dirty branch to content that either advances the active playable vertical slice or preserves the approved, verifiable Greenfield P0 asset pipeline, then validate and commit it.

**Architecture:** Treat `game/` Task 011-015 work as the playable-slice line and `production/assets/external_gpt_handoff/greenfield_p0/v001/` plus its validators as the parallel art-production line. Remove obsolete HomeArea one-off routes, temporary backup scenes, and premature runtime copies that are not referenced or approved.

**Tech Stack:** Godot 4.x scenes/GDScript, Python validation scripts, PowerShell, Git.

---

### Task 1: Classify The Dirty Worktree

**Files:**
- Read: `D:\那个村庄\.codex\status.md`
- Read: `D:\那个村庄\docs\10_CODEX_TASKS.md`
- Read: `D:\那个村庄\docs\14_ART_ASSET_PIPELINE.md`
- Read: `D:\那个村庄\docs\15_EXTERNAL_GPT_ASSET_HANDOFF.md`
- Read: `D:\那个村庄\docs\16_PROJECT_STRUCTURE.md`

- [ ] **Step 1: Snapshot branch state**

Run:

```powershell
git status --short --branch
git diff --name-status --cached
git diff --name-status
git ls-files --others --exclude-standard
```

Expected: Identify staged, unstaged, and untracked groups before any cleanup.

- [ ] **Step 2: Mark keep/delete classes**

Keep:

```text
Task 011/012 save-load and rumor files
Task 015 validators and minimal gameplay files once implemented
Greenfield P0 external handoff docs, manifests, incoming audit, generators, validators, and review scenes
Project structure and art pipeline audit/validation docs/tools
```

Delete or keep deleted:

```text
scenes/regions/region_home_area.before_*.tscn
obsolete HomeArea launch/formal/v006 route tools listed in docs/14_ART_ASSET_PIPELINE.md
premature unreferenced runtime copies under assets/art/greenfield_p0 if no scene/data reference exists
temporary caches or generated local-only artifacts outside production review contracts
```

### Task 2: Clean Non-Mainline Or Temporary Content

**Files:**
- Delete or keep deleted: `D:\那个村庄\scenes\regions\region_home_area.before_*.tscn`
- Delete or keep deleted: `D:\那个村庄\tools\build_region_home_area_launch_art_package.py`
- Delete or keep deleted: `D:\那个村庄\tools\integrate_home_area_formal_v001_split_scene.py`
- Delete or keep deleted: `D:\那个村庄\tools\prepare_home_area_formal_v001_source.py`
- Delete or keep deleted: `D:\那个村庄\tools\run_home_area_v006_first_batch_pipeline.ps1`
- Delete or keep deleted: `D:\那个村庄\tools\split_home_area_formal_v001_layers.py`
- Delete or keep deleted: `D:\那个村庄\tools\split_home_area_launch_quality_v001_layers.py`
- Delete or keep deleted: `D:\那个村庄\tools\test_region_home_area_launch_art_package.py`
- Delete or keep deleted: `D:\那个村庄\tools\validate_home_area_launch_quality_v001_package.py`
- Delete or keep deleted: `D:\那个村庄\tools\validate_home_area_launch_quality_v001_visual_sanity.py`
- Delete or keep deleted: `D:\那个村庄\tools\validate_region_home_area_launch_art_package.py`

- [ ] **Step 1: Remove only audited cleanup targets**

Use PowerShell `Remove-Item -LiteralPath` for explicit paths only after confirming they match the cleanup target list.

- [ ] **Step 2: Regenerate or update inventory if cleanup changes file inventory**

Run:

```powershell
python tools\audit_art_asset_inventory.py
python tools\validate_art_asset_pipeline.py
```

Expected: validator still reports art asset pipeline valid.

### Task 3: Finish The Playable Vertical Slice Merge

**Files:**
- Modify: `D:\那个村庄\game\scenes\Main.tscn`
- Create: `D:\那个村庄\game\scenes\home\PlayerHouse.tscn`
- Create: `D:\那个村庄\game\entities\interactable\ResourcePickup.gd`
- Create: `D:\那个村庄\game\entities\interactable\FlagInteractable.gd`
- Modify: `D:\那个村庄\game\scenes\world\PlayerYard.tscn`
- Modify if required: `D:\那个村庄\tools\validate_task015_vertical_slice.gd`

- [ ] **Step 1: Run the failing Task 015 Python contract**

Run:

```powershell
python tools\validate_task015_vertical_slice.py
```

Expected before implementation: FAIL on missing `PlayerHouse.tscn` or vertical-slice nodes.

- [ ] **Step 2: Add the smallest house-to-yard and yard-object implementation**

Implement only the required nodes and scripts from `docs/10_CODEX_TASKS.md` Task 015.

- [ ] **Step 3: Run Task 015 Python and Godot validation**

Run:

```powershell
python tools\validate_task015_vertical_slice.py
D:\Godot\Godot_v4.6.1-stable_win64_console.exe --headless --path . --script res://tools/validate_task015_vertical_slice.gd
```

Expected: both commands exit 0.

### Task 4: Stage, Commit, And Merge

**Files:**
- Update: `D:\那个村庄\.codex\status.md`
- Update if errors occur: `D:\那个村庄\.codex\learnings\errors.md`
- Update if process changes are introduced: `D:\那个村庄\.codex\learnings\improvements.md`

- [ ] **Step 1: Run final verification**

Run the focused validators for Task 011, Task 012, Task 015, project structure, art pipeline, and whitespace.

- [ ] **Step 2: Stage only approved files**

Run:

```powershell
git add <approved files>
git status --short --branch
```

Expected: no rejected temporary files staged.

- [ ] **Step 3: Commit and merge if the branch is ahead of master**

Run:

```powershell
git commit -m "Integrate greenfield pipeline cleanup and vertical slice"
git checkout master
git merge codex/greenfield-p0-art-assets
```

Expected: merge succeeds only after verification passes. If current branch and `master` are the same local branch tip before commit, commit on the feature branch first, then fast-forward `master`.
