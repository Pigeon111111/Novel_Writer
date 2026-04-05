# model_router/router.py
# -*- coding: utf-8 -*-
"""
多模型路由系统
为不同任务智能选择最优模型，平衡质量与成本
"""
import logging
from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime

from config_manager import ConfigManager


class TaskType(str, Enum):
    ARCHITECTURE = "architecture"
    CHAPTER_OUTLINE = "chapter_outline"
    DRAFT_WRITING = "draft_writing"
    CONSISTENCY_CHECK = "consistency_check"
    FINALIZATION = "finalization"
    AUDIT = "audit"
    REVISION = "revision"


class Priority(str, Enum):
    QUALITY = "quality"
    COST = "cost"
    BALANCED = "balanced"
    SPEED = "speed"


class ModelRouter:
    """
    模型路由器
    根据任务类型和优先级智能选择最优模型
    """
    
    TASK_MODEL_MAPPING = {
        TaskType.ARCHITECTURE: {
            "recommended": ["LongCat-Flash-Thinking-2601", "LongCatChat", "gpt-4"],
            "fallback": ["LongcatLite", "deepseek-chat", "gpt-3.5-turbo"],
            "requirements": {
                "context_window": 32000,
                "reasoning": "high",
                "description": "架构规划需要强大的推理能力"
            }
        },
        TaskType.CHAPTER_OUTLINE: {
            "recommended": ["LongCat-Flash-Thinking-2601", "LongCatChat", "gpt-4"],
            "fallback": ["LongcatLite", "deepseek-chat"],
            "requirements": {
                "context_window": 16000,
                "reasoning": "medium",
                "description": "章节大纲需要良好的结构规划能力"
            }
        },
        TaskType.DRAFT_WRITING: {
            "recommended": ["LongCatChat", "LongcatLite", "gpt-4"],
            "fallback": ["gpt-3.5-turbo", "deepseek-chat"],
            "requirements": {
                "context_window": 8000,
                "creativity": "high",
                "description": "草稿撰写需要高创造性"
            }
        },
        TaskType.CONSISTENCY_CHECK: {
            "recommended": ["LongCat-Flash-Thinking-2601", "LongCatChat", "gpt-4"],
            "fallback": ["LongcatLite", "deepseek-chat"],
            "requirements": {
                "context_window": 16000,
                "reasoning": "high",
                "description": "一致性检查需要强大的逻辑推理"
            }
        },
        TaskType.FINALIZATION: {
            "recommended": ["LongcatLite", "LongCatChat", "gpt-3.5-turbo"],
            "fallback": ["gpt-3.5-turbo", "deepseek-chat"],
            "requirements": {
                "context_window": 4000,
                "speed": "fast",
                "description": "定稿任务需要快速响应"
            }
        },
        TaskType.AUDIT: {
            "recommended": ["LongCat-Flash-Thinking-2601", "LongCatChat", "gpt-4"],
            "fallback": ["LongcatLite", "deepseek-chat"],
            "requirements": {
                "context_window": 16000,
                "reasoning": "high",
                "description": "审计任务需要深度分析能力"
            }
        },
        TaskType.REVISION: {
            "recommended": ["LongCatChat", "LongcatLite", "gpt-4"],
            "fallback": ["gpt-3.5-turbo", "deepseek-chat"],
            "requirements": {
                "context_window": 8000,
                "creativity": "medium",
                "description": "修订任务需要平衡创造性和准确性"
            }
        }
    }
    
    LONGCAT_MODELS = {
        "LongCatChat": {
            "max_tokens": 65536,
            "cost_per_1k_tokens": 0.001,
            "speed": "medium",
            "quality": "high"
        },
        "LongcatLite": {
            "max_tokens": 65536,
            "cost_per_1k_tokens": 0.0005,
            "speed": "fast",
            "quality": "medium"
        },
        "LongCat-Flash-Thinking-2601": {
            "max_tokens": 65536,
            "cost_per_1k_tokens": 0.002,
            "speed": "slow",
            "quality": "very_high"
        }
    }
    
    def __init__(self, config_manager: ConfigManager):
        """
        初始化模型路由器
        
        Args:
            config_manager: 配置管理器实例
        """
        self.config_manager = config_manager
        self.available_models = self._load_available_models()
        self.performance_history: List[Dict] = []
        
        logging.info(f"ModelRouter initialized with {len(self.available_models)} available models")
    
    def _load_available_models(self) -> Dict[str, Dict]:
        """
        加载可用模型配置
        
        Returns:
            可用模型字典
        """
        available = {}
        
        llm_configs = self.config_manager.get("llm_configs", {})
        
        logging.info(f"Found {len(llm_configs)} model configs")
        
        for model_name, config in llm_configs.items():
            api_key = config.get("api_key", "")
            logging.debug(f"Checking model {model_name}: api_key length = {len(api_key) if api_key else 0}")
            
            available[model_name] = {
                "config": config,
                "is_longcat": "LongCat" in model_name,
                "max_tokens": config.get("max_tokens", 4096),
                "temperature": config.get("temperature", 0.7)
            }
        
        logging.info(f"Available models: {list(available.keys())}")
        return available
    
    def select_model(self, task_type: TaskType, priority: Priority = Priority.BALANCED) -> Dict:
        """
        选择最优模型
        
        Args:
            task_type: 任务类型
            priority: 优先级策略
            
        Returns:
            选中的模型配置
        """
        task_config = self.TASK_MODEL_MAPPING.get(task_type, {})
        
        if priority == Priority.QUALITY:
            candidates = task_config.get("recommended", [])
        elif priority == Priority.COST:
            candidates = task_config.get("fallback", [])
        elif priority == Priority.SPEED:
            candidates = self._get_fast_models(task_config)
        else:  # BALANCED
            candidates = task_config.get("recommended", []) + task_config.get("fallback", [])
        
        for model_name in candidates:
            if model_name in self.available_models:
                selected = self.available_models[model_name]
                logging.info(f"Selected model {model_name} for task {task_type} with priority {priority}")
                return {
                    "model_name": model_name,
                    "config": selected["config"],
                    "is_longcat": selected["is_longcat"]
                }
        
        default_model = self.config_manager.get("choose_configs", {}).get("prompt_draft_llm", "LongCatChat")
        if default_model in self.available_models:
            selected = self.available_models[default_model]
            logging.warning(f"No suitable model found, using default: {default_model}")
            return {
                "model_name": default_model,
                "config": selected["config"],
                "is_longcat": selected["is_longcat"]
            }
        
        raise RuntimeError("No available models found")
    
    def _get_fast_models(self, task_config: Dict) -> List[str]:
        """
        获取快速模型列表
        
        Args:
            task_config: 任务配置
            
        Returns:
            快速模型列表
        """
        fast_models = []
        
        for model_name in task_config.get("recommended", []) + task_config.get("fallback", []):
            if model_name in self.LONGCAT_MODELS:
                if self.LONGCAT_MODELS[model_name]["speed"] == "fast":
                    fast_models.append(model_name)
            elif "lite" in model_name.lower() or "flash" in model_name.lower():
                fast_models.append(model_name)
        
        if not fast_models:
            fast_models = task_config.get("fallback", [])
        
        return fast_models
    
    def estimate_cost(self, task_type: TaskType, estimated_tokens: int) -> Dict:
        """
        估算任务成本
        
        Args:
            task_type: 任务类型
            estimated_tokens: 预估token数
            
        Returns:
            成本估算字典
        """
        estimates = {}
        
        for priority in [Priority.QUALITY, Priority.COST, Priority.BALANCED]:
            try:
                model_info = self.select_model(task_type, priority)
                model_name = model_info["model_name"]
                
                if model_name in self.LONGCAT_MODELS:
                    cost_per_1k = self.LONGCAT_MODELS[model_name]["cost_per_1k_tokens"]
                else:
                    cost_per_1k = 0.001
                
                estimated_cost = (estimated_tokens / 1000) * cost_per_1k
                
                estimates[priority.value] = {
                    "model": model_name,
                    "estimated_cost": estimated_cost,
                    "estimated_tokens": estimated_tokens
                }
            except Exception as e:
                logging.error(f"Failed to estimate cost for priority {priority}: {e}")
        
        return estimates
    
    def record_performance(self, task_type: TaskType, model_name: str,
                          quality_score: float, latency: float, 
                          tokens_used: int, cost: float):
        """
        记录模型性能
        
        Args:
            task_type: 任务类型
            model_name: 模型名称
            quality_score: 质量评分（0-1）
            latency: 延迟（秒）
            tokens_used: 使用的token数
            cost: 成本
        """
        record = {
            "task_type": task_type.value,
            "model": model_name,
            "quality_score": quality_score,
            "latency": latency,
            "tokens_used": tokens_used,
            "cost": cost,
            "timestamp": datetime.now().isoformat()
        }
        
        self.performance_history.append(record)
        
        if len(self.performance_history) % 100 == 0:
            self._analyze_performance()
    
    def _analyze_performance(self):
        """
        分析性能历史，优化模型选择策略
        """
        if not self.performance_history:
            return
        
        model_stats = {}
        
        for record in self.performance_history:
            model = record["model"]
            if model not in model_stats:
                model_stats[model] = {
                    "total_calls": 0,
                    "total_cost": 0,
                    "avg_quality": 0,
                    "avg_latency": 0,
                    "quality_scores": []
                }
            
            stats = model_stats[model]
            stats["total_calls"] += 1
            stats["total_cost"] += record["cost"]
            stats["quality_scores"].append(record["quality_score"])
        
        for model, stats in model_stats.items():
            if stats["quality_scores"]:
                stats["avg_quality"] = sum(stats["quality_scores"]) / len(stats["quality_scores"])
        
        logging.info(f"Performance analysis: {len(model_stats)} models tracked")
    
    def get_recommended_model_for_task(self, task_type: TaskType) -> str:
        """
        获取任务的推荐模型（简化接口）
        
        Args:
            task_type: 任务类型
            
        Returns:
            推荐的模型名称
        """
        model_info = self.select_model(task_type, Priority.BALANCED)
        return model_info["model_name"]
    
    def get_longcat_models(self) -> List[str]:
        """
        获取所有可用的LongCat模型
        
        Returns:
            LongCat模型列表
        """
        return [
            name for name, info in self.available_models.items()
            if info["is_longcat"]
        ]
    
    def refresh_models(self):
        """
        刷新可用模型列表
        """
        self.available_models = self._load_available_models()
        logging.info("Model list refreshed")
