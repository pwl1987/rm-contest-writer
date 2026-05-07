import json
import os
import uuid
from datetime import datetime
from pathlib import Path

MEMORY_DIR = Path(__file__).parent
INDEX_FILE = MEMORY_DIR / "index.json"
PROJECTS_DIR = MEMORY_DIR / "projects"


def _load_index():
    if INDEX_FILE.exists():
        return json.loads(INDEX_FILE.read_text())
    return {"projects_index": [], "user_profile": {}}


def _save_index(data):
    INDEX_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2))


class ContextManager:
    """项目上下文管理器：存储字段、追踪变更、执行级联更新"""

    # 字段依赖关系图：key变更 → 联动更新哪些字段
    FIELD_DEPENDENCIES = {
        "track": ["pain_points_focus", "key_tech_template", "comparison_table_dims", "resource_needs_template"],
        "ai_mode": ["model_choice_options", "resource_needs"],
        "side": ["pain_points_context", "existing_system"],
        "project_name": [],
    }

    def __init__(self, project_id=None):
        self.project_id = project_id or str(uuid.uuid4())[:8]
        self.data = {
            "project_id": self.project_id,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "current_track": None,
            "metadata": {
                "project_name": None,
                "side": None,
                "ai_mode": None,
                "model_choice": None,
            },
            "fields": {},
            "change_log": [],  # 变更记录：{field, old_value, new_value, cascade_from}
        }
        PROJECTS_DIR.mkdir(exist_ok=True)

    def load(self, project_id):
        """加载已有项目"""
        proj_file = PROJECTS_DIR / f"{project_id}.json"
        if proj_file.exists():
            self.project_id = project_id
            self.data = json.loads(proj_file.read_text())
            return True
        return False

    def save(self):
        """保存项目"""
        self.data["updated_at"] = datetime.now().isoformat()
        proj_file = PROJECTS_DIR / f"{self.project_id}.json"
        proj_file.write_text(json.dumps(self.data, ensure_ascii=False, indent=2))
        # 更新索引
        idx = _load_index()
        if self.project_id not in idx["projects_index"]:
            idx["projects_index"].append(self.project_id)
        _save_index(idx)

    def update_field(self, field_key, value, source="user_selected"):
        """
        更新字段，自动执行级联更新
        返回：{updated_fields: [...], conflicts: [...]} 让用户确认
        """
        old_value = self.data["metadata"].get(field_key)
        if old_value == value:
            return {"updated_fields": [], "conflicts": []}

        # 记录变更
        change = {"field": field_key, "old": old_value, "new": value, "cascade_from": None}
        self.data["change_log"].append(change)

        # 更新主字段
        self.data["metadata"][field_key] = value

        # 检查级联更新
        cascade_updates = []
        if field_key in self.FIELD_DEPENDENCIES:
            for dep_field in self.FIELD_DEPENDENCIES[field_key]:
                # 生成级联更新建议
                auto_update = self._generate_cascade(dep_field, field_key, value)
                if auto_update:
                    cascade_updates.append(auto_update)

        self.save()
        return {"updated_fields": cascade_updates, "conflicts": []}

    def _generate_cascade(self, dep_field, trigger_field, trigger_value):
        """根据字段变更生成级联更新建议"""
        if dep_field == "key_tech_template":
            if trigger_value == "技术研发类":
                return {
                    "field": "key_tech_template",
                    "recommendation": "技术研发类模板：具体模型名称（如Qwen3.5-VL-72B）+ 关键技术栈 + 算法创新点 + 量化对比",
                    "reason": "赛道为技术研发类，需突出技术先进性和量化指标"
                }
            elif trigger_value == "应用创新类":
                return {
                    "field": "key_tech_template",
                    "recommendation": "应用创新类模板：技术适配业务流程的具体改进点 + 效率提升数据",
                    "reason": "赛道为应用创新类，需突出落地可行性和效率数据"
                }
        elif dep_field == "comparison_table_dims":
            if trigger_value == "技术研发类":
                return {
                    "field": "comparison_table_dims",
                    "recommendation": "准确率 / 召回率 / 误报率 / 响应时延 / 并发量(QPS)",
                    "reason": "技术研发类评审标准要求5项量化对比"
                }
            elif trigger_value == "应用创新类":
                return {
                    "field": "comparison_table_dims",
                    "recommendation": "效率提升 / 成本节省 / 用户体验 / 上线周期 / 并发支持",
                    "reason": "应用创新类评审侧重业务流程优化效果"
                }
        elif dep_field == "resource_needs_template":
            if trigger_value == "私有化部署":
                return {
                    "field": "resource_needs_template",
                    "recommendation": "GPU服务器（RTX 4090×2 或 A100）+ 应用服务器4核8G×2 + 模型权重存储",
                    "reason": "私有化部署需本地GPU承载大模型推理"
                }
            elif trigger_value == "API模式":
                return {
                    "field": "resource_needs_template",
                    "recommendation": "云服务器4核8G×2 + API授权费用（按调用量计费）",
                    "reason": "API模式无需本地GPU，专注应用层部署"
                }
        elif dep_field == "pain_points_focus":
            if trigger_value == "广电侧":
                return {
                    "field": "pain_points_focus",
                    "recommendation": "播出系统依赖进口硬件 / 信号监控依赖人工 / 技审效率低 / 主备切换慢",
                    "reason": "广电侧痛点集中在播出安全和智能化"
                }
            elif trigger_value == "日报侧":
                return {
                    "field": "pain_points_focus",
                    "recommendation": "内容生产效率低 / 审核标准不统一 / 历史知识库缺失 / 数据孤岛",
                    "reason": "日报侧痛点集中在内容生产和数据打通"
                }
        return None

    def get_recent_projects(self):
        """获取最近项目列表"""
        idx = _load_index()
        projects = []
        for pid in reversed(idx["projects_index"][-5:]):
            proj_file = PROJECTS_DIR / f"{pid}.json"
            if proj_file.exists():
                data = json.loads(proj_file.read_text())
                projects.append({
                    "project_id": pid,
                    "project_name": data["metadata"].get("project_name") or "未命名项目",
                    "track": data["metadata"].get("current_track") or "未选择赛道",
                    "updated_at": data["updated_at"]
                })
        return projects

    def list_all(self):
        """列出所有项目"""
        return self.get_recent_projects()