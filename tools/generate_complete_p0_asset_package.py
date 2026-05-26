from __future__ import annotations

import json
import math
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ITEMS = ROOT / "game/data/items.json"
ITEM_DIR = ROOT / "assets/art/items"
NPC_DIR = ROOT / "assets/art/characters/npc"
PORTRAIT_DIR = ROOT / "assets/art/portraits"
ITEM_PACK = ROOT / "production/assets/items/p0_item_icons/v001"
NPC_PACK = ROOT / "production/assets/characters/p0_npc_complete_runtime/v001"
REPORT_DIR = ROOT / ".codex/reports"
NPCS = ["aoi", "gen", "mika", "hana"]
DIRS = ["down", "up", "left", "right"]
EXPRS = ["neutral", "happy", "thinking"]
LINE = (82, 62, 44, 255)
SHADOW = (66, 54, 40, 58)
CONFIG = {
    "aoi": ((232,183,145,255),(51,58,67,255),(91,132,142,255),(71,91,94,255),(224,190,92,255),"ledger"),
    "gen": ((221,171,132,255),(91,89,80,255),(118,100,78,255),(82,87,80,255),(174,117,71,255),"wood"),
    "mika": ((235,190,151,255),(77,63,55,255),(176,108,96,255),(99,86,102,255),(219,169,82,255),"mailbag"),
    "hana": ((238,190,151,255),(85,73,61,255),(143,126,169,255),(89,99,120,255),(211,154,174,255),"flower"),
}
COL = {
    "wood": (145,103,62,255), "stone": (138,137,126,255), "rice": (237,230,205,255),
    "turnip": (232,225,204,255), "strawberry": (196,76,78,255), "potato": (174,128,74,255),
    "cucumber": (82,151,94,255), "tomato": (202,78,66,255), "watermelon": (77,137,83,255),
    "pumpkin": (212,140,65,255), "daikon": (230,232,216,255), "persimmon": (219,133,56,255),
    "tea": (91,139,84,255), "fish": (123,154,170,255), "flower": (217,145,172,255),
    "bell": (190,151,80,255), "seed": (137,157,102,255), "spring": (121,169,113,255),
    "summer": (84,145,118,255), "autumn": (189,132,74,255), "winter": (132,159,176,255),
}


def ensure() -> None:
    for p in [ITEM_DIR, NPC_DIR, PORTRAIT_DIR, ITEM_PACK / "runtime_exports", NPC_PACK / "runtime_exports", REPORT_DIR]:
        p.mkdir(parents=True, exist_ok=True)


def res_path(path: str) -> Path:
    return ROOT / path.replace("res://", "", 1)


def shadow(img: Image.Image, box: tuple[int, int, int, int]) -> None:
    s = Image.new("RGBA", img.size, (0,0,0,0)); ImageDraw.Draw(s).ellipse(box, fill=SHADOW)
    img.alpha_composite(s.filter(ImageFilter.GaussianBlur(3)))


def e(d: ImageDraw.ImageDraw, b, fill, outline=LINE, w=2) -> None:
    d.ellipse(tuple(map(int,b)), fill=fill, outline=outline, width=w)


def rr(d: ImageDraw.ImageDraw, b, r, fill, outline=LINE, w=2) -> None:
    d.rounded_rectangle(tuple(map(int,b)), radius=r, fill=fill, outline=outline, width=w)


def poly(d: ImageDraw.ImageDraw, pts, fill, outline=LINE, w=2) -> None:
    d.polygon([(int(x), int(y)) for x,y in pts], fill=fill)
    d.line([(int(x), int(y)) for x,y in pts + [pts[0]]], fill=outline, width=w, joint="curve")


def pick(item_id: str):
    for key, color in COL.items():
        if key in item_id:
            return color
    return COL["seed"]


def draw_seed(d, item_id):
    color = pick(item_id)
    rr(d, (16,18,48,52), 7, (222,191,139,255))
    d.line((21,24,43,24), fill=(130,91,55,255), width=2)
    for x,y in [(27,32),(35,36),(29,43),(39,45)]: e(d, (x-4,y-3,x+4,y+3), color, w=1)


def draw_material(d, item_id):
    if item_id == "wood":
        rr(d, (13,27,52,42), 7, COL["wood"]); d.line((18,33,48,32), fill=(105,69,42,255), width=2); e(d,(40,29,48,38),(190,139,86,255),w=1)
    else:
        poly(d, [(17,40),(26,23),(45,21),(55,39),(42,52),(24,50)], COL["stone"]); d.line((28,27,39,45), fill=(112,111,101,255), width=2)


def draw_crop(d, item_id, category):
    color = pick(item_id)
    if "watermelon" in item_id: e(d,(14,25,52,50),color); d.arc((19,25,47,50),190,350,fill=(42,100,57,255),width=2)
    elif "pumpkin" in item_id: e(d,(13,25,53,52),color); [d.arc((x-12,25,x+12,53),80,280,fill=(162,93,45,255),width=2) for x in [24,32,40]]; d.line((32,25,36,18), fill=(83,121,64,255), width=3)
    elif "cucumber" in item_id: rr(d,(18,28,50,43),8,color)
    elif "strawberry" in item_id: e(d,(20,22,46,53),color); poly(d,[(23,23),(31,16),(40,23)],(91,147,82,255),w=1)
    elif "tomato" in item_id: e(d,(17,23,50,52),color); poly(d,[(27,25),(33,17),(39,25),(45,24),(38,30),(30,30)],(81,137,74,255),w=1)
    elif "potato" in item_id: e(d,(18,26,49,51),color); [e(d,(x,y,x+3,y+3),(113,77,47,255),outline=None,w=0) for x,y in [(28,35),(38,31),(40,43)]]
    elif "daikon" in item_id or "turnip" in item_id: e(d,(20,24,45,54),color); poly(d,[(26,25),(32,14),(38,25)],(93,145,83,255),w=1)
    elif "persimmon" in item_id: e(d,(17,23,50,52),COL["persimmon"]); poly(d,[(25,25),(33,17),(42,25),(35,30)],(96,119,68,255),w=1)
    else: e(d,(18,24,49,51),color)
    if category == "crop": d.arc((17,20,51,54),35,110,fill=(255,248,229,120),width=2)


def draw_gather(d, item_id):
    if item_id == "wildflower_spring":
        d.line((32,50,32,28), fill=(84,139,82,255), width=3)
        for cx,cy in [(25,30),(32,23),(40,30),(32,36)]: e(d,(cx-7,cy-7,cx+7,cy+7),COL["flower"],w=1)
        e(d,(28,27,36,35),(231,190,81,255),w=1)
    elif item_id == "tea_leaf":
        for cx,cy in [(26,35),(38,31),(35,43)]: e(d,(cx-9,cy-5,cx+9,cy+5),COL["tea"],w=1); d.line((cx-6,cy,cx+7,cy), fill=(194,218,157,255), width=1)
    elif item_id == "small_carp":
        e(d,(14,27,48,45),COL["fish"]); poly(d,[(48,36),(58,27),(57,45)],(105,135,151,255)); e(d,(22,32,25,35),(31,38,42,255),outline=None,w=0)
    else:
        poly(d,[(21,44),(32,18),(45,23),(42,49),(29,54)],COL["bell"]); d.line((27,47,40,35), fill=(130,93,52,255), width=2); e(d,(29,19,37,27),(225,190,111,255),w=1)


def draw_food(d, item_id):
    if "riceball" in item_id:
        poly(d,[(18,47),(32,18),(48,47)],(241,235,215,255)); rr(d,(26,37,40,48),3,(62,81,61,255),w=1)
        if "persimmon" in item_id: e(d,(38,21,49,33),COL["persimmon"],w=1)
    elif "soup" in item_id:
        rr(d,(15,31,51,50),8,(222,217,190,255)); e(d,(17,24,49,42),(213,151,86,255)); [e(d,(x-3,y-2,x+3,y+2),c,outline=None,w=0) for x,y,c in [(27,33,COL["turnip"]),(36,31,COL["tea"]),(41,36,COL["pumpkin"])]]
    elif "grilled" in item_id: draw_gather(d,"small_carp"); d.line((18,51,52,20), fill=(127,82,45,255), width=2)
    elif "tea" in item_id: rr(d,(17,30,45,50),6,(202,223,201,255)); d.arc((42,33,56,47),270,90,fill=LINE,width=3); e(d,(20,24,44,37),(116,152,89,255))
    else: e(d,(17,25,50,51),COL["rice"])


def item_icon(item):
    img = Image.new("RGBA", (64,64), (0,0,0,0)); shadow(img, (14,44,52,58)); d = ImageDraw.Draw(img, "RGBA")
    item_id, cat = item["item_id"], item["category"]
    if cat == "seed": draw_seed(d, item_id)
    elif cat == "material": draw_material(d, item_id)
    elif cat == "food": draw_food(d, item_id)
    elif cat in {"forage","fish","key"}: draw_gather(d, item_id)
    else: draw_crop(d, item_id, cat)
    return img


def body(d, cfg, direction, frame):
    skin,hair,top,bottom,accent,cue = cfg; step = [0,-3,0,3][frame % 4]; side = -1 if direction == "left" else 1
    if direction in {"up","down"}: side = -1 if frame % 2 else 1
    rr(d,(46,48,82,91),10,top); d.polygon([(52,89),(41,110+step),(57,111),(64,87)], fill=bottom, outline=LINE); d.polygon([(76,89),(87,110-step),(71,111),(64,87)], fill=bottom, outline=LINE)
    d.line((49,63,39,79+[4,-4,4,-4][frame%4]), fill=skin, width=6); d.line((79,63,89,79-[4,-4,4,-4][frame%4]), fill=skin, width=6)
    shift = 0 if direction in {"up","down"} else side*4; e(d,(47+shift,22,81+shift,56),skin); d.pieslice((45+shift,20,83+shift,45),180,360,fill=hair,outline=LINE,width=2)
    if direction != "up":
        if direction == "down": e(d,(56,38,59,41),(38,35,32,255),outline=None,w=0); e(d,(69,38,72,41),(38,35,32,255),outline=None,w=0)
        else: e(d,(64+side*6,38,67+side*6,41),(38,35,32,255),outline=None,w=0)
        d.arc((58+shift,43,72+shift,50),20,145,fill=(118,69,63,255),width=1)
    if cue == "mailbag": d.line((50,54,79,85), fill=accent, width=3); rr(d,(76,75,93,91),4,(171,125,76,255),w=1)
    elif cue == "ledger": rr(d,(77,66,91,83),2,(93,111,116,255),w=1)
    elif cue == "wood": d.line((82,66,95,83), fill=accent, width=4)
    elif cue == "flower": e(d,(76,13,86,23),accent,outline=(126,75,96,255),w=1)


def npc_sprite(npc_id, direction, frame=0):
    img = Image.new("RGBA", (128,128), (0,0,0,0)); shadow(img,(39,108,89,122)); body(ImageDraw.Draw(img,"RGBA"), CONFIG[npc_id], direction, frame); return img


def portrait(npc_id, expr):
    skin,hair,top,bottom,accent,cue = CONFIG[npc_id]; img = Image.new("RGBA", (512,512), (0,0,0,0)); d = ImageDraw.Draw(img,"RGBA")
    d.ellipse((66,56,446,458), fill=(232,218,190,210)); d.ellipse((105,94,408,420), fill=(247,238,216,220)); rr(d,(178,282,334,464),38,top,w=5)
    d.line((190,315,152,400), fill=skin, width=18); d.line((322,315,360,400), fill=skin, width=18); e(d,(157,104,355,316),skin,w=5); d.pieslice((145,86,367,235),180,360,fill=hair,outline=LINE,width=5)
    if expr == "happy": d.arc((204,207,232,228),20,160,fill=(42,37,32,255),width=5); d.arc((280,207,308,228),20,160,fill=(42,37,32,255),width=5); d.arc((222,250,292,292),10,170,fill=(130,70,66,255),width=5)
    elif expr == "thinking": d.line((202,214,232,216), fill=(42,37,32,255), width=5); e(d,(286,210,296,222),(42,37,32,255),outline=None,w=0); d.arc((230,258,286,286),190,340,fill=(130,70,66,255),width=4); d.ellipse((360,112,378,130), fill=(223,206,170,210), outline=(112,84,58,230), width=2)
    else: e(d,(208,212,219,224),(42,37,32,255),outline=None,w=0); e(d,(292,212,303,224),(42,37,32,255),outline=None,w=0); d.arc((230,254,284,280),20,160,fill=(130,70,66,255),width=4)
    d.ellipse((184,236,224,256), fill=(213,122,111,65)); d.ellipse((288,236,328,256), fill=(213,122,111,65))
    if cue == "ledger": rr(d,(316,342,388,424),8,(92,113,118,255),w=3)
    elif cue == "wood": rr(d,(308,346,392,380),12,(154,98,58,255),w=3)
    elif cue == "mailbag": d.line((175,306,335,456), fill=(217,165,84,255), width=13)
    elif cue == "flower": d.line((338,346,370,430), fill=(93,143,82,255), width=5); e(d,(350,326,386,362),accent,outline=(126,75,96,255),w=2)
    return img


def stats(path):
    img = Image.open(path).convert("RGBA"); a = img.getchannel("A"); vals = list(a.getdata()); bbox = a.getbbox()
    return {"width": img.width, "height": img.height, "transparent_pixels": sum(1 for v in vals if v == 0), "opaque_pixels": sum(1 for v in vals if v == 255), "alpha_bbox": list(bbox) if bbox else None}


def save(img, path):
    path.parent.mkdir(parents=True, exist_ok=True); img.save(path)


def copy_prod_portrait(npc_id, expr, dest):
    src = ROOT / f"production/assets/final_art/characters/npc/npc_{npc_id}_portrait_{expr}_512.png"
    if src.exists() and not dest.exists(): shutil.copy2(src, dest); return True
    return False


def build_items():
    recs = []
    for item in json.loads(ITEMS.read_text(encoding="utf-8-sig")):
        icon = res_path(item["icon"]); existed = icon.exists()
        if not existed: save(item_icon(item), icon)
        pc = ITEM_PACK / "runtime_exports" / icon.name; pc.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(icon, pc)
        recs.append({"item_id": item["item_id"], "name": item["name"], "category": item["category"], "runtime_file": icon.relative_to(ROOT).as_posix(), "package_file": pc.relative_to(ROOT).as_posix(), "source": "existing_runtime_reused" if existed else "generated_from_item_data", "size_px": [64,64], "alpha_check": stats(icon)})
    return recs


def build_npcs():
    recs = []
    for npc in NPCS:
        for direction in DIRS:
            p = NPC_DIR / f"npc_{npc}_idle_{direction}_128.png"; existed = p.exists()
            if not existed: save(npc_sprite(npc,direction,0), p)
            pc = NPC_PACK / "runtime_exports" / p.name; pc.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(p, pc)
            recs.append({"npc_id": npc, "kind": "idle", "direction": direction, "runtime_file": p.relative_to(ROOT).as_posix(), "package_file": pc.relative_to(ROOT).as_posix(), "source": "existing_runtime_reused" if existed else "generated_directional_sprite", "size_px": [128,128], "alpha_check": stats(p)})
        for direction in DIRS:
            p = NPC_DIR / f"npc_{npc}_walk_{direction}_4x128.png"; existed = p.exists()
            if not existed:
                sheet = Image.new("RGBA", (512,128), (0,0,0,0))
                for frame in range(4): sheet.alpha_composite(npc_sprite(npc,direction,frame), (frame*128, 0))
                save(sheet, p)
            pc = NPC_PACK / "runtime_exports" / p.name; pc.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(p, pc)
            recs.append({"npc_id": npc, "kind": "walk", "direction": direction, "runtime_file": p.relative_to(ROOT).as_posix(), "package_file": pc.relative_to(ROOT).as_posix(), "source": "existing_runtime_reused" if existed else "generated_4_frame_walk_sheet", "size_px": [512,128], "frame_count": 4, "frame_size_px": [128,128], "alpha_check": stats(p)})
        for expr in EXPRS:
            p = PORTRAIT_DIR / f"npc_{npc}_portrait_{expr}_512.png"; existed = p.exists(); copied = copy_prod_portrait(npc, expr, p)
            if not p.exists(): save(portrait(npc,expr), p)
            pc = NPC_PACK / "runtime_exports" / p.name; pc.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(p, pc)
            recs.append({"npc_id": npc, "kind": "portrait", "expression": expr, "runtime_file": p.relative_to(ROOT).as_posix(), "package_file": pc.relative_to(ROOT).as_posix(), "source": "existing_runtime_reused" if existed else ("copied_from_final_art_phase2" if copied else "generated_portrait"), "size_px": [512,512], "alpha_check": stats(p)})
    return recs


def sheet(records, path, thumb, cols):
    rows = math.ceil(len(records)/cols); cell=(thumb[0]+16, thumb[1]+38); out=Image.new("RGBA", (cols*cell[0], rows*cell[1]), (239,229,207,255)); d=ImageDraw.Draw(out)
    try: font = ImageFont.truetype("arial.ttf", 10)
    except OSError: font = ImageFont.load_default()
    for i,r in enumerate(records):
        img=Image.open(ROOT/r["runtime_file"]).convert("RGBA"); img.thumbnail(thumb, Image.Resampling.LANCZOS); c=i%cols; row=i//cols; x=c*cell[0]+8; y=row*cell[1]+8
        bg=Image.new("RGBA", thumb, (255,255,255,255)); bd=ImageDraw.Draw(bg)
        for yy in range(0, thumb[1], 12):
            for xx in range(0, thumb[0], 12):
                if (xx//12+yy//12)%2==0: bd.rectangle((xx,yy,xx+11,yy+11), fill=(221,213,199,255))
        out.alpha_composite(bg,(x,y)); out.alpha_composite(img,(x+(thumb[0]-img.width)//2,y+(thumb[1]-img.height)//2)); d.text((x,y+thumb[1]+4), Path(r["runtime_file"]).name[:32], fill=(81,62,45,255), font=font)
    path.parent.mkdir(parents=True, exist_ok=True); out.convert("RGB").save(path)


def write_outputs(item_records, npc_records):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    item_manifest = {"package_id":"p0_item_icons_v001","asset_type":"item_icon_batch","status":"usable","created_at":now,"source_data":"game/data/items.json","runtime_replacement":True,"launch_quality_approved":False,"human_visual_approval_required":True,"runtime_dir":"assets/art/items","runtime_exports":item_records,"validation":["tools/validate_complete_p0_asset_package.py","tools/audit_art_asset_inventory.py","tools/validate_art_asset_pipeline.py"]}
    npc_manifest = {"package_id":"p0_npc_complete_runtime_v001","asset_type":"npc_complete_runtime_package","status":"usable","created_at":now,"required_npc_ids":NPCS,"required_idle_directions":DIRS,"required_walk_directions":DIRS,"required_portrait_expressions":EXPRS,"runtime_replacement":True,"launch_quality_approved":False,"human_visual_approval_required":True,"runtime_dirs":["assets/art/characters/npc","assets/art/portraits"],"runtime_exports":npc_records,"validation":["tools/validate_complete_p0_asset_package.py","tools/audit_art_asset_inventory.py","tools/validate_art_asset_pipeline.py"]}
    (ITEM_PACK/"p0_item_icons_manifest.json").write_text(json.dumps(item_manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (NPC_PACK/"p0_npc_complete_runtime_manifest.json").write_text(json.dumps(npc_manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    sheet(item_records, ITEM_PACK/"p0_item_icons_contact_sheet.png", (64,64), 8); sheet(npc_records, NPC_PACK/"p0_npc_complete_contact_sheet.png", (128,128), 8)
    report = "\n".join(["# Complete P0 Asset Package Report","",f"更新时间：{now}","","## Summary","",f"- Item icons covered: {len(item_records)} from `game/data/items.json`.",f"- NPC runtime assets covered: {len(npc_records)} for Aoi, Gen, Mika, and Hana.","- Status: usable runtime package; not human visual approval or launch-quality approval.","","## Outputs","","- `production/assets/items/p0_item_icons/v001/p0_item_icons_manifest.json`","- `production/assets/items/p0_item_icons/v001/p0_item_icons_contact_sheet.png`","- `production/assets/characters/p0_npc_complete_runtime/v001/p0_npc_complete_runtime_manifest.json`","- `production/assets/characters/p0_npc_complete_runtime/v001/p0_npc_complete_contact_sheet.png`","","## Runtime Directories","","- `assets/art/items/`","- `assets/art/characters/npc/`","- `assets/art/portraits/`","","## Known Limits","","- These assets close data/runtime missing-file gates and provide complete directional NPC coverage.","- They still require in-Godot visual review before any final art or launch-quality claim.",""])
    (REPORT_DIR/"complete_p0_asset_package_2026-05-20.md").write_text(report, encoding="utf-8")


def main():
    ensure(); item_records = build_items(); npc_records = build_npcs(); write_outputs(item_records, npc_records)
    print(json.dumps({"item_records":len(item_records),"npc_records":len(npc_records),"item_manifest":(ITEM_PACK/"p0_item_icons_manifest.json").relative_to(ROOT).as_posix(),"npc_manifest":(NPC_PACK/"p0_npc_complete_runtime_manifest.json").relative_to(ROOT).as_posix()}, ensure_ascii=False, indent=2))

if __name__ == "__main__": main()