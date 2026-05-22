# Greenfield P0 External Asset Handoff

This folder is the handoff contract for externally generated Greenfield P0 art assets.

Workflow:
1. Codex writes detailed asset requests and exact incoming paths here.
2. The user generates PNGs externally from the request.
3. The user drops PNGs under `incoming/` with the exact relative paths.
4. Codex runs the intake validator, imports accepted assets, regenerates contact sheets/review scenes, and continues Godot development.

No generation model is named or required by this contract. The contract is path, size, alpha, style, and gameplay-readability based.

## Files
- `asset_request_manifest.json`: machine-readable full request and acceptance contract.
- `asset_request_table.csv`: spreadsheet-friendly request table.
- `prompt_briefs.md`: human-readable prompt list grouped by batch.
- `incoming/`: drop generated PNGs here, preserving listed paths.

## Batch Counts
- `batch_a_style_lock`: 6 assets
- `batch_b_regions`: 110 assets
- `batch_c_characters`: 116 assets
- `batch_d_system_assets`: 217 assets

## Validate Intake

Partial batch:
```powershell
py -3.12 tools\validate_greenfield_p0_external_asset_intake.py --allow-partial
```

Strict full package:
```powershell
py -3.12 tools\validate_greenfield_p0_external_asset_intake.py
```

Use any Python that has Pillow installed; on this machine `py -3.12` is the verified command.
