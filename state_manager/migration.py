# state_manager/migration.py
# -*- coding: utf-8 -*-
"""
状态迁移工具
将旧的txt状态文件迁移到新的JSON格式
"""
import os
import re
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from .models import (
    CurrentState,
    CharacterMatrix,
    CharacterState,
    ChapterSummariesIndex,
    ChapterSummary,
    PendingHooks
)
from .manager import StateManager


class StateMigrator:
    """
    状态迁移器
    负责将旧的txt格式状态文件迁移到新的JSON格式
    """
    
    def __init__(self, story_dir: str):
        """
        初始化迁移器
        
        Args:
            story_dir: 小说项目目录
        """
        self.story_dir = Path(story_dir)
        self.state_manager = StateManager(story_dir)
        
        logging.info(f"StateMigrator initialized for {story_dir}")
    
    def migrate_all(self):
        """
        迁移所有状态文件
        """
        logging.info("Starting full state migration...")
        
        self.migrate_character_state()
        self.migrate_global_summary()
        self.migrate_novel_setting()
        
        logging.info("Full state migration completed")
    
    def migrate_character_state(self):
        """
        迁移角色状态文件（character_state.txt）
        """
        old_file = self.story_dir / "character_state.txt"
        
        if not old_file.exists():
            logging.info("No character_state.txt found, skipping")
            return
        
        logging.info("Migrating character_state.txt...")
        
        try:
            with open(old_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            characters = self._parse_character_state(content)
            
            character_matrix = self.state_manager.load_state("character_matrix")
            
            for char_name, char_data in characters.items():
                character = CharacterState(
                    name=char_name,
                    location=char_data.get("location", "未知"),
                    status=char_data.get("status", "alive"),
                    emotional_state=char_data.get("emotional_state", "平静"),
                    last_appearance_chapter=char_data.get("last_chapter", 0),
                    background=char_data.get("background", ""),
                    personality=char_data.get("personality", [])
                )
                character_matrix.characters[char_name] = character
            
            self.state_manager.save_state("character_matrix", character_matrix)
            
            backup_file = old_file.with_suffix('.txt.backup')
            old_file.rename(backup_file)
            
            logging.info(f"Character state migrated successfully. Backup saved to {backup_file}")
            
        except Exception as e:
            logging.error(f"Failed to migrate character_state.txt: {e}")
            raise
    
    def migrate_global_summary(self):
        """
        迁移全局摘要文件（global_summary.txt）
        """
        old_file = self.story_dir / "global_summary.txt"
        
        if not old_file.exists():
            logging.info("No global_summary.txt found, skipping")
            return
        
        logging.info("Migrating global_summary.txt...")
        
        try:
            with open(old_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            summaries = self._parse_global_summary(content)
            
            chapter_summaries = self.state_manager.load_state("chapter_summaries")
            
            for chapter_num, summary_data in summaries.items():
                summary = ChapterSummary(
                    chapter_number=chapter_num,
                    title=summary_data.get("title", ""),
                    summary=summary_data.get("summary", ""),
                    key_events=summary_data.get("key_events", []),
                    word_count=summary_data.get("word_count", 0),
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                chapter_summaries.summaries[chapter_num] = summary
                chapter_summaries.total_word_count += summary.word_count
            
            if chapter_summaries.summaries:
                chapter_summaries.average_word_count = (
                    chapter_summaries.total_word_count / len(chapter_summaries.summaries)
                )
            
            self.state_manager.save_state("chapter_summaries", chapter_summaries)
            
            backup_file = old_file.with_suffix('.txt.backup')
            old_file.rename(backup_file)
            
            logging.info(f"Global summary migrated successfully. Backup saved to {backup_file}")
            
        except Exception as e:
            logging.error(f"Failed to migrate global_summary.txt: {e}")
            raise
    
    def migrate_novel_setting(self):
        """
        迁移小说设定文件（Novel_setting.txt）
        """
        old_file = self.story_dir / "Novel_setting.txt"
        
        if not old_file.exists():
            logging.info("No Novel_setting.txt found, skipping")
            return
        
        logging.info("Migrating Novel_setting.txt...")
        
        try:
            with open(old_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            current_state = self.state_manager.load_state("current_state")
            
            world_info = self._parse_novel_setting(content)
            current_state.world_state = world_info
            
            self.state_manager.save_state("current_state", current_state)
            
            backup_file = old_file.with_suffix('.txt.backup')
            old_file.rename(backup_file)
            
            logging.info(f"Novel setting migrated successfully. Backup saved to {backup_file}")
            
        except Exception as e:
            logging.error(f"Failed to migrate Novel_setting.txt: {e}")
            raise
    
    def _parse_character_state(self, content: str) -> Dict[str, Dict]:
        """
        解析角色状态文本
        
        Args:
            content: 文本内容
            
        Returns:
            角色状态字典
        """
        characters = {}
        
        char_pattern = r'【角色[：:]\s*(.+?)】\n(.*?)(?=【角色[：:]|$)'
        matches = re.findall(char_pattern, content, re.DOTALL)
        
        for char_name, char_content in matches:
            char_data = {}
            
            lines = char_content.strip().split('\n')
            for line in lines:
                if '：' in line or ':' in line:
                    key, value = re.split(r'[：:]', line, 1)
                    key = key.strip()
                    value = value.strip()
                    
                    if key == "当前位置":
                        char_data["location"] = value
                    elif key == "状态":
                        char_data["status"] = value
                    elif key == "情感状态":
                        char_data["emotional_state"] = value
                    elif key == "最后出场章节":
                        try:
                            char_data["last_chapter"] = int(value)
                        except:
                            char_data["last_chapter"] = 0
                    elif key == "性格特点":
                        char_data["personality"] = [p.strip() for p in value.split('、') if p.strip()]
                    elif key == "背景故事":
                        char_data["background"] = value
            
            characters[char_name.strip()] = char_data
        
        return characters
    
    def _parse_global_summary(self, content: str) -> Dict[int, Dict]:
        """
        解析全局摘要文本
        
        Args:
            content: 文本内容
            
        Returns:
            章节摘要字典
        """
        summaries = {}
        
        chapter_pattern = r'第(\d+)章[：:]\s*(.+?)(?=第\d+章|$)'
        matches = re.findall(chapter_pattern, content, re.DOTALL)
        
        for chapter_num_str, chapter_content in matches:
            chapter_num = int(chapter_num_str)
            summary_data = {}
            
            lines = chapter_content.strip().split('\n')
            summary_text = []
            key_events = []
            
            for line in lines:
                line = line.strip()
                if line.startswith('关键事件：') or line.startswith('关键事件:'):
                    events_str = line.split('：', 1)[-1].split(':', 1)[-1]
                    key_events = [e.strip() for e in events_str.split('、') if e.strip()]
                elif line:
                    summary_text.append(line)
            
            summary_data["summary"] = '\n'.join(summary_text)
            summary_data["key_events"] = key_events
            
            summaries[chapter_num] = summary_data
        
        return summaries
    
    def _parse_novel_setting(self, content: str) -> Dict[str, str]:
        """
        解析小说设定文本
        
        Args:
            content: 文本内容
            
        Returns:
            世界设定字典
        """
        world_info = {}
        
        sections = {
            "世界观": "world_view",
            "力量体系": "power_system",
            "主要势力": "main_factions",
            "地理环境": "geography",
            "历史背景": "history"
        }
        
        for section_name, key in sections.items():
            pattern = rf'【{section_name}[：:]\s*\】\n(.*?)(?=【|$)'
            match = re.search(pattern, content, re.DOTALL)
            if match:
                world_info[key] = match.group(1).strip()
        
        return world_info
    
    def rollback_migration(self):
        """
        回滚迁移，恢复旧的txt文件
        """
        logging.info("Rolling back migration...")
        
        backup_files = list(self.story_dir.glob("*.txt.backup"))
        
        for backup_file in backup_files:
            original_file = backup_file.with_suffix('')
            backup_file.rename(original_file)
            logging.info(f"Restored {original_file}")
        
        state_dir = self.story_dir / "state"
        if state_dir.exists():
            import shutil
            shutil.rmtree(state_dir)
            logging.info("Removed state directory")
        
        logging.info("Migration rollback completed")
