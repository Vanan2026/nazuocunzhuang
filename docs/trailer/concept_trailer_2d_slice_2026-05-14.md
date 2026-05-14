# 《那座村庄》Concept Trailer 准备包

更新时间：2026-05-14

## 目标

- 片长：18 秒，允许剪辑落在 15-20 秒。
- 素材范围：只使用当前已验证 2D slice：`world.tscn`、HomeArea、BackFarm、veranda rest、主角新动作、BackFarm 种植微循环。
- 情绪关键词：回到村庄、安静生活、可触摸的院子、开始种下第一块地。
- 剪辑原则：先让玩家看懂“可玩”，再给氛围；不展示未验证的 NPC、存档、天气、完整村庄生活。

## 15-20 秒镜头脚本

| 时间 | 镜头 ID | 画面 | 旁白 |
| --- | --- | --- | --- |
| 0.0-3.0s | `shot_01_home_wakeup` | HomeArea 默认出生点，主角站在院子里，房屋、树影和可交互物件入画。 | “有些地方，不需要地图也能记得路。” |
| 3.0-6.0s | `shot_02_cross_yard` | 主角横穿院子，保留新 walk/idle 动作的完整身体节奏。 | “推开门，旧院子先回应你。” |
| 6.0-9.0s | `shot_03_veranda_rest` | 触发 veranda rest，主角坐下，镜头停住半秒。 | “在廊下坐一会儿，时间会慢下来。” |
| 9.0-12.0s | `shot_04_back_farm_entry` | 从 HomeArea 切到 BackFarm，显示小菜地空间和出口方向。 | “屋后的小地，也等着重新开始。” |
| 12.0-15.0s | `shot_05_plant_and_water` | FarmPlot0 完成播种和浇水，保留交互反馈感。 | “种下第一粒种子，给它今天的水。” |
| 15.0-18.0s | `shot_06_harvest_close` | 快进到成熟并收获一次，最后停在主角和菜地。 | “明天醒来，村庄会多一点回应。” |

## 场景捕捉顺序

1. 运行包校验，确认文档和 manifest 没有脱节。
   `python tools/validate_concept_trailer_package.py`
   当前 Windows 环境没有 Python 时可用：
   `powershell -ExecutionPolicy Bypass -File tools/validate_concept_trailer_package.ps1`
2. 做 headless 契约检查，确认 `world.tscn`、HomeArea、BackFarm、veranda rest、FarmPlot0 都能被脚本定位。
   `Godot_v4.6.1-stable_win64_console.exe --headless --path . --script res://tools/capture_concept_trailer_frames.gd -- --check-only`
3. 用 display-backed Godot 导出 6 张关键帧。
   `Godot_v4.6.1-stable_win64_console.exe --path . --script res://tools/capture_concept_trailer_frames.gd`
4. 输出目录：`.codex/trailer/concept_trailer_2d_slice_2026-05-14/`。
5. 剪辑顺序按 manifest 的 `shots` 数组，不重排。

## 剪辑备注

- 每镜头 3 秒是工作版节奏；最终可把 `shot_02_cross_yard` 和 `shot_05_plant_and_water` 各压到 2.5 秒，让结尾 logo/title 多留 1 秒。
- `shot_03_veranda_rest` 必须保留坐下后的停顿，否则“治愈/生活感”会变成普通移动展示。
- `shot_05_plant_and_water` 与 `shot_06_harvest_close` 可以用轻微交叉淡化表达时间流逝；不要暗示已经有完整季节系统。
- 当前 HomeArea/BackFarm 仍有灰盒成分，成片文案应强调 concept / slice，不包装成完整内容版。

## 旁白整稿

有些地方，不需要地图也能记得路。推开门，旧院子先回应你。在廊下坐一会儿，时间会慢下来。屋后的小地，也等着重新开始。种下第一粒种子，给它今天的水。明天醒来，村庄会多一点回应。

## 字幕版

那座村庄  
回到旧院子  
坐一会儿  
种下第一粒种子  
明天，村庄会回应你  
Concept slice in development

## HeyGen 输入文案

用途：生成 18 秒中文旁白或主持人口播。建议选择温和、低语速、自然停顿的中文女声或中性声线，不要广告腔。

```text
请生成一段 18 秒左右的中文概念预告旁白，语气安静、克制、温暖，像回忆一个正在重新开始的乡村生活游戏。不要夸张，不要销售感。

旁白：
有些地方，不需要地图也能记得路。
推开门，旧院子先回应你。
在廊下坐一会儿，时间会慢下来。
屋后的小地，也等着重新开始。
种下第一粒种子，给它今天的水。
明天醒来，村庄会多一点回应。

收尾字幕：
《那座村庄》
Concept slice in development
```

## 辅助脚本

- `docs/trailer/concept_trailer_2d_slice_2026-05-14.json`：机器可读镜头 manifest。
- `tools/validate_concept_trailer_package.py`：校验文档、manifest、源文件引用、镜头时长和镜头 ID 一致性。
- `tools/validate_concept_trailer_package.ps1`：同等 PowerShell 校验入口，供没有 Python 的 Windows 环境使用。
- `tools/capture_concept_trailer_frames.gd`：Godot 关键帧捕捉脚本；`--check-only` 可在 headless 下跑契约验证。

## 已知风险

- 这是 concept trailer，不展示未验证的 NPC 生活、存档、天气、经济系统。
- display-backed 截图依赖本机 Godot 图形环境；CI/headless 环境只跑契约验证。
- HomeArea 和 BackFarm 仍包含原型/灰盒视觉，最终公开视频前应再做一次美术接受检查。
