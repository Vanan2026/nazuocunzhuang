from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "tools" / "validate_home_area_world2d_v001.py"


def main() -> None:
    if not VALIDATOR.exists():
        print("FAIL: missing HomeArea World2D v001 validator")
        raise SystemExit(1)

    result = subprocess.run(
        [sys.executable, str(VALIDATOR)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        print(result.stdout, end="")
        print(result.stderr, end="", file=sys.stderr)
        raise SystemExit(result.returncode)

    if "OK: HomeArea World2D v001 package and scene integration validated" not in result.stdout:
        print(result.stdout, end="")
        print("FAIL: validator did not report the expected success message")
        raise SystemExit(1)

    print("OK: HomeArea World2D v001 validator contract passed")


if __name__ == "__main__":
    main()
