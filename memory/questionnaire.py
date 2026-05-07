"""
融媒技术创新大赛 - 引导式问卷引擎

支持：
- 逐题展示 + 带理由的推荐选项
- 用户选推荐 / 自定义 / 跳过
- 级联更新（track/ai_mode/side变更自动联动）
- 多轮对话上下文记忆
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

# 导入上下文管理器
import sys
sys.path.insert(0, str(Path(__file__).parent))
from context_manager import ContextManager


# ============================================================
# 推荐数据（内置知识库）
# ============================================================

TRACK_OPTIONS = [
    {
        "value": "技术研发类",
        "label": "技术研发类",
        "reason": "适合新系统/新算法/新工具开发，需技术架构图+性能对比数据（准确率/召回率/误报率）",
        "when": "有明确的算法/模型/系统创新，且有技术架构可展示"
    },
    {
        "value": "应用创新类",
        "label": "应用创新类",
        "reason": "适合业务流程优化类项目，需效率提升数据+落地路径+三阶段推广计划",
        "when": "对现有流程进行优化、整合、智能化升级，效果可量化"
    },
    {
        "value": "内容创意类",
        "label": "内容创意类",
        "reason": "适合视频/H5/海报/数据新闻等创意内容，需受众分析+传播路径+商业价值",
        "when": "产出物为创意内容而非系统/工具"
    }
]

SIDE_OPTIONS = [
    {"value": "日报侧", "label": "日报侧（方正系统）", "reason": "2018年采购方正系统，具备中央厨房功能，内容生产为主"},
    {"value": "广电侧", "label": "广电侧（索贝系统）", "reason": "2018年采购索贝系统，具备广播电视播出功能，技术要求更高"},
    {"value": "跨两边", "label": "跨两边（需同时对接方正+索贝）", "reason": "同时对接日报和广电两个系统，解决双系统互通问题"}
]

AI_MODE_OPTIONS = [
    {
        "value": "API模式",
        "label": "API模式（调用云端模型）",
        "reason": "无需本地GPU，通过API调用智谱GLM-4/通义千问等云端模型，按调用量付费",
        "pros": "部署简单，无需GPU服务器，初期成本低",
        "cons": "有API调用费用，数据需外网传输（需确认安全性）"
    },
    {
        "value": "私有化部署",
        "label": "私有化部署（本地大模型推理）",
        "reason": "开源模型（如Qwen3.5-VL/Llama/GLM）本地部署，数据全程内网，无API费用",
        "pros": "数据不出内网，无API授权费，适合临沂融媒安全要求",
        "cons": "需GPU服务器（RTX 4090×2或A100），初期投入较高"
    }
]

PRIVATE_MODEL_OPTIONS = {
    "技术研发类": [
        {
            "value": "Qwen3.5-VL-72B",
            "label": "通义千问3.5-VL-72B（多模态）",
            "reason": "原生支持视频帧分析，单模型同时完成视觉检测+字幕OCR+语义理解，INT4量化约48GB需双卡RTX 4090",
            "hardware": "RTX 4090×2（张量并行）"
        },
        {
            "value": "Qwen2.5-72B + YOLOv8",
            "label": "通义千问2.5-72B + YOLOv8（双引擎）",
            "reason": "Qwen2.5处理文本理解，YOLOv8处理视觉检测，分工明确但架构较复杂",
            "hardware": "RTX 4090×2 或 A100×1"
        },
        {
            "value": "GLM-4-9B",
            "label": "智谱GLM-4-9B（轻量级）",
            "reason": "轻量级开源模型，单卡RTX 4090即可运行，适合简单文本任务",
            "hardware": "RTX 4090×1"
        }
    ],
    "应用创新类": [
        {
            "value": "Qwen2.5-7B",
            "label": "通义千问2.5-7B（轻量文本）",
            "reason": "轻量级开源模型，单卡即可运行，适合业务流程文本处理",
            "hardware": "RTX 4090×1"
        },
        {
            "value": "GLM-4-9B",
            "label": "智谱GLM-4-9B（轻量文本）",
            "reason": "轻量级国产开源模型，单卡运行，适合中文业务流程优化",
            "hardware": "RTX 4090×1"
        }
    ]
}

API_MODEL_OPTIONS = {
    "技术研发类": [
        {"value": "智谱GLM-4", "label": "智谱GLM-4（GLM-4V多模态）", "reason": "支持图像理解，适配视频帧分析场景，API调用稳定"},
        {"value": "通义千问2.1", "label": "通义千问2.1（Qwen-VL）", "reason": "阿里云视觉语言模型，视频帧分析能力强"}
    ],
    "应用创新类": [
        {"value": "智谱GLM-4", "label": "智谱GLM-4（文本）", "reason": "文本理解能力强，适合业务流程优化"},
        {"value": "通义千问2.0", "label": "通义千问2.0（文本）", "reason": "性价比高，适合常规文本处理"}
    ]
}

PAIN_POINTS_TEMPLATES = {
    "广电侧": [
        {"value": "系统封闭", "label": "传统播出系统依赖进口专用硬件", "impact": "单频道采购成本达百万级，迭代周期长"},
        {"value": "功能割裂", "label": "采集、编码、技审、编单、播出各环节独立运行", "impact": "人工串联效率低，故障排查困难"},
        {"value": "智能化缺失", "label": "技审依赖人工逐帧检查，无法实时发现静帧/黑场", "impact": "漏检风险高，人力成本高"},
        {"value": "集群能力弱", "label": "单机架构无法水平扩展", "impact": "高峰时段负载集中易出故障，播出安全性无法保障"},
        {"value": "应急响应慢", "label": "信号故障需人工发现和切换，主备倒换耗时数分钟", "impact": "不符合安全播出要求，事故响应慢"},
        {"value": "数据孤岛", "label": "日报与广电系统相互独立，不能互通", "impact": "内容协同困难，标准不统一"}
    ],
    "日报侧": [
        {"value": "效率低下", "label": "内容生产依赖人工，策划/采/编/发流程串行", "impact": "时效性差，多渠道发布效率低"},
        {"value": "审核标准不统一", "label": "内容审核依赖人工，标准不一致", "impact": "风险控制困难，审核质量不稳定"},
        {"value": "知识库缺失", "label": "历史稿件未形成结构化知识库", "impact": "素材复用困难，查询效率低"},
        {"value": "数据孤岛", "label": "日报与广电系统相互独立，数据不互通", "impact": "内容协同困难，跨渠道分发成本高"},
        {"value": "智能化缺失", "label": "内容推荐/生成依赖人工，无AI能力", "impact": "个性化程度低，用户粘性差"}
    ],
    "跨两边": [
        {"value": "系统互通难", "label": "方正系统与索贝系统无法对接", "impact": "内容需重复生产，协同效率低"},
        {"value": "标准不统一", "label": "日报与广电内容标准不统一", "impact": "跨渠道发布质量不一致"},
        {"value": "流程断裂", "label": "融媒体指挥调度与实际生产脱节", "impact": "协同决策难，执行跟踪弱"}
    ]
}

KEY_TECH_TEMPLATES = {
    "技术研发类": [
        "大模型选型：采用 [具体模型名称]，理由：[与融媒体场景的匹配度]",
        "推理引擎：[vLLM / TensorRT-LLM / ollama]，理由：[性能优化/显存优化/张量并行]",
        "算法优化：[具体优化点，如 RAG 检索策略 / 模型微调方案 / Prompt 优化设计]",
        "AIGC/Agent 突破：[具体突破点，如 多Agent协同决策 / 自动化工作流编排]"
    ],
    "应用创新类": [
        "流程优化设计：[具体业务流程改进点，描述优化前后对比]",
        "技术选型：[选用的技术栈 + 与现有系统的集成方式]",
        "数据处理：[如何利用历史数据/用户行为数据实现智能推荐/自动化]"
    ]
}

COMPARISON_TABLE_TEMPLATES = {
    "技术研发类": ["准确率", "召回率", "误报率", "响应时延", "并发量(QPS)"],
    "应用创新类": ["效率提升（步骤/时间）", "成本节省", "用户体验", "上线周期", "并发支持"]
}

RESOURCE_NEEDS_TEMPLATES = {
    "私有化部署": [
        {"type": "GPU服务器", "spec": "RTX 4090×2（24GB显存×2）", "usage": "vLLM张量并行 + 模型推理"},
        {"type": "应用服务器", "spec": "4核8G×2台", "usage": "负载均衡 + API网关"},
        {"type": "数据库服务器", "spec": "8核16G×1台", "usage": "MySQL + Redis集群"},
        {"type": "存储", "spec": "本地HDD 10TB", "usage": "素材与审核日志存储"},
        {"type": "模型权重", "spec": "[模型名]-INT4.gguf（约48GB）", "usage": "本地大模型推理，无API授权费"}
    ],
    "API模式": [
        {"type": "应用服务器", "spec": "4核8G×2台", "usage": "负载均衡 + API网关"},
        {"type": "数据库服务器", "spec": "8核16G×1台", "usage": "MySQL + Redis集群"},
        {"type": "API授权费", "spec": "按调用量计费", "usage": "[模型名] API调用费用"}
    ]
}


# ============================================================
# 问卷引擎
# ============================================================

class QuestionnaireEngine:
    """引导式问卷引擎：管理多步问答流程，生成推荐选项"""

    STEPS = [
        {"id": "track", "title": "赛道确认", "question": "请选择参赛赛道类别："},
        {"id": "side", "title": "项目归属", "question": "项目归属于融媒体中心哪个侧？"},
        {"id": "project_name", "title": "作品名称", "question": "请输入作品名称："},
        {"id": "ai_mode", "title": "AI部署方式", "question": "大模型采用什么部署方式？"},
        {"id": "model_choice", "title": "模型选择", "question": "请选择具体的大模型："},
        {"id": "pain_points", "title": "痛点分析", "question": "请选择或补充核心痛点："},
        {"id": "key_tech", "title": "关键技术", "question": "请确认关键技术方向："},
    ]

    def __init__(self, ctx: Optional[ContextManager] = None):
        self.ctx = ctx or ContextManager()
        self.current_step = 0
        self.answers = {}  # 存储用户回答

    @classmethod
    def from_project(cls, project_id: str):
        """从已有项目加载"""
        ctx = ContextManager()
        ctx.load(project_id)
        engine = cls(ctx)
        # 恢复已填答案
        for field_key, field_data in ctx.data.get("fields", {}).items():
            if field_data.get("value"):
                engine.answers[field_key] = field_data["value"]
        return engine

    def get_current_step(self):
        """获取当前步骤信息"""
        if self.current_step >= len(self.STEPS):
            return None
        step = self.STEPS[self.current_step]
        return {
            **step,
            "progress": f"{self.current_step + 1}/{len(self.STEPS)}",
            "recommendations": self._generate_recommendations(step["id"]),
            "current_value": self.answers.get(step["id"]),
            "cascade_updates": []  # 待用户确认的级联更新
        }

    def _generate_recommendations(self, step_id: str):
        """根据当前上下文生成推荐选项"""
        ctx = self.ctx.data
        track = ctx["metadata"].get("current_track")
        side = ctx["metadata"].get("side")
        ai_mode = ctx["metadata"].get("ai_mode")

        if step_id == "track":
            return TRACK_OPTIONS

        elif step_id == "side":
            return SIDE_OPTIONS

        elif step_id == "project_name":
            return []  # 项目名称无推荐，需用户输入

        elif step_id == "ai_mode":
            return AI_MODE_OPTIONS

        elif step_id == "model_choice":
            if ai_mode == "私有化部署":
                return PRIVATE_MODEL_OPTIONS.get(track, PRIVATE_MODEL_OPTIONS["应用创新类"])
            elif ai_mode == "API模式":
                return API_MODEL_OPTIONS.get(track, API_MODEL_OPTIONS["应用创新类"])
            return []

        elif step_id == "pain_points":
            side_key = side or "广电侧"
            return PAIN_POINTS_TEMPLATES.get(side_key, PAIN_POINTS_TEMPLATES["广电侧"])

        elif step_id == "key_tech":
            track_key = track or "应用创新类"
            return KEY_TECH_TEMPLATES.get(track_key, KEY_TECH_TEMPLATES["应用创新类"])

        return []

    def submit_answer(self, step_id: str, value, source="user_selected"):
        """
        提交答案，执行级联更新
        返回：{
            "next_step": int,
            "cascade_updates": [...],  # 需用户确认的级联更新
            "field_value": {...}       # 当前字段值
        }
        """
        # 保存答案
        self.answers[step_id] = value
        self.ctx.data["fields"][step_id] = {"value": value, "source": source}

        # 更新上下文管理器中的元数据
        metadata_map = {
            "track": "current_track",
            "side": "side",
            "project_name": "project_name",
            "ai_mode": "ai_mode",
            "model_choice": "model_choice"
        }
        if step_id in metadata_map:
            self.ctx.data["metadata"][metadata_map[step_id]] = value

        # 执行级联更新
        cascade_result = self.ctx.update_field(step_id, value, source)

        # 前进到下一步
        self.current_step += 1

        return {
            "next_step": self.current_step,
            "cascade_updates": cascade_result.get("updated_fields", []),
            "field_value": value
        }

    def apply_cascade(self, cascade_field: str, recommendation: str):
        """用户确认级联更新，应用推荐值"""
        self.ctx.data["fields"][cascade_field] = {
            "value": recommendation,
            "source": "cascade_recommendation"
        }
        self.answers[cascade_field] = recommendation
        return {"applied": cascade_field, "value": recommendation}

    def get_change_log(self):
        """获取变更记录"""
        return self.ctx.data.get("change_log", [])

    def is_complete(self):
        """是否所有步骤都已完成"""
        return self.current_step >= len(self.STEPS)

    def generate_summary(self):
        """生成采集结果摘要"""
        return {
            "project_id": self.ctx.project_id,
            "project_name": self.answers.get("project_name"),
            "track": self.answers.get("track"),
            "side": self.answers.get("side"),
            "ai_mode": self.answers.get("ai_mode"),
            "model_choice": self.answers.get("model_choice"),
            "pain_points": self.answers.get("pain_points", []),
            "key_tech": self.answers.get("key_tech", []),
            "completed_steps": self.current_step,
            "total_steps": len(self.STEPS)
        }


# ============================================================
# 问卷输出格式化
# ============================================================

def format_step_for_display(step_data: dict) -> str:
    """将步骤数据格式化为可读文本（用于CLI/对话输出）"""
    lines = []
    lines.append(f"\n{'='*50}")
    lines.append(f"📋 {step_data['title']} [{step_data['progress']}]")
    lines.append(f"{'='*50}")
    lines.append(f"\n{step_data['question']}")

    # 显示推荐选项
    recommendations = step_data.get("recommendations", [])
    if recommendations:
        lines.append("\n推荐选项：")
        for i, rec in enumerate(recommendations, 1):
            if isinstance(rec, dict):
                lines.append(f"  [{i}] {rec.get('label', rec.get('value'))}")
                if rec.get("reason"):
                    lines.append(f"      理由：{rec['reason']}")
            else:
                lines.append(f"  [{i}] {rec}")

    # 显示当前已选值
    if step_data.get("current_value"):
        lines.append(f"\n当前选择：{step_data['current_value']}")

    lines.append("\n输入选项编号，或输入自定义内容，或输入 'skip' 跳过")
    return "\n".join(lines)


def format_cascade_update_for_display(cascade_updates: list) -> str:
    """格式化级联更新通知"""
    if not cascade_updates:
        return ""

    lines = []
    lines.append("\n⚠️ 检测到以下联动更新：")
    for cu in cascade_updates:
        lines.append(f"\n📌 [{cu['field']}] 已自动更新")
        if cu.get("recommendation"):
            lines.append(f"   推荐内容：{cu['recommendation']}")
        if cu.get("reason"):
            lines.append(f"   原因：{cu['reason']}")
    lines.append("\n（联动更新已自动应用，可随时在结果中修改）")
    return "\n".join(lines)


# ============================================================
# 示例使用
# ============================================================

if __name__ == "__main__":
    # 测试问卷引擎
    engine = QuestionnaireEngine()

    print("🧭 融媒技术创新大赛 - 信息采集向导")
    print("=" * 50)

    while not engine.is_complete():
        step = engine.get_current_step()
        print(format_step_for_display(step))

        # 模拟用户输入
        user_input = input("\n请输入选项或内容（或输入q退出）: ").strip()
        if user_input.lower() == 'q':
            break

        # 解析输入
        if user_input.isdigit() and 1 <= int(user_input) <= len(step["recommendations"]):
            rec = step["recommendations"][int(user_input) - 1]
            value = rec.get("value") if isinstance(rec, dict) else rec
            source = "recommended"
        else:
            value = user_input if user_input != "skip" else None
            source = "user_customized" if user_input not in ["skip", ""] else "skipped"

        if value:
            result = engine.submit_answer(step["id"], value, source)
            print(format_cascade_update_for_display(result["cascade_updates"]))

    print("\n✅ 采集完成！")
    print(json.dumps(engine.generate_summary(), ensure_ascii=False, indent=2))