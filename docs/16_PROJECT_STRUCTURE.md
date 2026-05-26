# Project Structure

更新时间：2026-05-22

This document defines the current directory contract for the project. It is a working structure, not a claim that all legacy paths have already been migrated.

## Root Purpose

`D:\那个村庄` is a Godot 4.x project plus production asset workspace. The root should stay small and readable: project entry files, active runtime folders, production pipelines, tools, docs, and local Codex memory.

## Active Runtime

- `project.godot`: Godot project config. Do not change the main scene without a task-specific migration plan.
- `scenes/`: current active runtime scenes and dev review scenes.
- `scripts/`: current active runtime scripts used by the existing playable path.
- `sprites/`: legacy/current sprite assets still referenced by active scenes.
- `assets/`: newer stable runtime art/audio landing area used by `res://assets/...` references.
- `addons/`: Godot editor/runtime addons that are part of the project.
- `audio/`, `shaders/`, `resources/`, `data/`: current runtime support assets and content data.

## Forward Scaffold

- `game/`: newer canonical scaffold for future systems, scenes, data, and entities.
- `assets/art/`, `assets/audio/`: preferred future runtime asset locations.

Do not delete or rename the older active runtime folders until the scaffold has validated parity and `project.godot` has intentionally migrated.

## Production And Intake

- `production/`: production asset packages, external handoffs, reports, renders, and source manifests.
- `production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/`: formal external asset intake and audit staging, not final runtime.
- Superseded external intake drops should be removed from active production folders after validation; use Git history for rollback evidence instead of keeping importable duplicate PNG trees.

Accepted external assets should be validated in `production/` first, then copied or processed into `assets/` or Godot review scenes through a named import task.

## Tools And Automation

- `tools/`: scripts for generation, validation, auditing, rendering, and one-off production pipeline work.
- `mcp/`: local MCP/Godot helper code.
- `docs/`: design, pipeline, implementation, and project-structure documentation.
- `prompts/`: prompt/source prompt references that are still useful to production.

## Local And Ignored State

- `.codex/`: project memory, task snapshots, reports, and local automation context.
- `.godot/`: Godot editor cache.
- `.git/`: version control internals.
- `.superpowers/`: local Superpowers runtime/brainstorm cache. It should not remain at root; archive useful contents under `.codex/archive/` if needed.

## Cleanup Rules

- Prefer archive over deletion unless a directory is verified empty.
- Do not move `scenes/`, `scripts/`, `sprites/`, `assets/`, or `production/` in broad cleanup passes.
- Do not overwrite user or generated changes during cleanup.
- Every structural cleanup pass must update `.codex/status.md` and run `tools/validate_project_structure.py`.
- Deeper migration work must be separate and validated with Godot scene/resource checks.
