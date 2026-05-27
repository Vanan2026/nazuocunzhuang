# Greenfield P0 External GPT Handoff v002

This folder is the current small-batch handoff contract for externally generated Greenfield P0 art.

Use `prompt_briefs.md` for copy-paste generation requests. Use `asset_request_manifest.json` as the machine-readable contract for paths, sizes, alpha rules, and replacement destinations.

## Why v002

`v001` contains useful historical request data, but it includes very large region batches. `v002` is split into smaller executable batches so each generation task can be reviewed, replaced, and validated without asking for a huge image set at once.

## Incoming Root

```text
production/assets/external_gpt_handoff/greenfield_p0/v002/incoming/
```

Generated files must preserve the exact relative paths listed in `prompt_briefs.md`.

## Batch Size

Each batch contains 12 or fewer assets. Region layers must be generated as one coordinated full-canvas set so the layers stay registration-perfect.

## Validation

Handoff contract:

```powershell
py -3.12 tools\validate_greenfield_p0_gpt_asset_handoff_v002.py
```

Generated incoming files after delivery:

```powershell
py -3.12 tools\validate_greenfield_p0_external_asset_intake.py --manifest production\assets\external_gpt_handoff\greenfield_p0\v002\asset_request_manifest.json --allow-partial
```

## Approval Boundary

Passing validation means paths, canvas sizes, alpha rules, and contracts are usable. It does not mean final visual approval. Human visual approval is still required before any generated asset is marked launch-quality.
