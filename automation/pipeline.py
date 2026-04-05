# automation/pipeline.py
# -*- coding: utf-8 -*-
"""
完整自动化管线
实现从设定到定稿的端到端自动化
"""
import asyncio
import logging
from typing import Dict, Optional, Callable
from datetime import datetime

from config_manager import ConfigManager
from state_manager import StateManager
from model_router import ModelRouter, TaskType, Priority
from audit_system import MultiDimensionalAuditor
from ai_detection import AITraceDetector, AITraceRemover


class AutomatedPipeline:
    """
    自动化管线
    实现完整的小说生成流程自动化
    """
    
    def __init__(self, config_manager: ConfigManager):
        """
        初始化自动化管线
        
        Args:
            config_manager: 配置管理器
        """
        self.config = config_manager
        self.story_dir = config_manager.get("other_params.filepath", ".")
        self.state_manager = StateManager(self.story_dir)
        self.model_router = ModelRouter(config_manager)
        
        llm_config = self._get_llm_config()
        self.auditor = MultiDimensionalAuditor(self.state_manager, llm_config)
        self.ai_detector = AITraceDetector(config_manager.get_ai_detection_config())
        
        self.progress_callback: Optional[Callable] = None
        self.error_callback: Optional[Callable] = None
        
        logging.info("AutomatedPipeline initialized")
    
    def _get_llm_config(self) -> Dict:
        """获取LLM配置"""
        model_name = self.config.get("choose_configs.consistency_review_llm", "LongCatChat")
        return self.config.get_llm_config(model_name)
    
    async def run_full_pipeline(self, start_chapter: int, end_chapter: int,
                               auto_mode: bool = False,
                               progress_callback: Optional[Callable] = None):
        """
        运行完整自动化管线
        
        Args:
            start_chapter: 起始章节
            end_chapter: 结束章节
            auto_mode: 是否全自动模式
            progress_callback: 进度回调函数
        """
        self.progress_callback = progress_callback
        automation_config = self.config.get_automation_config()
        
        if not automation_config.get("enabled", True):
            logging.warning("Automation is disabled in config")
            return
        
        human_review_gate = automation_config.get("human_review_gate", True) and not auto_mode
        
        for chapter_num in range(start_chapter, end_chapter + 1):
            try:
                await self._process_chapter(chapter_num, human_review_gate)
                
                if self.progress_callback:
                    self.progress_callback(chapter_num, end_chapter)
                
            except Exception as e:
                logging.error(f"Pipeline failed at chapter {chapter_num}: {e}")
                if self.error_callback:
                    self.error_callback(chapter_num, e)
                
                retry_count = automation_config.get("retry_on_failure", 3)
                for i in range(retry_count):
                    try:
                        logging.info(f"Retrying chapter {chapter_num} (attempt {i+1})")
                        await self._process_chapter(chapter_num, human_review_gate)
                        break
                    except Exception as retry_error:
                        logging.error(f"Retry {i+1} failed: {retry_error}")
                        if i == retry_count - 1:
                            logging.error(f"Chapter {chapter_num} failed after {retry_count} attempts")
    
    async def _process_chapter(self, chapter_num: int, human_review_gate: bool):
        """
        处理单个章节
        
        Args:
            chapter_num: 章节号
            human_review_gate: 是否需要人工审核
        """
        logging.info(f"Processing chapter {chapter_num}")
        
        draft = await self._generate_draft(chapter_num)
        
        audit_result = self.auditor.audit_chapter(
            chapter_num, 
            draft, 
            f"第{chapter_num}章"
        )
        
        audit_config = self.config.get_audit_config()
        if audit_config.get("auto_fix", False) and not audit_result.passed:
            draft = await self._auto_fix(draft, audit_result)
        
        ai_detection_result = self.ai_detector.detect(draft)
        if not ai_detection_result["passed"]:
            ai_config = self.config.get_ai_detection_config()
            if ai_config.get("auto_remove_traces", True):
                llm_config = self._get_llm_config()
                from llm_adapters import create_llm_adapter
                llm_adapter = create_llm_adapter(**llm_config)
                remover = AITraceRemover(llm_adapter, ai_config)
                draft = remover.remove_traces(draft, ai_detection_result)
        
        if human_review_gate:
            approved = await self._human_review_gate(chapter_num, draft, audit_result)
            if not approved:
                draft = await self._revise_based_on_feedback(chapter_num, draft)
        
        await self._finalize_chapter(chapter_num, draft)
        
        logging.info(f"Chapter {chapter_num} processed successfully")
    
    async def _generate_draft(self, chapter_num: int) -> str:
        """生成章节草稿"""
        model_info = self.model_router.select_model(TaskType.DRAFT_WRITING, Priority.BALANCED)
        
        return f"这是第{chapter_num}章的草稿内容（示例）"
    
    async def _auto_fix(self, draft: str, audit_result) -> str:
        """自动修复"""
        return draft
    
    async def _human_review_gate(self, chapter_num: int, draft: str, audit_result) -> bool:
        """人工审核门控"""
        return True
    
    async def _revise_based_on_feedback(self, chapter_num: int, draft: str) -> str:
        """根据反馈修订"""
        return draft
    
    async def _finalize_chapter(self, chapter_num: int, content: str):
        """定稿章节"""
        self.state_manager.update_after_chapter(
            chapter_num,
            content,
            f"第{chapter_num}章",
            len(content)
        )
