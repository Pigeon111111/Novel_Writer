# ai_detection/detector.py
# -*- coding: utf-8 -*-
"""
AI痕迹检测器
检测文本中的AI生成痕迹
"""
import re
import logging
from typing import Dict, List, Tuple
from pathlib import Path


class AITraceDetector:
    """
    AI痕迹检测器
    使用规则和启发式方法检测AI生成文本的特征
    """
    
    FORBIDDEN_PATTERNS = [
        (r"然而[，,]?\s*.*?却", "转折句式过于程式化"),
        (r"就在这时[，,]?", "时间过渡词使用频繁"),
        (r"不禁.*?起来", "情感表达模式化"),
        (r"心中.*?涌起", "内心描写程式化"),
        (r"一股.*?涌上心头", "情感描写模板化"),
        (r"仿佛.*?一般", "比喻句式重复"),
        (r"如同.*?一样", "比喻句式重复"),
        (r"可以说[，,]?", "过渡词使用频繁"),
        (r"不得不说[，,]?", "过渡词使用频繁"),
        (r"众所周知[，,]?", "开头程式化"),
        (r"总而言之[，,]?", "结尾程式化"),
        (r"综上所述[，,]?", "结尾程式化"),
    ]
    
    def __init__(self, config: Dict):
        """
        初始化检测器
        
        Args:
            config: 配置字典
        """
        self.config = config
        self.detection_threshold = config.get("detection_threshold", 0.3)
        self.enabled = config.get("enabled", True)
        
        logging.info("AITraceDetector initialized")
    
    def detect(self, content: str) -> Dict:
        """
        检测AI痕迹
        
        Args:
            content: 文本内容
            
        Returns:
            检测结果字典
        """
        if not self.enabled:
            return {
                "score": 0.0,
                "issues": [],
                "passed": True
            }
        
        issues = []
        total_score = 0.0
        
        for pattern, description in self.FORBIDDEN_PATTERNS:
            matches = re.findall(pattern, content)
            if matches:
                count = len(matches)
                score = count * 0.05
                total_score += score
                issues.append({
                    "type": "forbidden_pattern",
                    "pattern": pattern,
                    "description": description,
                    "count": count,
                    "score": score,
                    "examples": matches[:3]
                })
        
        repetition_score = self._check_repetition(content)
        if repetition_score > 0:
            total_score += repetition_score
            issues.append({
                "type": "repetition",
                "description": "内容重复度较高",
                "score": repetition_score
            })
        
        vocabulary_score = self._check_vocabulary_diversity(content)
        if vocabulary_score > 0:
            total_score += vocabulary_score
            issues.append({
                "type": "vocabulary",
                "description": "词汇多样性不足",
                "score": vocabulary_score
            })
        
        sentence_score = self._check_sentence_structure(content)
        if sentence_score > 0:
            total_score += sentence_score
            issues.append({
                "type": "sentence",
                "description": "句式结构单一",
                "score": sentence_score
            })
        
        passed = total_score < self.detection_threshold
        
        return {
            "score": total_score,
            "issues": issues,
            "passed": passed,
            "threshold": self.detection_threshold
        }
    
    def _check_repetition(self, content: str) -> float:
        """检查内容重复度"""
        sentences = re.split(r'[。！？\n]', content)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
        
        if not sentences:
            return 0.0
        
        unique_sentences = set(sentences)
        repetition_rate = 1 - len(unique_sentences) / len(sentences)
        
        if repetition_rate > 0.3:
            return repetition_rate * 0.5
        
        return 0.0
    
    def _check_vocabulary_diversity(self, content: str) -> float:
        """检查词汇多样性"""
        words = re.findall(r'[\u4e00-\u9fa5]+', content)
        
        if not words:
            return 0.0
        
        unique_words = set(words)
        diversity_rate = len(unique_words) / len(words)
        
        if diversity_rate < 0.3:
            return (0.3 - diversity_rate) * 0.5
        
        return 0.0
    
    def _check_sentence_structure(self, content: str) -> float:
        """检查句式结构"""
        sentences = re.split(r'[。！？]', content)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 5]
        
        if not sentences:
            return 0.0
        
        structures = []
        for sentence in sentences:
            if "，" in sentence:
                parts = sentence.split("，")
                structure = f"{len(parts)}段"
                structures.append(structure)
        
        if not structures:
            return 0.0
        
        from collections import Counter
        structure_counts = Counter(structures)
        most_common_count = structure_counts.most_common(1)[0][1]
        
        repetition_rate = most_common_count / len(structures)
        
        if repetition_rate > 0.5:
            return repetition_rate * 0.3
        
        return 0.0
