# auto_pipeline.py
# -*- coding: utf-8 -*-
"""
智能批量生成流水线
实现一键生成完整小说的功能
"""

import os
import json
import logging
import asyncio
from typing import List, Dict, Optional, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from enum import Enum

from llm_adapters import create_llm_adapter
from novel_generator.chapter import generate_chapter_draft
from novel_generator.architecture import Novel_architecture_generate
from consistency_checker import check_consistency
from utils import read_file, save_string_to_txt, clear_file_content

logging.basicConfig(
    filename='app.log',
    filemode='a',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


class GenerationStatus(Enum):
    """生成状态枚举"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class GenerationTask:
    """生成任务数据类"""
    task_id: str
    chapter_num: int
    status: GenerationStatus
    result: Optional[str] = None
    error: Optional[str] = None
    retry_count: int = 0


class AutoGenerationPipeline:
    """
    智能批量生成流水线
    实现一键生成完整小说的核心功能
    """
    
    def __init__(self, config: Dict):
        """
        初始化流水线
        
        Args:
            config: 配置字典，包含API密钥、模型参数等
        """
        self.config = config
        self.llm_adapter = None
        self.tasks: Dict[str, GenerationTask] = {}
        self.progress_callback: Optional[Callable] = None
        self.executor = ThreadPoolExecutor(max_workers=1)
        self._cancel_flag: Optional[Callable] = None
        
        self.total_tasks = 0
        self.completed_tasks = 0
        self.failed_tasks = 0
        
    def set_cancel_flag(self, flag_func: Callable):
        """
        设置取消标志函数
        
        Args:
            flag_func: 返回布尔值的函数，True表示需要取消
        """
        self._cancel_flag = flag_func
        
    def _check_cancelled(self) -> bool:
        """检查是否被取消"""
        if self._cancel_flag and self._cancel_flag():
            return True
        return False
        
    def _init_llm_adapter(self, config: Dict = None):
        """初始化LLM适配器"""
        use_config = config or self.config
        try:
            self.llm_adapter = create_llm_adapter(
                interface_format=use_config.get("interface_format", "OpenAI"),
                base_url=use_config.get("base_url", ""),
                model_name=use_config.get("model_name", ""),
                api_key=use_config.get("api_key", ""),
                temperature=use_config.get("temperature", 0.7),
                max_tokens=use_config.get("max_tokens", 2048),
                timeout=use_config.get("timeout", 600)
            )
            logging.info("LLM adapter initialized successfully")
        except Exception as e:
            logging.error(f"Failed to initialize LLM adapter: {e}")
            raise
    
    def set_progress_callback(self, callback: Callable):
        """
        设置进度回调函数
        
        Args:
            callback: 回调函数，接收进度信息
        """
        self.progress_callback = callback
    
    def _update_progress(self, task_id: str, status: GenerationStatus, progress: float):
        """更新进度信息"""
        if self.progress_callback:
            self.progress_callback({
                "task_id": task_id,
                "status": status.value,
                "progress": progress,
                "completed": self.completed_tasks,
                "total": self.total_tasks
            })
    
    def _get_task_config(self, task_type: str, get_config_func: Callable = None) -> Dict:
        """
        获取任务特定配置
        
        Args:
            task_type: 任务类型
            get_config_func: 获取配置的函数
            
        Returns:
            配置字典
        """
        if get_config_func:
            return get_config_func(task_type)
        return self.config
    
    def generate_novel_setting(self, topic: str, genre: str, num_chapters: int, 
                                get_config_func: Callable = None) -> str:
        """
        自动生成小说设定
        
        Args:
            topic: 小说主题
            genre: 小说类型
            num_chapters: 章节数量
            get_config_func: 获取配置的函数
            
        Returns:
            生成的小说设定文本
        """
        logging.info(f"Generating novel setting for topic: {topic}")
        
        config = self._get_task_config("architecture", get_config_func)
        
        try:
            Novel_architecture_generate(
                interface_format=config.get("interface_format", "OpenAI"),
                api_key=config.get("api_key", ""),
                base_url=config.get("base_url", ""),
                llm_model=config.get("model_name", ""),
                topic=topic,
                genre=genre,
                number_of_chapters=num_chapters,
                word_number=config.get("word_number", 4000),
                filepath=config.get("filepath", "./output"),
                user_guidance=config.get("user_guidance", ""),
                temperature=config.get("temperature", 0.7),
                max_tokens=config.get("max_tokens", 2048),
                timeout=config.get("timeout", 600)
            )
            
            arch_file = os.path.join(config.get("filepath", "./output"), "Novel_architecture.txt")
            if os.path.exists(arch_file):
                setting_text = read_file(arch_file)
                logging.info("Novel setting generated successfully")
                return setting_text
            else:
                raise FileNotFoundError("Novel architecture file not found")
                
        except Exception as e:
            logging.error(f"Failed to generate novel setting: {e}")
            raise
    
    def generate_chapter_directory(self, setting: str, num_chapters: int) -> List[Dict]:
        """
        自动生成章节目录
        
        Args:
            setting: 小说设定文本
            num_chapters: 章节数量
            
        Returns:
            章节信息列表
        """
        logging.info(f"Generating chapter directory for {num_chapters} chapters")
        
        try:
            directory_file = os.path.join(self.config.get("filepath", "./output"), "Novel_directory.txt")
            if os.path.exists(directory_file):
                directory_text = read_file(directory_file)
                chapters = self._parse_directory_text(directory_text, num_chapters)
                logging.info(f"Chapter directory generated: {len(chapters)} chapters")
                return chapters
            else:
                return self._generate_default_directory(num_chapters)
                
        except Exception as e:
            logging.error(f"Failed to generate chapter directory: {e}")
            return self._generate_default_directory(num_chapters)
    
    def _parse_directory_text(self, directory_text: str, num_chapters: int) -> List[Dict]:
        """解析目录文本为结构化数据"""
        chapters = []
        lines = directory_text.split('\n')
        
        for i, line in enumerate(lines):
            if f"第{i+1}章" in line or f"Chapter {i+1}" in line:
                chapter_info = {
                    "chapter_number": i + 1,
                    "chapter_title": f"第{i+1}章",
                    "chapter_role": "常规章节",
                    "chapter_purpose": "内容推进",
                    "suspense_level": "中等",
                    "foreshadowing": "无",
                    "plot_twist_level": "★☆☆☆☆",
                    "chapter_summary": line.strip()
                }
                chapters.append(chapter_info)
        
        if len(chapters) < num_chapters:
            return self._generate_default_directory(num_chapters)
            
        return chapters
    
    def _generate_default_directory(self, num_chapters: int) -> List[Dict]:
        """生成默认目录结构"""
        return [
            {
                "chapter_number": i + 1,
                "chapter_title": f"第{i+1}章",
                "chapter_role": "常规章节",
                "chapter_purpose": "内容推进",
                "suspense_level": "中等",
                "foreshadowing": "无",
                "plot_twist_level": "★☆☆☆☆",
                "chapter_summary": f"第{i+1}章内容"
            }
            for i in range(num_chapters)
        ]
    
    def _generate_single_chapter(self, task: GenerationTask, get_config_func: Callable = None) -> GenerationTask:
        """生成单章内容"""
        if self._check_cancelled():
            task.status = GenerationStatus.CANCELLED
            self._update_progress(task.task_id, task.status, 0.0)
            return task
            
        try:
            task.status = GenerationStatus.IN_PROGRESS
            self._update_progress(task.task_id, task.status, 0.0)
            
            config = self._get_task_config("prompt_draft", get_config_func)
            
            chapter_content = generate_chapter_draft(
                api_key=config.get("api_key", ""),
                base_url=config.get("base_url", ""),
                model_name=config.get("model_name", ""),
                filepath=config.get("filepath", "./output"),
                novel_number=task.chapter_num,
                word_number=config.get("word_number", 4000),
                temperature=config.get("temperature", 0.7),
                user_guidance=config.get("user_guidance", ""),
                characters_involved=config.get("characters_involved", ""),
                key_items=config.get("key_items", ""),
                scene_location=config.get("scene_location", ""),
                time_constraint=config.get("time_constraint", ""),
                embedding_api_key=config.get("embedding_api_key", ""),
                embedding_url=config.get("embedding_url", ""),
                embedding_interface_format=config.get("embedding_interface_format", ""),
                embedding_model_name=config.get("embedding_model_name", ""),
                embedding_retrieval_k=config.get("embedding_retrieval_k", 2),
                interface_format=config.get("interface_format", "OpenAI"),
                max_tokens=config.get("max_tokens", 2048),
                timeout=config.get("timeout", 600)
            )
            
            if self._check_cancelled():
                task.status = GenerationStatus.CANCELLED
                self._update_progress(task.task_id, task.status, 0.0)
                return task
            
            task.result = chapter_content
            task.status = GenerationStatus.COMPLETED
            self.completed_tasks += 1
            
            logging.info(f"Chapter {task.chapter_num} generated successfully")
            
        except Exception as e:
            task.error = str(e)
            task.status = GenerationStatus.FAILED
            self.failed_tasks += 1
            
            logging.error(f"Failed to generate chapter {task.chapter_num}: {e}")
            
            if task.retry_count < 2:
                task.retry_count += 1
                task.status = GenerationStatus.PENDING
                logging.info(f"Retrying chapter {task.chapter_num}, attempt {task.retry_count}")
        
        self._update_progress(task.task_id, task.status, 1.0)
        return task
    
    def batch_generate_chapters(self, chapters: List[Dict], start_chapter: int = 1,
                                 get_config_func: Callable = None) -> Dict[int, str]:
        """
        批量生成章节
        
        Args:
            chapters: 章节信息列表
            start_chapter: 起始章节号
            get_config_func: 获取配置的函数
            
        Returns:
            章节编号到内容的映射
        """
        logging.info(f"Batch generating chapters from {start_chapter}")
        
        chapters_to_generate = [c for c in chapters if c['chapter_number'] >= start_chapter]
        
        future_to_task = {}
        for chapter_info in chapters_to_generate:
            if self._check_cancelled():
                break
                
            task_id = f"chapter_{chapter_info['chapter_number']}"
            task = GenerationTask(
                task_id=task_id,
                chapter_num=chapter_info['chapter_number'],
                status=GenerationStatus.PENDING
            )
            self.tasks[task_id] = task
            
            future = self.executor.submit(self._generate_single_chapter, task, get_config_func)
            future_to_task[future] = task
        
        self.total_tasks = len(future_to_task)
        self.completed_tasks = 0
        self.failed_tasks = 0
        
        results = {}
        for future in as_completed(future_to_task):
            if self._check_cancelled():
                break
                
            task = future_to_task[future]
            try:
                completed_task = future.result(timeout=600)
                if completed_task.status == GenerationStatus.COMPLETED:
                    results[completed_task.chapter_num] = completed_task.result
                elif completed_task.status == GenerationStatus.CANCELLED:
                    logging.info(f"Task {task.task_id} was cancelled")
            except Exception as e:
                logging.error(f"Task {task.task_id} failed with exception: {e}")
                task.status = GenerationStatus.FAILED
                self.failed_tasks += 1
        
        logging.info(f"Batch generation completed: {len(results)} success, {self.failed_tasks} failed")
        return results
    
    def check_consistency_all(self, chapters: Dict[int, str], 
                               get_config_func: Callable = None) -> Dict[int, str]:
        """
        检查所有章节的一致性
        
        Args:
            chapters: 章节内容映射
            get_config_func: 获取配置的函数
            
        Returns:
            一致性检查结果
        """
        logging.info("Starting consistency check for all chapters")
        
        config = self._get_task_config("consistency_review", get_config_func)
        consistency_results = {}
        
        for chapter_num, chapter_text in chapters.items():
            if self._check_cancelled():
                break
                
            try:
                filepath = config.get("filepath", "./output")
                
                novel_setting = read_file(os.path.join(filepath, "Novel_architecture.txt"))
                character_state = read_file(os.path.join(filepath, "character_state.txt"))
                global_summary = read_file(os.path.join(filepath, "global_summary.txt"))
                
                consistency_result = check_consistency(
                    novel_setting=novel_setting,
                    character_state=character_state,
                    global_summary=global_summary,
                    chapter_text=chapter_text,
                    api_key=config.get("api_key", ""),
                    base_url=config.get("base_url", ""),
                    model_name=config.get("model_name", ""),
                    temperature=0.3,
                    plot_arcs="",
                    interface_format=config.get("interface_format", "OpenAI"),
                    max_tokens=1024,
                    timeout=300
                )
                
                consistency_results[chapter_num] = consistency_result
                
                if "冲突" in consistency_result and "无明显冲突" not in consistency_result:
                    logging.warning(f"Consistency issues found in chapter {chapter_num}")
                    
            except Exception as e:
                logging.error(f"Consistency check failed for chapter {chapter_num}: {e}")
                consistency_results[chapter_num] = f"检查失败: {str(e)}"
        
        return consistency_results
    
    def one_click_generate_from_chapter(self, topic: str, genre: str, num_chapters: int,
                                         start_chapter: int = 1,
                                         get_config_func: Callable = None) -> Dict:
        """
        一键生成完整小说（从指定章节开始）
        
        Args:
            topic: 小说主题
            genre: 小说类型
            num_chapters: 章节数量
            start_chapter: 起始章节号
            get_config_func: 获取配置的函数
            
        Returns:
            生成结果字典
        """
        logging.info(f"Starting one-click generation from chapter {start_chapter}")
        
        filepath = None
        
        try:
            self._update_progress("pipeline", GenerationStatus.IN_PROGRESS, 0.1)
            
            if start_chapter == 1:
                self.generate_novel_setting(topic, genre, num_chapters, get_config_func)
            
            if self._check_cancelled():
                return self._create_cancelled_result(filepath)
            
            current_config = self._get_task_config("architecture", get_config_func)
            filepath = current_config.get("filepath", "./output")
            
            self._update_progress("pipeline", GenerationStatus.IN_PROGRESS, 0.2)
            setting = read_file(os.path.join(filepath, "Novel_architecture.txt"))
            chapters = self.generate_chapter_directory(setting, num_chapters)
            
            if self._check_cancelled():
                return self._create_cancelled_result(filepath)
            
            self._update_progress("pipeline", GenerationStatus.IN_PROGRESS, 0.3)
            chapter_results = self.batch_generate_chapters(chapters, start_chapter, get_config_func)
            
            if self._check_cancelled():
                return self._create_cancelled_result(filepath)
            
            self._update_progress("pipeline", GenerationStatus.IN_PROGRESS, 0.8)
            consistency_results = self.check_consistency_all(chapter_results, get_config_func)
            
            self._update_progress("pipeline", GenerationStatus.IN_PROGRESS, 0.9)
            final_result = {
                "setting": setting,
                "chapters": chapter_results,
                "consistency_results": consistency_results,
                "filepath": filepath,
                "statistics": {
                    "total_chapters": num_chapters,
                    "successful_chapters": len(chapter_results),
                    "failed_chapters": self.failed_tasks,
                    "chapters_with_issues": len([r for r in consistency_results.values() if "冲突" in r and "无明显冲突" not in r])
                }
            }
            
            self._save_final_result(final_result)
            
            self._update_progress("pipeline", GenerationStatus.COMPLETED, 1.0)
            logging.info("One-click generation completed successfully")
            
            return final_result
            
        except Exception as e:
            logging.error(f"One-click generation failed: {e}")
            self._update_progress("pipeline", GenerationStatus.FAILED, 0.0)
            raise
    
    def one_click_generate(self, topic: str, genre: str, num_chapters: int) -> Dict:
        """
        一键生成完整小说（从第1章开始）
        
        Args:
            topic: 小说主题
            genre: 小说类型
            num_chapters: 章节数量
            
        Returns:
            生成结果字典
        """
        return self.one_click_generate_from_chapter(topic, genre, num_chapters, 1, None)
    
    def _create_cancelled_result(self, filepath: str = None) -> Dict:
        """创建取消结果"""
        return {
            "setting": "",
            "chapters": {},
            "consistency_results": {},
            "filepath": filepath or self.config.get("filepath", "./output"),
            "statistics": {
                "total_chapters": self.total_tasks,
                "successful_chapters": self.completed_tasks,
                "failed_chapters": self.failed_tasks,
                "chapters_with_issues": 0,
                "cancelled": True
            }
        }
    
    def _save_final_result(self, result: Dict):
        """保存最终结果到文件"""
        filepath = result.get("filepath", self.config.get("filepath", "./output"))
        os.makedirs(filepath, exist_ok=True)
        
        setting_file = os.path.join(filepath, "final_setting.txt")
        clear_file_content(setting_file)
        save_string_to_txt(result["setting"], setting_file)
        
        chapters_dir = os.path.join(filepath, "final_chapters")
        os.makedirs(chapters_dir, exist_ok=True)
        
        for chapter_num, content in result["chapters"].items():
            chapter_file = os.path.join(chapters_dir, f"chapter_{chapter_num}.txt")
            clear_file_content(chapter_file)
            save_string_to_txt(content, chapter_file)
        
        stats_file = os.path.join(filepath, "generation_statistics.json")
        with open(stats_file, "w", encoding="utf-8") as f:
            json.dump(result["statistics"], f, ensure_ascii=False, indent=2)
        
        logging.info(f"Final results saved to {filepath}")
    
    def cancel_all_tasks(self):
        """取消所有任务"""
        for task in self.tasks.values():
            if task.status == GenerationStatus.PENDING or task.status == GenerationStatus.IN_PROGRESS:
                task.status = GenerationStatus.CANCELLED
        
        logging.info("All tasks cancelled")
    
    def get_task_status(self, task_id: str) -> Optional[GenerationTask]:
        """获取任务状态"""
        return self.tasks.get(task_id)
    
    def get_pipeline_status(self) -> Dict:
        """获取流水线整体状态"""
        return {
            "total_tasks": self.total_tasks,
            "completed_tasks": self.completed_tasks,
            "failed_tasks": self.failed_tasks,
            "pending_tasks": len([t for t in self.tasks.values() if t.status == GenerationStatus.PENDING]),
            "progress": self.completed_tasks / max(self.total_tasks, 1)
        }


if __name__ == "__main__":
    config = {
        "api_key": "your_api_key",
        "base_url": "https://api.openai.com/v1",
        "model_name": "gpt-4",
        "temperature": 0.7,
        "max_tokens": 2048,
        "filepath": "./output",
        "word_number": 4000,
        "embedding_api_key": "your_embedding_api_key",
        "embedding_url": "https://api.openai.com/v1",
        "embedding_model_name": "text-embedding-ada-002",
        "embedding_retrieval_k": 2
    }
    
    pipeline = AutoGenerationPipeline(config)
    
    def progress_callback(progress_info):
        print(f"Progress: {progress_info}")
    
    pipeline.set_progress_callback(progress_callback)
    
    try:
        result = pipeline.one_click_generate(
            topic="科幻冒险故事",
            genre="科幻",
            num_chapters=5
        )
        print("Generation completed!")
        print(f"Statistics: {result['statistics']}")
    except Exception as e:
        print(f"Generation failed: {e}")
