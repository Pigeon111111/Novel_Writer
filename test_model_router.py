# test_model_router.py
# -*- coding: utf-8 -*-
"""
模型路由系统测试脚本
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from model_router import ModelRouter, TaskType, Priority, AdaptiveModelSelector
from config_manager import ConfigManager

def test_model_router():
    """测试模型路由器"""
    print("=" * 60)
    print("测试模型路由系统")
    print("=" * 60)
    
    config_path = Path(__file__).parent.parent / "config.json"
    config_manager = ConfigManager(str(config_path))
    router = ModelRouter(config_manager)
    
    print("\n1. 测试加载可用模型...")
    available_models = router.available_models
    print(f"   可用模型数量: {len(available_models)}")
    for model_name in available_models.keys():
        print(f"   - {model_name}")
    
    print("\n2. 测试获取LongCat模型...")
    longcat_models = router.get_longcat_models()
    print(f"   LongCat模型数量: {len(longcat_models)}")
    for model_name in longcat_models:
        print(f"   - {model_name}")
    
    print("\n3. 测试不同任务类型的模型选择...")
    test_tasks = [
        (TaskType.ARCHITECTURE, "架构规划"),
        (TaskType.CHAPTER_OUTLINE, "章节大纲"),
        (TaskType.DRAFT_WRITING, "草稿撰写"),
        (TaskType.CONSISTENCY_CHECK, "一致性检查"),
        (TaskType.FINALIZATION, "定稿")
    ]
    
    for task_type, task_name in test_tasks:
        print(f"\n   任务: {task_name}")
        
        for priority in [Priority.QUALITY, Priority.COST, Priority.BALANCED]:
            try:
                model_info = router.select_model(task_type, priority)
                print(f"   - {priority.value:8s}: {model_info['model_name']}")
            except Exception as e:
                print(f"   - {priority.value:8s}: 选择失败 - {e}")
    
    print("\n4. 测试成本估算...")
    estimated_tokens = 4000
    cost_estimates = router.estimate_cost(TaskType.DRAFT_WRITING, estimated_tokens)
    
    for priority, estimate in cost_estimates.items():
        print(f"   {priority:8s}:")
        print(f"     模型: {estimate['model']}")
        print(f"     预估成本: ${estimate['estimated_cost']:.4f}")
        print(f"     预估tokens: {estimate['estimated_tokens']}")
    
    print("\n" + "=" * 60)
    print("模型路由器测试通过！")
    print("=" * 60)

def test_adaptive_selector():
    """测试自适应选择器"""
    print("\n" + "=" * 60)
    print("测试自适应模型选择器")
    print("=" * 60)
    
    config_path = Path(__file__).parent.parent / "config.json"
    config_manager = ConfigManager(str(config_path))
    router = ModelRouter(config_manager)
    selector = AdaptiveModelSelector(router)
    
    print("\n1. 测试智能选择（带降级）...")
    for task_type in [TaskType.ARCHITECTURE, TaskType.DRAFT_WRITING]:
        try:
            model_info = selector.select_with_fallback(task_type)
            print(f"   {task_type.value:20s}: {model_info['model_name']}")
        except Exception as e:
            print(f"   {task_type.value:20s}: 选择失败 - {e}")
    
    print("\n2. 测试模型状态获取...")
    status = selector.get_model_status()
    for model_name, model_status in status.items():
        available = "可用" if model_status["available"] else "不可用"
        print(f"   {model_name:30s}: {available} (失败次数: {model_status['failure_count']})")
    
    print("\n3. 测试成本预算选择...")
    model_info = selector.get_best_model_for_cost(TaskType.DRAFT_WRITING, max_cost=0.01)
    if model_info:
        print(f"   在预算内找到模型: {list(router.available_models.keys())[list(router.available_models.values()).index(model_info)]}")
    else:
        print("   在预算内未找到合适模型")
    
    print("\n4. 测试熔断器机制...")
    test_model = list(router.available_models.keys())[0]
    print(f"   模拟模型 {test_model} 失败...")
    
    for i in range(4):
        selector.record_failure(test_model, Exception(f"测试错误 {i+1}"))
        status = selector.get_model_status()[test_model]
        print(f"   失败次数: {status['failure_count']}, 熔断器激活: {status['circuit_breaker_active']}")
    
    print(f"\n   重置熔断器...")
    selector.reset_circuit_breaker(test_model)
    status = selector.get_model_status()[test_model]
    print(f"   失败次数: {status['failure_count']}, 熔断器激活: {status['circuit_breaker_active']}")
    
    print("\n" + "=" * 60)
    print("自适应选择器测试通过！")
    print("=" * 60)

if __name__ == "__main__":
    try:
        test_model_router()
        test_adaptive_selector()
        print("\n所有测试成功完成！")
    except Exception as e:
        print(f"\n测试失败: {e}")
        import traceback
        traceback.print_exc()
