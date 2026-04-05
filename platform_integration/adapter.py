# platform_integration/adapter.py
# -*- coding: utf-8 -*-
"""
平台适配器基类
定义统一的平台接口
"""
from abc import ABC, abstractmethod
from typing import Dict, Optional
import logging


class PlatformAdapter(ABC):
    """
    平台适配器基类
    所有平台适配器都需要实现这个接口
    """
    
    def __init__(self, config: Dict):
        """
        初始化适配器
        
        Args:
            config: 平台配置
        """
        self.config = config
        self.session = None
        self.logged_in = False
        
        logging.info(f"{self.__class__.__name__} initialized")
    
    @abstractmethod
    def login(self, credentials: Dict) -> bool:
        """
        登录平台
        
        Args:
            credentials: 登录凭证
            
        Returns:
            是否登录成功
        """
        pass
    
    @abstractmethod
    def upload_chapter(self, novel_id: str, chapter_num: int,
                      title: str, content: str) -> Dict:
        """
        上传章节
        
        Args:
            novel_id: 小说ID
            chapter_num: 章节号
            title: 章节标题
            content: 章节内容
            
        Returns:
            上传结果
        """
        pass
    
    @abstractmethod
    def get_novel_status(self, novel_id: str) -> Dict:
        """
        获取小说状态
        
        Args:
            novel_id: 小说ID
            
        Returns:
            小说状态信息
        """
        pass
    
    @abstractmethod
    def format_content(self, content: str) -> str:
        """
        格式化内容以符合平台要求
        
        Args:
            content: 原始内容
            
        Returns:
            格式化后的内容
        """
        pass
    
    def logout(self):
        """登出平台"""
        self.logged_in = False
        self.session = None
        logging.info(f"{self.__class__.__name__} logged out")
    
    def is_logged_in(self) -> bool:
        """检查是否已登录"""
        return self.logged_in
