from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "production" / "assets" / "regions" / "home_area_bake" / "region_home_area_bake_contract.json"
CANDIDATE_DIR = ROOT / "production" / "assets" / "regions" / "home_area_bake" / "candidates" / "v001"
MANIFEST = CANDIDATE_DIR / "region_home_area_bake_candidate_manifest.json"
PREVIEW = CANDIDATE_DIR / "region_home_area_bake_candidate_preview.png"


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def require_dict(value: Any, label: str) -> dict[str, Any]:
    require(isinstance(value, dict), f"{label} must be an object")
    return value


def nontransparent_bbox(image: Image.Image) -> tuple[int, int, int, int] | None:
    if image.mode != "RGBA":
        return None
    return image.getchannel("A").getbbox()


def main() -> None:
    require(CONTRACT.exists(), f"missing contract: {CONTRACT}")
    require(MANIFEST.exists(), f"missing candidate manifest: {MANIFEST}")
    require(PREVIEW.exists(), f"missing candidate preview: {PREVIEW}")

    contract = require_dict(json.loads(CONTRACT.read_text(encoding="utf-8")), "contract")
    manifest = require_dict(json.loads(MANIFEST.read_text(encoding="utf-8")), "manifest")
    manifest_layers = manifest.get("layers")
    require(isinstance(manifest_layers, list) and manifest_layers, "manifest layers must be a non-empty list")

    expected_layers = contract.get("export_layers")
    require(isinstance(expected_layers, list) and expected_layers, "contract export_layers must be a non-empty list")
    expected_ids = {layer["id"] for layer in expected_layers}
    manifest_by_id = {layer.get("id"): layer for layer in manifest_layers if isinstance(layer, dict)}
    missing = expected_ids - set(manifest_by_id)
    require(not missing, f"candidate manifest missing layers: {sorted(missing)}")

    for contract_layer in expected_layers:
        layer_id = contract_layer["id"]
        manifest_layer = require_dict(manifest_by_id[layer_id], f"manifest layer {layer_id}")
        output = CANDIDATE_DIR / str(manifest_layer.get("file"))
        require(output.exists(), f"missing candidate PNG for {layer_id}: {output}")
        require(output.name == contract_layer["export_name"], f"{layer_id} output must match contract export name")

        with Image.open(output) as image:
            require(image.mode == "RGBA", f"{layer_id} must be RGBA")
            width, height = image.size
            require(width > 0 and height > 0, f"{layer_id} must have non-zero dimensions")
            bbox = nontransparent_bbox(image)
            require(bbox is not None, f"{layer_id} must contain visible pixels")

            if contract_layer["type"] in {"ground_patch", "path_patch", "light_overlay"}:
                require(width >= 512 and height >= 256, f"{layer_id} patch is too small")
            if "occluder" in contract_layer["type"] or contract_layer["target_parent"] == "ForegroundStatic":
                alpha_bbox_width = bbox[2] - bbox[0]
                alpha_bbox_height = bbox[3] - bbox[1]
                require(alpha_bbox_width <= width and alpha_bbox_height <= height, f"{layer_id} alpha bounds invalid")

    with Image.open(PREVIEW) as preview:
        require(preview.mode == "RGBA", "preview must be RGBA")
        require(preview.size == (1536, 1024), "preview must be 1536x1024")
        require(nontransparent_bbox(preview) is not None, "preview must contain visible pixels")

    print("OK: Region_HomeArea bake candidate outputs validated")


if __name__ == "__main__":
    main()
