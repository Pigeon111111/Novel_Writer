# audit_system/__init__.py
# -*- coding: utf-8 -*-
"""
审计系统模块
"""
from .dimensions import AuditDimension, AuditCategory, Severity
from .result import AuditResult, AuditIssue, AuditReport
from .auditor import MultiDimensionalAuditor

__all__ = [
    'AuditDimension',
    'AuditCategory',
    'Severity',
    'AuditResult',
    'AuditIssue',
    'AuditReport',
    'MultiDimensionalAuditor'
]
