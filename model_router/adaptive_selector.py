# model_router/adaptive_selector.py
# -*- coding: utf-8 -*-
"""
自适应模型选择器
根据性能历史和实时状态智能选择模型
"""
import logging
import time
from typing import Dict, Optional
from datetime import datetime, timedelta

from .router import ModelRouter, TaskType, Priority


class AdaptiveModelSelector:
    """
    自适应模型选择器
    根据性能历史、成本预算和实时可用性智能选择模型
    """
    
    def __init__(self, model_router: ModelRouter):
        """
        初始化自适应选择器
        
        Args:
            model_router: 模型路由器实例
        """
        self.router = model_router
        self.failure_counts: Dict[str, int] = {}
        self.last_failure_time: Dict[str, datetime] = {}
        self.circuit_breaker_timeout = timedelta(minutes=5)
        self.max_failures = 3
        
        logging.info("AdaptiveModelSelector initialized")
    
    def select_with_fallback(self, task_type: TaskType, 
                            context: Optional[Dict] = None) -> Dict:
        """
        智能选择模型，支持自动降级
        
        Args:
            task_type: 任务类型
            context: 上下文信息（可选）
            
        Returns:
            选中的模型配置
        """
        priorities = [Priority.BALANCED, Priority.COST]
        
        for priority in priorities:
            try:
                model_info = self.router.select_model(task_type, priority)
                model_name = model_info["model_name"]
                
                if self._is_model_available(model_name):
                    logging.info(f"Selected model {model_name} with priority {priority}")
                    return model_info
                else:
                    logging.warning(f"Model {model_name} is currently unavailable (circuit breaker)")
                    
            except Exception as e:
                logging.error(f"Failed to select model with priority {priority}: {e}")
                continue
        
        try:
            default_model = self._get_any_available_model()
            logging.warning(f"All preferred models failed, using fallback: {default_model}")
            return default_model
        except Exception as e:
            logging.critical(f"No models available: {e}")
            raise RuntimeError("No available models found after all fallback attempts")
    
    def _is_model_available(self, model_name: str) -> bool:
        """
        检查模型是否可用（熔断器机制）
        
        Args:
            model_name: 模型名称
            
        Returns:
            是否可用
        """
        if model_name not in self.failure_counts:
            return True
        
        failure_count = self.failure_counts[model_name]
        last_failure = self.last_failure_time.get(model_name)
        
        if failure_count < self.max_failures:
            return True
        
        if last_failure and (datetime.now() - last_failure) > self.circuit_breaker_timeout:
            logging.info(f"Circuit breaker reset for model {model_name}")
            self.failure_counts[model_name] = 0
            return True
        
        return False
    
    def record_success(self, model_name: str):
        """
        记录模型调用成功
        
        Args:
            model_name: 模型名称
        """
        if model_name in self.failure_counts:
            self.failure_counts[model_name] = max(0, self.failure_counts[model_name] - 1)
        
        logging.debug(f"Model {model_name} call succeeded")
    
    def record_failure(self, model_name: str, error: Exception):
        """
        记录模型调用失败
        
        Args:
            model_name: 模型名称
            error: 错误信息
        """
        if model_name not in self.failure_counts:
            self.failure_counts[model_name] = 0
        
        self.failure_counts[model_name] += 1
        self.last_failure_time[model_name] = datetime.now()
        
        logging.warning(
            f"Model {model_name} call failed (failure count: {self.failure_counts[model_name]}): {error}"
        )
        
        if self.failure_counts[model_name] >= self.max_failures:
            logging.error(
                f"Circuit breaker triggered for model {model_name}. "
                f"Model will be unavailable for {self.circuit_breaker_timeout.total_seconds()} seconds"
            )
    
    def _get_any_available_model(self) -> Dict:
        """
        获取任意可用模型
        
        Returns:
            模型配置
        """
        for model_name in self.router.available_models.keys():
            if self._is_model_available(model_name):
                model_info = self.router.available_models[model_name]
                return {
                    "model_name": model_name,
                    "config": model_info["config"],
                    "is_longcat": model_info["is_longcat"]
                }
        
        raise RuntimeError("No available models found")
    
    def get_model_status(self) -> Dict:
        """
        获取所有模型的状态
        
        Returns:
            模型状态字典
        """
        status = {}
        
        for model_name in self.router.available_models.keys():
            is_available = self._is_model_available(model_name)
            failure_count = self.failure_counts.get(model_name, 0)
            last_failure = self.last_failure_time.get(model_name)
            
            status[model_name] = {
                "available": is_available,
                "failure_count": failure_count,
                "last_failure": last_failure.isoformat() if last_failure else None,
                "circuit_breaker_active": failure_count >= self.max_failures
            }
        
        return status
    
    def reset_circuit_breaker(self, model_name: Optional[str] = None):
        """
        重置熔断器
        
        Args:
            model_name: 指定模型名称，如果为None则重置所有
        """
        if model_name:
            if model_name in self.failure_counts:
                self.failure_counts[model_name] = 0
                logging.info(f"Circuit breaker reset for model {model_name}")
        else:
            self.failure_counts.clear()
            self.last_failure_time.clear()
            logging.info("All circuit breakers reset")
    
    def test_model_availability(self, model_name: str, timeout: int = 5) -> bool:
        """
        测试模型可用性
        
        Args:
            model_name: 模型名称
            timeout: 超时时间（秒）
            
        Returns:
            是否可用
        """
        if model_name not in self.router.available_models:
            return False
        
        try:
            from llm_adapters import create_llm_adapter
            
            model_info = self.router.available_models[model_name]
            config = model_info["config"]
            
            adapter = create_llm_adapter(
                interface_format=config.get("interface_format", "OpenAI"),
                base_url=config.get("base_url"),
                model_name=config.get("model_name"),
                api_key=config.get("api_key"),
                temperature=0.1,
                max_tokens=10,
                timeout=timeout
            )
            
            start_time = time.time()
            response = adapter.invoke("测试")
            latency = time.time() - start_time
            
            if response:
                self.record_success(model_name)
                logging.info(f"Model {model_name} availability test passed (latency: {latency:.2f}s)")
                return True
            else:
                return False
                
        except Exception as e:
            self.record_failure(model_name, e)
            logging.error(f"Model {model_name} availability test failed: {e}")
            return False
    
    def get_best_model_for_cost(self, task_type: TaskType, 
                                max_cost: float) -> Optional[Dict]:
        """
        根据成本预算选择最佳模型
        
        Args:
            task_type: 任务类型
            max_cost: 最大成本（美元）
            
        Returns:
            模型配置，如果没有符合条件的模型则返回None
        """
        estimated_tokens = 4000
        
        cost_estimates = self.router.estimate_cost(task_type, estimated_tokens)
        
        for priority in [Priority.COST, Priority.BALANCED, Priority.QUALITY]:
            if priority.value in cost_estimates:
                estimate = cost_estimates[priority.value]
                if estimate["estimated_cost"] <= max_cost:
                    model_name = estimate["model"]
                    if self._is_model_available(model_name):
                        return self.router.available_models[model_name]
        
        return None
