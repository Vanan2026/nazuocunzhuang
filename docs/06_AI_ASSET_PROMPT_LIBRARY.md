# 06 — AI 美术资产 Prompt Library

版本：v1.0  
用途：给 Codex 或其他 AI 资产生成流程使用。所有 prompt 都应遵守美术圣经，不引用具体受版权保护作品风格。

---

## 1. 全局风格锁定 Prompt

### 1.1 中文版

```text
为一款无战斗治愈系乡村生活模拟游戏制作 2D 游戏资产。风格为温暖低饱和的日式乡村绘本感，固定 3/4 俯视视角，轻手绘材质，柔和深棕描边，大色块，少细节，清晰轮廓，适合 Godot 游戏中直接使用。画面应温柔、干净、安静、有生活感。不要写实，不要暗黑，不要战斗幻想，不要复杂厚涂，不要高饱和霓虹色，不要模仿任何具体现有游戏或动画作品。
```

### 1.2 English Version

```text
Create a 2D game-ready asset for a non-combat cozy countryside life simulation game. Warm low-saturation Japanese rural storybook feeling, fixed top-down 3/4 perspective, soft hand-painted texture, gentle dark-brown outlines, large readable color shapes, minimal details, clear silhouette, suitable for direct import into Godot. The mood should be calm, warm, clean, quiet, and domestic. Avoid realism, dark fantasy, combat aesthetics, complex painterly rendering, neon colors, and imitation of any specific existing game or animation style.
```

---

## 2. 通用 Negative Prompt

```text
photorealistic, realistic 3D, dark horror, combat, weapon, armor, monster, blood, skull, cyberpunk, neon, high contrast, gritty texture, complex anime illustration, hyper detailed hair, heavy oil painting, dramatic cinematic lighting, copyrighted character, logo, text watermark, isometric angle mismatch, side view, front portrait only, messy background, transparent background failure
```

---

## 3. 主角游戏角色 Prompt

```text
Create a game-ready 2D sprite character for a cozy countryside life simulation game, fixed top-down 3/4 perspective. The character is a young adult returning to a rural village, gentle and ordinary, 3.5-head body proportion, slightly large head, simple rounded hands and feet, clear silhouette, short hair or low ponytail, warm off-white loose shirt, muted grass-green apron, warm brown shoes, small cloth bag, tiny persimmon-orange hair ribbon. Soft dark-brown outline, warm low-saturation colors, minimal clothing folds, readable at small size, transparent background.
```

输出：

```text
chr_player_base_idle_down_128.png
chr_player_base_idle_up_128.png
chr_player_base_idle_left_128.png
chr_player_base_idle_right_128.png
```

验收：

- 缩小到 128x128 仍可读。
- 不能像复杂立绘。
- 服装结构便于动画。

---

## 4. NPC Prompt 模板

```text
Create a game-ready 2D NPC sprite for a cozy countryside life simulation game, fixed top-down 3/4 perspective. NPC role: {role}. Personality: {personality}. Visual anchors: {visual_anchors}. 3.5 to 4-head body proportion, clear silhouette, warm low-saturation colors, simple clothing, soft dark-brown outline, gentle storybook texture, readable at small size, transparent background. No combat elements, no weapons, no fantasy armor.
```

示例：杂货店主葵

```text
NPC role: small village grocery store owner. Personality: careful, warm, slightly worried about the declining village. Visual anchors: simple apron, small account book, pencil tucked near the ear, muted blue skirt, warm cream shirt.
```

---

## 5. NPC 对话头像 Prompt

```text
Create a square 2D dialogue portrait for a cozy countryside life simulation game. Character: {npc_name}, role {role}, expression {expression}. Warm low-saturation storybook style, soft hand-painted texture, gentle dark-brown line, simple readable face, calm rural atmosphere, no complex background, no dramatic lighting, no copyrighted style imitation. 512x512.
```

情绪建议：

```text
neutral, happy, thinking, worried, surprised, gentle_smile
```

---

## 6. 场景模块 Prompt

```text
Create a modular 2D environment asset for a cozy countryside life simulation game, fixed top-down 3/4 perspective. Asset: {asset_name}. Warm low-saturation Japanese rural storybook style, soft hand-painted texture, clear readable silhouette, gentle dark-brown outline, transparent background, game-ready, no characters, no text. The asset should be reusable as a Godot prop or tile.
```

示例：木制信箱

```text
Asset: old wooden village mailbox with a small roof, slightly weathered but warm, simple shape, visible red-brown flag, domestic rural feeling.
```

---

## 7. 主角家 Prompt

```text
Create modular 2D game environment pieces for an old rural Japanese-style player house exterior, fixed top-down 3/4 perspective. Warm low-saturation storybook style, soft hand-painted wood texture, clear readable shapes, cozy and slightly old but not abandoned. Generate separate transparent background pieces: front wall, roof, sliding door, small window, wooden engawa porch, soft ground shadow. No people, no text, no dramatic darkness.
```

---

## 8. 柿子树 Prompt

```text
Create a 2D game-ready persimmon tree asset for a cozy countryside life simulation game, fixed top-down 3/4 perspective, transparent background. Warm low-saturation storybook style, soft hand-painted leaves, clear trunk silhouette, gentle dark-brown outline. The tree should feel iconic and peaceful, suitable for a player yard. Variant: {season_variant}.
```

变体：

```text
spring_new_leaves
summer_full_green
autumn_orange_fruit
winter_bare_branches
```

---

## 9. 作物 Prompt 模板

```text
Create a 2D crop growth stage sprite for a cozy countryside farming game, top-down 3/4 view, 64x64, transparent background. Crop: {crop_name}. Stage: {stage}. Warm low-saturation colors, simple readable silhouette, soft dark-brown outline, minimal detail, game-ready, must be clearly distinguishable from other growth stages.
```

阶段：

```text
seeded
sprout
growing
ready_to_harvest
```

---

## 10. UI 图标 Prompt

```text
Create a 64x64 hand-drawn UI icon for a cozy countryside life simulation game. Icon: {icon_name}. Warm low-saturation color palette, soft dark-brown outline, simple readable shape, paper-and-wood storybook UI feeling, transparent background, no text, no realism, no neon.
```

---

## 11. 背包物品 Prompt

```text
Create a 64x64 inventory item icon for a cozy countryside life simulation game. Item: {item_name}. Warm low-saturation storybook style, clear silhouette, gentle outline, transparent background, centered composition, readable at small size, no text.
```

---

## 12. 天气图标 Prompt

```text
Create a 64x64 weather UI icon for a cozy countryside life simulation game. Weather: {weather_type}. Warm low-saturation hand-drawn style, simple readable symbol, soft outline, transparent background, paper journal feeling, no text.
```

天气：

```text
sunny, cloudy, rainy, windy, snowy, foggy
```

---

## 13. 生成批次模板

Codex 生成或调用资产流程时，每批都应按下面格式写任务：

```text
Batch name: MVP Yard Props 01
Style lock: use global style prompt v1
Output format: transparent PNG
Perspective: fixed top-down 3/4
Size: 128x128 unless specified
Assets:
  - prop_mailbox_wood_default_128.png
  - prop_watering_can_old_128.png
  - prop_wooden_bucket_128.png
  - prop_wind_chime_default_64.png
Negative prompt: use global negative prompt
Acceptance: readable at 100% and 50%, no combat elements, no text watermark, warm low-saturation palette
```

---

## 14. 资产重绘指令模板

```text
Regenerate this asset while preserving the project art bible. Problems to fix: {problems}. Keep the same filename target, transparent background, fixed top-down 3/4 view, warm low-saturation storybook style, clear game-readable silhouette. Do not add unrelated objects, text, weapons, dramatic lighting, or high-detail illustration rendering.
```

---

## 15. 不要使用的 Prompt 写法

不要写：

```text
Make it like Stardew Valley.
Make it like Studio Ghibli.
Make it exactly like Animal Crossing.
Copy the style of [artist name].
```

应该写：

```text
Warm low-saturation cozy countryside 2D game asset, soft hand-painted storybook texture, fixed top-down 3/4 view, clear readable silhouette, gentle dark-brown outline.
```
