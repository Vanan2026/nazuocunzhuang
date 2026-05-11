# Scene Directory Status

## Active Main World

- `scenes/regions/region_home_area.tscn`
  - Current project entry scene.
  - Owns the explorable 2D world structure from the v0.1 spec.
  - Uses Region/ground/path/detail/YSortWorld/ForegroundStatic/LightAndWeather/CameraRig/UI structure.
  - Contains modular `GroundModules` and `PathModules` under `TileMapLayer_*` as the replacement path for large one-off ground polygons.

## Connected Active Regions

- `scenes/regions/region_home_back_farm.tscn`
  - First connected backyard/farm region.
  - Entered from `Region_HomeArea/YSortWorld/Interactables/BackyardFarmEntrance`.
  - Returns through `Region_HomeBackFarm/YSortWorld/Interactables/HomeAreaEntrance`.
  - Uses the same Region/TileMapLayer/module/WalkableZone/YSortWorld/CameraRig structure.

## Active Tools

- `tools/validate_region_home_area_scene.py`
  - Current scene contract, active-path guard, and connected region contract.
  - Fails if entry scripts or default test tools point back to `scenes/world/*`.
- `tools/load_scene.gd`
- `tools/test_scene.gd`
- `tools/render_scene_snapshot.gd`
  - Default to `Region_HomeArea`.

## Reference / Legacy Visual Slices

- `scenes/world/cloud_village_homeyard.tscn`
  - Reference playable visual slice for the earlier single-homeyard composition.
  - Keep for art comparison, protagonist scale checks, and source-layer validation.
  - Do not add new core world systems here.

- `scenes/world/cloud_house.tscn`
  - Earlier porch/homeyard asset integration scene.
  - Keep only as a legacy asset check until its useful pieces are migrated into `Region_HomeArea`.

- `scenes/world/cloud_village.tscn`
  - Older broad village scene.
  - Keep as legacy until Region/Chunk flow replaces it.

## Rule

New explorable-world work goes under:

- `scenes/regions/`
- `scripts/world/` for shared world components
- `tools/validate_region_*` for region contracts

Do not create another main playable home-area scene under `scenes/world/`.

Legacy cloud/homeyard generation and validation scripts live under:

- `tools/legacy_homeyard/`

Do not use those scripts as the active build/load gate for the playable world.
