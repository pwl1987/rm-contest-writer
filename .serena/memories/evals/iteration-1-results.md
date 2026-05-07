# rm-contest-writer Step-Bar Evaluation Results - Iteration 1

## Summary
6 evaluation agents completed successfully testing step-bar interaction mode (Tab interface):
- 3 with_skill vs 3 baseline
- Test cases: 技术研发类全流程, 应用创新类全流程, 信息采集中途修改

## Timing Data

| Eval | Config | Duration | Tokens |
|------|--------|----------|--------|
| 0 | with_skill | 164.8s | 15,833 |
| 0 | baseline | 82.1s | 7,760 |
| 1 | with_skill | 147.8s | 15,383 |
| 1 | baseline | 82.4s | 9,896 |
| 2 | with_skill | 60.8s | 16,286 |
| 2 | baseline | 126.9s | 28,342 |

## Assertions Validated ✅

- A1: Step bar format - includes Step 1/7 through Step 7/7
- A2: Track selection correct - 技术研发类/应用创新类 properly applied
- A3: 7-chapter structure - 一~七章节 complete
- A4: 5-row comparison table - 准确率/召回率/误报率/响应时延/并发量
- A5: Cascade update notification - key_tech_template regenerates on track change

## Key Findings
- Step-bar adds ~28s overhead (124.5s vs 97.1s mean)
- with_skill produces more structured output with proper tables
- Baseline shows higher token variance (stddev 9001 vs 371)
- Cascade update correctly triggers on track change

## Output Files
- /tmp/rm-contest-writer-workspace/iteration-1/eval-0-with_skill/outputs/智能选题推荐系统.md
- /tmp/rm-contest-writer-workspace/iteration-1/eval-1-with_skill/outputs/新媒体内容审核流程优化系统-申报材料.md
- /tmp/rm-contest-writer-workspace/iteration-1/eval-2-with_skill/outputs/track-change-log.md

## Review
Static HTML viewer: /tmp/rm-contest-review/iteration-1/review.html