# 可探索 2D 世界落地方案 v0.1

来源：`C:/Users/23732/Downloads/那座村庄_可探索2D世界规格文档_v0.1.docx`

## 当前落地范围

- 先把 `CloudVillageHomeyard` 作为第一块可探索世界样板，而不是继续按静态视觉小说背景推进。
- 首阶段锁定：脚底锚点、稳定角色尺寸、Y-sort actor 层、最小透明前景遮挡、平滑 CameraRig、交互对象 ID 与中文提示。
- 当前庭院仍是 1280x720 运行视口内的样板场景；后续再扩成文档建议的固定大地图和 Region/Chunk。

## 已实现到代码的规则

- `scripts/world/camera_rig.gd`：可复用 Camera2D 跟随脚底原点玩家节点。
- `scenes/world/cloud_village_homeyard.tscn`：
  - 根相机替换为 `CameraRig`。
  - 根节点记录 `metadata/world_model = "explorable_2d_oblique_region_v0_1"`。
  - `Layer_15_Player` 保持 `y_sort_enabled = true`。
  - `ForegroundOccluders` 标记为 `minimal_transparent_cutouts_only`。
  - 玩家保持 `depth_scale_enabled = false`，避免不同状态或移动中尺寸漂移。
- `scripts/player_controller.gd`：
  - 移动速度降为更适合慢生活探索的 `82.0`。
  - 步态微偏移只改变 sprite/shadow 的位置，不改变 scale。
- `tools/validate_cloud_village_homeyard_scene.py`：
  - 校验 CameraRig、玩家尺度、前景透明裁切占比、遮挡坐标和动画契约。

## 下一阶段

- 把庭院扩成至少 5 屏体感的大地图灰盒，再替换为 TileMapLayer + 独立 Sprite 资产。
- 为交互对象增加状态保存字段：`unique_id / region_id / chunk_id / state / interact_radius`。
- 拆出树木、房屋、道具的 Y-sort 资产模板，避免继续把复杂空间画死在一张图里。
