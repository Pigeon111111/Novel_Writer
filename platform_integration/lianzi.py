# platform_integration/lianzi.py
# -*- coding: utf-8 -*-
"""
炼字工坊平台适配器
"""
import logging
from typing import Dict
import requests

from .adapter import PlatformAdapter


class LianziWorkshopAdapter(PlatformAdapter):
    """
    炼字工坊适配器
    支持自动投稿到炼字工坊平台
    """
    
    BASE_URL = "https://lianzigongfang.com"
    
    def __init__(self, config: Dict):
        """
        初始化炼字工坊适配器
        
        Args:
            config: 配置字典
        """
        super().__init__(config)
        self.api_key = config.get("api_key", "")
        self.user_id = config.get("user_id", "")
        
        logging.info("LianziWorkshopAdapter initialized")
    
    def login(self, credentials: Dict) -> bool:
        """
        登录炼字工坊
        
        Args:
            credentials: 登录凭证
            
        Returns:
            是否登录成功
        """
        try:
            if "api_key" in credentials:
                self.api_key = credentials["api_key"]
                self.user_id = credentials.get("user_id", "")
                
                self.session = requests.Session()
                self.session.headers.update({
                    "Authorization": f"Bearer {self.api_key}",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                })
                
                self.logged_in = True
                logging.info("Lianzi login successful")
                return True
            
            else:
                logging.error("No valid credentials provided")
                return False
                
        except Exception as e:
            logging.error(f"Lianzi login failed: {e}")
            return False
    
    def upload_chapter(self, novel_id: str, chapter_num: int,
                      title: str, content: str) -> Dict:
        """
        上传章节到炼字工坊
        
        Args:
            novel_id: 小说ID
            chapter_num: 章节号
            title: 章节标题
            content: 章节内容
            
        Returns:
            上传结果
        """
        if not self.logged_in:
            return {
                "success": False,
                "error": "Not logged in"
            }
        
        try:
            formatted_content = self.format_content(content)
            
            endpoint = f"{self.BASE_URL}/api/v1/novels/{novel_id}/chapters"
            
            payload = {
                "chapter_number": chapter_num,
                "title": title,
                "content": formatted_content,
                "user_id": self.user_id
            }
            
            response = self.session.post(endpoint, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                logging.info(f"Chapter {chapter_num} uploaded successfully to Lianzi")
                return {
                    "success": True,
                    "chapter_id": data.get("chapter_id"),
                    "message": "上传成功"
                }
            else:
                error_msg = f"HTTP {response.status_code}: {response.text}"
                logging.error(f"Failed to upload chapter: {error_msg}")
                return {
                    "success": False,
                    "error": error_msg
                }
                
        except Exception as e:
            logging.error(f"Exception during upload: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_novel_status(self, novel_id: str) -> Dict:
        """
        获取小说状态
        
        Args:
            novel_id: 小说ID
            
        Returns:
            小说状态信息
        """
        if not self.logged_in:
            return {
                "success": False,
                "error": "Not logged in"
            }
        
        try:
            endpoint = f"{self.BASE_URL}/api/v1/novels/{novel_id}"
            response = self.session.get(endpoint)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "status": data.get("status"),
                    "chapter_count": data.get("chapter_count"),
                    "word_count": data.get("word_count")
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}"
                }
                
        except Exception as e:
            logging.error(f"Failed to get novel status: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def format_content(self, content: str) -> str:
        """
        格式化内容以符合炼字工坊要求
        
        Args:
            content: 原始内容
            
        Returns:
            格式化后的内容
        """
        formatted = content.strip()
        formatted = formatted.replace('\r\n', '\n')
        formatted = formatted.replace('\r', '\n')
        
        while '\n\n\n' in formatted:
            formatted = formatted.replace('\n\n\n', '\n\n')
        
        return formatted
