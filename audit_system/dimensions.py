# audit_system/dimensions.py
# -*- coding: utf-8 -*-
"""
审计维度定义
定义33个审计维度，覆盖角色、剧情、文本、设定四大类
"""
from enum import Enum
from typing import List, Dict


class AuditCategory(str, Enum):
    CHARACTER = "角色相关"
    PLOT = "剧情相关"
    TEXT = "文本相关"
    SETTING = "设定相关"


class AuditDimension(Enum):
    # 角色相关（10个维度）
    CHARACTER_OOC = ("角色出戏", AuditCategory.CHARACTER, "行为不符合人设")
    CHARACTER_MEMORY = ("角色记忆崩坏", AuditCategory.CHARACTER, "忘记重要信息")
    CHARACTER_ABILITY = ("能力崩坏", AuditCategory.CHARACTER, "战力前后矛盾")
    CHARACTER_RELATIONSHIP = ("关系崩坏", AuditCategory.CHARACTER, "人物关系突变")
    CHARACTER_MOTIVATION = ("动机缺失", AuditCategory.CHARACTER, "行为缺乏动机")
    CHARACTER_DEVELOPMENT = ("成长断层", AuditCategory.CHARACTER, "角色成长不自然")
    CHARACTER_DIALOGUE = ("对话违和", AuditCategory.CHARACTER, "对话风格不符")
    CHARACTER_EMOTION = ("情感违和", AuditCategory.CHARACTER, "情感反应不当")
    CHARACTER_APPEARANCE = ("出场矛盾", AuditCategory.CHARACTER, "角色突然出现/消失")
    CHARACTER_KNOWLEDGE = ("知识泄露", AuditCategory.CHARACTER, "角色不应知道的信息")
    
    # 剧情相关（10个维度）
    PLOT_PACING = ("节奏单调", AuditCategory.PLOT, "剧情节奏问题")
    PLOT_HOLE = ("剧情漏洞", AuditCategory.PLOT, "逻辑漏洞")
    PLOT_CONTRADICTION = ("前后矛盾", AuditCategory.PLOT, "剧情冲突")
    PLOT_FORESHADOW = ("伏笔断裂", AuditCategory.PLOT, "伏笔未回收")
    PLOT_DEUS_EX = ("机械降神", AuditCategory.PLOT, "不合理的解决方案")
    PLOT_TIMELINE = ("时间线混乱", AuditCategory.PLOT, "时间顺序错误")
    PLOT_CAUSALITY = ("因果断裂", AuditCategory.PLOT, "缺乏因果关系")
    PLOT_TONE = ("基调突变", AuditCategory.PLOT, "风格突然变化")
    PLOT_FOCUS = ("焦点模糊", AuditCategory.PLOT, "主线不清晰")
    PLOT_RESOLUTION = ("结局仓促", AuditCategory.PLOT, "结局处理不当")
    
    # 文本相关（8个维度）
    TEXT_REPETITION = ("内容重复", AuditCategory.TEXT, "重复描写")
    TEXT_VOCABULARY = ("词汇疲劳", AuditCategory.TEXT, "用词单调")
    TEXT_SENTENCE = ("句式单一", AuditCategory.TEXT, "句式重复")
    TEXT_AI_TRACE = ("AI痕迹明显", AuditCategory.TEXT, "AI生成特征")
    TEXT_CLICHE = ("套话堆砌", AuditCategory.TEXT, "陈词滥调")
    TEXT_GRAMMAR = ("语法错误", AuditCategory.TEXT, "基础语法问题")
    TEXT_PUNCTUATION = ("标点错误", AuditCategory.TEXT, "标点使用不当")
    TEXT_FORMAT = ("格式混乱", AuditCategory.TEXT, "排版格式问题")
    
    # 设定相关（5个维度）
    SETTING_WORLD = ("世界观崩坏", AuditCategory.SETTING, "违反世界观设定")
    SETTING_RULE = ("规则矛盾", AuditCategory.SETTING, "设定规则冲突")
    SETTING_LOCATION = ("地点矛盾", AuditCategory.SETTING, "地理位置错误")
    SETTING_ITEM = ("物品矛盾", AuditCategory.SETTING, "道具前后矛盾")
    SETTING_POWER = ("战力崩坏", AuditCategory.SETTING, "力量体系混乱")
    
    def __init__(self, display_name: str, category: AuditCategory, description: str):
        self.display_name = display_name
        self.category = category
        self.description = description
    
    @classmethod
    def get_by_category(cls, category: AuditCategory) -> List['AuditDimension']:
        """获取指定类别的所有维度"""
        return [dim for dim in cls if dim.category == category]
    
    @classmethod
    def get_all_dimensions(cls) -> List['AuditDimension']:
        """获取所有维度"""
        return list(cls)


class Severity(str, Enum):
    CRITICAL = "critical"
    MAJOR = "major"
    MINOR = "minor"
    SUGGESTION = "suggestion"


SEVERITY_WEIGHTS = {
    Severity.CRITICAL: 1.0,
    Severity.MAJOR: 0.7,
    Severity.MINOR: 0.3,
    Severity.SUGGESTION: 0.1
}

SEVERITY_DESCRIPTIONS = {
    Severity.CRITICAL: "严重问题，必须修复",
    Severity.MAJOR: "重要问题，强烈建议修复",
    Severity.MINOR: "次要问题，建议修复",
    Severity.SUGGESTION: "优化建议，可选修复"
}
