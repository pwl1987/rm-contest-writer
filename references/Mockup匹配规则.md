# Mockup 截图生成与嵌入规则

---

## 7.1 动态 Mockup 生成流程（Python）

**核心工具**：`word-gen/generate-mockup.py`

**执行流程**：
```
Step 1: 读取项目配置 memory/projects/{project_id}.json
Step 2: python3 word-gen/generate-mockup.py <config.json> <output_dir>
Step 3: python3 word-gen/capture-diagram.py <html路径> <output.png>
Step 4: 嵌入 Markdown
```

**自动 Mockup 类型判断**（根据 core_functions 关键词）：
| 关键词 | Mockup 类型 |
|--------|------------|
| 监播/监控/信号/报警/切换/延时 | signal-monitor |
| 推荐/发现/热点/选题 | dashboard |
| 审核/风控/合规 | audit-workbench |
| 大屏/指挥/数据新闻/可视化 | data-visualization |
| （始终生成） | architecture |

**Python 命令**：
```bash
# 生成动态 Mockup HTML
python3 word-gen/generate-mockup.py memory/projects/{project_id}.json screenshots/

# 截图每个生成的 HTML
for html in screenshots/*.html; do
    python3 word-gen/capture-diagram.py "$html" "${html%.html}.png"
done
```

---

## 7.2 描述驱动的 Mockup 匹配（旧流程 - 已废弃）

~~根据用户提供的**功能描述关键词**，从描述信号表中匹配最接近的 Mockup 模板。~~

**新版**：直接使用 generate-mockup.py 从项目配置生成，无需手动匹配。

---

## 7.3 用户上传自有图片

当用户提供自有图片时，执行以下流程：

1. **接收图片**：用户通过文件上传或 URL 提供图片
2. **AI 辅助排版建议**：根据申报材料的版式要求，给出图片位置、尺寸、标注建议
3. **嵌入 Markdown**：将图片保存至 `screenshots/` 目录，插入对应章节

---

## 7.4 截图嵌入 Markdown

```markdown
## 三、方案设计

### 3.1 总体架构

![系统架构图](screenshots/architecture.png)

### 3.2 核心功能

![信号监控界面](screenshots/signal-monitor.png)

如图所示，系统包含...
```

---

## Mockup 模板路径速查

**动态生成**（Python）：
```
word-gen/generate-mockup.py
    ├── generate_dashboard_html()        → dashboard.html/dashboard.png
    ├── generate_signal_monitor_html()  → signal-monitor.html/signal-monitor.png
    ├── generate_data_visualization_html() → data-visualization.html/data-visualization.png
    ├── generate_audit_workbench_html()  → audit-workbench.html/audit-workbench.png
    └── generate_architecture_html()     → architecture.html/architecture.png
```

**截图命令**：
```bash
python3 word-gen/capture-diagram.py <html路径> <输出png路径>
```

---

## 附录：generate-mockup.py 配置字段

```json
{
  "project_name": "广电智能监播系统",
  "track": "技术研发类",
  "ai_mode": "私有化部署",
  "model_choice": "Qwen3.5-VL-72B",
  "core_functions": ["信号监测", "故障报警", "自动切换", "延时联动"]
}
```

> **注意**：core_functions 决定自动生成哪些界面 Mockup，architecture 始终生成。