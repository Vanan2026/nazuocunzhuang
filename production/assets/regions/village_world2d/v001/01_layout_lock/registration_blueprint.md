# Village Plaza Registration Blueprint

This blueprint is the spatial contract for `Region_Village / VillagePlaza`. It is a production guide, not a runtime asset and not final art approval.

## Canvas

- Source canvas: `1800x1200`
- Godot texture scale: `0.18`
- Runtime preview size: about `324x216`
- Export rule: full canvas, shared origin, no crop, no auto-trim

## Locked gameplay anchors

| Anchor | Source point | Runtime point | Purpose |
| --- | --- | --- | --- |
| `VillageNotice` | `622,489` | `112,88` | One formal village entry hint |
| `SeedStallProxy` | `1167,578` | `210,104` | Daily advice service, not a shop economy |
| `OldMapleClue` | `1422,933` | `256,168` | Optional environmental clue |
| `VillageReturnPath` | `122,756` | `22,136` | Return to PlayerYard |
| `AoiVillageStandLateMorning` | `1089,622` | `196,112` | Aoi schedule proof |
| `BenchRestProp` | `684,924` | source only | Rest prop below the plaza |

## Road connector spines

These spines make the full-region canvas read as one plaza node with future exits. They are layout guides for the source image, not pixel-perfect brush edges.

| Spine | Source points | Purpose |
| --- | --- | --- |
| `west_east_connector_spine` | `144,720 -> 622,711 -> 1167,578 -> 1656,600` | Keeps the PlayerYard return and future east lane visually tied to the plaza. |
| `north_south_connector_spine` | `792,96 -> 760,500 -> 1167,578 -> 1134,1104` | Keeps the future north and south exits visibly connected through the plaza. |

## Art direction

- Small village plaza node, not a full town.
- Houses and props sit back from roads so player movement remains readable.
- The plaza should support talking, checking a notice, asking at the seed stall, and noticing a quiet tree clue.
- Hidden exploration is environmental only. Do not bake quest instructions, UI arrows, or clue labels into runtime art.

## Layer rule

All runtime layers must derive from one `village_painted_source`. Transparent layers must keep the same full canvas and alpha outside painted areas.
