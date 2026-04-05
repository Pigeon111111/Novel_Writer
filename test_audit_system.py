# test_audit_system.py
# -*- coding: utf-8 -*-
"""
审计系统测试脚本
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from audit_system import AuditDimension, AuditCategory, Severity, AuditResult, AuditIssue

def test_dimensions():
    """测试审计维度"""
    print("=" * 60)
    print("测试审计维度定义")
    print("=" * 60)
    
    print("\n1. 测试获取所有维度...")
    all_dimensions = AuditDimension.get_all_dimensions()
    print(f"   总维度数: {len(all_dimensions)}")
    
    print("\n2. 测试按类别获取维度...")
    for category in AuditCategory:
        dims = AuditDimension.get_by_category(category)
        print(f"   {category.value}: {len(dims)}个维度")
        for dim in dims[:3]:
            print(f"     - {dim.display_name}: {dim.description}")
    
    print("\n" + "=" * 60)
    print("审计维度测试通过！")
    print("=" * 60)

def test_audit_result():
    """测试审计结果"""
    print("\n" + "=" * 60)
    print("测试审计结果模型")
    print("=" * 60)
    
    print("\n1. 创建审计结果...")
    result = AuditResult(chapter_number=1)
    print(f"   初始质量评分: {result.quality_score}")
    print(f"   初始通过状态: {result.passed}")
    
    print("\n2. 添加问题...")
    issues = [
        AuditIssue(
            dimension=AuditDimension.CHARACTER_OOC,
            severity=Severity.MAJOR,
            title="角色行为不符合人设",
            description="主角突然变得胆小，与之前勇敢的形象不符",
            location="第3段",
            suggestion="调整角色行为，使其符合人设"
        ),
        AuditIssue(
            dimension=AuditDimension.PLOT_FORESHADOW,
            severity=Severity.MINOR,
            title="伏笔未回收",
            description="第一章提到的神秘玉佩未在本章出现",
            location="全文",
            suggestion="考虑回收或提及该伏笔"
        ),
        AuditIssue(
            dimension=AuditDimension.TEXT_REPETITION,
            severity=Severity.SUGGESTION,
            title="重复描写",
            description="多次使用相同的描写方式",
            location="第5、7、9段",
            suggestion="丰富描写方式"
        )
    ]
    
    for issue in issues:
        result.add_issue(issue)
        print(f"   添加问题: {issue.title} ({issue.severity.value})")
    
    print("\n3. 查看结果统计...")
    print(f"   总问题数: {result.total_issues}")
    print(f"   严重问题: {result.critical_count}")
    print(f"   重要问题: {result.major_count}")
    print(f"   次要问题: {result.minor_count}")
    print(f"   建议数: {result.suggestion_count}")
    print(f"   质量评分: {result.quality_score:.1f}")
    print(f"   通过状态: {'通过' if result.passed else '未通过'}")
    
    print("\n4. 测试问题筛选...")
    major_issues = result.get_issues_by_severity(Severity.MAJOR)
    print(f"   重要问题数: {len(major_issues)}")
    
    character_issues = result.get_issues_by_dimension(AuditDimension.CHARACTER_OOC)
    print(f"   角色问题数: {len(character_issues)}")
    
    print("\n5. 查看摘要...")
    print(result.get_summary())
    
    print("=" * 60)
    print("审计结果测试通过！")
    print("=" * 60)

if __name__ == "__main__":
    try:
        test_dimensions()
        test_audit_result()
        print("\n所有测试成功完成！")
    except Exception as e:
        print(f"\n测试失败: {e}")
        import traceback
        traceback.print_exc()
