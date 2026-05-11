# Homeyard mother-image split batch

- Source image: `resources/设计图/主角家檐廊.png`.
- Runtime base plate: `sprites/environments/homeyard/bg/homeyard_bg_sky_01.png` is the resized mother image, not a synthetic sky-only layer.
- Source splits: full-scene transparent layers are extracted from the mother image and hidden by default in `cloud_house.tscn` to avoid double rendering.
- Props absent from the mother image (`well`, `bucket`) remain generated cutouts but are hidden by default.
