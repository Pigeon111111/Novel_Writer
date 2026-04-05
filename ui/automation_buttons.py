# ui/automation_buttons.py
# -*- coding: utf-8 -*-
"""
自动化功能按钮集成
将新开发的自动化功能添加到现有GUI中
"""
import os
import threading
import logging
from tkinter import messagebox
import customtkinter as ctk

from auto_pipeline import AutoGenerationPipeline, GenerationStatus
from smart_consistency_checker import SmartConsistencyChecker
from utils import read_file
from llm_adapters import create_llm_adapter

logging.basicConfig(
    filename='app.log',
    filemode='a',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

_pipeline_instance = None
_is_generating = False
_cancel_requested = False


def add_automation_buttons(self, parent_frame, row=1):
    """
    添加自动化功能按钮到主界面
    
    Args:
        self: GUI实例
        parent_frame: 父容器
        row: 起始行
    """
    global _pipeline_instance
    
    auto_frame = ctk.CTkFrame(parent_frame)
    auto_frame.grid(row=row, column=0, sticky="ew", padx=5, pady=5)
    auto_frame.columnconfigure((0, 1, 2, 3), weight=1)
    
    self.btn_one_click = ctk.CTkButton(
        auto_frame,
        text="🚀 一键生成完整小说",
        command=lambda: run_one_click_generation(self),
        font=("Microsoft YaHei", 12, "bold"),
        fg_color="#FF6B6B",
        hover_color="#FF5252"
    )
    self.btn_one_click.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
    
    self.btn_stop_generation = ctk.CTkButton(
        auto_frame,
        text="⏹️ 停止生成",
        command=lambda: stop_generation(self),
        font=("Microsoft YaHei", 12),
        fg_color="#E74C3C",
        hover_color="#C0392B",
        state="disabled"
    )
    self.btn_stop_generation.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
    
    self.btn_batch_consistency = ctk.CTkButton(
        auto_frame,
        text="🔍 批量一致性检查",
        command=lambda: run_batch_consistency_check(self),
        font=("Microsoft YaHei", 12),
        fg_color="#4ECDC4",
        hover_color="#45B7AA"
    )
    self.btn_batch_consistency.grid(row=0, column=2, padx=5, pady=5, sticky="ew")
    
    self.btn_context_analysis = ctk.CTkButton(
        auto_frame,
        text="📊 上下文分析",
        command=lambda: run_context_analysis(self),
        font=("Microsoft YaHei", 12),
        fg_color="#95E1D3",
        hover_color="#7BCCC0"
    )
    self.btn_context_analysis.grid(row=0, column=3, padx=5, pady=5, sticky="ew")


def get_llm_config_by_name(self, config_name):
    """
    根据配置名称获取LLM配置
    
    Args:
        self: GUI实例
        config_name: 配置名称
        
    Returns:
        配置字典
    """
    llm_configs = self.loaded_config.get("llm_configs", {})
    if config_name in llm_configs:
        return llm_configs[config_name]
    return None


def build_pipeline_config(self, task_type="architecture"):
    """
    构建流水线配置，根据任务类型使用对应的模型配置
    
    Args:
        self: GUI实例
        task_type: 任务类型 (architecture, chapter_outline, prompt_draft, final_chapter, consistency_review)
        
    Returns:
        配置字典
    """
    task_model_map = {
        "architecture": self.architecture_llm_var.get(),
        "chapter_outline": self.chapter_outline_llm_var.get(),
        "prompt_draft": self.prompt_draft_llm_var.get(),
        "final_chapter": self.final_chapter_llm_var.get(),
        "consistency_review": self.consistency_review_llm_var.get()
    }
    
    model_config_name = task_model_map.get(task_type, self.architecture_llm_var.get())
    model_config = get_llm_config_by_name(self, model_config_name)
    
    if model_config:
        interface_format = model_config.get("interface_format", "OpenAI")
        api_key = model_config.get("api_key", "")
        base_url = model_config.get("base_url", "")
        model_name = model_config.get("model_name", "")
        temperature = model_config.get("temperature", 0.7)
        max_tokens = model_config.get("max_tokens", 8192)
        timeout = model_config.get("timeout", 600)
    else:
        interface_format = self.interface_format_var.get()
        api_key = self.api_key_var.get()
        base_url = self.base_url_var.get()
        model_name = self.model_name_var.get()
        temperature = self.temperature_var.get()
        max_tokens = self.max_tokens_var.get()
        timeout = self.timeout_var.get()
    
    config = {
        "interface_format": interface_format,
        "api_key": api_key,
        "base_url": base_url,
        "model_name": model_name,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "timeout": timeout,
        
        "filepath": self.filepath_var.get(),
        "word_number": self.safe_get_int(self.word_number_var, 3000),
        
        "embedding_api_key": self.embedding_api_key_var.get(),
        "embedding_url": self.embedding_url_var.get(),
        "embedding_interface_format": self.embedding_interface_format_var.get(),
        "embedding_model_name": self.embedding_model_name_var.get(),
        "embedding_retrieval_k": self.safe_get_int(self.embedding_retrieval_k_var, 4),
        
        "user_guidance": self.user_guide_text.get("0.0", "end").strip() if hasattr(self, 'user_guide_text') else "",
        "characters_involved": self.char_inv_text.get("0.0", "end").strip() if hasattr(self, 'char_inv_text') else "",
        "key_items": self.key_items_text.get("0.0", "end").strip() if hasattr(self, 'key_items_text') else "",
        "scene_location": self.scene_loc_text.get("0.0", "end").strip() if hasattr(self, 'scene_loc_text') else "",
        "time_constraint": self.time_const_text.get("0.0", "end").strip() if hasattr(self, 'time_const_text') else "",
        
        "architecture_llm": self.architecture_llm_var.get(),
        "chapter_outline_llm": self.chapter_outline_llm_var.get(),
        "prompt_draft_llm": self.prompt_draft_llm_var.get(),
        "final_chapter_llm": self.final_chapter_llm_var.get(),
        "consistency_review_llm": self.consistency_review_llm_var.get(),
        
        "llm_configs": self.loaded_config.get("llm_configs", {})
    }
    
    return config


def get_existing_chapters(filepath):
    """
    获取已存在的章节列表
    
    Args:
        filepath: 文件路径
        
    Returns:
        已存在的章节编号列表
    """
    chapters_dir = os.path.join(filepath, "chapters")
    if not os.path.exists(chapters_dir):
        return []
    
    existing = []
    for f in os.listdir(chapters_dir):
        if f.startswith("chapter_") and f.endswith(".txt"):
            try:
                num = int(f.split('_')[1].split('.')[0])
                existing.append(num)
            except:
                pass
    
    return sorted(existing)


def check_prerequisites(self):
    """
    检查一键生成的前置条件
    
    Args:
        self: GUI实例
        
    Returns:
        (bool, str) - (是否可以继续, 消息)
    """
    filepath = self.filepath_var.get().strip()
    if not filepath:
        return False, "请先选择保存文件路径"
    
    topic = self.topic_text.get("0.0", "end").strip()
    if not topic:
        return False, "请先输入小说主题"
    
    arch_file = os.path.join(filepath, "Novel_architecture.txt")
    dir_file = os.path.join(filepath, "Novel_directory.txt")
    
    if not os.path.exists(arch_file):
        return False, "请先生成小说架构 (Step1)"
    
    if not os.path.exists(dir_file):
        return False, "请先生成章节目录 (Step2)"
    
    return True, "检查通过"


def stop_generation(self):
    """
    停止生成
    """
    global _pipeline_instance, _cancel_requested, _is_generating
    
    if _pipeline_instance:
        _cancel_requested = True
        _pipeline_instance.cancel_all_tasks()
        self.log("⏹️ 正在停止生成...")
        self.btn_stop_generation.configure(state="disabled")


def run_one_click_generation(self):
    """
    运行一键生成完整小说
    """
    global _pipeline_instance, _is_generating, _cancel_requested
    
    if _is_generating:
        messagebox.showwarning("警告", "已有生成任务正在进行中")
        return
    
    can_continue, msg = check_prerequisites(self)
    if not can_continue:
        messagebox.showwarning("警告", msg)
        return
    
    existing_chapters = get_existing_chapters(self.filepath_var.get())
    num_chapters = self.safe_get_int(self.num_chapters_var, 10)
    
    start_chapter = 1
    if existing_chapters:
        max_existing = max(existing_chapters)
        if max_existing >= num_chapters:
            messagebox.showinfo("提示", f"所有章节已生成完成 (共{num_chapters}章)")
            return
        
        confirm = messagebox.askyesno(
            "续写确认",
            f"检测到已有 {max_existing} 章内容。\n\n"
            f"是否从第 {max_existing + 1} 章继续生成？\n\n"
            f"选择「是」：续写第 {max_existing + 1} 到 {num_chapters} 章\n"
            f"选择「否」：重新生成所有章节"
        )
        
        if confirm:
            start_chapter = max_existing + 1
        else:
            start_chapter = 1
    
    def task():
        global _pipeline_instance, _is_generating, _cancel_requested
        
        _is_generating = True
        _cancel_requested = False
        
        try:
            self.disable_button_safe(self.btn_one_click)
            self.master.after(0, lambda: self.btn_stop_generation.configure(state="normal"))
            
            topic = self.topic_text.get("0.0", "end").strip()
            genre = self.genre_var.get().strip()
            filepath = self.filepath_var.get()
            
            self.log("=" * 50)
            self.log("🚀 开始一键生成...")
            self.log(f"主题: {topic}")
            self.log(f"类型: {genre}")
            self.log(f"总章节数: {num_chapters}")
            self.log(f"起始章节: {start_chapter}")
            self.log("=" * 50)
            
            progress_window = create_progress_window(self, "正在一键生成小说...")
            
            config = build_pipeline_config(self)
            
            _pipeline_instance = AutoGenerationPipeline(config)
            _pipeline_instance.set_cancel_flag(lambda: _cancel_requested)
            
            def progress_callback(info):
                if _cancel_requested:
                    return
                update_progress_window(progress_window, info)
                if 'task_id' in info:
                    chapter_num = info['task_id'].replace('chapter_', '') if 'chapter_' in info.get('task_id', '') else ''
                    if info.get('status') == 'in_progress':
                        self.safe_log(f"📝 正在生成第 {chapter_num} 章...")
                    elif info.get('status') == 'completed':
                        self.safe_log(f"✅ 第 {chapter_num} 章生成完成")
                    elif info.get('status') == 'failed':
                        self.safe_log(f"❌ 第 {chapter_num} 章生成失败")
            
            _pipeline_instance.set_progress_callback(progress_callback)
            
            result = _pipeline_instance.one_click_generate_from_chapter(
                topic=topic,
                genre=genre,
                num_chapters=num_chapters,
                start_chapter=start_chapter,
                get_config_func=lambda t: build_pipeline_config(self, t)
            )
            
            progress_window.destroy()
            
            if _cancel_requested:
                self.log("⏹️ 生成已停止")
                messagebox.showinfo("已停止", "生成任务已被用户停止")
            else:
                show_generation_result(self, result)
                
                if hasattr(self, 'refresh_chapters_list'):
                    self.refresh_chapters_list()
                
                self.log("✅ 一键生成完成！")
                messagebox.showinfo(
                    "完成",
                    f"小说生成完成！\n\n"
                    f"成功章节: {result['statistics']['successful_chapters']}\n"
                    f"失败章节: {result['statistics']['failed_chapters']}\n"
                    f"有问题章节: {result['statistics']['chapters_with_issues']}"
                )
            
        except Exception as e:
            logging.error(f"One-click generation failed: {e}")
            self.log(f"❌ 生成失败: {str(e)}")
            messagebox.showerror("错误", f"生成失败:\n{str(e)}")
        finally:
            _is_generating = False
            _pipeline_instance = None
            self.enable_button_safe(self.btn_one_click)
            self.master.after(0, lambda: self.btn_stop_generation.configure(state="disabled"))
    
    threading.Thread(target=task, daemon=True).start()


def run_batch_consistency_check(self):
    """
    运行批量一致性检查
    """
    def task():
        try:
            self.disable_button_safe(self.btn_batch_consistency)
            
            filepath = self.filepath_var.get().strip()
            if not filepath:
                messagebox.showwarning("警告", "请先设置保存路径")
                return
            
            chapters_dir = os.path.join(filepath, "chapters")
            if not os.path.exists(chapters_dir):
                messagebox.showwarning("警告", "没有找到章节文件\n请先生成章节内容")
                return
            
            chapter_files = [
                f for f in os.listdir(chapters_dir)
                if f.startswith("chapter_") and f.endswith(".txt")
            ]
            
            if not chapter_files:
                messagebox.showwarning("警告", "没有找到章节内容")
                return
            
            self.log(f"开始批量一致性检查，共 {len(chapter_files)} 个章节...")
            
            config = build_pipeline_config(self, "consistency_review")
            
            checker = SmartConsistencyChecker(config)
            
            chapters = {}
            for chapter_file in chapter_files:
                chapter_num = int(chapter_file.split('_')[1].split('.')[0])
                chapter_path = os.path.join(chapters_dir, chapter_file)
                with open(chapter_path, 'r', encoding='utf-8') as f:
                    chapters[chapter_num] = f.read()
            
            context = {
                "genre": self.genre_var.get().strip(),
                "world_setting": load_world_setting(filepath)
            }
            
            results = checker.batch_check_chapters(chapters, context)
            
            report = checker.generate_consistency_report(results)
            
            show_consistency_report(self, report, results)
            
            self.log("✅ 批量一致性检查完成！")
            messagebox.showinfo("完成", f"批量检查完成！\n检查章节: {len(chapters)}")
            
        except Exception as e:
            logging.error(f"Batch consistency check failed: {e}")
            self.log(f"❌ 检查失败: {str(e)}")
            messagebox.showerror("错误", f"检查失败:\n{str(e)}")
        finally:
            self.enable_button_safe(self.btn_batch_consistency)
    
    threading.Thread(target=task, daemon=True).start()


def run_context_analysis(self):
    """
    运行上下文分析
    """
    try:
        filepath = self.filepath_var.get().strip()
        if not filepath:
            messagebox.showwarning("警告", "请先设置保存路径")
            return
        
        chapter_num = self.safe_get_int(self.chapter_num_var, 1)
        
        chapter_file = os.path.join(filepath, "chapters", f"chapter_{chapter_num}.txt")
        if not os.path.exists(chapter_file):
            messagebox.showwarning("警告", f"第{chapter_num}章文件不存在")
            return
        
        with open(chapter_file, 'r', encoding='utf-8') as f:
            chapter_content = f.read()
        
        word_count = len(chapter_content)
        paragraphs = len([p for p in chapter_content.split('\n\n') if p.strip()])
        dialogues = chapter_content.count('"') + chapter_content.count('"')
        
        analysis_text = f"""
📊 章节分析 - 第{chapter_num}章
===========================

📝 基础统计:
  - 总字数: {word_count}
  - 段落数: {paragraphs}
  - 对话数量: {dialogues // 2}

📖 内容分析:
  - 平均段落长度: {word_count // max(paragraphs, 1)}
  - 对话密度: {dialogues / max(word_count, 1) * 100:.1f}%

💡 建议:
  - {"对话较多，注意平衡叙述和对话" if dialogues > word_count * 0.3 else "对话适中，节奏良好"}
  - {"段落较短，可以考虑合并部分段落" if paragraphs > 20 else "段落长度适中"}
        """
        
        show_analysis_window(self, analysis_text)
        
    except Exception as e:
        logging.error(f"Context analysis failed: {e}")
        messagebox.showerror("错误", f"分析失败:\n{str(e)}")


def create_progress_window(self, title):
    """
    创建进度窗口
    """
    progress_window = ctk.CTkToplevel(self.master)
    progress_window.title(title)
    progress_window.geometry("500x180")
    progress_window.transient(self.master)
    progress_window.grab_set()
    
    progress_bar = ctk.CTkProgressBar(progress_window)
    progress_bar.pack(pady=20, padx=20, fill="x")
    progress_bar.set(0)
    
    status_label = ctk.CTkLabel(progress_window, text="正在初始化...", font=("Microsoft YaHei", 12))
    status_label.pack(pady=10)
    
    stats_label = ctk.CTkLabel(progress_window, text="", font=("Microsoft YaHei", 10))
    stats_label.pack(pady=5)
    
    progress_window.progress_bar = progress_bar
    progress_window.status_label = status_label
    progress_window.stats_label = stats_label
    
    return progress_window


def update_progress_window(progress_window, info):
    """
    更新进度窗口
    """
    try:
        if progress_window.winfo_exists():
            if 'progress' in info:
                progress_window.progress_bar.set(info['progress'])
            
            if 'status' in info:
                status_text = info['status']
                if status_text == 'in_progress':
                    status_text = "正在进行中..."
                elif status_text == 'completed':
                    status_text = "已完成"
                elif status_text == 'failed':
                    status_text = "失败"
                progress_window.status_label.configure(text=f"状态: {status_text}")
            
            if 'completed' in info and 'total' in info:
                progress_window.stats_label.configure(
                    text=f"进度: {info['completed']}/{info['total']}"
                )
    except Exception as e:
        logging.warning(f"Progress update error: {e}")


def show_generation_result(self, result):
    """
    显示生成结果
    """
    result_window = ctk.CTkToplevel(self.master)
    result_window.title("生成结果")
    result_window.geometry("600x400")
    
    text_area = ctk.CTkTextbox(result_window, wrap="word", font=("Microsoft YaHei", 11))
    text_area.pack(fill="both", expand=True, padx=10, pady=10)
    
    result_text = f"""
📊 生成统计
===========
总章节数: {result['statistics']['total_chapters']}
成功章节: {result['statistics']['successful_chapters']}
失败章节: {result['statistics']['failed_chapters']}
有问题章节: {result['statistics']['chapters_with_issues']}

📝 文件保存位置
=============
{result.get('filepath', 'N/A')}

✅ 生成完成！
请查看相应文件了解详细内容。
    """
    
    text_area.insert("0.0", result_text)
    text_area.configure(state="disabled")


def show_consistency_report(self, report, results):
    """
    显示一致性检查报告
    """
    report_window = ctk.CTkToplevel(self.master)
    report_window.title("一致性检查报告")
    report_window.geometry("800x600")
    
    text_area = ctk.CTkTextbox(report_window, wrap="word", font=("Microsoft YaHei", 11))
    text_area.pack(fill="both", expand=True, padx=10, pady=10)
    
    text_area.insert("0.0", report)
    text_area.configure(state="disabled")


def show_analysis_window(self, analysis_text):
    """
    显示分析窗口
    """
    analysis_window = ctk.CTkToplevel(self.master)
    analysis_window.title("上下文分析")
    analysis_window.geometry("600x500")
    
    text_area = ctk.CTkTextbox(analysis_window, wrap="word", font=("Microsoft YaHei", 11))
    text_area.pack(fill="both", expand=True, padx=10, pady=10)
    
    text_area.insert("0.0", analysis_text)
    text_area.configure(state="disabled")


def load_world_setting(filepath):
    """
    加载世界观设定
    """
    try:
        setting_file = os.path.join(filepath, "Novel_architecture.txt")
        if os.path.exists(setting_file):
            with open(setting_file, 'r', encoding='utf-8') as f:
                return f.read()
    except Exception as e:
        logging.warning(f"Could not load world setting: {e}")
    return ""
