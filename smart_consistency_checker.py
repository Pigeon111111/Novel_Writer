# smart_consistency_checker.py
# -*- coding: utf-8 -*-
"""
智能一致性检查系统
提供自动化的章节一致性检查和质量评估
"""

import os
import logging
import re
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, as_completed

from llm_adapters import create_llm_adapter
from consistency_checker import check_consistency

logging.basicConfig(
    filename='app.log',
    filemode='a',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


class IssueType(Enum):
    """问题类型枚举"""
    CHARACTER_INCONSISTENCY = "character_inconsistency"
    PLOT_INCONSISTENCY = "plot_inconsistency"
    WORLD_BUILDING_INCONSISTENCY = "world_building_inconsistency"
    TIMELINE_INCONSISTENCY = "timeline_inconsistency"
    LOGICAL_CONTRADICTION = "logical_contradiction"
    REPETITION = "repetition"
    PACING_ISSUE = "pacing_issue"
    STYLE_INCONSISTENCY = "style_inconsistency"


class Severity(Enum):
    """严重程度枚举"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ConsistencyIssue:
    """一致性问�据类"""
    issue_id: str
    issue_type: IssueType
    severity: Severity
    chapter: int
    description: str
    location: Optional[str] = None
    suggested_fix: Optional[str] = None
    auto_fixable: bool = False


@dataclass
class CheckResult:
    """检查结果数据类"""
    chapter: int
    issues: List[ConsistencyIssue]
    overall_score: float
    quality_score: float
    readability_score: float
    suggestions: List[str]


class SmartConsistencyChecker:
    """
    智能一致性检查系统
    提供自动化的章节一致性检查和质量评估
    """
    
    def __init__(self, config: Dict):
        """
        初始化智能一致性检查器
        
        Args:
            config: 配置字典
        """
        self.config = config
        self.llm_adapter = None
        self.checkers = []
        
        # 初始化LLM适配器
        self._init_llm_adapter()
        
        # 注册检查器
        self._register_checkers()
        
        logging.info("SmartConsistencyChecker initialized successfully")
    
    def _init_llm_adapter(self):
        """初始化LLM适配器"""
        try:
            self.llm_adapter = create_llm_adapter(
                interface_format=self.config.get("interface_format", "OpenAI"),
                base_url=self.config.get("base_url", ""),
                model_name=self.config.get("model_name", ""),
                api_key=self.config.get("api_key", ""),
                temperature=0.3,  # 使用较低温度进行一致性检查
                max_tokens=2048,
                timeout=300
            )
            logging.info("LLM adapter initialized for consistency checking")
        except Exception as e:
            logging.error(f"Failed to initialize LLM adapter: {e}")
            raise
    
    def _register_checkers(self):
        """注册各种检查器"""
        self.checkers = [
            CharacterConsistencyChecker(),
            PlotConsistencyChecker(),
            WorldBuildingConsistencyChecker(),
            TimelineConsistencyChecker(),
            LogicalConsistencyChecker(),
            QualityAssessmentChecker()
        ]
        logging.info(f"Registered {len(self.checkers)} checkers")
    
    def check_chapter(self, chapter_num: int, chapter_content: str, context: Dict) -> CheckResult:
        """
        检查单个章节
        
        Args:
            chapter_num: 章节号
            chapter_content: 章节内容
            context: 上下文信息
            
        Returns:
            检查结果
        """
        logging.info(f"Checking chapter {chapter_num}")
        
        issues = []
        suggestions = []
        
        # 执行所有检查器
        for checker in self.checkers:
            try:
                checker_issues = checker.check(chapter_num, chapter_content, context)
                issues.extend(checker_issues)
            except Exception as e:
                logging.error(f"Checker {checker.__class__.__name__} failed: {e}")
        
        # 计算评分
        overall_score = self._calculate_overall_score(issues)
        quality_score = self._calculate_quality_score(chapter_content)
        readability_score = self._calculate_readability_score(chapter_content)
        
        # 生成建议
        suggestions = self._generate_suggestions(issues, chapter_content)
        
        return CheckResult(
            chapter=chapter_num,
            issues=issues,
            overall_score=overall_score,
            quality_score=quality_score,
            readability_score=readability_score,
            suggestions=suggestions
        )
    
    def batch_check_chapters(self, chapters: Dict[int, str], context: Dict) -> Dict[int, CheckResult]:
        """
        批量检查多个章节
        
        Args:
            chapters: 章节映射（章节号 -> 内容）
            context: 上下文信息
            
        Returns:
            检查结果映射
        """
        logging.info(f"Batch checking {len(chapters)} chapters")
        
        results = {}
        
        # 使用线程池并行检查
        with ThreadPoolExecutor(max_workers=2) as executor:
            future_to_chapter = {}
            
            for chapter_num, content in chapters.items():
                future = executor.submit(self.check_chapter, chapter_num, content, context)
                future_to_chapter[future] = chapter_num
            
            for future in as_completed(future_to_chapter):
                chapter_num = future_to_chapter[future]
                try:
                    result = future.result(timeout=300)
                    results[chapter_num] = result
                except Exception as e:
                    logging.error(f"Check failed for chapter {chapter_num}: {e}")
                    # 创建错误结果
                    results[chapter_num] = CheckResult(
                        chapter=chapter_num,
                        issues=[ConsistencyIssue(
                            issue_id=f"error_{chapter_num}",
                            issue_type=IssueType.LOGICAL_CONTRADICTION,
                            severity=Severity.HIGH,
                            chapter=chapter_num,
                            description=f"检查过程出错: {str(e)}"
                        )],
                        overall_score=0.0,
                        quality_score=0.0,
                        readability_score=0.0,
                        suggestions=["请检查章节内容格式是否正确"]
                    )
        
        return results
    
    def _calculate_overall_score(self, issues: List[ConsistencyIssue]) -> float:
        """计算总体评分"""
        if not issues:
            return 100.0
        
        # 根据问题严重程度计算扣分
        penalty = 0
        for issue in issues:
            if issue.severity == Severity.CRITICAL:
                penalty += 20
            elif issue.severity == Severity.HIGH:
                penalty += 10
            elif issue.severity == Severity.MEDIUM:
                penalty += 5
            elif issue.severity == Severity.LOW:
                penalty += 2
        
        return max(0, 100 - penalty)
    
    def _calculate_quality_score(self, content: str) -> float:
        """计算质量评分"""
        score = 50  # 基础分
        
        # 长度检查
        length = len(content)
        if 3000 <= length <= 5000:
            score += 20
        elif 2000 <= length < 3000:
            score += 10
        
        # 多样性检查（简化的实现）
        unique_words = len(set(content.split()))
        total_words = len(content.split())
        if total_words > 0:
            diversity_ratio = unique_words / total_words
            if diversity_ratio > 0.5:
                score += 15
            elif diversity_ratio > 0.3:
                score += 5
        
        # 结构检查
        if "第" in content and "章" in content:
            score += 10
        
        # 对话比例（简化的实现）
        dialogue_lines = len([line for line in content.split('\n') if '"' in line or '：' in line])
        total_lines = len(content.split('\n'))
        if total_lines > 0:
            dialogue_ratio = dialogue_lines / total_lines
            if 0.2 <= dialogue_ratio <= 0.6:
                score += 5
        
        return min(100, score)
    
    def _calculate_readability_score(self, content: str) -> float:
        """计算可读性评分"""
        score = 50  # 基础分
        
        # 句子长度检查
        sentences = re.split(r'[。！？]', content)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if sentences:
            avg_sentence_length = sum(len(s) for s in sentences) / len(sentences)
            if 10 <= avg_sentence_length <= 30:
                score += 20
            elif 5 <= avg_sentence_length < 10:
                score += 10
        
        # 段落结构
        paragraphs = content.split('\n\n')
        if 3 <= len(paragraphs) <= 10:
            score += 15
        elif len(paragraphs) > 0:
            score += 5
        
        # 连贯性检查（简化的实现）
        transition_words = ['然后', '接着', '但是', '因此', '所以', '然而']
        transition_count = sum(content.count(word) for word in transition_words)
        if transition_count >= 3:
            score += 10
        elif transition_count >= 1:
            score += 5
        
        return min(100, score)
    
    def _generate_suggestions(self, issues: List[ConsistencyIssue], content: str) -> List[str]:
        """生成改进建议"""
        suggestions = []
        
        # 根据问题类型生成建议
        issue_types = [issue.issue_type for issue in issues]
        
        if IssueType.CHARACTER_INCONSISTENCY in issue_types:
            suggestions.append("检查角色行为和对话是否符合设定")
        
        if IssueType.PLOT_INCONSISTENCY in issue_types:
            suggestions.append("确保剧情发展逻辑连贯，避免突兀转折")
        
        if IssueType.REPETITION in issue_types:
            suggestions.append("减少重复描述，增加内容多样性")
        
        if IssueType.PACING_ISSUE in issue_types:
            suggestions.append("调整叙事节奏，避免过快或过慢")
        
        # 基于内容分析的建议
        if len(content) < 2000:
            suggestions.append("章节内容较短，建议增加细节描写")
        elif len(content) > 6000:
            suggestions.append("章节内容较长，建议适当精简或分章")
        
        # 对话比例建议
        dialogue_lines = len([line for line in content.split('\n') if '"' in line])
        total_lines = len(content.split('\n'))
        if total_lines > 0:
            dialogue_ratio = dialogue_lines / total_lines
            if dialogue_ratio < 0.1:
                suggestions.append("增加角色对话，提升生动性")
            elif dialogue_ratio > 0.8:
                suggestions.append("减少纯对话，增加叙述和描写")
        
        return suggestions
    
    def auto_fix_simple_issues(self, content: str, issues: List[ConsistencyIssue]) -> Tuple[str, List[ConsistencyIssue]]:
        """
        自动修复简单问题
        
        Args:
            content: 原始内容
            issues: 问题列表
            
        Returns:
            修复后的内容和未修复的问题
        """
        fixed_content = content
        remaining_issues = []
        
        for issue in issues:
            if issue.auto_fixable:
                # 简化的自动修复逻辑
                if issue.issue_type == IssueType.REPETITION:
                    # 尝试删除重复段落
                    fixed_content = self._remove_repetition(fixed_content)
                    logging.info(f"Auto-fixed repetition issue: {issue.issue_id}")
                else:
                    remaining_issues.append(issue)
            else:
                remaining_issues.append(issue)
        
        return fixed_content, remaining_issues
    
    def _remove_repetition(self, content: str) -> str:
        """移除重复内容（简化实现）"""
        paragraphs = content.split('\n\n')
        unique_paragraphs = []
        seen = set()
        
        for para in paragraphs:
            if para not in seen:
                seen.add(para)
                unique_paragraphs.append(para)
        
        return '\n\n'.join(unique_paragraphs)
    
    def generate_consistency_report(self, results: Dict[int, CheckResult]) -> str:
        """
        生成一致性检查报告
        
        Args:
            results: 检查结果映射
            
        Returns:
            报告文本
        """
        report_parts = []
        
        # 总体统计
        total_chapters = len(results)
        chapters_with_issues = len([r for r in results.values() if r.issues])
        avg_score = sum(r.overall_score for r in results.values()) / total_chapters if total_chapters > 0 else 0
        
        report_parts.append("# 一致性检查报告")
        report_parts.append(f"\n## 总体统计")
        report_parts.append(f"- 总章节数: {total_chapters}")
        report_parts.append(f"- 有问题章节: {chapters_with_issues}")
        report_parts.append(f"- 平均评分: {avg_score:.2f}")
        
        # 问题类型统计
        issue_type_counts = {}
        severity_counts = {}
        
        for result in results.values():
            for issue in result.issues:
                issue_type_counts[issue.issue_type] = issue_type_counts.get(issue.issue_type, 0) + 1
                severity_counts[issue.severity] = severity_counts.get(issue.severity, 0) + 1
        
        report_parts.append(f"\n## 问题类型统计")
        for issue_type, count in issue_type_counts.items():
            report_parts.append(f"- {issue_type.value}: {count}")
        
        report_parts.append(f"\n## 严重程度统计")
        for severity, count in severity_counts.items():
            report_parts.append(f"- {severity.value}: {count}")
        
        # 章节详细结果
        report_parts.append(f"\n## 章节详细结果")
        for chapter_num in sorted(results.keys()):
            result = results[chapter_num]
            report_parts.append(f"\n### 第{chapter_num}章")
            report_parts.append(f"- 总体评分: {result.overall_score:.2f}")
            report_parts.append(f"- 质量评分: {result.quality_score:.2f}")
            report_parts.append(f"- 可读性评分: {result.readability_score:.2f}")
            report_parts.append(f"- 问题数量: {len(result.issues)}")
            
            if result.suggestions:
                report_parts.append(f"- 改进建议: {', '.join(result.suggestions[:3])}")
        
        return '\n'.join(report_parts)


# 具体检查器实现
class CharacterConsistencyChecker:
    """角色一致性检查器"""
    
    def check(self, chapter_num: int, content: str, context: Dict) -> List[ConsistencyIssue]:
        issues = []
        
        try:
            # 简化的角色一致性检查
            # 实际应该使用更复杂的NLP技术
            
            # 检查角色名称一致性
            character_names = self._extract_character_names(content)
            for name in character_names:
                if self._has_character_inconsistency(name, content):
                    issues.append(ConsistencyIssue(
                        issue_id=f"char_{chapter_num}_{name}",
                        issue_type=IssueType.CHARACTER_INCONSISTENCY,
                        severity=Severity.MEDIUM,
                        chapter=chapter_num,
                        description=f"角色 '{name}' 的行为或描述可能不符合设定",
                        auto_fixable=False
                    ))
        
        except Exception as e:
            logging.warning(f"Character consistency check failed: {e}")
        
        return issues
    
    def _extract_character_names(self, content: str) -> List[str]:
        """提取角色名称（简化实现）"""
        names = []
        lines = content.split('\n')
        for line in lines:
            if '：' in line or ':' in line:
                # 可能包含角色对话
                parts = line.split('：', 1) if '：' in line else line.split(':', 1)
                if len(parts) > 1:
                    name = parts[0].strip()
                    if len(name) <= 10 and len(name) > 0:  # 合理的角色名称长度
                        names.append(name)
        return list(set(names))
    
    def _has_character_inconsistency(self, character_name: str, content: str) -> bool:
        """检查角色是否一致（简化实现）"""
        # 这里应该使用更复杂的逻辑
        return False


class PlotConsistencyChecker:
    """剧情一致性检查器"""
    
    def check(self, chapter_num: int, content: str, context: Dict) -> List[ConsistencyIssue]:
        issues = []
        
        try:
            # 检查剧情逻辑
            if self._has_plot_hole(content):
                issues.append(ConsistencyIssue(
                    issue_id=f"plot_{chapter_num}_hole",
                    issue_type=IssueType.PLOT_INCONSISTENCY,
                    severity=Severity.HIGH,
                    chapter=chapter_num,
                    description="剧情可能存在逻辑漏洞或突兀转折",
                    auto_fixable=False
                ))
            
            # 检查时间线一致性
            if self._has_timeline_issue(content, context):
                issues.append(ConsistencyIssue(
                    issue_id=f"plot_{chapter_num}_timeline",
                    issue_type=IssueType.TIMELINE_INCONSISTENCY,
                    severity=Severity.MEDIUM,
                    chapter=chapter_num,
                    description="时间线可能存在不一致",
                    auto_fixable=False
                ))
        
        except Exception as e:
            logging.warning(f"Plot consistency check failed: {e}")
        
        return issues
    
    def _has_plot_hole(self, content: str) -> bool:
        """检查是否有剧情漏洞（简化实现）"""
        # 检查是否有突兀的事件转折
        abrupt_transitions = ['突然', '没想到', '谁知道', '意外']
        count = sum(content.count(word) for word in abrupt_transitions)
        return count > 5  # 如果太多突兀转折，可能有剧情漏洞
    
    def _has_timeline_issue(self, content: str, context: Dict) -> bool:
        """检查时间线问题（简化实现）"""
        # 这里应该检查时间线一致性
        return False


class WorldBuildingConsistencyChecker:
    """世界观一致性检查器"""
    
    def check(self, chapter_num: int, content: str, context: Dict) -> List[ConsistencyIssue]:
        issues = []
        
        try:
            # 检查世界观一致性
            world_setting = context.get("world_setting", "")
            if world_setting and self._has_world_building_inconsistency(content, world_setting):
                issues.append(ConsistencyIssue(
                    issue_id=f"world_{chapter_num}_inconsistency",
                    issue_type=IssueType.WORLD_BUILDING_INCONSISTENCY,
                    severity=Severity.HIGH,
                    chapter=chapter_num,
                    description="内容与世界观设定可能存在冲突",
                    auto_fixable=False
                ))
        
        except Exception as e:
            logging.warning(f"World building consistency check failed: {e}")
        
        return issues
    
    def _has_world_building_inconsistency(self, content: str, world_setting: str) -> bool:
        """检查世界观一致性（简化实现）"""
        # 这里应该使用更复杂的文本匹配技术
        return False


class TimelineConsistencyChecker:
    """时间线一致性检查器"""
    
    def check(self, chapter_num: int, content: str, context: Dict) -> List[ConsistencyIssue]:
        issues = []
        
        try:
            # 检查时间线
            timeline_issues = self._check_timeline_consistency(content, context)
            for issue_desc in timeline_issues:
                issues.append(ConsistencyIssue(
                    issue_id=f"timeline_{chapter_num}_{len(issues)}",
                    issue_type=IssueType.TIMELINE_INCONSISTENCY,
                    severity=Severity.MEDIUM,
                    chapter=chapter_num,
                    description=issue_desc,
                    auto_fixable=False
                ))
        
        except Exception as e:
            logging.warning(f"Timeline consistency check failed: {e}")
        
        return issues
    
    def _check_timeline_consistency(self, content: str, context: Dict) -> List[str]:
        """检查时间线一致性（简化实现）"""
        issues = []
        
        # 检查时间词
        time_words = ['昨天', '今天', '明天', '前天', '后天', '去年', '今年', '明年']
        time_mentions = {word: content.count(word) for word in time_words if content.count(word) > 0}
        
        if len(time_mentions) > 3:
            issues.append("时间描述可能混乱，建议简化时间线")
        
        return issues


class LogicalConsistencyChecker:
    """逻辑一致性检查器"""
    
    def check(self, chapter_num: int, content: str, context: Dict) -> List[ConsistencyIssue]:
        issues = []
        
        try:
            # 检查逻辑矛盾
            contradictions = self._find_contradictions(content)
            for contradiction in contradictions:
                issues.append(ConsistencyIssue(
                    issue_id=f"logic_{chapter_num}_{len(issues)}",
                    issue_type=IssueType.LOGICAL_CONTRADICTION,
                    severity=Severity.HIGH,
                    chapter=chapter_num,
                    description=contradiction,
                    auto_fixable=False
                ))
            
            # 检查重复内容
            repetition_issues = self._check_repetition(content)
            for issue_desc in repetition_issues:
                issues.append(ConsistencyIssue(
                    issue_id=f"repetition_{chapter_num}_{len(issues)}",
                    issue_type=IssueType.REPETITION,
                    severity=Severity.LOW,
                    chapter=chapter_num,
                    description=issue_desc,
                    auto_fixable=True
                ))
        
        except Exception as e:
            logging.warning(f"Logical consistency check failed: {e}")
        
        return issues
    
    def _find_contradictions(self, content: str) -> List[str]:
        """寻找逻辑矛盾（简化实现）"""
        contradictions = []
        
        # 检查自相矛盾的表述
        patterns = [
            (r'从不.*却.*', "可能存在矛盾表述"),
            (r'永远.*但是.*', "可能存在绝对化表述的矛盾"),
        ]
        
        for pattern, desc in patterns:
            if re.search(pattern, content, re.DOTALL):
                contradictions.append(desc)
        
        return contradictions
    
    def _check_repetition(self, content: str) -> List[str]:
        """检查重复内容（简化实现）"""
        issues = []
        
        # 检查段落重复
        paragraphs = content.split('\n\n')
        unique_paragraphs = set(paragraphs)
        
        if len(paragraphs) - len(unique_paragraphs) > 2:
            issues.append("存在较多重复段落")
        
        # 检查句子重复
        sentences = re.split(r'[。！？]', content)
        sentences = [s.strip() for s in sentences if s.strip()]
        unique_sentences = set(sentences)
        
        if len(sentences) - len(unique_sentences) > 5:
            issues.append("存在较多重复句子")
        
        return issues


class QualityAssessmentChecker:
    """质量评估检查器"""
    
    def check(self, chapter_num: int, content: str, context: Dict) -> List[ConsistencyIssue]:
        issues = []
        
        try:
            # 检查节奏问题
            pacing_issues = self._check_pacing(content)
            for issue_desc in pacing_issues:
                issues.append(ConsistencyIssue(
                    issue_id=f"pacing_{chapter_num}_{len(issues)}",
                    issue_type=IssueType.PACING_ISSUE,
                    severity=Severity.LOW,
                    chapter=chapter_num,
                    description=issue_desc,
                    auto_fixable=True
                ))
            
            # 检查风格一致性
            style_issues = self._check_style_consistency(content, context)
            for issue_desc in style_issues:
                issues.append(ConsistencyIssue(
                    issue_id=f"style_{chapter_num}_{len(issues)}",
                    issue_type=IssueType.STYLE_INCONSISTENCY,
                    severity=Severity.LOW,
                    chapter=chapter_num,
                    description=issue_desc,
                    auto_fixable=False
                ))
        
        except Exception as e:
            logging.warning(f"Quality assessment check failed: {e}")
        
        return issues
    
    def _check_pacing(self, content: str) -> List[str]:
        """检查节奏问题（简化实现）"""
        issues = []
        
        # 检查描述和对话的比例
        descriptive_lines = len([line for line in content.split('\n') if len(line) > 20 and '"' not in line])
        dialogue_lines = len([line for line in content.split('\n') if '"' in line])
        
        if descriptive_lines > 0 and dialogue_lines > 0:
            ratio = dialogue_lines / descriptive_lines
            if ratio < 0.1:
                issues.append("描述过多，对话较少，可能节奏缓慢")
            elif ratio > 3:
                issues.append("对话过多，描述较少，可能节奏过快")
        
        return issues
    
    def _check_style_consistency(self, content: str, context: Dict) -> List[str]:
        """检查风格一致性（简化实现）"""
        issues = []
        
        # 检查是否有现代词汇（如果设定是古代背景）
        modern_words = ['手机', '电脑', '网络', '互联网']
        genre = context.get("genre", "")
        
        if genre in ["玄幻", "武侠", "古装"]:
            modern_count = sum(content.count(word) for word in modern_words)
            if modern_count > 0:
                issues.append("可能存在不符合时代背景的词汇")
        
        return issues


# 使用示例
if __name__ == "__main__":
    config = {
        "api_key": "your_api_key",
        "base_url": "https://api.openai.com/v1",
        "model_name": "gpt-4",
        "filepath": "./output"
    }
    
    checker = SmartConsistencyChecker(config)
    
    # 示例章节内容
    chapter_content = """
    第一章 开始
    
    这是一个关于冒险的故事。主人公小明踏上了寻找宝藏的旅程。
    
    小明说："我要找到传说中的宝藏！"
    
    他穿过了茂密的森林，越过了险峻的山脉。
    
    突然，他遇到了一只巨大的怪物。
    """
    
    context = {
        "genre": "冒险",
        "world_setting": "一个充满魔法和怪物的奇幻世界"
    }
    
    result = checker.check_chapter(1, chapter_content, context)
    print(f"Chapter 1 check result:")
    print(f"Overall score: {result.overall_score}")
    print(f"Issues: {len(result.issues)}")
    for issue in result.issues:
        print(f"  - {issue.description}")