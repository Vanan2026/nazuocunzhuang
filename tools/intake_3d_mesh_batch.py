from __future__ import annotations

import json
import shutil
import struct
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "assets" / "3d" / "raw"
PROCESSED_DIR = ROOT / "assets" / "3d" / "processed"
REPORT = ROOT / ".codex" / "mesh_3d_intake_report.md"

INPUTS = [
    Path(r"C:/Users/23732/Downloads/cb790243ea4e7e4dbf40fc8d995eff5d.glb"),
    Path(r"C:/Users/23732/Downloads/c01097343d578a9b755a7c0c07a89795.glb"),
    Path(r"C:/Users/23732/Downloads/effad4009179ed5681340ba9adc2b0a0.glb"),
    Path(r"C:/Users/23732/Downloads/5571ddffb0e493df35384702913f5f41.glb"),
]

# Warm low-saturation fallback tint for first 3D preview phase.
TINT = (0.82, 0.74, 0.67)

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
        fail(f"{path.name} too short")
    magic, version, total_len = struct.unpack_from("<III", data, 0)
    if magic != GLB_MAGIC:
        fail(f"{path.name} invalid GLB magic")
    if total_len != len(data):
        fail(f"{path.name} length mismatch")

    offset = 12
    gltf: dict | None = None
    bin_chunk: bytes | None = None
    while offset + 8 <= len(data):
        chunk_len, chunk_type = struct.unpack_from("<II", data, offset)
        offset += 8
        chunk = data[offset : offset + chunk_len]
        offset += chunk_len
        if chunk_type == JSON_CHUNK:
            gltf = json.loads(chunk.decode("utf-8"))
        elif chunk_type == BIN_CHUNK:
            bin_chunk = chunk
    if gltf is None:
        fail(f"{path.name} missing JSON chunk")
    return GlbData(version=version, gltf=gltf, bin_chunk=bin_chunk)


def pad4(data: bytes, pad_byte: bytes) -> bytes:
    rem = len(data) % 4
    return data if rem == 0 else data + pad_byte * (4 - rem)


def write_glb(path: Path, glb: GlbData) -> None:
    json_bytes = json.dumps(glb.gltf, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    json_bytes = pad4(json_bytes, b" ")
    body = struct.pack("<II", len(json_bytes), JSON_CHUNK) + json_bytes
    if glb.bin_chunk is not None:
        bin_bytes = pad4(glb.bin_chunk, b"\x00")
        body += struct.pack("<II", len(bin_bytes), BIN_CHUNK) + bin_bytes
    header = struct.pack("<III", GLB_MAGIC, glb.version, 12 + len(body))
    path.write_bytes(header + body)


def add_tint_material(gltf: dict, tint: tuple[float, float, float]) -> int:
    materials = gltf.setdefault("materials", [])
    index = len(materials)
    materials.append(
        {
            "name": "Mesh3D_FirstPassTint",
            "pbrMetallicRoughness": {
                "baseColorFactor": [tint[0], tint[1], tint[2], 1.0],
                "metallicFactor": 0.0,
                "roughnessFactor": 0.92,
            },
        }
    )
    return index


def bind_material(gltf: dict, material_index: int) -> int:
    count = 0
    for mesh in gltf.get("meshes", []):
        for prim in mesh.get("primitives", []):
            prim["material"] = material_index
            count += 1
    return count


def has_attr(gltf: dict, attr: str) -> bool:
    for mesh in gltf.get("meshes", []):
        for prim in mesh.get("primitives", []):
            if attr in prim.get("attributes", {}):
                return True
    return False


def summarize(gltf: dict) -> dict:
    anim_names = [str(a.get("name", "")) for a in gltf.get("animations", [])]
    return {
        "meshes": len(gltf.get("meshes", [])),
        "skins": len(gltf.get("skins", [])),
        "animations": len(gltf.get("animations", [])),
        "materials": len(gltf.get("materials", [])),
        "textures": len(gltf.get("textures", [])),
        "images": len(gltf.get("images", [])),
        "has_uv": has_attr(gltf, "TEXCOORD_0"),
        "anim_names": anim_names,
    }


def write_report(rows: list[tuple[str, dict]]) -> None:
    lines = ["# First 3D Mesh Intake Report", "", "## Files"]
    for name, s in rows:
        lines.append(
            f"- `{name}` meshes={s['meshes']} skins={s['skins']} anims={s['animations']} "
            f"materials={s['materials']} textures={s['textures']} uv={s['has_uv']}"
        )
    lines += ["", "## Gaps"]
    for name, s in rows:
        if s["animations"] == 0:
            lines.append(f"- `{name}` missing animation clip")
        if not s["has_uv"]:
            lines.append(f"- `{name}` missing TEXCOORD_0")
        if s["textures"] == 0:
            lines.append(f"- `{name}` missing texture payload")
        if any(n.lower() == "armature" for n in s["anim_names"]):
            lines.append(f"- `{name}` has generic animation name `Armature`")
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    rows: list[tuple[str, dict]] = []
    for src in INPUTS:
        if not src.exists():
            fail(f"missing input file: {src}")
        raw_name = src.name
        raw_dst = RAW_DIR / raw_name
        shutil.copy2(src, raw_dst)

        glb = read_glb(src)
        material_index = add_tint_material(glb.gltf, TINT)
        bind_material(glb.gltf, material_index)
        processed_name = f"{src.stem}_firstpass.glb"
        processed_dst = PROCESSED_DIR / processed_name
        write_glb(processed_dst, glb)
        rows.append((processed_name, summarize(glb.gltf)))

    write_report(rows)
    print(f"OK: copied raw GLBs -> {RAW_DIR}")
    print(f"OK: wrote first-pass GLBs -> {PROCESSED_DIR}")
    print(f"OK: wrote intake report -> {REPORT}")


if __name__ == "__main__":
    main()
