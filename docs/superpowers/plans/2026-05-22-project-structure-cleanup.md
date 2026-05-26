# Project Structure Cleanup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the project directory readable without breaking current Godot runtime paths or deleting useful production evidence.

**Architecture:** This cleanup is a conservative first pass. Active runtime and production folders stay in place; only local tool clutter and empty template folders are removed or archived, while structure standards and validation scripts prevent drift.

**Tech Stack:** Godot 4.x project, Python structure audit scripts, Markdown project documentation.

---

### Task 1: Document Canonical Structure

**Files:**
- Create: `docs/16_PROJECT_STRUCTURE.md`

- [ ] **Step 1: Write the directory contract**

Create a concise reference that classifies top-level folders as runtime, forward scaffold, production, external intake, toolchain, or archive.

- [ ] **Step 2: Record migration boundaries**

Document that `scenes/`, `scripts/`, `sprites/`, `assets/`, and `production/` remain active until task-specific migrations validate replacements.

### Task 2: Add Structure Audit Tooling

**Files:**
- Create: `tools/audit_project_structure.py`
- Create: `tools/validate_project_structure.py`

- [ ] **Step 1: Add audit script**

The audit script should write a JSON report under `.codex/reports/` with top-level counts, empty root dirs, deprecated root clutter, and current incoming contract status.

- [ ] **Step 2: Add validator**

The validator should fail on known root clutter returning, missing required docs, and dirty external incoming layout.

- [ ] **Step 3: Run validation**

Run:

```powershell
python tools/audit_project_structure.py
python tools/validate_project_structure.py
```

Expected: audit JSON is written and validation exits 0.

### Task 3: Low-Risk Root Cleanup

**Files:**
- Modify: `.gitignore`
- Move: `.superpowers/` to `.codex/archive/superpowers_brainstorm_2026-05-22/`
- Remove empty directories only: `export_templates/`, `feature_profiles/`, `script_templates/`, `text_editor_themes/`

- [ ] **Step 1: Ignore local Superpowers runtime state**

Add `.superpowers/` to `.gitignore`.

- [ ] **Step 2: Archive local brainstorm output**

Move `.superpowers/` into `.codex/archive/` so it no longer clutters the repository root.

- [ ] **Step 3: Remove empty root template folders**

Delete only directories verified to contain zero files and zero subdirectories.

### Task 4: Update Project Memory

**Files:**
- Modify: `.codex/status.md`
- Modify: `.codex/context/project_state.md`
- Modify: `.codex/context/roadmap.md`
- Modify: `.codex/context/decisions.md`
- Modify: `.codex/learnings/improvements.md`
- Create: `.codex/tasks/done/2026-05-22-project-structure-cleanup-pass1.md`

- [ ] **Step 1: Record what changed**

Summarize low-risk cleanup, validation commands, and remaining migration boundaries.

- [ ] **Step 2: Keep future work explicit**

Mark deeper migrations as separate tasks requiring Godot scene/resource validation.
