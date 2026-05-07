#!/usr/bin/env python3
"""
动态生成项目定制化 Mockup HTML
根据项目配置（赛道、核心功能、AI部署模式）生成真实感界面

用法:
    python3 generate-mockup.py <project_config.json> <output_dir>
"""

import json
import os
import sys
from pathlib import Path

# ===== Mockup 模板组件 =====

CSS_BASE = """
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: "Microsoft YaHei", "PingFang SC", sans-serif; background: #0f1419; color: #e7e9ea; }
.mockup-container { width: 1200px; min-height: 700px; padding: 20px; }
.header { display: flex; justify-content: space-between; align-items: center; padding: 12px 20px; background: #1a1f26; border-radius: 8px 8px 0 0; border-bottom: 2px solid #2d333b; }
.header-title { font-size: 16px; font-weight: 600; color: #fff; }
.header-time { font-size: 12px; color: #8b949e; }
.main-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; margin-top: 16px; }
.panel { background: #161b22; border-radius: 8px; border: 1px solid #2d333b; padding: 16px; }
.panel-title { font-size: 13px; color: #8b949e; margin-bottom: 12px; border-bottom: 1px solid #2d333b; padding-bottom: 8px; }
.metric { text-align: center; padding: 12px; }
.metric-value { font-size: 32px; font-weight: 700; color: #58a6ff; }
.metric-label { font-size: 11px; color: #8b949e; margin-top: 4px; }
.status-badge { display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 500; }
.status-ok { background: #238636; color: #fff; }
.status-warn { background: #9e6a03; color: #fff; }
.status-error { background: #da3633; color: #fff; }
.chart-area { height: 200px; background: linear-gradient(180deg, rgba(88,166,255,0.1) 0%, transparent 100%); border-radius: 4px; position: relative; overflow: hidden; }
.chart-line { position: absolute; bottom: 0; left: 0; right: 0; height: 60%; background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 100" preserveAspectRatio="none"><polyline fill="none" stroke="%2358a6ff" stroke-width="2" points="0,80 50,60 100,70 150,40 200,55 250,30 300,45 350,35 400,50"/></svg>') no-repeat bottom center; background-size: 100% 100%; }
.table-ui { width: 100%; border-collapse: collapse; }
.table-ui th { text-align: left; padding: 8px 12px; background: #1f2937; color: #8b949e; font-size: 11px; font-weight: 500; border-bottom: 1px solid #2d333b; }
.table-ui td { padding: 10px 12px; border-bottom: 1px solid #2d333b; font-size: 12px; }
.table-ui tr:hover { background: rgba(88,166,255,0.05); }
.tag { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 10px; background: #21262d; color: #8b949e; margin-right: 4px; }
.tag-primary { background: rgba(88,166,255,0.2); color: #58a6ff; }
.footer { margin-top: 16px; padding: 12px 20px; background: #1a1f26; border-radius: 0 0 8px 8px; display: flex; justify-content: space-between; font-size: 11px; color: #8b949e; }
</style>
"""


def generate_dashboard_html(config: dict) -> str:
    """生成仪表盘/工作台 Mockup"""
    project_name = config.get('project_name', '智能系统')
    metrics = config.get('metrics', {})
    status_items = config.get('status_items', [])

    metrics_html = ""
    for k, v in metrics.items():
        metrics_html += f"""
        <div class="panel">
            <div class="metric">
                <div class="metric-value">{v['value']}</div>
                <div class="metric-label">{v['label']}</div>
            </div>
        </div>"""

    status_html = ""
    for item in status_items:
        status_class = f"status-{item['status']}"
        status_html += f"""
        <tr>
            <td>{item['name']}</td>
            <td><span class="status-badge {status_class}">{item['label']}</span></td>
            <td style="color:#8b949e">{item['time']}</td>
        </tr>"""

    return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>{project_name}</title>{CSS_BASE}</head>
<body>
<div class="mockup-container">
    <div class="header">
        <span class="header-title">📊 {project_name} - 监控大屏</span>
        <span class="header-time">更新时间: 2026-05-07 14:32:15</span>
    </div>
    <div class="main-grid">
        {metrics_html}
    </div>
    <div style="display:grid; grid-template-columns: 2fr 1fr; gap:16px; margin-top:16px;">
        <div class="panel">
            <div class="panel-title">📈 系统运行趋势</div>
            <div class="chart-area"><div class="chart-line"></div></div>
        </div>
        <div class="panel">
            <div class="panel-title">⚡ 实时状态</div>
            <table class="table-ui">
                <thead><tr><th>项目</th><th>状态</th><th>时间</th></tr></thead>
                <tbody>{status_html}</tbody>
            </table>
        </div>
    </div>
    <div class="footer">
        <span>临沂市融媒体中心 · 智能监控系统</span>
        <span>v2.1.0 | 连接正常</span>
    </div>
</div>
</body></html>"""


def generate_signal_monitor_html(config: dict) -> str:
    """生成广播监控系统 Mockup"""
    project_name = config.get('project_name', '广播监控系统')
    channels = config.get('channels', [])
    alerts = config.get('alerts', [])

    channels_html = ""
    for ch in channels:
        status_class = f"status-{ch['status']}"
        channels_html += f"""
        <tr>
            <td style="color:#58a6ff">{ch['id']}</td>
            <td>{ch['name']}</td>
            <td>{ch['signal']}%</td>
            <td>
                <div style="width:80px;height:6px;background:#21262d;border-radius:3px;">
                    <div style="width:{ch['signal']}%;height:100%;background:{'#238636' if ch['status']=='ok' else '#da3633'};border-radius:3px;"></div>
                </div>
            </td>
            <td><span class="status-badge {status_class}">{ch['label']}</span></td>
        </tr>"""

    alerts_html = ""
    for alert in alerts:
        alerts_html += f"""
        <tr style="background: rgba(218,54,51,0.1);">
            <td>🔴</td>
            <td>{alert['time']}</td>
            <td>{alert['channel']}</td>
            <td style="color:#f85149">{alert['message']}</td>
            <td><button style="background:#da3633;border:none;color:#fff;padding:4px 12px;border-radius:4px;cursor:pointer;">处理</button></td>
        </tr>"""

    return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>{project_name}</title>{CSS_BASE}</head>
<body>
<div class="mockup-container">
    <div class="header">
        <span class="header-title">📡 {project_name} - 信号监测</span>
        <span class="header-time">2026-05-07 14:32 | 系统正常</span>
    </div>
    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-top:16px;">
        <div class="panel"><div class="metric"><div class="metric-value" style="color:#238636">32</div><div class="metric-label">在线频道</div></div></div>
        <div class="panel"><div class="metric"><div class="metric-value" style="color:#f85149">2</div><div class="metric-label">异常告警</div></div></div>
        <div class="panel"><div class="metric"><div class="metric-value">99.7%</div><div class="metric-label">信号质量</div></div></div>
        <div class="panel"><div class="metric"><div class="metric-value">45ms</div><div class="metric-label">响应延迟</div></div></div>
    </div>
    <div style="display:grid;grid-template-columns:2fr 1fr;gap:16px;margin-top:16px;">
        <div class="panel">
            <div class="panel-title">📺 频道信号状态</div>
            <table class="table-ui">
                <thead><tr><th>频道号</th><th>频道名称</th><th>信号强度</th><th>信号条</th><th>状态</th></tr></thead>
                <tbody>{channels_html}</tbody>
            </table>
        </div>
        <div class="panel">
            <div class="panel-title">🚨 实时告警</div>
            <table class="table-ui">
                <thead><tr><th></th><th>时间</th><th>频道</th><th>信息</th><th>操作</th></tr></thead>
                <tbody>{alerts_html}</tbody>
            </table>
        </div>
    </div>
    <div class="footer">
        <span>临沂市广播电视台 · 智能监播系统</span>
        <span>自动切换: 开启 | 延时联动: 激活</span>
    </div>
</div>
</body></html>"""


def generate_data_visualization_html(config: dict) -> str:
    """生成数据可视化大屏 Mockup"""
    project_name = config.get('project_name', '数据大屏')
    kpis = config.get('kpis', [])

    kpis_html = ""
    for kpi in kpis:
        kpis_html += f"""
        <div class="panel">
            <div class="metric">
                <div class="metric-value" style="color:{'#58a6ff' if kpi['trend']=='up' else '#f85149'}">{kpi['value']}</div>
                <div class="metric-label">{kpi['label']}</div>
                <div style="font-size:11px;color:#8b949e;margin-top:4px;">{kpi['change']}</div>
            </div>
        </div>"""

    return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>{project_name}</title>{CSS_BASE}</head>
<body style="background:#000;">
<div class="mockup-container" style="background:linear-gradient(135deg,#0f1419 0%,#1a1f26 100%);border-radius:12px;border:1px solid #2d333b;">
    <div class="header" style="background:linear-gradient(90deg,#1a1f26,#2d333b);">
        <span class="header-title" style="font-size:20px;">📊 {project_name}</span>
        <span class="header-time">数据更新: 2026-05-07 14:32:15 | 实时</span>
    </div>
    <div class="main-grid">
        {kpis_html}
    </div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:16px;">
        <div class="panel">
            <div class="panel-title">📈 趋势分析</div>
            <div class="chart-area" style="height:180px;">
                <svg viewBox="0 0 400 120" style="width:100%;height:100%;">
                    <defs>
                        <linearGradient id="grad" x1="0%" y1="0%" x2="0%" y2="100%">
                            <stop offset="0%" style="stop-color:#58a6ff;stop-opacity:0.4"/>
                            <stop offset="100%" style="stop-color:#58a6ff;stop-opacity:0"/>
                        </linearGradient>
                    </defs>
                    <polygon fill="url(#grad)" points="0,100 50,70 100,80 150,50 200,60 250,35 300,45 350,30 400,40 400,120 0,120"/>
                    <polyline fill="none" stroke="#58a6ff" stroke-width="2" points="0,100 50,70 100,80 150,50 200,60 250,35 300,45 350,30 400,40"/>
                </svg>
            </div>
        </div>
        <div class="panel">
            <div class="panel-title">🏆 排名 TOP 5</div>
            <table class="table-ui">
                <thead><tr><th>排名</th><th>名称</th><th>数值</th><th>趋势</th></tr></thead>
                <tbody>
                    <tr><td style="color:#ffd700">🥇</td><td>新闻频道</td><td style="color:#58a6ff">98.5%</td><td style="color:#238636">↑ 2.3%</td></tr>
                    <tr><td style="color:#c0c0c0">🥈</td><td>综合频道</td><td style="color:#58a6ff">95.2%</td><td style="color:#238636">↑ 1.8%</td></tr>
                    <tr><td style="color:#cd7f32">🥉</td><td>公共频道</td><td style="color:#58a6ff">91.8%</td><td style="color:#f85149">↓ 0.5%</td></tr>
                    <tr><td>4</td><td>文艺频道</td><td style="color:#58a6ff">89.3%</td><td style="color:#238636">↑ 0.9%</td></tr>
                    <tr><td>5</td><td>教育频道</td><td style="color:#58a6ff">87.1%</td><td style="color:#8b949e">→</td></tr>
                </tbody>
            </table>
        </div>
    </div>
    <div class="footer">
        <span>临沂市融媒体中心 · 数据驾驶舱</span>
        <span>🟢 服务正常 | 数据延迟: 0ms</span>
    </div>
</div>
</body></html>"""


def generate_audit_workbench_html(config: dict) -> str:
    """生成审核工作台 Mockup"""
    project_name = config.get('project_name', '审核系统')
    workflow_steps = config.get('workflow_steps', [])
    pending_items = config.get('pending_items', [])

    workflow_html = ""
    for i, step in enumerate(workflow_steps):
        workflow_html += f"""
        <div style="display:flex;align-items:center;gap:8px;">
            <div style="width:32px;height:32px;background:{'#238636' if step['done'] else '#21262d'};color:#fff;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:14px;">{i+1}</div>
            <span style="color:{'#8b949e' if not step['done'] else '#e7e9ea'};font-size:13px;">{step['name']}</span>
            {"→" if i < len(workflow_steps)-1 else ""}
        </div>"""

    pending_html = ""
    for item in pending_items:
        pending_html += f"""
        <tr>
            <td>{item['id']}</td>
            <td style="max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">{item['title']}</td>
            <td><span class="tag tag-primary">{item['type']}</span></td>
            <td><span class="status-badge status-warn">待审核</span></td>
            <td><button style="background:#58a6ff;border:none;color:#fff;padding:4px 12px;border-radius:4px;cursor:pointer;">审核</button></td>
        </tr>"""

    return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>{project_name}</title>{CSS_BASE}</head>
<body>
<div class="mockup-container">
    <div class="header">
        <span class="header-title">✅ {project_name} - 审核工作台</span>
        <span class="header-time">当前用户: 管理员 | 待处理: 12 项</span>
    </div>
    <div class="panel" style="margin-top:16px;">
        <div class="panel-title">📋 审核流程</div>
        <div style="display:flex;align-items:center;gap:16px;padding:16px 0;">
            {workflow_html}
        </div>
    </div>
    <div class="panel" style="margin-top:16px;">
        <div class="panel-title">⏳ 待审核内容 ({len(pending_items)} 项)</div>
        <table class="table-ui">
            <thead><tr><th>ID</th><th>标题</th><th>类型</th><th>状态</th><th>操作</th></tr></thead>
            <tbody>{pending_html}</tbody>
        </table>
    </div>
    <div class="footer">
        <span>临沂市融媒体中心 · 内容审核系统</span>
        <span>多级审核: 开启 | 自动风控: 激活</span>
    </div>
</div>
</body></html>"""


def generate_architecture_html(config: dict) -> str:
    """生成架构图 Mockup"""
    track = config.get('track', '技术研发类')
    ai_mode = config.get('ai_mode', '私有化部署')
    model = config.get('model_choice', 'Qwen3.5-VL-72B')
    components = config.get('components', [])

    if track == '技术研发类':
        layer_data = [
            ("数据源层", ["电视直播信号", "新媒体数据流", "第三方API"]),
            ("输入处理层", ["信号解码器", "YUV色彩空间分析", "多帧缓冲"]),
            ("AI模型层", [f"{model}", "TensorRT加速引擎", "模型量化模块"]),
            ("业务逻辑层", ["信号监测", "故障报警", "自动切换", "延时联动"]),
            ("输出展示层", ["监控大屏", "告警通知", "日志记录"])
        ]
    elif track == '应用创新类':
        layer_data = [
            ("采集层", ["用户操作数据", "系统日志", "业务数据"]),
            ("处理层", ["数据清洗", "特征提取", "规则引擎"]),
            ("AI服务层", ["智能分析", "推荐算法", "风控模型"]),
            ("应用层", ["流程优化", "效率提升", "数据看板"]),
            ("展示层", ["Web端", "移动端", "大屏展示"])
        ]
    else:  # 内容创意类
        layer_data = [
            ("素材层", ["视频素材", "图文内容", "H5模板"]),
            ("编辑层", ["智能剪辑", "特效生成", "字幕匹配"]),
            ("AI生成层", ["AIGC内容", "模板渲染", "多模态融合"]),
            ("发布层", ["多平台发布", "社交分享", "数据分析"])
        ]

    layers_html = ""
    for i, (layer_name, items) in enumerate(layer_data):
        items_html = "".join([f'<span class="tag tag-primary">{item}</span>' for item in items])
        layers_html += f"""
        <div style="display:flex;align-items:stretch;gap:8px;margin-bottom:12px;">
            <div style="width:100px;padding:12px;background:#21262d;border-radius:6px;font-size:12px;font-weight:600;color:#58a6ff;text-align:center;display:flex;align-items:center;justify-content:center;">
                {layer_name}
            </div>
            <div style="flex:1;padding:12px;background:#161b22;border-radius:6px;display:flex;gap:8px;flex-wrap:wrap;align-items:center;">
                {items_html}
            </div>
        </div>"""

    return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>系统架构图</title>{CSS_BASE}</head>
<body>
<div class="mockup-container">
    <div class="header">
        <span class="header-title">🏗️ 系统架构图 - {track}</span>
        <span class="header-time">AI模式: {ai_mode} | 模型: {model}</span>
    </div>
    <div class="panel" style="margin-top:16px;">
        <div class="panel-title">📐 技术架构</div>
        <div style="padding:20px;">
            {layers_html}
        </div>
    </div>
    <div class="panel" style="margin-top:16px;">
        <div class="panel-title">🔗 数据流向</div>
        <div style="display:flex;align-items:center;justify-content:center;padding:20px;font-size:24px;color:#58a6ff;">
            数据源 → 处理 → AI推理 → 业务逻辑 → 展示输出
        </div>
    </div>
    <div class="footer">
        <span>临沂市融媒体中心 · 架构设计</span>
        <span>技术方案版本 v1.0</span>
    </div>
</div>
</body></html>"""


# ===== 主函数 =====

MOCKUP_GENERATORS = {
    'dashboard': generate_dashboard_html,
    'signal-monitor': generate_signal_monitor_html,
    'data-visualization': generate_data_visualization_html,
    'audit-workbench': generate_audit_workbench_html,
    'architecture': generate_architecture_html
}


def generate_mockup(config_path: str, output_dir: str) -> dict:
    """根据项目配置生成所有需要的 Mockup HTML"""
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    os.makedirs(output_dir, exist_ok=True)

    results = {}
    core_functions = config.get('core_functions', [])
    track = config.get('track', '技术研发类')
    ai_mode = config.get('ai_mode', '私有化部署')
    model_choice = config.get('model_choice', '')
    project_name = config.get('project_name', '智能系统')

    # 基础指标数据
    base_metrics = {
        'signal-monitor': {
            'metrics': [
                {'value': '32', 'label': '在线频道'},
                {'value': '2', 'label': '异常告警', 'style': 'color:#f85149'},
                {'value': '99.7%', 'label': '信号质量'},
                {'value': '45ms', 'label': '响应延迟'}
            ],
            'channels': [
                {'id': 'CCTV-1', 'name': '中央一套', 'signal': 98, 'status': 'ok', 'label': '正常'},
                {'id': 'CCTV-2', 'name': '中央二套', 'signal': 95, 'status': 'ok', 'label': '正常'},
                {'id': 'SDTV-1', 'name': '山东卫视', 'signal': 87, 'status': 'warn', 'label': '信号偏弱'},
                {'id': 'LYTV-1', 'name': '临沂一套', 'signal': 99, 'status': 'ok', 'label': '正常'},
                {'id': 'LYTV-2', 'name': '临沂二套', 'signal': 76, 'status': 'error', 'label': '故障'}
            ],
            'alerts': [
                {'time': '14:30:22', 'channel': 'LYTV-2', 'message': '信号中断超过30秒'},
                {'time': '14:28:15', 'channel': 'SDTV-1', 'message': '码率异常波动'}
            ]
        },
        'dashboard': {
            'metrics': [
                {'value': '1,258', 'label': '日活跃用户'},
                {'value': '99.2%', 'label': '系统可用性'},
                {'value': '156ms', 'label': '平均响应'},
                {'value': '3.2M', 'label': '日处理量'}
            ],
            'status_items': [
                {'name': 'API服务', 'status': 'ok', 'label': '正常', 'time': '14:32:00'},
                {'name': '数据库', 'status': 'ok', 'label': '正常', 'time': '14:32:00'},
                {'name': '模型推理', 'status': 'ok', 'label': '正常', 'time': '14:32:00'},
                {'name': '监控告警', 'status': 'ok', 'label': '正常', 'time': '14:32:00'}
            ]
        },
        'data-visualization': {
            'kpis': [
                {'value': '98.5%', 'label': '覆盖率', 'trend': 'up', 'change': '↑ 2.3%'},
                {'value': '156ms', 'label': '平均延迟', 'trend': 'down', 'change': '↓ 15ms'},
                {'value': '1.2M', 'label': '日PV', 'trend': 'up', 'change': '↑ 8.5%'},
                {'value': '87.3%', 'label': '用户满意度', 'trend': 'up', 'change': '↑ 1.2%'}
            ]
        },
        'audit-workbench': {
            'workflow_steps': [
                {'name': '内容提交', 'done': True},
                {'name': 'AI预审', 'done': True},
                {'name': '人工复核', 'done': True},
                {'name': '最终审批', 'done': False},
                {'name': '发布上线', 'done': False}
            ],
            'pending_items': [
                {'id': 'A001', 'title': '关于临沂市两会特别报道的审核申请', 'type': '视频'},
                {'id': 'A002', 'title': '【H5】春日赏花攻略，收藏！', 'type': 'H5'},
                {'id': 'A003', 'title': '2026年第一季度财报数据新闻', 'type': '图文'}
            ]
        }
    }

    # 根据核心功能判断需要的 Mockup 类型
    mockups_needed = []
    func_str = ' '.join(core_functions) if isinstance(core_functions, list) else str(core_functions)

    if any(kw in func_str for kw in ['监播', '监控', '信号', '报警', '切换', '延时']):
        mockups_needed.append('signal-monitor')
    if any(kw in func_str for kw in ['推荐', '发现', '热点', '选题']):
        mockups_needed.append('dashboard')
    if any(kw in func_str for kw in ['审核', '风控', '合规']):
        mockups_needed.append('audit-workbench')
    if any(kw in func_str for kw in ['大屏', '指挥', '数据新闻', '可视化']):
        mockups_needed.append('data-visualization')

    # 始终生成架构图
    mockups_needed.append('architecture')

    # 生成每个 Mockup
    for mockup_type in set(mockups_needed):  # 去重
        if mockup_type in MOCKUP_GENERATORS:
            html_config = {'track': track, 'ai_mode': ai_mode, 'model_choice': model_choice, 'project_name': project_name}

            # 填充模板数据
            if mockup_type in base_metrics:
                html_config.update(base_metrics[mockup_type])

            html_content = MOCKUP_GENERATORS[mockup_type](html_config)
            output_path = os.path.join(output_dir, f'{mockup_type}.html')

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)

            results[mockup_type] = output_path
            print(f"生成 Mockup: {output_path}")

    return results


def main():
    if len(sys.argv) < 3:
        print(f"用法: python3 {sys.argv[0]} <project_config.json> <output_dir>")
        print("\n示例 project_config.json:")
        print(json.dumps({
            'project_name': '广电智能监播系统',
            'track': '技术研发类',
            'ai_mode': '私有化部署',
            'model_choice': 'Qwen3.5-VL-72B',
            'core_functions': ['信号监测', '故障报警', '自动切换', '延时联动']
        }, indent=2, ensure_ascii=False))
        sys.exit(1)

    config_path = sys.argv[1]
    output_dir = sys.argv[2]

    results = generate_mockup(config_path, output_dir)
    print(f"\n完成! 生成了 {len(results)} 个 Mockup HTML")
    for k, v in results.items():
        print(f"  {k}: {v}")


if __name__ == '__main__':
    main()