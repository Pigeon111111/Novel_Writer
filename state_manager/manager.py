# state_manager/manager.py
# -*- coding: utf-8 -*-
"""
状态管理器核心实现
"""
import os
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime

from .models import (
    CurrentState,
    ParticleLedger,
    PendingHooks,
    ChapterSummariesIndex,
    SubplotBoard,
    EmotionalArcs,
    CharacterMatrix,
    CharacterState,
    PendingHook,
    ChapterSummary,
    HookStatus
)


class StateManager:
    """
    状态管理器
    负责管理小说创作过程中的所有状态文件
    """
    
    STATE_FILES = {
        "current_state": CurrentState,
        "particle_ledger": ParticleLedger,
        "pending_hooks": PendingHooks,
        "chapter_summaries": ChapterSummariesIndex,
        "subplot_board": SubplotBoard,
        "emotional_arcs": EmotionalArcs,
        "character_matrix": CharacterMatrix
    }
    
    def __init__(self, story_dir: str):
        """
        初始化状态管理器
        
        Args:
            story_dir: 小说项目目录路径
        """
        self.story_dir = Path(story_dir)
        self.state_dir = self.story_dir / "state"
        self.state_dir.mkdir(parents=True, exist_ok=True)
        
        self._cache: Dict[str, Any] = {}
        
        logging.info(f"StateManager initialized with story_dir: {story_dir}")
    
    def load_state(self, state_type: str, use_cache: bool = True) -> Any:
        """
        加载指定类型的状态
        
        Args:
            state_type: 状态类型（current_state, particle_ledger等）
            use_cache: 是否使用缓存
            
        Returns:
            对应的状态模型实例
        """
        if state_type not in self.STATE_FILES:
            raise ValueError(f"Unknown state type: {state_type}")
        
        if use_cache and state_type in self._cache:
            return self._cache[state_type]
        
        file_path = self.state_dir / f"{state_type}.json"
        
        if not file_path.exists():
            state_instance = self._get_default_state(state_type)
        else:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    state_class = self.STATE_FILES[state_type]
                    state_instance = state_class(**data)
            except Exception as e:
                logging.error(f"Failed to load state {state_type}: {e}")
                state_instance = self._get_default_state(state_type)
        
        if use_cache:
            self._cache[state_type] = state_instance
        
        return state_instance
    
    def save_state(self, state_type: str, state: Any, update_time: bool = True):
        """
        保存状态到JSON文件
        
        Args:
            state_type: 状态类型
            state: 状态模型实例
            update_time: 是否更新时间戳
        """
        if state_type not in self.STATE_FILES:
            raise ValueError(f"Unknown state type: {state_type}")
        
        file_path = self.state_dir / f"{state_type}.json"
        
        if update_time and hasattr(state, 'last_updated'):
            state.last_updated = datetime.now()
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(
                    state.model_dump(),
                    f,
                    ensure_ascii=False,
                    indent=2,
                    default=str
                )
            
            if state_type in self._cache:
                self._cache[state_type] = state
            
            logging.info(f"State {state_type} saved successfully")
        except Exception as e:
            logging.error(f"Failed to save state {state_type}: {e}")
            raise
    
    def _get_default_state(self, state_type: str) -> Any:
        """获取默认状态实例"""
        state_class = self.STATE_FILES[state_type]
        return state_class()
    
    def update_after_chapter(self, chapter_num: int, chapter_content: str,
                            chapter_title: str = "", word_count: int = 0):
        """
        章节定稿后更新所有状态
        
        Args:
            chapter_num: 章节号
            chapter_content: 章节内容
            chapter_title: 章节标题
            word_count: 字数
        """
        logging.info(f"Updating states after chapter {chapter_num}")
        
        current_state = self.load_state("current_state")
        current_state.current_chapter = chapter_num
        current_state.last_updated = datetime.now()
        self.save_state("current_state", current_state)
        
        chapter_summaries = self.load_state("chapter_summaries")
        summary = ChapterSummary(
            chapter_number=chapter_num,
            title=chapter_title,
            word_count=word_count,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        chapter_summaries.summaries[chapter_num] = summary
        chapter_summaries.total_word_count += word_count
        chapter_summaries.average_word_count = (
            chapter_summaries.total_word_count / len(chapter_summaries.summaries)
        )
        self.save_state("chapter_summaries", chapter_summaries)
        
        logging.info(f"All states updated for chapter {chapter_num}")
    
    def add_character(self, character_name: str, character_data: Optional[Dict] = None):
        """
        添加角色
        
        Args:
            character_name: 角色名称
            character_data: 角色数据
        """
        character_matrix = self.load_state("character_matrix")
        
        if character_name in character_matrix.characters:
            logging.warning(f"Character {character_name} already exists")
            return
        
        character = CharacterState(
            name=character_name,
            **(character_data or {})
        )
        
        character_matrix.characters[character_name] = character
        self.save_state("character_matrix", character_matrix)
        
        logging.info(f"Character {character_name} added")
    
    def update_character_state(self, character_name: str, updates: Dict[str, Any]):
        """
        更新角色状态
        
        Args:
            character_name: 角色名称
            updates: 更新数据
        """
        character_matrix = self.load_state("character_matrix")
        
        if character_name not in character_matrix.characters:
            logging.warning(f"Character {character_name} not found, creating new")
            self.add_character(character_name, updates)
            return
        
        character = character_matrix.characters[character_name]
        for key, value in updates.items():
            if hasattr(character, key):
                setattr(character, key, value)
        
        self.save_state("character_matrix", character_matrix)
        logging.info(f"Character {character_name} updated")
    
    def plant_hook(self, hook_id: str, description: str, planted_chapter: int,
                   expected_resolve_chapter: Optional[int] = None,
                   priority: str = "medium",
                   related_characters: Optional[List[str]] = None):
        """
        埋下伏笔
        
        Args:
            hook_id: 伏笔ID
            description: 伏笔描述
            planted_chapter: 埋下章节
            expected_resolve_chapter: 预期回收章节
            priority: 优先级
            related_characters: 相关角色
        """
        pending_hooks = self.load_state("pending_hooks")
        
        hook = PendingHook(
            hook_id=hook_id,
            description=description,
            planted_chapter=planted_chapter,
            expected_resolve_chapter=expected_resolve_chapter,
            priority=priority,
            related_characters=related_characters or []
        )
        
        pending_hooks.hooks[hook_id] = hook
        pending_hooks.pending_count += 1
        
        self.save_state("pending_hooks", pending_hooks)
        logging.info(f"Hook {hook_id} planted at chapter {planted_chapter}")
    
    def resolve_hook(self, hook_id: str, resolved_chapter: int):
        """
        回收伏笔
        
        Args:
            hook_id: 伏笔ID
            resolved_chapter: 回收章节
        """
        pending_hooks = self.load_state("pending_hooks")
        
        if hook_id not in pending_hooks.hooks:
            logging.warning(f"Hook {hook_id} not found")
            return
        
        hook = pending_hooks.hooks[hook_id]
        hook.status = HookStatus.RESOLVED
        hook.resolved_chapter = resolved_chapter
        
        pending_hooks.pending_count -= 1
        pending_hooks.resolved_count += 1
        
        self.save_state("pending_hooks", pending_hooks)
        logging.info(f"Hook {hook_id} resolved at chapter {resolved_chapter}")
    
    def get_pending_hooks(self, priority: Optional[str] = None) -> List[PendingHook]:
        """
        获取待处理的伏笔
        
        Args:
            priority: 优先级过滤（可选）
            
        Returns:
            待处理伏笔列表
        """
        pending_hooks = self.load_state("pending_hooks")
        
        hooks = [
            hook for hook in pending_hooks.hooks.values()
            if hook.status == HookStatus.PENDING
        ]
        
        if priority:
            hooks = [hook for hook in hooks if hook.priority == priority]
        
        return sorted(hooks, key=lambda h: h.planted_chapter)
    
    def get_character_by_name(self, character_name: str) -> Optional[CharacterState]:
        """
        根据名称获取角色
        
        Args:
            character_name: 角色名称
            
        Returns:
            角色状态实例
        """
        character_matrix = self.load_state("character_matrix")
        return character_matrix.characters.get(character_name)
    
    def get_chapter_summary(self, chapter_num: int) -> Optional[ChapterSummary]:
        """
        获取章节摘要
        
        Args:
            chapter_num: 章节号
            
        Returns:
            章节摘要实例
        """
        chapter_summaries = self.load_state("chapter_summaries")
        return chapter_summaries.summaries.get(chapter_num)
    
    def export_all_states(self) -> Dict[str, Any]:
        """
        导出所有状态
        
        Returns:
            所有状态的字典
        """
        all_states = {}
        for state_type in self.STATE_FILES.keys():
            state = self.load_state(state_type)
            all_states[state_type] = state.model_dump()
        return all_states
    
    def import_states(self, states_data: Dict[str, Any]):
        """
        导入状态数据
        
        Args:
            states_data: 状态数据字典
        """
        for state_type, data in states_data.items():
            if state_type in self.STATE_FILES:
                state_class = self.STATE_FILES[state_type]
                state = state_class(**data)
                self.save_state(state_type, state)
        
        logging.info("States imported successfully")
    
    def clear_cache(self):
        """清空缓存"""
        self._cache.clear()
        logging.info("State cache cleared")
    
    def backup_states(self, backup_dir: str):
        """
        备份状态文件
        
        Args:
            backup_dir: 备份目录
        """
        backup_path = Path(backup_dir)
        backup_path.mkdir(parents=True, exist_ok=True)
        
        for state_type in self.STATE_FILES.keys():
            src_file = self.state_dir / f"{state_type}.json"
            if src_file.exists():
                dst_file = backup_path / f"{state_type}.json"
                with open(src_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                with open(dst_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        
        logging.info(f"States backed up to {backup_dir}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取统计信息
        
        Returns:
            统计信息字典
        """
        current_state = self.load_state("current_state")
        character_matrix = self.load_state("character_matrix")
        pending_hooks = self.load_state("pending_hooks")
        chapter_summaries = self.load_state("chapter_summaries")
        
        return {
            "current_chapter": current_state.current_chapter,
            "total_chapters": current_state.total_chapters,
            "total_characters": len(character_matrix.characters),
            "active_characters": len(current_state.active_characters),
            "pending_hooks": pending_hooks.pending_count,
            "resolved_hooks": pending_hooks.resolved_count,
            "total_word_count": chapter_summaries.total_word_count,
            "average_word_count": chapter_summaries.average_word_count
        }
