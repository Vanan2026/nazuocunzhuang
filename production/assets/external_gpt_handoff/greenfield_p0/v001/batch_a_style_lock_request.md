# Batch A - Style Lock Request

用途：先锁定《那座村庄》Greenfield P0 的整体视觉语言和 UI 方向。
交付方式：请在外部 GPT 生成 PNG 后，按下方相对路径放入 `incoming/` 目录。
Incoming 根目录：

```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/
```

验收命令：

```powershell
py -3.12 tools\validate_greenfield_p0_external_asset_intake.py --allow-partial
```

## 全局风格锁定

Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD.

## 全局负面要求

Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.

## 交付清单

### 1. greenfield_p0_style_mother

- 文件路径：

```text
01_mother_images/style/greenfield_p0_style_mother.png
```

- 完整放置路径：

```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/01_mother_images/style/greenfield_p0_style_mother.png
```

- 尺寸：`1200x760`
- 背景：完全不透明 PNG
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Create greenfield_p0_style_mother; exact canvas 1200x760 px; fully opaque complete review image. Show a compact style board for a cozy rural life sim: palette swatches, ground texture samples, foliage samples, wood/stone material samples, one small house/prop sample, one tiny 3/4 top-down character proportion sample, and simple paper/wood UI motif samples. Keep it original and not tied to any named franchise.
```

### 2. ui_screen_hud

- 文件路径：

```text
01_mother_images/ui/screens/greenfield_p0_ui_screen_hud.png
```

- 完整放置路径：

```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/01_mother_images/ui/screens/greenfield_p0_ui_screen_hud.png
```

- 尺寸：`1280x720`
- 背景：完全不透明 PNG
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Create a UI screen mother layout for ui_screen_hud; exact canvas 1280x720 px; fully opaque complete review image; paper/wood diary style, dense but readable game interface, no real text labels required. Include top-left date/time/weather cluster, top-right money/village status cluster, bottom-center tool belt, subtle interaction prompt area, and enough world background hint to judge contrast.
```

### 3. ui_screen_inventory

- 文件路径：

```text
01_mother_images/ui/screens/greenfield_p0_ui_screen_inventory.png
```

- 完整放置路径：

```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/01_mother_images/ui/screens/greenfield_p0_ui_screen_inventory.png
```

- 尺寸：`1280x720`
- 背景：完全不透明 PNG
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Create a UI screen mother layout for ui_screen_inventory; exact canvas 1280x720 px; fully opaque complete review image; paper/wood diary style, dense but readable game interface, no real text labels required. Include category tabs, a grid of inventory slots, selected item detail panel, item count area, and quiet hand-drawn frame styling.
```

### 4. ui_screen_journal_map

- 文件路径：

```text
01_mother_images/ui/screens/greenfield_p0_ui_screen_journal_map.png
```

- 完整放置路径：

```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/01_mother_images/ui/screens/greenfield_p0_ui_screen_journal_map.png
```

- 尺寸：`1280x720`
- 背景：完全不透明 PNG
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Create a UI screen mother layout for ui_screen_journal_map; exact canvas 1280x720 px; fully opaque complete review image; paper/wood diary style, dense but readable game interface, no real text labels required. Include a left journal task/page list, a right hand-drawn village map panel with 10 connected areas, small relationship/season note spaces, and soft paper texture.
```

### 5. ui_screen_dialogue_gift

- 文件路径：

```text
01_mother_images/ui/screens/greenfield_p0_ui_screen_dialogue_gift.png
```

- 完整放置路径：

```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/01_mother_images/ui/screens/greenfield_p0_ui_screen_dialogue_gift.png
```

- 尺寸：`1280x720`
- 背景：完全不透明 PNG
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Create a UI screen mother layout for ui_screen_dialogue_gift; exact canvas 1280x720 px; fully opaque complete review image; paper/wood diary style, dense but readable game interface, no real text labels required. Include NPC portrait panel, dialogue box, gentle choice buttons, small gift selection strip, and relationship feedback area; keep it calm and readable.
```

### 6. ui_screen_pause_settings

- 文件路径：

```text
01_mother_images/ui/screens/greenfield_p0_ui_screen_pause_settings.png
```

- 完整放置路径：

```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/01_mother_images/ui/screens/greenfield_p0_ui_screen_pause_settings.png
```

- 尺寸：`1280x720`
- 背景：完全不透明 PNG
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Create a UI screen mother layout for ui_screen_pause_settings; exact canvas 1280x720 px; fully opaque complete review image; paper/wood diary style, dense but readable game interface, no real text labels required. Include centered pause/settings menu, save slot hints, audio/display/control rows, and soft dimmed village background treatment.
```

## 本批验收标准

- 6 张 PNG 全部按路径放入 `incoming/`。
- 尺寸必须完全一致。
- PNG 必须为 RGBA 或可读取为 RGBA。
- 本批全部要求完全不透明，不需要透明背景。
- 不能有水印、模型签名、乱文字、错透视、战斗元素、科幻 HUD。
- UI screen 是“母图/方向稿”，不是最终可点击界面；但布局层级、风格、信息密度要能指导后续拆分和实现。
