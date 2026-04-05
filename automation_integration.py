# automation_integration.py
# -*- coding: utf-8 -*-
"""
自动化功能集成模块
将新开发的自动化功能与现有GUI集成
"""

import os
import threading
import logging
from typing import Dict, Optional, Callable
import customtkinter as ctk
from tkinter import messagebox

from auto_pipeline import AutoGenerationPipeline
from enhanced_vectorstore import EnhancedVectorStore
from smart_consistency_checker import SmartConsistencyChecker
from config_manager import load_config

logging.basicConfig(
    filename='app.log',
    filemode='a',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


class AutomationIntegration:
    """
    自动化功能集成器
    负责将新开发的自动化功能与现有GUI无缝集成
    """
    
    def __init__(self, gui_master):
        """
        初始化集成器
        
        Args:
            gui_master: GUI主实例
        """
        self.gui = gui_master
        self.pipeline: Optional[AutoGenerationPipeline] = None
        self.vector_store: Optional[EnhancedVectorStore] = None
        self.consistency_checker: Optional[SmartConsistencyChecker] = None
        
        # 加载配置
        self.config = self._load_config()
        
        # 初始化自动化组件
        self._init_automation_components()
        
        logging.info("AutomationIntegration initialized")
    
    def _load_config(self) -> Dict:
        """加载配置"""
        try:
            config_file = "config.json"
            loaded_config = load_config(config_file)
            if loaded_config:
                return loaded_config
            else:
                # 返回默认配置
                return {
                    "api_key": "",
                    "base_url": "https://api.openai.com/v1",
                    "model_name": "gpt-4",
                    "temperature": 0.7,
                    "max_tokens": 2048,
                    "filepath": "./output",
                    "embedding_api_key": "",
                    "embedding_url": "https://api.openai.com/v1",
                    "embedding_model_name": "text-embedding-ada-002",
                    "embedding_retrieval_k": 4
                }
        except Exception as e:
            logging.error(f"Failed to load config: {e}")
            return {}
    
    def _init_automation_components(self):
        """初始化自动化组件"""
        try:
            # 初始化流水线
            self.pipeline = AutoGenerationPipeline(self.config)
            
            # 初始化增强向量存储
            self.vector_store = EnhancedVectorStore(self.config)
            
            # 初始化智能一致性检查器
            self.consistency_checker = SmartConsistencyChecker(self.config)
            
            logging.info("Automation components initialized successfully")
            
        except Exception as e:
            logging.error(f"Failed to initialize automation components: {e}")
    
    def integrate_one_click_generation(self):
        """
        集成一键生成功能到GUI
        """
        # 创建一键生成按钮
        self._create_one_click_button()
        
        # 添加进度回调
        if self.pipeline:
            self.pipeline.set_progress_callback(self._progress_callback)
        
        logging.info("One-click generation integrated")
    
    def _create_one_click_button(self):
        """创建一键生成按钮"""
        try:
            # 在主标签页添加按钮
            if hasattr(self.gui, 'main_tab'):
                # 查找合适的位置添加按钮
                self._add_button_to_main_tab()
            else:
                # 创建独立的一键生成窗口
                self._create_one_click_window()
                
        except Exception as e:
            logging.error(f"Failed to create one-click button: {e}")
    
    def _add_button_to_main_tab(self):
        """添加到主标签页"""
        try:
            # 假设主标签页有按钮区域
            btn_one_click = ctk.CTkButton(
                self.gui.main_tab,
                text="🚀 一键生成完整小说",
                command=self._run_one_click_generation,
                font=("Microsoft YaHei", 14, "bold"),
                fg_color="#FF6B6B",
                hover_color="#FF5252"
            )
            
            # 放置在合适位置（需要根据实际GUI结构调整）
            if hasattr(self.gui, 'button_frame'):
                btn_one_click.pack(in_=self.gui.button_frame, side="left", padx=10, pady=10)
            
        except Exception as e:
            logging.warning(f"Could not add button to main tab: {e}")
            # 回退到独立窗口
            self._create_one_click_window()
    
    def _create_one_click_window(self):
        """创建独立的一键生成窗口"""
        # 这个方法将在用户点击菜单或按钮时调用
        pass
    
    def _run_one_click_generation(self):
        """运行一键生成"""
        def task():
            try:
                # 禁用按钮
                self.gui.disable_button_safe(self.gui.btn_generate_architecture)
                
                # 获取参数
                topic = self.gui.topic_text.get("0.0", "end").strip()
                genre = self.gui.genre_var.get().strip()
                num_chapters = self.gui.safe_get_int(self.gui.num_chapters_var, 10)
                
                if not topic:
                    messagebox.showwarning("警告", "请先输入小说主题")
                    return
                
                if not self.pipeline:
                    messagebox.showerror("错误", "自动化流水线未初始化")
                    return
                
                # 显示进度窗口
                progress_window = self._create_progress_window()
                
                # 运行生成
                result = self.pipeline.one_click_generate(
                    topic=topic,
                    genre=genre,
                    num_chapters=num_chapters
                )
                
                # 关闭进度窗口
                progress_window.destroy()
                
                # 显示结果
                self._show_generation_result(result)
                
                # 刷新章节列表
                if hasattr(self.gui, 'refresh_chapters_list'):
                    self.gui.refresh_chapters_list()
                
                messagebox.showinfo("完成", f"小说生成完成！\n成功章节: {result['statistics']['successful_chapters']}")
                
            except Exception as e:
                logging.error(f"One-click generation failed: {e}")
                messagebox.showerror("错误", f"生成失败: {str(e)}")
            finally:
                # 启用按钮
                self.gui.enable_button_safe(self.gui.btn_generate_architecture)
        
        # 在新线程中运行
        threading.Thread(target=task, daemon=True).start()
    
    def _create_progress_window(self):
        """创建进度窗口"""
        progress_window = ctk.CTkToplevel(self.gui.master)
        progress_window.title("正在生成小说...")
        progress_window.geometry("400x200")
        progress_window.transient(self.gui.master)
        progress_window.grab_set()
        
        # 进度条
        progress_bar = ctk.CTkProgressBar(progress_window)
        progress_bar.pack(pady=20, padx=20, fill="x")
        progress_bar.start()
        
        # 状态标签
        status_label = ctk.CTkLabel(progress_window, text="正在生成...")
        status_label.pack(pady=10)
        
        # 存储引用以便更新
        progress_window.progress_bar = progress_bar
        progress_window.status_label = status_label
        
        return progress_window
    
    def _progress_callback(self, progress_info: Dict):
        """进度回调函数"""
        try:
            # 更新进度窗口
            if hasattr(self, '_progress_window') and self._progress_window.winfo_exists():
                # 更新进度条
                if 'progress' in progress_info:
                    self._progress_window.progress_bar.set(progress_info['progress'])
                
                # 更新状态文本
                if 'status' in progress_info:
                    self._progress_window.status_label.configure(text=f"状态: {progress_info['status']}")
                
                # 更新统计信息
                if 'completed' in progress_info and 'total' in progress_info:
                    stats_label = getattr(self._progress_window, 'stats_label', None)
                    if stats_label:
                        stats_label.configure(text=f"进度: {progress_info['completed']}/{progress_info['total']}")
        
        except Exception as e:
            logging.warning(f"Progress callback error: {e}")
    
    def _show_generation_result(self, result: Dict):
        """显示生成结果"""
        result_window = ctk.CTkToplevel(self.gui.master)
        result_window.title("生成结果")
        result_window.geometry("600x400")
        
        # 创建文本框显示结果
        text_area = ctk.CTkTextbox(result_window, wrap="word")
        text_area.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 格式化结果文本
        result_text = f"""
📊 生成统计
===========
总章节数: {result['statistics']['total_chapters']}
成功章节: {result['statistics']['successful_chapters']}
失败章节: {result['statistics']['failed_chapters']}
有问题章节: {result['statistics']['chapters_with_issues']}

📝 文件保存位置
=============
{self.config.get('filepath', './output')}

✅ 生成完成！请查看相应文件。
        """
        
        text_area.insert("0.0", result_text)
        text_area.configure(state="disabled")
    
    def integrate_enhanced_context(self):
        """
        集成增强上下文功能
        """
        if not self.vector_store:
            logging.warning("Enhanced vector store not available")
            return
        
        # 替换原有的向量检索逻辑
        self._replace_vector_retrieval()
        
        # 添加上下文管理界面
        self._add_context_management_ui()
        
        logging.info("Enhanced context integration completed")
    
    def _replace_vector_retrieval(self):
        """替换向量检索逻辑"""
        try:
            # 这里需要找到原有的向量检索调用并替换
            # 由于代码结构复杂，这里提供概念性实现
            
            # 1. 在chapter.py中替换get_relevant_context_from_vector_store调用
            # 2. 使用EnhancedVectorStore的get_enhanced_context方法
            # 3. 确保向后兼容性
            
            logging.info("Vector retrieval replacement would be done here")
            
        except Exception as e:
            logging.error(f"Failed to replace vector retrieval: {e}")
    
    def _add_context_management_ui(self):
        """添加上下文管理界面"""
        try:
            # 在设置标签页添加上下文管理选项
            if hasattr(self.gui, 'settings_tab'):
                self._add_context_controls()
        except Exception as e:
            logging.warning(f"Could not add context management UI: {e}")
    
    def integrate_smart_consistency_check(self):
        """
        集成智能一致性检查
        """
        if not self.consistency_checker:
            logging.warning("Smart consistency checker not available")
            return
        
        # 增强现有的一致性检查功能
        self._enhance_consistency_check()
        
        # 添加批量检查功能
        self._add_batch_check_ui()
        
        logging.info("Smart consistency check integration completed")
    
    def _enhance_consistency_check(self):
        """增强一致性检查"""
        try:
            # 替换原有的check_consistency调用
            # 使用SmartConsistencyChecker的check_chapter方法
            # 提供更详细的分析结果
            
            logging.info("Consistency check enhancement would be done here")
            
        except Exception as e:
            logging.error(f"Failed to enhance consistency check: {e}")
    
    def _add_batch_check_ui(self):
        """添加批量检查UI"""
        try:
            # 在审校按钮旁边添加批量检查按钮
            if hasattr(self.gui, 'btn_check_consistency'):
                btn_batch_check = ctk.CTkButton(
                    self.gui.btn_check_consistency.master,
                    text="🔍 批量检查",
                    command=self._run_batch_consistency_check,
                    font=("Microsoft YaHei", 12)
                )
                btn_batch_check.pack(side="left", padx=5)
                
        except Exception as e:
            logging.warning(f"Could not add batch check button: {e}")
    
    def _run_batch_consistency_check(self):
        """运行批量一致性检查"""
        def task():
            try:
                filepath = self.gui.filepath_var.get().strip()
                if not filepath:
                    messagebox.showwarning("警告", "请先设置保存路径")
                    return
                
                # 获取所有章节
                chapters_dir = os.path.join(filepath, "chapters")
                if not os.path.exists(chapters_dir):
                    messagebox.showwarning("警告", "没有找到章节文件")
                    return
                
                chapters = {}
                chapter_files = [f for f in os.listdir(chapters_dir) if f.startswith("chapter_") and f.endswith(".txt")]
                
                for chapter_file in chapter_files:
                    chapter_num = int(chapter_file.split('_')[1].split('.')[0])
                    chapter_path = os.path.join(chapters_dir, chapter_file)
                    with open(chapter_path, 'r', encoding='utf-8') as f:
                        chapters[chapter_num] = f.read()
                
                if not chapters:
                    messagebox.showwarning("警告", "没有找到章节内容")
                    return
                
                # 准备上下文
                context = {
                    "genre": self.gui.genre_var.get().strip(),
                    "world_setting": self._load_world_setting(filepath)
                }
                
                # 运行批量检查
                results = self.consistency_checker.batch_check_chapters(chapters, context)
                
                # 生成报告
                report = self.consistency_checker.generate_consistency_report(results)
                
                # 显示结果
                self._show_consistency_report(report, results)
                
                messagebox.showinfo("完成", f"批量检查完成！\n检查章节: {len(chapters)}")
                
            except Exception as e:
                logging.error(f"Batch consistency check failed: {e}")
                messagebox.showerror("错误", f"检查失败: {str(e)}")
        
        threading.Thread(target=task, daemon=True).start()
    
    def _load_world_setting(self, filepath: str) -> str:
        """加载世界观设定"""
        try:
            setting_file = os.path.join(filepath, "Novel_architecture.txt")
            if os.path.exists(setting_file):
                with open(setting_file, 'r', encoding='utf-8') as f:
                    return f.read()
        except Exception as e:
            logging.warning(f"Could not load world setting: {e}")
        return ""
    
    def _show_consistency_report(self, report: str, results: Dict):
        """显示一致性检查报告"""
        report_window = ctk.CTkToplevel(self.gui.master)
        report_window.title("一致性检查报告")
        report_window.geometry("800x600")
        
        # 创建文本框
        text_area = ctk.CTkTextbox(report_window, wrap="word")
        text_area.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 插入报告
        text_area.insert("0.0", report)
        text_area.configure(state="disabled")
    
    def integrate_all_features(self):
        """
        集成所有自动化功能
        """
        logging.info("Starting integration of all automation features")
        
        # 按顺序集成各个功能
        self.integrate_one_click_generation()
        self.integrate_enhanced_context()
        self.integrate_smart_consistency_check()
        
        # 添加高级功能菜单
        self._add_advanced_features_menu()
        
        logging.info("All automation features integrated")
    
    def _add_advanced_features_menu(self):
        """添加高级功能菜单"""
        try:
            # 创建菜单栏或工具栏
            if hasattr(self.gui, 'master'):
                menubar = getattr(self.gui.master, 'menubar', None)
                if not menubar:
                    menubar = tk.Menu(self.gui.master)
                    self.gui.master.config(menu=menubar)
                
                # 添加自动化菜单
                automation_menu = tk.Menu(menubar, tearoff=0)
                menubar.add_cascade(label="🚀 自动化", menu=automation_menu)
                
                automation_menu.add_command(
                    label="一键生成完整小说",
                    command=self._run_one_click_generation
                )
                automation_menu.add_command(
                    label="批量一致性检查",
                    command=self._run_batch_consistency_check
                )
                automation_menu.add_separator()
                automation_menu.add_command(
                    label="向量库管理",
                    command=self._show_vectorstore_manager
                )
                automation_menu.add_command(
                    label="上下文分析",
                    command=self._show_context_analysis
                )
                
        except Exception as e:
            logging.warning(f"Could not add advanced features menu: {e}")
    
    def _show_vectorstore_manager(self):
        """显示向量库管理器"""
        if not self.vector_store:
            messagebox.showwarning("警告", "向量库未初始化")
            return
        
        # 显示向量库统计信息
        stats = self.vector_store.get_statistics()
        stats_text = f"""
📊 向量库统计
===========
总文档数: {stats.get('total_documents', 0)}
角色节点: {stats.get('character_graph_stats', {}).get('nodes', 0)}
角色关系: {stats.get('character_graph_stats', {}).get('edges', 0)}
伏笔总数: {stats.get('foreshadowing_stats', {}).get('total', 0)}
已解决伏笔: {stats.get('foreshadowing_stats', {}).get('resolved', 0)}
待解决伏笔: {stats.get('foreshadowing_stats', {}).get('pending', 0)}
        """
        
        messagebox.showinfo("向量库管理", stats_text)
    
    def _show_context_analysis(self):
        """显示上下文分析"""
        try:
            filepath = self.gui.filepath_var.get().strip()
            if not filepath:
                messagebox.showwarning("警告", "请先设置保存路径")
                return
            
            # 获取当前章节
            chapter_num = self.gui.safe_get_int(self.gui.chapter_num_var, 1)
            
            # 获取章节内容
            chapter_file = os.path.join(filepath, "chapters", f"chapter_{chapter_num}.txt")
            if not os.path.exists(chapter_file):
                messagebox.showwarning("警告", "当前章节文件不存在")
                return
            
            with open(chapter_file, 'r', encoding='utf-8') as f:
                chapter_content = f.read()
            
            # 分析上下文
            query = f"第{chapter_num}章内容分析"
            context = self.vector_store.get_enhanced_context(query, chapter_num, k=5)
            
            # 显示分析结果
            analysis_text = f"""
🔍 上下文分析 - 第{chapter_num}章
==============================

📋 向量检索结果: {len(context.get('vector_results', []))} 条
⚖️ 加权结果: {len(context.get('weighted_results', []))} 条
👥 角色上下文: {len(context.get('character_context', []))} 条
🎯 伏笔上下文: {len(context.get('foreshadowing_context', []))} 条

📝 压缩上下文长度: {len(context.get('compressed_context', ''))} 字符
            """
            
            messagebox.showinfo("上下文分析", analysis_text)
            
        except Exception as e:
            logging.error(f"Context analysis failed: {e}")
            messagebox.showerror("错误", f"分析失败: {str(e)}")


# 使用示例
def integrate_automation_features(gui_instance):
    """
    将自动化功能集成到GUI实例
    
    Args:
        gui_instance: GUI主实例
    """
    try:
        automation = AutomationIntegration(gui_instance)
        automation.integrate_all_features()
        return automation
    except Exception as e:
        logging.error(f"Failed to integrate automation features: {e}")
        return None


# 如果直接运行，提供测试功能
if __name__ == "__main__":
    print("Automation Integration Module")
    print("This module should be imported and used with the main GUI application.")