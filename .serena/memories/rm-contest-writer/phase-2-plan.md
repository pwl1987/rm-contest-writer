# Phase 2: word-gen JS-only 统一

## Context

Phase 1 BLOCK gates 验证通过 (5/5 PASS)。Phase 2 消除 word-gen/ 双实现维护负担。

**当前状态：**
- word-gen/ 下 3 对 Python/JS 重复文件
- Python 版本已部分 delegating to JS (capture-diagram.py)
- preflight-check.js 比 Python 版本更完整

## 实现计划

### Plan 2-1: JS 版本功能完整性验证

检查 3 个 JS 文件的核心功能：

| 文件 | 核心功能 | 状态 |
|------|----------|------|
| generate-contest-docs.js | generateDoc(), markdown→docx | ✅ 有 main() |
| capture-diagram.js | captureDiagram(), screenshot | ✅ 有 main() |
| preflight-check.js | checkChromium, checkPlaywright | ✅ 有 main() |

所有 JS 文件都有完整的入口函数。

### Plan 2-2: Python 版本标记 deprecated

编辑 3 个 .py 文件头部添加注释：

```
# DEPRECATED - 使用 .js 版本
# 保留至 Phase 2 完成验证
```

文件：
- word-gen/preflight-check.py
- word-gen/capture-diagram.py
- word-gen/generate-contest-docs.py

### Plan 2-3: 更新 SKILL.md

检查 SKILL.md 中对 .py 文件的引用 → 改为 .js

## 关键文件

- word-gen/generate-contest-docs.js ✅
- word-gen/generate-contest-docs.py → deprecated
- word-gen/capture-diagram.js ✅
- word-gen/capture-diagram.py → deprecated
- word-gen/preflight-check.js ✅
- word-gen/preflight-check.py → deprecated
- SKILL.md (引用更新)

## 验证

1. `node word-gen/generate-contest-docs.js --help` 执行成功
2. `node word-gen/capture-diagram.js --help` 执行成功  
3. `node word-gen/preflight-check.js --help` 执行成功
4. SKILL.md 无新增 .py 引用

## Success Criteria

word-gen/ 无活跃 Python 文件 (全部标注 deprecated)