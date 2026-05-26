# External GPT Asset Handoff

本项目的外部生图协作方式固定为：

1. Codex 根据项目设计文档、manifest 和 Godot 接入需求，生成详细资产需求。
2. 用户在外部 GPT 中按需求生产 PNG。
3. 用户把 PNG 放入指定 `incoming/` 目录，保持文件名、相对路径、尺寸和透明规则一致。
4. Codex 运行 intake validator，合格后导入 Godot、生成 review scene、更新 manifest，并继续开发。

本流程不绑定任何指定图像模型名；验收依据是资产契约，而不是模型来源。

## 当前 Handoff

Greenfield P0 当前 handoff 目录：

```text
production/assets/external_gpt_handoff/greenfield_p0/v001/
```

关键文件：

```text
README.md
asset_request_manifest.json
asset_request_table.csv
prompt_briefs.md
incoming/
```

`asset_request_manifest.json` 是机器可读契约；`prompt_briefs.md` 是给用户外部生图时看的需求清单。

## Incoming 规则

用户交付资产时，必须把 PNG 放在：

```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/
```

并保持 request manifest 中列出的相对路径。例如：

```text
incoming/02_runtime_exports/regions/village/layers/village_base_ground.png
incoming/02_runtime_exports/characters/player/chr_player_base_walk_down_4x128.png
incoming/01_mother_images/ui/screens/greenfield_p0_ui_screen_hud.png
```

## 验证命令

允许分批交付：

```powershell
py -3.12 tools\validate_greenfield_p0_external_asset_intake.py --allow-partial
```

严格完整包：

```powershell
py -3.12 tools\validate_greenfield_p0_external_asset_intake.py
```

使用任意已安装 Pillow 的 Python 均可；当前机器已验证 `py -3.12`。

## 验收底线

- 文件名和相对目录必须完全匹配。
- PNG 尺寸必须完全匹配。
- 需要透明的资产必须有有效 alpha。
- 母图、UI screen 等要求不透明的图必须完全不透明。
- 固定 3/4 俯视，温暖低饱和绘本风。
- 不得复制任何现有作品、角色、地图或具名风格。
- 不得包含水印、无关文字、战斗元素或现代科幻 HUD。
