# platform_integration/__init__.py
# -*- coding: utf-8 -*-
"""
平台集成模块
"""
from .adapter import PlatformAdapter
from .fanqie import FanqieWriterAdapter
from .lianzi import LianziWorkshopAdapter
from .manager import PlatformManager

__all__ = [
    'PlatformAdapter',
    'FanqieWriterAdapter',
    'LianziWorkshopAdapter',
    'PlatformManager'
]
