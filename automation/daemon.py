# automation/daemon.py
# -*- coding: utf-8 -*-
"""
守护进程模式
支持后台自动生成，无需人工值守
"""
import asyncio
import signal
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional

from .pipeline import AutomatedPipeline
from config_manager import ConfigManager


class DaemonMode:
    """
    守护进程模式
    支持7x24小时自动生成
    """
    
    def __init__(self, pipeline: AutomatedPipeline):
        """
        初始化守护进程
        
        Args:
            pipeline: 自动化管线实例
        """
        self.pipeline = pipeline
        self.running = False
        self.pid_file = Path("daemon.pid")
        
        logging.info("DaemonMode initialized")
    
    async def start_daemon(self, config: dict):
        """
        启动守护进程
        
        Args:
            config: 守护进程配置
        """
        if self._is_running():
            raise RuntimeError("Daemon is already running")
        
        self._write_pid()
        
        signal.signal(signal.SIGTERM, self._handle_shutdown)
        signal.signal(signal.SIGINT, self._handle_shutdown)
        
        self.running = True
        await self._main_loop(config)
    
    async def _main_loop(self, config: dict):
        """
        主循环
        
        Args:
            config: 配置字典
        """
        while self.running:
            try:
                if self._should_generate_next():
                    next_chapter = self._get_next_chapter()
                    
                    await self.pipeline.run_full_pipeline(
                        start_chapter=next_chapter,
                        end_chapter=next_chapter,
                        auto_mode=True
                    )
                
                await asyncio.sleep(60)
                
            except Exception as e:
                logging.error(f"Daemon error: {e}")
                await asyncio.sleep(300)
    
    def _should_generate_next(self) -> bool:
        """判断是否应该生成下一章"""
        return True
    
    def _get_next_chapter(self) -> int:
        """获取下一章号"""
        return 1
    
    def _is_running(self) -> bool:
        """检查是否已有守护进程运行"""
        if not self.pid_file.exists():
            return False
        
        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            import os
            try:
                os.kill(pid, 0)
                return True
            except OSError:
                self.pid_file.unlink()
                return False
        except:
            return False
    
    def _write_pid(self):
        """写入PID文件"""
        import os
        with open(self.pid_file, 'w') as f:
            f.write(str(os.getpid()))
    
    def _handle_shutdown(self, signum, frame):
        """处理关闭信号"""
        logging.info(f"Received signal {signum}, shutting down daemon")
        self.running = False
    
    def stop_daemon(self):
        """停止守护进程"""
        self.running = False
        if self.pid_file.exists():
            self.pid_file.unlink()
        logging.info("Daemon stopped")
