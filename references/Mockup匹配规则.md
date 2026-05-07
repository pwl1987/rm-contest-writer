# Mockup 截图生成与嵌入规则

---

## 7.1 描述驱动的 Mockup 匹配

**匹配规则：** 根据用户提供的**功能描述关键词**，从描述信号表中匹配最接近的 Mockup 模板。赛道只影响架构图模板，不影响界面 Mockup。

**界面 Mockup 模板（按描述信号匹配）：**

| 描述关键词 | 匹配模板 | 截图文件 |
|-----------|---------|---------|
| dashboard.html | dashboard.png | 工作台/仪表盘 |
| discovery.html | discovery.png | 内容发现 |
| recommendation.html | recommendation.png | 智能推荐 |
| trending.html | trending.png | 热点追踪 |
| preview.html | preview.png | 预览窗口 |
| "审核" / "多级审核" / "风控" | audit-workbench.html | audit-workbench.png | 审核工作台 |
| "大屏" / "指挥" / "数据新闻" | data-visualization.html | data-visualization.png | 数据大屏 |
| "视频" / "H5" / "海报" | content-display.html | content-display.png | 内容展示 |
| "监播" / "信号" / "报警" | signal-monitor.html | signal-monitor.png | 广播监控 |

**架构图模板（仅根据赛道选择）：**

| 赛道 | 架构图模板 | 截图文件 |
|------|-----------|---------|
| 技术研发类 | architecture-tech-rnd.html | scr-03-architecture-tech-rnd.png |
| 应用创新类 | architecture-app-innov.html | scr-04-architecture-app-innov.png |
| 内容创意类 | architecture-content.html | scr-05-architecture-content.png |

> **匹配示例**：用户说"需要一个展示数据大屏的界面图" → 匹配 data-visualization.html → 截图嵌入 → `![数据大屏](screenshots/data-visualization.png)`
>
> **多模板匹配**：同一项目可匹配多个界面模板（如"数据大屏+指挥"→ data-visualization + dashboard），按项目需求合理组合。

---

## 7.2 用户上传自有图片

当用户提供自有图片时，执行以下流程：

1. **接收图片**：用户通过文件上传或 URL 提供图片
2. **AI 辅助排版建议**：根据申报材料的版式要求，给出图片位置、尺寸、标注建议
3. **嵌入 Markdown**：将图片保存至 `screenshots/` 目录，插入对应章节

```
用户上传流程示例：
> 我有一张我自己做的数据大屏截图，能不能用在我的申报材料里？
AI：当然可以！请上传图片文件，然后告诉我：
  ① 这张图用在哪个章节（总体架构/核心功能/效果展示）？
  ② 是否需要AI辅助添加标注或箭头指向？
AI 将根据版面自动调整尺寸，嵌入对应位置。
```

---

## 7.3 执行截图命令

```bash
# 截图 HTML 页面
python3 word-gen/capture-diagram.py <html路径> <输出png路径>
```

---

## 7.4 截图嵌入 Markdown

```markdown
## 三、方案设计

### 3.1 总体架构

![系统架构图](screenshots/scr-03-architecture-tech-rnd.png)

### 3.2 核心功能

![系统界面-工作台](screenshots/dashboard.png)

如图所示，系统包含...
```

---

## Mockup 模板路径速查

**界面 Mockup**（根据功能描述匹配，与赛道无关）：
```
memory/templates/system-mockups/
├── dashboard.html          → dashboard.png         (工作台/仪表盘)
├── discovery.html          → discovery.png         (内容发现)
├── recommendation.html     → recommendation.png    (智能推荐)
├── trending.html          → trending.png          (热点追踪)
├── preview.html           → preview.png           (预览窗口)
├── audit-workbench.html   → audit-workbench.png   (审核工作台)
├── data-visualization.html → data-visualization.png (数据大屏)
├── content-display.html   → content-display.png   (内容展示)
└── signal-monitor.html   → signal-monitor.png    (广播监控)
```

**架构图**（仅根据赛道选择）：
```
memory/templates/
├── architecture-tech-rnd.html    → scr-03-architecture-tech-rnd.png   (技术研发类)
├── architecture-app-innov.html   → scr-04-architecture-app-innov.png (应用创新类)
└── architecture-content.html     → scr-05-architecture-content.png   (内容创意类)
```

**用户上传图片**：保存至 `memory/templates/screenshots/` 目录，嵌入时使用相对路径 `screenshots/xxx.png`。