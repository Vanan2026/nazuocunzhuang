from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "production" / "assets" / "final_art" / "home_area" / "props"
RUNTIME_DIR = ROOT / "assets" / "art" / "props"
OUT_DIR = ROOT / "production" / "assets" / "final_art" / "runtime_landing_pass1"
MANIFEST_PATH = OUT_DIR / "art_landing_pass1_manifest.json"

PROP_FILES = {
    "region_home_area_prop_mailbox_v001.png": "mailbox",
    "region_home_area_prop_road_sign_v001.png": "road_sign",
    "region_home_area_prop_well_broken_v001.png": "old_well_broken",
    "region_home_area_prop_bench_v001.png": "bench",
}


def main() -> None:
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    assets: list[dict[str, object]] = []
    for filename, role in PROP_FILES.items():
        source_path = SOURCE_DIR / filename
        if not source_path.is_file():
            raise FileNotFoundError(source_path)
        runtime_path = RUNTIME_DIR / filename
        evidence_path = OUT_DIR / filename
        shutil.copy2(source_path, runtime_path)
        shutil.copy2(source_path, evidence_path)
        assets.append(
            {
                "role": role,
                "source": str(source_path.relative_to(ROOT)).replace("\\", "/"),
                "runtime_file": str(runtime_path.relative_to(ROOT)).replace("\\", "/"),
                "evidence_file": str(evidence_path.relative_to(ROOT)).replace("\\", "/"),
            }
        )

    MANIFEST_PATH.write_text(
        json.dumps(
            {
                "package_id": "art_landing_pass1_runtime_props",
                "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "runtime_replacement": True,
                "source_batch": "final_art_phase2_batch_c_interactable_props",
                "assets": assets,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"OK: copied {len(assets)} runtime props and wrote {MANIFEST_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
