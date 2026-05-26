# Village layout structure draft review

Candidate: `village_layout_structure_draft_v001`

Status: structure/layout draft only. This is not final painted source art, not final `village_painted_source`, and must not be split into runtime layers.

## Files

- Structure draft: `02_source_generation/village_painted_source.png`
- Review overlay: `05_review_and_qa/village_painted_source_review_overlay_v001.png`
- Acceptance record: `02_source_generation/source_acceptance.json`

## Review checklist

- Roads connect west, north, east, and south seams without visual breaks.
- `VillageNotice`, `SeedStallProxy`, `OldMapleClue`, `VillageReturnPath`, Aoi's standing pocket, and `BenchRestProp` are readable.
- Hidden discovery remains environmental; no quest text or explicit clue label is baked into source art.
- A seamless OutdoorWorld master blueprint and true storybook `village_painted_source` are still required before layer export or runtime replacement.

## Codex visual precheck

Status: pass for structure/layout readability. This is not human visual approval and not final painted source approval.

- Composition: pass. The image reads as a compact village entry plaza, not a full town.
- Roads: pass. The west return road and north/east/south future connector roads visibly tie into the central plaza.
- VillageNotice: pass. The notice silhouette is clear and contains only unreadable decorative strokes.
- SeedStallProxy: pass. The stall reads as a small advice/service point, not a full shop economy.
- OldMapleClue: pass. The old maple is visually prominent and remains an environmental clue without baked instructions.
- Aoi standing pocket: pass with caution. The empty standing patch beside the stall is visible; later layer work must keep it open and avoid filling it with flowers or props.
- BenchRestProp: pass. The bench reads as a quiet rest prop below the main plaza path.

Blocking note: keep `human_visual_approval=false`, `layer_export_approved=false`, and `runtime_replacement=false`. Do not split layers from this structure draft.
