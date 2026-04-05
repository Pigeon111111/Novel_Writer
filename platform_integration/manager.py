# platform_integration/manager.py
# -*- coding: utf-8 -*-
"""
平台管理器
统一管理多个平台的接入和投稿
"""
import logging
from typing import Dict, List, Optional

from .adapter import PlatformAdapter
from .fanqie import FanqieWriterAdapter
from .lianzi import LianziWorkshopAdapter


class PlatformManager:
    """
    平台管理器
    管理多个平台的接入和自动投稿
    """
    
    ADAPTERS = {
        "fanqie": FanqieWriterAdapter,
        "lianzi": LianziWorkshopAdapter
    }
    
    def __init__(self, config: Dict):
        """
        初始化平台管理器
        
        Args:
            config: 配置字典
        """
        self.config = config
        self.adapters: Dict[str, PlatformAdapter] = {}
        
        logging.info("PlatformManager initialized")
    
    def register_platform(self, platform_name: str, credentials: Dict) -> bool:
        """
        注册平台
        
        Args:
            platform_name: 平台名称
            credentials: 登录凭证
            
        Returns:
            是否注册成功
        """
        if platform_name not in self.ADAPTERS:
            logging.error(f"Unsupported platform: {platform_name}")
            return False
        
        platform_config = self.config.get(f"platform_configs.{platform_name}", {})
        platform_config.update(credentials)
        
        adapter_class = self.ADAPTERS[platform_name]
        adapter = adapter_class(platform_config)
        
        if adapter.login(credentials):
            self.adapters[platform_name] = adapter
            logging.info(f"Platform {platform_name} registered successfully")
            return True
        else:
            logging.error(f"Failed to register platform {platform_name}")
            return False
    
    async def publish_to_multiple(self, novel_id: str, chapter_num: int,
                                  title: str, content: str,
                                  platforms: List[str]) -> Dict[str, Dict]:
        """
        发布到多个平台
        
        Args:
            novel_id: 小说ID
            chapter_num: 章节号
            title: 章节标题
            content: 章节内容
            platforms: 平台列表
            
        Returns:
            各平台的发布结果
        """
        results = {}
        
        for platform_name in platforms:
            if platform_name not in self.adapters:
                results[platform_name] = {
                    "success": False,
                    "error": "Platform not registered"
                }
                continue
            
            adapter = self.adapters[platform_name]
            result = adapter.upload_chapter(novel_id, chapter_num, title, content)
            results[platform_name] = result
        
        return results
    
    def get_platform_status(self, platform_name: str) -> Dict:
        """
        获取平台状态
        
        Args:
            platform_name: 平台名称
            
        Returns:
            平台状态信息
        """
        if platform_name not in self.adapters:
            return {
                "registered": False,
                "logged_in": False
            }
        
        adapter = self.adapters[platform_name]
        return {
            "registered": True,
            "logged_in": adapter.is_logged_in()
        }
    
    def get_all_platforms_status(self) -> Dict[str, Dict]:
        """
        获取所有平台状态
        
        Returns:
            所有平台的状态信息
        """
        status = {}
        
        for platform_name in self.ADAPTERS.keys():
            status[platform_name] = self.get_platform_status(platform_name)
        
        return status
    
    def unregister_platform(self, platform_name: str):
        """
        注销平台
        
        Args:
            platform_name: 平台名称
        """
        if platform_name in self.adapters:
            self.adapters[platform_name].logout()
            del self.adapters[platform_name]
            logging.info(f"Platform {platform_name} unregistered")
    
    def get_supported_platforms(self) -> List[str]:
        """
        获取支持的平台列表
        
        Returns:
            平台名称列表
        """
        return list(self.ADAPTERS.keys())
