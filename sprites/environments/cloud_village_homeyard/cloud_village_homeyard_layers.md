# CloudVillageHomeyard Layers

Source: `resources/设计图/CloudVillageHomeyard_无人物母图.png`

All positions are in original source-image coordinates. Godot scales `LayeredHomeyardRoot` to fit 1280x720.

| Node | File | Source box | Position | Size | Z | Note |
| --- | --- | --- | --- | --- | --- | --- |
| CleanBase | `base/homeyard_clean_base.png` | `(0, 0, 1672, 941)` | `(0, 0)` | `(1672, 941)` | -100 | Opaque no-character base with runtime cloud and wind-chime regions removed. |
| Clouds | `fx/homeyard_clouds.png` | `(430, 0, 1410, 390)` | `(430, 0)` | `(980, 390)` | -88 | Transparent cloud layer, cut from the mother image and animated slowly. |
| LeafMotionTop | `fx/homeyard_leaf_motion_top.png` | `(0, 0, 820, 390)` | `(0, 0)` | `(820, 390)` | 38 | Transparent top-left leaf highlight layer for subtle wind motion. |
| DappleShadow | `fx/homeyard_dapple_shadow.png` | `(0, 520, 1320, 941)` | `(0, 520)` | `(1320, 421)` | 48 | Transparent dapple shadow overlay for slow light movement. |
| WindChime | `props/homeyard_wind_chime.png` | `(1490, 235, 1590, 465)` | `(1490, 235)` | `(100, 230)` | 55 | Transparent wind chime under the eaves. |
| VerandaFrontOccluder | `fg/homeyard_occluder_veranda_front.png` | `(760, 610, 1672, 725)` | `(760, 610)` | `(912, 115)` | 32 | Foreground porch/veranda lip that covers feet when the player rests or walks behind the edge. |
| LeftGrassOccluder | `fg/homeyard_occluder_left_grass.png` | `(0, 595, 430, 885)` | `(0, 595)` | `(430, 290)` | 34 | Left-front shrub and grass occluder for lower-leg overlap near the foreground route. |
| RightFlowersOccluder | `fg/homeyard_occluder_right_flowers.png` | `(1015, 550, 1672, 915)` | `(1015, 550)` | `(657, 365)` | 36 | Right-front flowers, stone wall, and bucket occluder for foreground depth. |
