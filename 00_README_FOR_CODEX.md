# 《那座村庄》Codex 开发文档包

版本：v1.0  
日期：2026-05-14  
项目方向：无战斗、治愈系、日式乡村、模块化 2D 绘本风、Godot 优先实现

---

## 0. 这套文档的用途

这套文档用于让 Codex 或其他代码代理在不了解上下文的情况下，能够稳定推进《那座村庄》的开发、美术资产生产、数据结构搭建与垂直切片实现。

文档分为四组：

1. **项目设计文档**：定义游戏是什么、玩家为什么持续玩、哪些内容不能做。
2. **美术设计与资产圣经**：定义统一视觉风格、资产分类、命名、尺寸、输出规则。
3. **Godot 开发规范**：定义系统架构、场景结构、数据驱动方式、保存逻辑与验收标准。
4. **Codex 执行文档**：定义任务顺序、禁止事项、每个阶段的交付物和检查清单。

---

## 1. 给 Codex 的最高优先级规则

Codex 在执行任何任务前必须读取：

```text
AGENTS.md
00_README_FOR_CODEX.md
docs/01_PROJECT_DESIGN_GDD.md
docs/04_ART_DIRECTION_BIBLE.md
docs/05_ART_ASSET_BIBLE.md
docs/10_CODEX_TASKS.md
```

如果任务涉及系统实现，还必须读取：

```text
docs/02_CORE_SYSTEMS_SPEC.md
docs/07_GODOT_IMPLEMENTATION_SPEC.md
docs/08_CONTENT_DATA_SCHEMA.md
```

如果任务涉及美术资产或占位图，还必须读取：

```text
docs/04_ART_DIRECTION_BIBLE.md
docs/05_ART_ASSET_BIBLE.md
docs/06_AI_ASSET_PROMPT_LIBRARY.md
data/style_palette.json
data/asset_catalog.csv
```

---

## 2. 不可变更的核心决定

以下内容是项目基线，Codex 不得自行改变：

| 项目 | 决定 |
|---|---|
| 游戏类型 | 治愈系乡村生活模拟 |
| 战斗 | **完全不做战斗** |
| 玩家压力 | 低压力，无死亡惩罚，无装备掉落，无硬核生存 |
| 参考方向 | 参考《星露谷物语》的生活循环与长线目标，但不复制其视觉和内容 |
| 美术方向 | 模块化 2D 治愈绘本风，固定 3/4 俯视视角 |
| 主题 | 回到村庄、修复老屋、恢复村庄、认识村民、发现温柔的秘密 |
| 引擎 | Godot 4.x 优先 |
| 开发方式 | 数据驱动、模块化、可扩展、适合 AI 批量生成资产 |

---

## 3. 推荐仓库落地结构

```text
project_root/
  AGENTS.md
  README.md
  docs/
    01_PROJECT_DESIGN_GDD.md
    02_CORE_SYSTEMS_SPEC.md
    03_NARRATIVE_WORLD_BIBLE.md
    04_ART_DIRECTION_BIBLE.md
    05_ART_ASSET_BIBLE.md
    06_AI_ASSET_PROMPT_LIBRARY.md
    07_GODOT_IMPLEMENTATION_SPEC.md
    08_CONTENT_DATA_SCHEMA.md
    09_MVP_ROADMAP_BACKLOG.md
    10_CODEX_TASKS.md
    11_ACCEPTANCE_CHECKLIST.md
  data/
    asset_catalog.csv
    npc_catalog.csv
    crop_catalog.csv
    item_catalog.csv
    recipe_catalog.csv
    style_palette.json
    project_config.yaml
  prompts/
    CODEX_MASTER_PROMPT.md
  game/
    autoload/
    systems/
    entities/
    ui/
    scenes/
    data/
  assets/
    art/
      characters/
      environments/
      props/
      ui/
      icons/
      fx/
    audio/
```

---

## 4. 使用方式

### 第一步：把文档复制到仓库根目录

将本包中的 `AGENTS.md` 放在仓库根目录，将 `docs/`、`data/`、`prompts/` 放入对应目录。

### 第二步：给 Codex 第一条任务

使用 `prompts/CODEX_MASTER_PROMPT.md` 作为第一条任务，让 Codex 读取所有文档并创建基础项目结构。

### 第三步：按 `docs/10_CODEX_TASKS.md` 分阶段执行

不要一次要求 Codex 完成整个游戏。按任务包执行：

1. 项目骨架
2. 时间/季节/天气
3. 玩家移动与交互
4. 农田与作物
5. 背包与物品
6. NPC 与对话
7. 村庄修复
8. 美术占位资产
9. UI
10. 垂直切片整合

---

## 5. 风格一句话

《那座村庄》是一款无战斗的治愈系乡村生活模拟游戏。玩家回到一座被树木包围的旧村庄，在修复老屋、经营庭院、种植作物、做饭、拜访村民、参加季节活动的日常中，逐渐让村庄恢复生机，并发现被时间和自然藏起来的温柔秘密。
