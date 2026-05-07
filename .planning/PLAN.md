# PLAN.md Phase 4

**Phase:** 4 — UI Mockup 剩余项 + 截图嵌入流程
**Goal:** 完成 Phase 1 遗留的 UI mockup 模板，创建截图嵌入工作流

---

## Context

Phase 1 完成了 3 个架构模板中的 1 个（architecture-tech-rnd.html），剩余：
- architecture-app-innov.html — **已存在**（209 行）
- architecture-content.html — **已存在**（196 行）
- material-preview.html — **缺失**（内容创意类物料预览）
- export.html — **缺失**（文档导出预览）
- screenshots/ — **缺失**（截图输出目录）

---

## Task 04-01: material-preview.html 创建

**新建 `memory/templates/material-preview.html`，约 200 行**

### Actions
1. 参考 `architecture-content.html` 结构，创建内容创意类物料预览模板
2. 包含：视频预览区、H5 页面预览区、海报/数据新闻卡片网格
3. 标题：「内容创意类物料预览」
4. 轨道标签：内容创意类

### Files
- `memory/templates/material-preview.html` — 新建

### Verification
- `grep -c "material-preview" memory/templates/material-preview.html` → ≥1

<done>
- material-preview.html 创建完成
- 包含视频预览区、H5 预览区、海报网格
- 标题为「内容创意类物料预览」
</done>

---

## Task 04-02: export.html 创建

**新建 `memory/templates/export.html`，约 150 行**

### Actions
1. 创建文档导出预览页面
2. 包含：Word 预览卡片、PDF 预览卡片、导出进度指示器
3. 标题：「申报材料导出预览」
4. 集成字体文件路径（fonts/）

### Files
- `memory/templates/export.html` — 新建

### Verification
- `grep -c "export" memory/templates/export.html` → ≥3

<done>
- export.html 创建完成
- 包含 Word/PDF 预览卡片和导出进度指示器
- 集成 fonts/ 字体路径
</done>

---

## Task 04-03: screenshots/ 目录创建与截图脚本

**创建 `memory/templates/screenshots/` 目录结构**

### Actions
1. 创建 `screenshots/` 目录
2. 创建 `memory/templates/screenshots/README.md`，说明截图命名规则：
   - `scr-01-project-init.png`
   - `scr-02-analysis-confirm.png`
   - `scr-03-architecture-tech-rnd.png`
   - `scr-04-architecture-app-innov.png`
   - `scr-05-architecture-content.png`
   - `scr-06-material-preview.png`
   - `scr-07-export.png`
3. 在 SKILL.md 第七步（Mockup 截图生成与嵌入）中添加截图命名引用

### Files
- `memory/templates/screenshots/README.md` — 新建

### Verification
- `ls memory/templates/screenshots/` → 目录存在

<done>
- screenshots/ 目录创建完成
- README.md 包含 7 个截图命名规则
- SKILL.md Step 7 更新了截图引用
</done>

---

## Verification Summary

| 验证项 | 命令 | 期望 |
|--------|------|------|
| material-preview.html | `test -f memory/templates/material-preview.html && echo OK` | OK |
| export.html | `test -f memory/templates/export.html && echo OK` | OK |
| screenshots/ | `test -d memory/templates/screenshots && echo OK` | OK |
| SKILL.md Step 7 更新 | `grep "scr-0" SKILL.md` | 7 个截图引用 |

---

## Dependencies
- Task 04-01 → Task 04-03（模板创建后更新截图命名规则）
- Task 04-02 → Task 04-03

## Gate
- Pre-flight: `memory/templates/` 目录存在
- Revision: `test -f` 验证文件创建
- Abort: 无
