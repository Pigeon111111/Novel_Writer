# automation/__init__.py
# -*- coding: utf-8 -*-
"""
自动化模块
"""
from .pipeline import AutomatedPipeline
from .daemon import DaemonMode

__all__ = ['AutomatedPipeline', 'DaemonMode']
