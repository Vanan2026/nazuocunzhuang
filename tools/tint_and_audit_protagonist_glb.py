from __future__ import annotations

import json
import struct
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "production" / "assets" / "protagonist_3d" / "recolored"
REPORT_PATH = ROOT / ".codex" / "protagonist_3d_asset_audit.md"

INPUTS = [
    Path(r"C:/Users/23732/Downloads/cb790243ea4e7e4dbf40fc8d995eff5d.glb"),
    Path(r"C:/Users/23732/Downloads/c01097343d578a9b755a7c0c07a89795.glb"),
    Path(r"C:/Users/23732/Downloads/effad4009179ed5681340ba9adc2b0a0.glb"),
    Path(r"C:/Users/23732/Downloads/5571ddffb0e493df35384702913f5f41.glb"),
]

# Current project heroine palette approximation (single-color fallback).
TINT_RGB = (0.83, 0.72, 0.63)

GLB_MAGIC = 0x46546C67
JSON_CHUNK = 0x4E4F534A
BIN_CHUNK = 0x004E4942


@dataclass
class GlbData:
    version: int
    gltf: dict
    bin_chunk: bytes | None


def fail(msg: str) -> None:
    raise SystemExit(f"FAIL: {msg}")


def read_glb(path: Path) -> GlbData:
    data = path.read_bytes()
    if len(data) < 20:
        fail(f"{path} is too short to be a GLB")
    magic, version, total_len = struct.unpack_from("<III", data, 0)
    if magic != GLB_MAGIC:
        fail(f"{path} is not a GLB file")
    if total_len != len(data):
        fail(f"{path} length mismatch: header={total_len} actual={len(data)}")

    offset = 12
    json_obj: dict | None = None
    bin_chunk: bytes | None = None

    while offset + 8 <= len(data):
        chunk_len, chunk_type = struct.unpack_from("<II", data, offset)
        offset += 8
        chunk = data[offset : offset + chunk_len]
        offset += chunk_len
        if chunk_type == JSON_CHUNK:
            json_obj = json.loads(chunk.decode("utf-8"))
        elif chunk_type == BIN_CHUNK:
            bin_chunk = chunk

    if json_obj is None:
        fail(f"{path} has no JSON chunk")
    return GlbData(version=version, gltf=json_obj, bin_chunk=bin_chunk)


def pad4(payload: bytes, filler: bytes = b" ") -> bytes:
    rem = len(payload) % 4
    if rem == 0:
        return payload
    return payload + filler * (4 - rem)


def write_glb(path: Path, glb: GlbData) -> None:
    json_bytes = json.dumps(glb.gltf, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    json_bytes = pad4(json_bytes, b" ")
    chunks: list[bytes] = []

    chunks.append(struct.pack("<II", len(json_bytes), JSON_CHUNK))
    chunks.append(json_bytes)

    if glb.bin_chunk is not None:
        bin_bytes = pad4(glb.bin_chunk, b"\x00")
        chunks.append(struct.pack("<II", len(bin_bytes), BIN_CHUNK))
        chunks.append(bin_bytes)

    body = b"".join(chunks)
    header = struct.pack("<III", GLB_MAGIC, glb.version, 12 + len(body))
    path.write_bytes(header + body)


def ensure_tint_material(gltf: dict, tint_rgb: tuple[float, float, float]) -> int:
    mats = gltf.setdefault("materials", [])
    material_index = len(mats)
    mats.append(
        {
            "name": "CodexTint_Protagonist",
            "pbrMetallicRoughness": {
                "baseColorFactor": [float(tint_rgb[0]), float(tint_rgb[1]), float(tint_rgb[2]), 1.0],
                "metallicFactor": 0.0,
                "roughnessFactor": 0.95,
            },
            "doubleSided": False,
        }
    )
    return material_index


def apply_tint_material(gltf: dict, material_index: int) -> int:
    applied = 0
    for mesh in gltf.get("meshes", []):
        for prim in mesh.get("primitives", []):
            prim["material"] = material_index
            applied += 1
    return applied


def has_attr(gltf: dict, attr: str) -> bool:
    for mesh in gltf.get("meshes", []):
        for prim in mesh.get("primitives", []):
            if attr in prim.get("attributes", {}):
                return True
    return False


def animation_names(gltf: dict) -> list[str]:
    return [str(a.get("name", "")) for a in gltf.get("animations", [])]


def summarize(path: Path, gltf: dict) -> dict:
    return {
        "path": str(path),
        "name": path.name,
        "meshes": len(gltf.get("meshes", [])),
        "skins": len(gltf.get("skins", [])),
        "anims": len(gltf.get("animations", [])),
        "materials": len(gltf.get("materials", [])),
        "textures": len(gltf.get("textures", [])),
        "images": len(gltf.get("images", [])),
        "has_uv": has_attr(gltf, "TEXCOORD_0"),
        "has_vertex_color": has_attr(gltf, "COLOR_0"),
        "anim_names": animation_names(gltf),
    }


def write_report(rows: list[dict], out_paths: list[Path]) -> None:
    missing_animation = [r["name"] for r in rows if r["anims"] == 0]
    missing_uv = [r["name"] for r in rows if not r["has_uv"]]
    missing_texture = [r["name"] for r in rows if r["textures"] == 0]
    generic_anim_name = [r["name"] for r in rows if any(name == "Armature" for name in r["anim_names"])]

    lines: list[str] = []
    lines.append("# Protagonist 3D Asset Audit")
    lines.append("")
    lines.append("## Recolor Output")
    for p in out_paths:
        lines.append(f"- `{p}`")
    lines.append("")
    lines.append("## Structural Summary")
    for r in rows:
        lines.append(
            f"- `{r['name']}`: meshes={r['meshes']}, skins={r['skins']}, anims={r['anims']}, "
            f"materials={r['materials']}, textures={r['textures']}, uv={r['has_uv']}, vertex_color={r['has_vertex_color']}"
        )
    lines.append("")
    lines.append("## Gaps To Fill")
    if missing_animation:
        lines.append(f"- Missing animation clips: {', '.join(missing_animation)}")
    if missing_uv:
        lines.append(f"- Missing UV set (TEXCOORD_0): {', '.join(missing_uv)}")
    if missing_texture:
        lines.append(f"- Missing texture/image payload: {', '.join(missing_texture)}")
    if generic_anim_name:
        lines.append(f"- Generic animation naming (`Armature`) needs clip naming: {', '.join(generic_anim_name)}")
    lines.append("- No material slots by part (hair/skin/top/bottom/shoes), so current tint is whole-body uniform color only.")
    lines.append("")
    lines.append("## Recommended Next Batch")
    lines.append("- Export one rig with named clips: `idle`, `walk`, `interact`, `sit_down`, `sit_idle`, `stand_up`.")
    lines.append("- Ensure mesh includes `TEXCOORD_0` and at least one texture set (base color).")
    lines.append("- Split materials at least into: skin, hair, cloth_top, cloth_bottom, shoes.")
    lines.append("- Keep fixed scale and root orientation consistent across all clips.")
    lines.append("")
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows: list[dict] = []
    out_paths: list[Path] = []

    for src in INPUTS:
        if not src.exists():
            fail(f"missing input GLB: {src}")
        glb = read_glb(src)
        tint_index = ensure_tint_material(glb.gltf, TINT_RGB)
        prim_count = apply_tint_material(glb.gltf, tint_index)
        out = OUT_DIR / f"{src.stem}_tinted.glb"
        write_glb(out, glb)
        rows.append(summarize(out, glb.gltf) | {"prims_tinted": prim_count})
        out_paths.append(out)

    write_report(rows, out_paths)
    print(f"OK: wrote tinted GLBs -> {OUT_DIR}")
    print(f"OK: wrote audit report -> {REPORT_PATH}")


if __name__ == "__main__":
    main()
