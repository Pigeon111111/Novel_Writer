# state_manager/models.py
# -*- coding: utf-8 -*-
"""
结构化状态管理系统的数据模型定义
使用Pydantic进行数据验证和序列化
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum


class CharacterStatus(str, Enum):
    ALIVE = "alive"
    DEAD = "dead"
    MISSING = "missing"
    INJURED = "injured"
    UNKNOWN = "unknown"


class HookPriority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class HookStatus(str, Enum):
    PENDING = "pending"
    RESOLVED = "resolved"
    ABANDONED = "abandoned"


class CharacterState(BaseModel):
    name: str = Field(..., description="角色名称")
    location: str = Field(default="未知", description="当前位置")
    status: CharacterStatus = Field(default=CharacterStatus.ALIVE, description="角色状态")
    relationships: Dict[str, str] = Field(default_factory=dict, description="角色关系映射")
    abilities: List[str] = Field(default_factory=list, description="能力列表")
    items: List[str] = Field(default_factory=list, description="持有物品")
    emotional_state: str = Field(default="平静", description="情感状态")
    last_appearance_chapter: int = Field(default=0, description="最后出场章节")
    development_arcs: List[str] = Field(default_factory=list, description="成长轨迹")
    background: str = Field(default="", description="背景故事")
    personality: List[str] = Field(default_factory=list, description="性格特点")
    
    class Config:
        use_enum_values = True


class PendingHook(BaseModel):
    hook_id: str = Field(..., description="伏笔ID")
    description: str = Field(..., description="伏笔描述")
    planted_chapter: int = Field(..., description="埋下伏笔的章节")
    expected_resolve_chapter: Optional[int] = Field(None, description="预期回收章节")
    priority: HookPriority = Field(default=HookPriority.MEDIUM, description="优先级")
    status: HookStatus = Field(default=HookStatus.PENDING, description="状态")
    related_characters: List[str] = Field(default_factory=list, description="相关角色")
    resolved_chapter: Optional[int] = Field(None, description="实际回收章节")
    notes: str = Field(default="", description="备注")
    
    class Config:
        use_enum_values = True


class ChapterSummary(BaseModel):
    chapter_number: int = Field(..., description="章节号")
    title: str = Field(default="", description="章节标题")
    summary: str = Field(default="", description="章节摘要")
    key_events: List[str] = Field(default_factory=list, description="关键事件")
    character_appearances: List[str] = Field(default_factory=list, description="出场角色")
    hooks_planted: List[str] = Field(default_factory=list, description="埋下的伏笔ID")
    hooks_resolved: List[str] = Field(default_factory=list, description="回收的伏笔ID")
    word_count: int = Field(default=0, description="字数")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")


class SubplotProgress(BaseModel):
    subplot_id: str = Field(..., description="支线ID")
    subplot_name: str = Field(..., description="支线名称")
    description: str = Field(default="", description="支线描述")
    start_chapter: int = Field(..., description="起始章节")
    current_status: str = Field(default="进行中", description="当前状态")
    progress_percentage: float = Field(default=0.0, description="进度百分比")
    related_characters: List[str] = Field(default_factory=list, description="相关角色")
    key_milestones: List[str] = Field(default_factory=list, description="关键里程碑")
    expected_end_chapter: Optional[int] = Field(None, description="预期结束章节")


class EmotionalArc(BaseModel):
    character_name: str = Field(..., description="角色名称")
    arc_type: str = Field(default="成长", description="弧线类型：成长、堕落、救赎等")
    start_emotion: str = Field(default="", description="起始情感")
    current_emotion: str = Field(default="", description="当前情感")
    target_emotion: str = Field(default="", description="目标情感")
    key_events: List[str] = Field(default_factory=list, description="关键事件")
    progress_chapters: List[int] = Field(default_factory=list, description="进展章节")


class CurrentState(BaseModel):
    current_chapter: int = Field(default=0, description="当前章节")
    current_location: str = Field(default="", description="当前位置")
    active_characters: List[str] = Field(default_factory=list, description="活跃角色")
    time_line: str = Field(default="", description="时间线")
    world_state: Dict[str, str] = Field(default_factory=dict, description="世界状态")
    last_updated: datetime = Field(default_factory=datetime.now, description="最后更新时间")
    novel_title: str = Field(default="", description="小说标题")
    total_chapters: int = Field(default=0, description="总章节数")


class ParticleLedger(BaseModel):
    items: Dict[str, Dict[str, Any]] = Field(default_factory=dict, description="物品账本")
    skills: Dict[str, Dict[str, Any]] = Field(default_factory=dict, description="技能账本")
    wealth: Dict[str, float] = Field(default_factory=dict, description="财富账本")
    other_resources: Dict[str, Any] = Field(default_factory=dict, description="其他资源")


class CharacterMatrix(BaseModel):
    characters: Dict[str, CharacterState] = Field(default_factory=dict, description="角色矩阵")
    relationship_graph: Dict[str, Dict[str, str]] = Field(default_factory=dict, description="关系图谱")
    faction_structure: Dict[str, List[str]] = Field(default_factory=dict, description="派系结构")


class ChapterSummariesIndex(BaseModel):
    summaries: Dict[int, ChapterSummary] = Field(default_factory=dict, description="章节摘要索引")
    total_word_count: int = Field(default=0, description="总字数")
    average_word_count: float = Field(default=0.0, description="平均字数")


class SubplotBoard(BaseModel):
    subplots: Dict[str, SubplotProgress] = Field(default_factory=dict, description="支线进度板")
    active_subplots: List[str] = Field(default_factory=list, description="活跃支线")
    completed_subplots: List[str] = Field(default_factory=list, description="已完成支线")


class EmotionalArcs(BaseModel):
    arcs: Dict[str, EmotionalArc] = Field(default_factory=dict, description="情感弧线")
    active_arcs: List[str] = Field(default_factory=list, description="活跃弧线")


class PendingHooks(BaseModel):
    hooks: Dict[str, PendingHook] = Field(default_factory=dict, description="伏笔池")
    pending_count: int = Field(default=0, description="待处理数量")
    resolved_count: int = Field(default=0, description="已解决数量")
    abandoned_count: int = Field(default=0, description="已放弃数量")
