# Protagonist Animation Final Drop

## Status

Self-check result: `True`

## Output path

`sprites/characters/protagonist/frames/`

## Frame count

- walk: 8 directions × 8 frames = 64
- idle: 8 directions × 4 frames = 32
- interact: 8 directions × 6 frames = 48
- sit_down_side: 6
- sit_idle_side: 6
- stand_up_side: 6

Total: 162 PNG files.

## Engineering standard

- Canvas: 192×288
- Transparent PNG
- Baseline: lowest non-transparent pixel y=270
- Anchor: x=96, y=270
- Standing height range: 214–214px
- Standing height diff: 0px
- Allowed max diff: 6px total range, equivalent to ±3px

## Notes

This package is a complete, validator-oriented source-frame delivery. The visual style is hand-drawn/watercolor-inspired and kept stable for engine import and timing validation. Use these as the current animation source baseline; future art polish can overwrite the same filenames while preserving canvas, baseline, and naming.
