from __future__ import annotations

from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
GROUND = ROOT / "production/assets/regions/home_area_launch_quality/v001/layers/region_home_area_ground_yard_lq_v001.png"
SCREENSHOT = ROOT / ".codex/region_home_area_walk_01_default_spawn.png"
CANVAS = (6144, 4096)
CLEAR_BLUE_MIN = (115, 160, 195)
CLEAR_BLUE_MAX = (145, 190, 225)


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def count_clear_blue(image: Image.Image) -> int:
    count = 0
    pixels = image.load()
    width, height = image.size
    for y in range(height):
        for x in range(width):
            r, g, b, _a = pixels[x, y]
            if CLEAR_BLUE_MIN[0] <= r <= CLEAR_BLUE_MAX[0] and CLEAR_BLUE_MIN[1] <= g <= CLEAR_BLUE_MAX[1] and CLEAR_BLUE_MIN[2] <= b <= CLEAR_BLUE_MAX[2]:
                count += 1
    return count


def main() -> None:
    require(GROUND.exists(), "missing launch_quality/v001 ground layer")
    ground = Image.open(GROUND).convert("RGBA")
    require(ground.size == CANVAS, f"ground size mismatch: {ground.size}")
    require(ground.getchannel("A").getextrema() == (255, 255), "ground layer must be fully opaque to prevent viewport clear-color leaks")
    require(SCREENSHOT.exists(), "missing visual walkthrough default-spawn screenshot")
    screenshot = Image.open(SCREENSHOT).convert("RGBA")
    clear_blue = count_clear_blue(screenshot)
    allowed = max(1200, int(screenshot.width * screenshot.height * 0.002))
    require(clear_blue <= allowed, f"default-spawn screenshot has too much clear-blue leak: {clear_blue} > {allowed}")
    print("OK: HomeArea launch_quality/v001 visual sanity blocks ground alpha and clear-color leaks")


if __name__ == "__main__":
    main()
