# config_manager.py
# -*- coding: utf-8 -*-
"""
配置管理器 - 支持个人配置优先
"""
import json
import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional


class ConfigManager:
    """
    配置管理器
    支持三层配置优先级：
    1. 个人配置（最高优先级）- config.json
    2. 项目默认配置 - config.default.json
    3. 系统默认配置（最低优先级）
    """
    
    DEFAULT_CONFIG = {
        "last_interface_format": "OpenAI",
        "last_embedding_interface_format": "OpenAI",
        "llm_configs": {},
        "embedding_configs": {},
        "other_params": {
            "topic": "",
            "genre": "",
            "num_chapters": 0,
            "word_number": 0,
            "filepath": "",
            "chapter_num": "120",
            "user_guidance": "",
            "characters_involved": "",
            "key_items": "",
            "scene_location": "",
            "time_constraint": ""
        },
        "choose_configs": {
            "prompt_draft_llm": "LongCatChat",
            "chapter_outline_llm": "LongCat-Flash-Thinking-2601",
            "architecture_llm": "LongCat-Flash-Thinking-2601",
            "final_chapter_llm": "LongcatLite",
            "consistency_review_llm": "LongCat-Flash-Thinking-2601"
        },
        "proxy_setting": {
            "proxy_url": "127.0.0.1",
            "proxy_port": "",
            "enabled": False
        },
        "webdav_config": {
            "webdav_url": "",
            "webdav_username": "",
            "webdav_password": ""
        },
        "audit_config": {
            "enabled": True,
            "auto_fix": False,
            "quality_threshold": 80.0,
            "critical_threshold": 0,
            "major_threshold": 2
        },
        "ai_detection_config": {
            "enabled": True,
            "auto_remove_traces": True,
            "detection_threshold": 0.3,
            "max_iterations": 3
        },
        "automation_config": {
            "enabled": True,
            "auto_mode": False,
            "human_review_gate": True,
            "batch_size": 10,
            "retry_on_failure": 3
        }
    }
    
    def __init__(self, config_file: str = "config.json"):
        """
        初始化配置管理器
        
        Args:
            config_file: 个人配置文件路径
        """
        self.config_file = Path(config_file)
        self.project_root = self.config_file.parent
        
        self._user_config = {}
        self._project_config = {}
        self._merged_config = {}
        
        self._load_all_configs()
        
        logging.info(f"ConfigManager initialized with config file: {config_file}")
    
    def _load_all_configs(self):
        """加载所有配置并合并"""
        self._user_config = self._load_config_file(self.config_file)
        
        project_config_file = self.project_root / "config.default.json"
        self._project_config = self._load_config_file(project_config_file)
        
        self._merged_config = self._deep_merge(
            self.DEFAULT_CONFIG,
            self._project_config,
            self._user_config
        )
        
        logging.info("All configs loaded and merged (user > project > default)")
    
    def _load_config_file(self, config_path: Path) -> Dict:
        """加载配置文件"""
        if not config_path.exists():
            logging.debug(f"Config file not found: {config_path}")
            return {}
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                logging.debug(f"Loaded config from: {config_path}")
                return config
        except Exception as e:
            logging.error(f"Failed to load config from {config_path}: {e}")
            return {}
    
    def _deep_merge(self, *dicts) -> Dict:
        """
        深度合并多个字典（后面的优先级更高）
        
        Args:
            *dicts: 要合并的字典列表
            
        Returns:
            合并后的字典
        """
        result = {}
        
        for d in dicts:
            if not isinstance(d, dict):
                continue
            
            for key, value in d.items():
                if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = self._deep_merge(result[key], value)
                else:
                    result[key] = value
        
        return result
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置项（支持点号分隔的嵌套键）
        
        Args:
            key: 配置键
            default: 默认值
            
        Returns:
            配置值
        """
        keys = key.split('.')
        value = self._merged_config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any, save: bool = True):
        """
        设置配置项（保存到个人配置）
        
        Args:
            key: 配置键
            value: 配置值
            save: 是否立即保存
        """
        keys = key.split('.')
        config = self._user_config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        
        if save:
            self.save_user_config()
        
        self._merged_config = self._deep_merge(
            self.DEFAULT_CONFIG,
            self._project_config,
            self._user_config
        )
    
    def save_user_config(self):
        """保存个人配置到文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self._user_config, f, ensure_ascii=False, indent=4)
            logging.info(f"User config saved to {self.config_file}")
        except Exception as e:
            logging.error(f"Failed to save user config: {e}")
            raise
    
    def reload(self):
        """重新加载所有配置"""
        self._load_all_configs()
        logging.info("Config reloaded")
    
    def get_all(self) -> Dict:
        """获取所有配置（合并后的）"""
        return self._merged_config.copy()
    
    def get_user_config(self) -> Dict:
        """获取个人配置"""
        return self._user_config.copy()
    
    def get_llm_config(self, model_name: str) -> Dict:
        """
        获取指定模型的配置
        
        Args:
            model_name: 模型名称
            
        Returns:
            模型配置字典
        """
        return self._merged_config.get("llm_configs", {}).get(model_name, {})
    
    def get_embedding_config(self, provider: str) -> Dict:
        """
        获取指定embedding提供商的配置
        
        Args:
            provider: 提供商名称
            
        Returns:
            Embedding配置字典
        """
        return self._merged_config.get("embedding_configs", {}).get(provider, {})
    
    def get_audit_config(self) -> Dict:
        """获取审计配置"""
        return self._merged_config.get("audit_config", self.DEFAULT_CONFIG["audit_config"])
    
    def get_ai_detection_config(self) -> Dict:
        """获取AI检测配置"""
        return self._merged_config.get("ai_detection_config", self.DEFAULT_CONFIG["ai_detection_config"])
    
    def get_automation_config(self) -> Dict:
        """获取自动化配置"""
        return self._merged_config.get("automation_config", self.DEFAULT_CONFIG["automation_config"])
    
    def reset_to_default(self, key: Optional[str] = None):
        """
        重置配置为默认值
        
        Args:
            key: 要重置的配置键，None表示重置所有
        """
        if key is None:
            self._user_config = {}
            self.save_user_config()
        else:
            keys = key.split('.')
            config = self._user_config
            
            for k in keys[:-1]:
                if k not in config:
                    return
                config = config[k]
            
            if keys[-1] in config:
                del config[keys[-1]]
                self.save_user_config()
        
        self._load_all_configs()
        logging.info(f"Config reset: {key if key else 'all'}")


def load_config(config_file: str) -> dict:
    """从指定的 config_file 加载配置，若不存在则创建一个默认配置文件。"""
    if not os.path.exists(config_file):
        create_config(config_file)
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}


def create_config(config_file: str) -> dict:
    """创建一个创建默认配置文件。"""
    config = ConfigManager.DEFAULT_CONFIG.copy()
    save_config(config, config_file)


def save_config(config_data: dict, config_file: str) -> bool:
    """将 config_data 保存到 config_file 中，返回 True/False 表示是否成功。"""
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, ensure_ascii=False, indent=4)
        return True
    except:
        return False


def test_llm_config(interface_format, api_key, base_url, model_name, temperature, max_tokens, timeout, log_func, handle_exception_func):
    """测试当前的LLM配置是否可用"""
    from llm_adapters import create_llm_adapter
    import threading
    
    def task():
        try:
            log_func("开始测试LLM配置...")
            llm_adapter = create_llm_adapter(
                interface_format=interface_format,
                base_url=base_url,
                model_name=model_name,
                api_key=api_key,
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=timeout
            )
            
            test_prompt = "Please reply 'OK'"
            response = llm_adapter.invoke(test_prompt)
            if response:
                log_func("LLM配置测试成功！")
                log_func(f"测试回复: {response}")
            else:
                log_func("LLM配置测试失败：未获取到响应")
        except Exception as e:
            log_func(f"LLM配置测试出错: {str(e)}")
            handle_exception_func("测试LLM配置时出错")
    
    threading.Thread(target=task, daemon=True).start()


def test_embedding_config(api_key, base_url, interface_format, model_name, log_func, handle_exception_func):
    """测试当前的Embedding配置是否可用"""
    from embedding_adapters import create_embedding_adapter
    import threading
    
    def task():
        try:
            log_func("开始测试Embedding配置...")
            embedding_adapter = create_embedding_adapter(
                interface_format=interface_format,
                api_key=api_key,
                base_url=base_url,
                model_name=model_name
            )
            
            test_text = "测试文本"
            embeddings = embedding_adapter.embed_query(test_text)
            if embeddings and len(embeddings) > 0:
                log_func("Embedding配置测试成功！")
                log_func(f"生成的向量维度: {len(embeddings)}")
            else:
                log_func("Embedding配置测试失败：未获取到向量")
        except Exception as e:
            log_func(f"Embedding配置测试出错: {str(e)}")
            handle_exception_func("测试Embedding配置时出错")
    
    threading.Thread(target=task, daemon=True).start()
