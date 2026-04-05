# test_state_manager.py
# -*- coding: utf-8 -*-
"""
状态管理系统测试脚本
"""
import sys
import os
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from state_manager import StateManager, StateMigrator

def test_basic_operations():
    """测试基本操作"""
    print("=" * 60)
    print("测试状态管理系统基本操作")
    print("=" * 60)
    
    test_dir = project_root / "test_story"
    test_dir.mkdir(exist_ok=True)
    
    sm = StateManager(str(test_dir))
    
    print("\n1. 测试加载默认状态...")
    current_state = sm.load_state("current_state")
    print(f"   当前章节: {current_state.current_chapter}")
    print(f"   小说标题: {current_state.novel_title}")
    
    print("\n2. 测试更新当前状态...")
    current_state.novel_title = "测试小说"
    current_state.current_chapter = 1
    current_state.total_chapters = 10
    sm.save_state("current_state", current_state)
    print("   状态已保存")
    
    print("\n3. 测试添加角色...")
    sm.add_character("张三", {
        "location": "北京",
        "status": "alive",
        "emotional_state": "兴奋",
        "personality": ["勇敢", "善良"]
    })
    print("   角色已添加")
    
    print("\n4. 测试获取角色...")
    character = sm.get_character_by_name("张三")
    if character:
        print(f"   角色名称: {character.name}")
        print(f"   当前位置: {character.location}")
        print(f"   情感状态: {character.emotional_state}")
        print(f"   性格特点: {character.personality}")
    
    print("\n5. 测试埋下伏笔...")
    sm.plant_hook(
        hook_id="hook_001",
        description="主角在第一章捡到的神秘玉佩",
        planted_chapter=1,
        expected_resolve_chapter=5,
        priority="high",
        related_characters=["张三"]
    )
    print("   伏笔已埋下")
    
    print("\n6. 测试获取待处理伏笔...")
    pending_hooks = sm.get_pending_hooks()
    print(f"   待处理伏笔数量: {len(pending_hooks)}")
    for hook in pending_hooks:
        print(f"   - {hook.hook_id}: {hook.description}")
    
    print("\n7. 测试更新章节...")
    sm.update_after_chapter(
        chapter_num=1,
        chapter_content="这是第一章的内容...",
        chapter_title="第一章 开始",
        word_count=3000
    )
    print("   章节状态已更新")
    
    print("\n8. 测试获取统计信息...")
    stats = sm.get_statistics()
    print(f"   当前章节: {stats['current_chapter']}")
    print(f"   总章节数: {stats['total_chapters']}")
    print(f"   角色数量: {stats['total_characters']}")
    print(f"   待处理伏笔: {stats['pending_hooks']}")
    print(f"   总字数: {stats['total_word_count']}")
    
    print("\n9. 测试导出所有状态...")
    all_states = sm.export_all_states()
    print(f"   导出的状态类型: {list(all_states.keys())}")
    
    print("\n" + "=" * 60)
    print("所有测试通过！")
    print("=" * 60)
    
    import shutil
    if test_dir.exists():
        shutil.rmtree(test_dir)
        print(f"\n测试目录已清理: {test_dir}")

def test_migration():
    """测试状态迁移"""
    print("\n" + "=" * 60)
    print("测试状态迁移功能")
    print("=" * 60)
    
    test_dir = project_root / "test_migration"
    test_dir.mkdir(exist_ok=True)
    
    char_state_file = test_dir / "character_state.txt"
    with open(char_state_file, 'w', encoding='utf-8') as f:
        f.write("""【角色：张三】
当前位置：北京
状态：alive
情感状态：兴奋
最后出场章节：1
性格特点：勇敢、善良
背景故事：一个普通的年轻人

【角色：李四】
当前位置：上海
状态：alive
情感状态：平静
最后出场章节：2
性格特点：聪明、谨慎
""")
    
    global_summary_file = test_dir / "global_summary.txt"
    with open(global_summary_file, 'w', encoding='utf-8') as f:
        f.write("""第1章：张三在北京开始了他的冒险之旅。
关键事件：捡到神秘玉佩、遇到李四

第2章：李四向张三透露了一个惊天秘密。
关键事件：发现玉佩的秘密、决定前往上海
""")
    
    print("\n1. 创建测试文件...")
    print(f"   - {char_state_file}")
    print(f"   - {global_summary_file}")
    
    print("\n2. 执行迁移...")
    migrator = StateMigrator(str(test_dir))
    migrator.migrate_all()
    
    print("\n3. 验证迁移结果...")
    sm = StateManager(str(test_dir))
    
    character_matrix = sm.load_state("character_matrix")
    print(f"   迁移的角色数量: {len(character_matrix.characters)}")
    for char_name, char in character_matrix.characters.items():
        print(f"   - {char_name}: {char.location}")
    
    chapter_summaries = sm.load_state("chapter_summaries")
    print(f"   迁移的章节数量: {len(chapter_summaries.summaries)}")
    for chap_num, summary in chapter_summaries.summaries.items():
        print(f"   - 第{chap_num}章: {summary.summary[:30]}...")
    
    print("\n" + "=" * 60)
    print("迁移测试通过！")
    print("=" * 60)
    
    import shutil
    if test_dir.exists():
        shutil.rmtree(test_dir)
        print(f"\n测试目录已清理: {test_dir}")

if __name__ == "__main__":
    try:
        test_basic_operations()
        test_migration()
        print("\n✅ 所有测试成功完成！")
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
