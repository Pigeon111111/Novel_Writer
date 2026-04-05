# audit_system/auditor.py
# -*- coding: utf-8 -*-
"""
多维度审计引擎
对章节内容进行全面审计
"""
import logging
import time
from typing import List, Optional, Dict
from datetime import datetime

from .dimensions import AuditDimension, AuditCategory, Severity
from .result import AuditResult, AuditIssue
from state_manager import StateManager
from llm_adapters import create_llm_adapter


class MultiDimensionalAuditor:
    """
    多维度审计器
    对小说章节进行全面审计，覆盖33个维度
    """
    
    def __init__(self, state_manager: StateManager, llm_config: Dict):
        """
        初始化审计器
        
        Args:
            state_manager: 状态管理器
            llm_config: LLM配置
        """
        self.state_manager = state_manager
        self.llm_config = llm_config
        self.llm_adapter = create_llm_adapter(
            interface_format=llm_config.get("interface_format", "OpenAI"),
            base_url=llm_config.get("base_url"),
            model_name=llm_config.get("model_name"),
            api_key=llm_config.get("api_key"),
            temperature=0.3,
            max_tokens=4096,
            timeout=llm_config.get("timeout", 600)
        )
        
        logging.info("MultiDimensionalAuditor initialized")
    
    def audit_chapter(self, chapter_num: int, chapter_content: str,
                     chapter_title: str = "") -> AuditResult:
        """
        审计章节
        
        Args:
            chapter_num: 章节号
            chapter_content: 章节内容
            chapter_title: 章节标题
            
        Returns:
            审计结果
        """
        start_time = time.time()
        
        logging.info(f"Starting audit for chapter {chapter_num}")
        
        result = AuditResult(
            chapter_number=chapter_num,
            audit_time=datetime.now()
        )
        
        current_state = self.state_manager.load_state("current_state")
        character_matrix = self.state_manager.load_state("character_matrix")
        pending_hooks = self.state_manager.load_state("pending_hooks")
        chapter_summaries = self.state_manager.load_state("chapter_summaries")
        
        for category in AuditCategory:
            category_issues = self._audit_category(
                category, chapter_num, chapter_content,
                current_state, character_matrix, pending_hooks, chapter_summaries
            )
            
            for issue in category_issues:
                result.add_issue(issue)
        
        result.duration_seconds = time.time() - start_time
        
        logging.info(
            f"Audit completed for chapter {chapter_num}: "
            f"{result.total_issues} issues found, "
            f"quality score: {result.quality_score:.1f}"
        )
        
        return result
    
    def _audit_category(self, category: AuditCategory, chapter_num: int,
                       chapter_content: str, current_state, character_matrix,
                       pending_hooks, chapter_summaries) -> List[AuditIssue]:
        """
        审计指定类别
        
        Args:
            category: 审计类别
            chapter_num: 章节号
            chapter_content: 章节内容
            current_state: 当前状态
            character_matrix: 角色矩阵
            pending_hooks: 待处理伏笔
            chapter_summaries: 章节摘要
            
        Returns:
            问题列表
        """
        issues = []
        dimensions = AuditDimension.get_by_category(category)
        
        for dimension in dimensions:
            try:
                dimension_issues = self._audit_dimension(
                    dimension, chapter_num, chapter_content,
                    current_state, character_matrix, pending_hooks, chapter_summaries
                )
                issues.extend(dimension_issues)
            except Exception as e:
                logging.error(f"Failed to audit dimension {dimension.name}: {e}")
        
        return issues
    
    def _audit_dimension(self, dimension: AuditDimension, chapter_num: int,
                        chapter_content: str, current_state, character_matrix,
                        pending_hooks, chapter_summaries) -> List[AuditIssue]:
        """
        审计单个维度
        
        Args:
            dimension: 审计维度
            chapter_num: 章节号
            chapter_content: 章节内容
            current_state: 当前状态
            character_matrix: 角色矩阵
            pending_hooks: 待处理伏笔
            chapter_summaries: 章节摘要
            
        Returns:
            问题列表
        """
        audit_method_name = f"_audit_{dimension.name.lower()}"
        audit_method = getattr(self, audit_method_name, None)
        
        if audit_method:
            return audit_method(
                chapter_num, chapter_content,
                current_state, character_matrix, pending_hooks, chapter_summaries
            )
        else:
            return self._generic_llm_audit(
                dimension, chapter_num, chapter_content,
                current_state, character_matrix, pending_hooks
            )
    
    def _audit_plot_foreshadow(self, chapter_num: int, chapter_content: str,
                               current_state, character_matrix, pending_hooks,
                               chapter_summaries) -> List[AuditIssue]:
        """
        审计伏笔断裂
        
        Args:
            chapter_num: 章节号
            chapter_content: 章节内容
            current_state: 当前状态
            character_matrix: 角色矩阵
            pending_hooks: 待处理伏笔
            chapter_summaries: 章节摘要
            
        Returns:
            问题列表
        """
        issues = []
        
        for hook_id, hook in pending_hooks.hooks.items():
            if hook.status == "pending" and hook.expected_resolve_chapter:
                if chapter_num >= hook.expected_resolve_chapter:
                    issues.append(AuditIssue(
                        dimension=AuditDimension.PLOT_FORESHADOW,
                        severity=Severity.MAJOR,
                        title=f"伏笔未回收：{hook.description[:30]}",
                        description=f"伏笔'{hook.description}'应在第{hook.expected_resolve_chapter}章回收，但当前仍未处理",
                        location=f"第{chapter_num}章",
                        suggestion="考虑在本章回收该伏笔，或调整回收计划",
                        auto_fixable=False
                    ))
        
        return issues
    
    def _audit_character_appearance(self, chapter_num: int, chapter_content: str,
                                    current_state, character_matrix, pending_hooks,
                                    chapter_summaries) -> List[AuditIssue]:
        """
        审计角色出场矛盾
        
        Args:
            chapter_num: 章节号
            chapter_content: 章节内容
            current_state: 当前状态
            character_matrix: 角色矩阵
            pending_hooks: 待处理伏笔
            chapter_summaries: 章节摘要
            
        Returns:
            问题列表
        """
        issues = []
        
        for char_name, character in character_matrix.characters.items():
            if char_name in chapter_content:
                if character.last_appearance_chapter > 0:
                    gap = chapter_num - character.last_appearance_chapter
                    if gap > 10 and character.status == "alive":
                        issues.append(AuditIssue(
                            dimension=AuditDimension.CHARACTER_APPEARANCE,
                            severity=Severity.MINOR,
                            title=f"角色长期未出场：{char_name}",
                            description=f"角色'{char_name}'已{gap}章未出场，最后出现在第{character.last_appearance_chapter}章",
                            location=f"第{chapter_num}章",
                            suggestion="考虑安排角色出场或说明其去向",
                            auto_fixable=False
                        ))
        
        return issues
    
    def _generic_llm_audit(self, dimension: AuditDimension, chapter_num: int,
                          chapter_content: str, current_state, character_matrix,
                          pending_hooks) -> List[AuditIssue]:
        """
        使用LLM进行通用审计
        
        Args:
            dimension: 审计维度
            chapter_num: 章节号
            chapter_content: 章节内容
            current_state: 当前状态
            character_matrix: 角色矩阵
            pending_hooks: 待处理伏笔
            
        Returns:
            问题列表
        """
        prompt = self._build_audit_prompt(
            dimension, chapter_num, chapter_content,
            current_state, character_matrix, pending_hooks
        )
        
        try:
            response = self.llm_adapter.invoke(prompt)
            return self._parse_audit_response(dimension, response)
        except Exception as e:
            logging.error(f"LLM audit failed for {dimension.name}: {e}")
            return []
    
    def _build_audit_prompt(self, dimension: AuditDimension, chapter_num: int,
                           chapter_content: str, current_state, character_matrix,
                           pending_hooks) -> str:
        """
        构建审计提示词
        
        Args:
            dimension: 审计维度
            chapter_num: 章节号
            chapter_content: 章节内容
            current_state: 当前状态
            character_matrix: 角色矩阵
            pending_hooks: 待处理伏笔
            
        Returns:
            提示词
        """
        character_info = "\n".join([
            f"- {name}: {char.location}, 状态: {char.status}"
            for name, char in list(character_matrix.characters.items())[:10]
        ])
        
        prompt = f"""
请检查以下章节是否存在【{dimension.display_name}】问题。

审计维度：{dimension.display_name}
问题描述：{dimension.description}

章节信息：
- 章节号：第{chapter_num}章
- 内容长度：{len(chapter_content)}字

角色信息（部分）：
{character_info}

章节内容：
{chapter_content[:2000]}

请按以下格式列出发现的问题（如果没有问题，请返回"无问题"）：

【问题1】
严重程度：critical/major/minor/suggestion
标题：简短描述
描述：详细说明问题所在
位置：具体位置（如"第X段"）
建议：修复建议

【问题2】
...

请开始审计：
"""
        return prompt
    
    def _parse_audit_response(self, dimension: AuditDimension,
                             response: str) -> List[AuditIssue]:
        """
        解析审计响应
        
        Args:
            dimension: 审计维度
            response: LLM响应
            
        Returns:
            问题列表
        """
        issues = []
        
        if "无问题" in response or "未发现" in response:
            return issues
        
        import re
        
        problem_blocks = re.split(r'【问题\d+】', response)
        
        for block in problem_blocks[1:]:
            if not block.strip():
                continue
            
            severity = Severity.MINOR
            if "critical" in block.lower() or "严重" in block:
                severity = Severity.CRITICAL
            elif "major" in block.lower() or "重要" in block:
                severity = Severity.MAJOR
            elif "suggestion" in block.lower() or "建议" in block:
                severity = Severity.SUGGESTION
            
            title_match = re.search(r'标题[：:]\s*(.+)', block)
            desc_match = re.search(r'描述[：:]\s*(.+)', block, re.DOTALL)
            loc_match = re.search(r'位置[：:]\s*(.+)', block)
            sug_match = re.search(r'建议[：:]\s*(.+)', block)
            
            issue = AuditIssue(
                dimension=dimension,
                severity=severity,
                title=title_match.group(1).strip() if title_match else "未命名问题",
                description=desc_match.group(1).strip() if desc_match else block.strip(),
                location=loc_match.group(1).strip() if loc_match else "",
                suggestion=sug_match.group(1).strip() if sug_match else "",
                auto_fixable=False
            )
            
            issues.append(issue)
        
        return issues
