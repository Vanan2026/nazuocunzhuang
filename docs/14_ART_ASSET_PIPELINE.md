# Art Asset Pipeline

本文件定义《那座村庄》的项目级美术资产生产线。目标不是继续围绕单个场景反复 patch，而是把资产生产变成可盘点、可验证、可回滚、可批量扩展的流程。执行原则：不要围绕单个场景反复 patch。

## 当前结论

HomeArea 的历史问题不是某一张图没修好，而是生产方式错位：单张生成图、临时拆层、临时贴回 Godot、再用场景节点修补，最后会产生大量备份场景、旧脚本、旧目录和无法判断状态的图片。后续美术落地必须先过资产生产线，再进入场景。

## 资产状态

所有生产资产必须落到以下状态之一，不能靠文件夹名字猜：

机器可检索状态枚举：draft / usable / approved / rejected / archived

- draft：草稿、试验、未进入 Godot。
- usable：可用于开发验证，但不代表视觉批准。
- approved：经过人工视觉确认，可作为当前版本目标资产。
- rejected：失败路线或被否决版本，只能作为诊断参考。
- archived：保留回滚或证据，不能被 Godot 主流程导入和引用。

生产线中允许 structural placeholder，但必须显式标注 `launch_quality_approved=false`。自动化验证只能证明结构和引用正确，不能代替人工视觉审批。

## 目录分层

推荐资产流向：

```text
production/assets/
  regions/<region>_world2d/v001/
    00_brief/
    01_blockout/
    02_source/
    03_layer_export/
    04_godot_review/
    workflow_manifest.json
  characters/<character_id>/v001/
  items/<batch_id>/v001/

assets/art/
  characters/
  portraits/
  items/
  crops/
  props/
  environments/
  icons/
  ui/
```

`production/assets/` 保存来源、版本、prompt、mask、review 图和 manifest。`assets/art/` 只放 Godot 运行时稳定引用的导出文件。场景和数据表不应直接引用 `production/assets/`。

## Region 生产线

区域美术必须走 source-first：

1. 锁定布局或 3D blockout。
2. 生成或绘制一张统一 source composition。
3. 从同一个 source 导出 coordinate-stable layers。
4. 每层保持同源坐标或记录明确 pivot/offset。
5. 集成到 Godot review scene。
6. 运行脚本验证。
7. 人工视觉审批后，才允许进入 approved 或 promotion。

禁止把 flattened review plate、局部贴片、mask-derived sticker 或历史失败目录当作最终结构层。

## Item / NPC 生产线

P0 item icon 批次必须以 `game/data/items.json` 为源，不手工猜清单。每个 icon 输出 64px runtime PNG，并写入 batch manifest。当前优先补 seed、material、forage、fish、food、key，附带处理仍缺失的 crop 图标。

完整 P0 NPC runtime package 为：

- `assets/art/characters/npc/npc_<id>_idle_down_128.png`
- `assets/art/characters/npc/npc_<id>_idle_up_128.png`
- `assets/art/characters/npc/npc_<id>_idle_left_128.png`
- `assets/art/characters/npc/npc_<id>_idle_right_128.png`
- `assets/art/characters/npc/npc_<id>_walk_down_4x128.png`
- `assets/art/characters/npc/npc_<id>_walk_up_4x128.png`
- `assets/art/characters/npc/npc_<id>_walk_left_4x128.png`
- `assets/art/characters/npc/npc_<id>_walk_right_4x128.png`
- `assets/art/portraits/npc_<id>_portrait_neutral_512.png`
- `assets/art/portraits/npc_<id>_portrait_happy_512.png`
- `assets/art/portraits/npc_<id>_portrait_thinking_512.png`

Aoi、Gen、Mika、Hana 都按完整包追踪。不要先扩 NPC 剧情、日程或新村民，直到 P0 NPC 完整 runtime package 补齐。

## Manifest required fields

每个生产包至少记录：

```json
{
  "package_id": "region_home_area_world2d_v001",
  "asset_type": "region_world2d",
  "status": "usable",
  "source_first": true,
  "runtime_replacement": false,
  "launch_quality_approved": false,
  "human_visual_approval_required": true,
  "source_files": [],
  "runtime_exports": [],
  "godot_refs": [],
  "validation": []
}
```

状态字段必须比文件存在更重要。图片存在不等于可上线；场景引用不等于视觉批准。

## 脏数据策略

脏数据先分类，不先大删：

- importable backup scene：例如 `scenes/regions/region_home_area.before_*.tscn`，风险是 Godot 仍会导入并触发 UID 或旧引用问题。
- rejected source dir：历史失败生产线目录，只能作为诊断证据。
- stale tool：服务旧路线的脚本，先登记，确认无回滚价值后归档。
- unreferenced runtime art：不一定无效，但必须知道当前没有被扫描到引用。
- missing data refs：数据表引用了不存在的图，是 P0 生产缺口。

清理顺序：先 inventory，后 archive，再删除。删除前必须有回滚路径或明确任务记录。

## 当前审计入口

生成库存：

```powershell
python tools/audit_art_asset_inventory.py
```

验证生产线：

```powershell
python tools/validate_art_asset_pipeline.py
```

当前库存输出：

```text
production/assets/art_asset_inventory_2026-05-20.json
```

这份 inventory 是项目级美术生产排期的入口，后续每次新增资产包、归档旧目录、补 item icon 或补 NPC art 后都应重新生成。

## 当前 P0 顺序

1. 运行 HomeArea world2d/v001 的 Godot capture 和人工 review，决定 polish 还是重做 source-aligned layers。
2. 补齐 `game/data/items.json` 缺失 item icons。
3. 补完整 P0 NPC runtime package：Aoi、Gen、Mika、Hana 的 4 向 idle、4 向 walk、neutral/happy/thinking portraits。
4. 保持 HomeArea importable backup scenes 为 0；如需回滚，只从 git 历史按需取回诊断文件。
5. HomeArea 稳定后再启动 `village_world2d/v001`，不要同时开多个区域美术主线。
## 强清理规则

当用户明确选择强清理时，已列入 allowlist 的废弃场景和旧路线工具应直接删除，而不是移动到 archive。当前强清理目标状态：

- `scenes/regions/region_home_area.before_*.tscn` 必须为 0。
- `tools/legacy_homeyard/` 必须不存在。
- 旧 HomeArea launch/formal/v006 路线脚本必须不存在。
- `tools/audit_art_asset_inventory.py` 必须继续把 item icon 和完整 P0 NPC 包缺口列为 P0 backlog。
- 清理后仍需要保留 `home_area_world2d/v001`、BackFarm v002 和 art pipeline validator。

强清理不等于补资产，也不等于视觉批准。删除历史失败路线后，下一步仍然是 item icon 批量包、完整 P0 NPC runtime package 和 HomeArea capture/human review。