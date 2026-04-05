# audit_system/result.py
# -*- coding: utf-8 -*-
"""
审计结果模型
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

from .dimensions import AuditDimension, Severity


class AuditIssue(BaseModel):
    """单个审计问题"""
    dimension: AuditDimension = Field(..., description="审计维度")
    severity: Severity = Field(..., description="严重程度")
    title: str = Field(..., description="问题标题")
    description: str = Field(..., description="问题描述")
    location: str = Field(default="", description="问题位置")
    context: str = Field(default="", description="上下文片段")
    suggestion: str = Field(default="", description="修复建议")
    auto_fixable: bool = Field(default=False, description="是否可自动修复")
    
    class Config:
        use_enum_values = False


class AuditResult(BaseModel):
    """章节审计结果"""
    chapter_number: int = Field(..., description="章节号")
    total_issues: int = Field(default=0, description="总问题数")
    critical_count: int = Field(default=0, description="严重问题数")
    major_count: int = Field(default=0, description="重要问题数")
    minor_count: int = Field(default=0, description="次要问题数")
    suggestion_count: int = Field(default=0, description="建议数")
    
    issues: List[AuditIssue] = Field(default_factory=list, description="问题列表")
    
    quality_score: float = Field(default=100.0, description="质量评分（0-100）")
    passed: bool = Field(default=True, description="是否通过审计")
    
    audit_time: datetime = Field(default_factory=datetime.now, description="审计时间")
    duration_seconds: float = Field(default=0.0, description="审计耗时（秒）")
    
    def add_issue(self, issue: AuditIssue):
        """添加问题"""
        self.issues.append(issue)
        self.total_issues += 1
        
        if issue.severity == Severity.CRITICAL:
            self.critical_count += 1
        elif issue.severity == Severity.MAJOR:
            self.major_count += 1
        elif issue.severity == Severity.MINOR:
            self.minor_count += 1
        else:
            self.suggestion_count += 1
        
        self._update_quality_score()
        self._update_passed_status()
    
    def _update_quality_score(self):
        """更新质量评分"""
        from .dimensions import SEVERITY_WEIGHTS
        
        penalty = 0.0
        for issue in self.issues:
            penalty += SEVERITY_WEIGHTS[issue.severity] * 5
        
        self.quality_score = max(0.0, 100.0 - penalty)
    
    def _update_passed_status(self):
        """更新通过状态"""
        self.passed = self.critical_count == 0 and self.major_count <= 2
    
    def get_issues_by_severity(self, severity: Severity) -> List[AuditIssue]:
        """获取指定严重程度的问题"""
        return [issue for issue in self.issues if issue.severity == severity]
    
    def get_issues_by_dimension(self, dimension: AuditDimension) -> List[AuditIssue]:
        """获取指定维度的问题"""
        return [issue for issue in self.issues if issue.dimension == dimension]
    
    def get_auto_fixable_issues(self) -> List[AuditIssue]:
        """获取可自动修复的问题"""
        return [issue for issue in self.issues if issue.auto_fixable]
    
    def get_summary(self) -> str:
        """获取摘要"""
        status = "✅ 通过" if self.passed else "❌ 未通过"
        summary = f"""
审计结果：{status}
质量评分：{self.quality_score:.1f}/100
总问题数：{self.total_issues}
  - 严重：{self.critical_count}
  - 重要：{self.major_count}
  - 次要：{self.minor_count}
  - 建议：{self.suggestion_count}
"""
        return summary


class AuditReport(BaseModel):
    """完整审计报告"""
    novel_title: str = Field(default="", description="小说标题")
    start_chapter: int = Field(..., description="起始章节")
    end_chapter: int = Field(..., description="结束章节")
    
    chapter_results: dict[int, AuditResult] = Field(
        default_factory=dict, 
        description="章节审计结果"
    )
    
    overall_quality_score: float = Field(default=100.0, description="整体质量评分")
    overall_passed: bool = Field(default=True, description="整体是否通过")
    
    report_time: datetime = Field(default_factory=datetime.now, description="报告生成时间")
    
    def add_chapter_result(self, chapter_num: int, result: AuditResult):
        """添加章节结果"""
        self.chapter_results[chapter_num] = result
        self._update_overall_metrics()
    
    def _update_overall_metrics(self):
        """更新整体指标"""
        if not self.chapter_results:
            return
        
        total_score = sum(r.quality_score for r in self.chapter_results.values())
        self.overall_quality_score = total_score / len(self.chapter_results)
        
        self.overall_passed = all(r.passed for r in self.chapter_results.values())
    
    def get_summary(self) -> str:
        """获取摘要"""
        status = "✅ 通过" if self.overall_passed else "❌ 未通过"
        summary = f"""
审计报告：{self.novel_title}
审计范围：第{self.start_chapter}章 - 第{self.end_chapter}章
整体结果：{status}
整体评分：{self.overall_quality_score:.1f}/100
审计章节数：{len(self.chapter_results)}
"""
        return summary
