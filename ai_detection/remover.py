# ai_detection/remover.py
# -*- coding: utf-8 -*-
"""
AI痕迹消除器
消除文本中的AI生成痕迹
"""
import re
import logging
from typing import Dict, List


class AITraceRemover:
    """
    AI痕迹消除器
    通过重写和替换消除AI生成痕迹
    """
    
    REPLACEMENT_RULES = {
        "然而，": ["可是，", "但是，", "不过，"],
        "然而,": ["可是,", "但是,", "不过,"],
        "就在这时，": ["突然，", "忽然，", "这时，"],
        "就在这时,": ["突然,", "忽然,", "这时,"],
        "不禁": ["忍不住", "不由得", "不由"],
        "心中": ["心里", "心头", "内心"],
        "涌起": ["升起", "产生", "泛起"],
        "一股": ["一阵", "一种", "一丝"],
        "涌上心头": ["涌上心间", "涌上心头", "浮上心头"],
        "仿佛": ["好像", "似乎", "宛如"],
        "如同": ["好像", "仿佛", "犹如"],
        "可以说，": ["可以说", ""],
        "可以说,": ["可以说", ""],
        "不得不说，": ["不得不说", ""],
        "不得不说,": ["不得不说", ""],
        "众所周知，": ["", "大家都知道，"],
        "众所周知,": ["", "大家都知道,"],
        "总而言之，": ["总之，", "总的来说，"],
        "总而言之,": ["总之,", "总的来说,"],
        "综上所述，": ["综上，", "总的来说，"],
        "综上所述,": ["综上,", "总的来说,"],
    }
    
    def __init__(self, llm_adapter, config: Dict):
        """
        初始化消除器
        
        Args:
            llm_adapter: LLM适配器
            config: 配置字典
        """
        self.llm = llm_adapter
        self.config = config
        self.max_iterations = config.get("max_iterations", 3)
        self.auto_remove = config.get("auto_remove_traces", True)
        
        logging.info("AITraceRemover initialized")
    
    def remove_traces(self, content: str, detection_result: Dict) -> str:
        """
        消除AI痕迹
        
        Args:
            content: 文本内容
            detection_result: 检测结果
            
        Returns:
            处理后的文本
        """
        if not self.auto_remove:
            return content
        
        processed_content = content
        
        processed_content = self._apply_replacement_rules(processed_content)
        
        if detection_result["score"] > 0.3:
            processed_content = self._style_rewrite(processed_content)
        
        for _ in range(self.max_iterations):
            from .detector import AITraceDetector
            detector = AITraceDetector(self.config)
            new_detection = detector.detect(processed_content)
            
            if new_detection["passed"]:
                break
            
            processed_content = self._targeted_fix(
                processed_content, 
                new_detection["issues"]
            )
        
        return processed_content
    
    def _apply_replacement_rules(self, content: str) -> str:
        """应用替换规则"""
        for old, replacements in self.REPLACEMENT_RULES.items():
            if old in content:
                import random
                new = random.choice(replacements)
                content = content.replace(old, new, 1)
        
        return content
    
    def _style_rewrite(self, content: str) -> str:
        """风格重写"""
        prompt = f"""
请对以下文本进行风格重写，使其更自然、更有人味：

要求：
1. 保持原意不变
2. 增加口语化表达
3. 减少书面化、程式化表达
4. 增加情感波动和个性化描写
5. 避免AI生成的典型特征（如"然而"、"就在这时"等）

原文：
{content[:1000]}

请返回重写后的文本。
"""
        
        try:
            rewritten = self.llm.invoke(prompt)
            return rewritten if rewritten else content
        except Exception as e:
            logging.error(f"Style rewrite failed: {e}")
            return content
    
    def _targeted_fix(self, content: str, issues: List[Dict]) -> str:
        """针对性修复"""
        for issue in issues:
            if issue["type"] == "forbidden_pattern":
                pattern = issue["pattern"]
                examples = issue.get("examples", [])
                
                for example in examples:
                    if example in self.REPLACEMENT_RULES:
                        import random
                        replacement = random.choice(self.REPLACEMENT_RULES[example])
                        content = content.replace(example, replacement, 1)
        
        return content
