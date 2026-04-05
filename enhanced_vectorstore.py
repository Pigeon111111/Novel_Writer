# enhanced_vectorstore.py
# -*- coding: utf-8 -*-
"""
增强型向量检索系统
提供多粒度上下文管理和智能检索功能
"""

import os
import logging
import numpy as np
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import networkx as nx
from collections import defaultdict

from langchain_chroma import Chroma
from langchain.docstore.document import Document
from chromadb.config import Settings
from sklearn.metrics.pairwise import cosine_similarity

from embedding_adapters import create_embedding_adapter
from novel_generator.vectorstore_utils import (
    load_vector_store, init_vector_store, split_text_for_vectorstore
)

logging.basicConfig(
    filename='app.log',
    filemode='a',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


@dataclass
class ContextItem:
    """上下文项数据类"""
    content: str
    metadata: Dict
    embedding: Optional[List[float]] = None
    timestamp: datetime = None
    weight: float = 1.0
    source_type: str = "general"  # setting, character, plot, chapter, knowledge


class EnhancedVectorStore:
    """
    增强型向量检索系统
    提供多粒度上下文管理、时间衰减加权、角色关系图谱等功能
    """
    
    def __init__(self, config: Dict):
        """
        初始化增强向量存储
        
        Args:
            config: 配置字典
        """
        self.config = config
        self.embedding_adapter = None
        self.vector_store = None
        self.context_cache = {}
        self.character_graph = nx.DiGraph()
        self.foreshadowing_tracker = defaultdict(list)
        
        # 初始化嵌入适配器
        self._init_embedding_adapter()
        
        # 加载或创建向量存储
        self._init_vector_store()
        
        # 初始化角色关系图谱
        self._init_character_graph()
        
        logging.info("EnhancedVectorStore initialized successfully")
    
    def _init_embedding_adapter(self):
        """初始化嵌入适配器"""
        try:
            self.embedding_adapter = create_embedding_adapter(
                self.config.get("embedding_interface_format", "OpenAI"),
                self.config.get("embedding_api_key", ""),
                self.config.get("embedding_url", ""),
                self.config.get("embedding_model_name", "")
            )
            logging.info("Embedding adapter initialized")
        except Exception as e:
            logging.error(f"Failed to initialize embedding adapter: {e}")
            raise
    
    def _init_vector_store(self):
        """初始化向量存储"""
        try:
            filepath = self.config.get("filepath", "./output")
            self.vector_store = load_vector_store(self.embedding_adapter, filepath)
            
            if self.vector_store is None:
                # 创建新的向量存储
                self.vector_store = init_vector_store(
                    self.embedding_adapter, 
                    [],  # 空初始化
                    filepath
                )
                logging.info("Created new vector store")
            else:
                logging.info("Loaded existing vector store")
                
        except Exception as e:
            logging.error(f"Failed to initialize vector store: {e}")
            self.vector_store = None
    
    def _init_character_graph(self):
        """初始化角色关系图谱"""
        try:
            # 从现有文件加载角色信息
            filepath = self.config.get("filepath", "./output")
            character_file = os.path.join(filepath, "character_state.txt")
            
            if os.path.exists(character_file):
                character_data = self._parse_character_data(character_file)
                self._build_character_graph(character_data)
                logging.info("Character graph initialized")
        except Exception as e:
            logging.warning(f"Failed to initialize character graph: {e}")
    
    def _parse_character_data(self, character_file: str) -> Dict:
        """解析角色数据"""
        # 简化的解析逻辑，实际应该更复杂
        return {
            "characters": [],
            "relationships": []
        }
    
    def _build_character_graph(self, character_data: Dict):
        """构建角色关系图谱"""
        for char in character_data.get("characters", []):
            self.character_graph.add_node(char["name"], **char)
        
        for rel in character_data.get("relationships", []):
            self.character_graph.add_edge(
                rel["from"], 
                rel["to"], 
                relationship=rel["type"],
                strength=rel.get("strength", 1.0)
            )
    
    def add_context(self, content: str, metadata: Dict, source_type: str = "general"):
        """
        添加上下文到存储
        
        Args:
            content: 内容文本
            metadata: 元数据
            source_type: 来源类型
        """
        try:
            # 创建上下文项
            context_item = ContextItem(
                content=content,
                metadata=metadata,
                timestamp=datetime.now(),
                source_type=source_type
            )
            
            # 生成嵌入
            if self.embedding_adapter:
                embeddings = self.embedding_adapter.embed_documents([content])
                if embeddings and len(embeddings) > 0:
                    context_item.embedding = embeddings[0]
            
            # 添加到向量存储
            if self.vector_store:
                doc = Document(
                    page_content=content,
                    metadata={
                        **metadata,
                        "source_type": source_type,
                        "timestamp": context_item.timestamp.isoformat()
                })
                self.vector_store.add_documents([doc])
            
            # 更新角色图谱
            if source_type == "character" and "character_name" in metadata:
                self._update_character_graph(metadata)
            
            # 更新伏笔追踪
            if "foreshadowing" in metadata:
                self._track_foreshadowing(metadata)
            
            logging.info(f"Added context: {source_type}, metadata: {metadata}")
            
        except Exception as e:
            logging.error(f"Failed to add context: {e}")
    
    def _update_character_graph(self, character_metadata: Dict):
        """更新角色关系图谱"""
        try:
            char_name = character_metadata.get("character_name")
            if char_name:
                if char_name not in self.character_graph:
                    self.character_graph.add_node(char_name, **character_metadata)
                else:
                    # 更新节点属性
                    for key, value in character_metadata.items():
                        self.character_graph.nodes[char_name][key] = value
        except Exception as e:
            logging.warning(f"Failed to update character graph: {e}")
    
    def _track_foreshadowing(self, metadata: Dict):
        """追踪伏笔"""
        try:
            if "foreshadowing" in metadata and "chapter" in metadata:
                chapter_num = metadata["chapter"]
                foreshadowing = metadata["foreshadowing"]
                self.foreshadowing_tracker[chapter_num].append({
                    "content": foreshadowing,
                    "resolved": False,
                    "metadata": metadata
                })
        except Exception as e:
            logging.warning(f"Failed to track foreshadowing: {e}")
    
    def get_enhanced_context(self, query: str, chapter_num: int, k: int = 5) -> Dict:
        """
        获取增强的上下文信息
        
        Args:
            query: 查询文本
            chapter_num: 当前章节号
            k: 检索数量
            
        Returns:
            增强的上下文信息
        """
        try:
            # 1. 向量检索
            vector_results = self._vector_search(query, k)
            
            # 2. 时间衰减加权
            weighted_results = self._apply_temporal_weighting(vector_results, chapter_num)
            
            # 3. 角色关系增强
            character_context = self._get_character_context(chapter_num)
            
            # 4. 伏笔追踪
            foreshadowing_context = self._get_foreshadowing_context(chapter_num)
            
            # 5. 动态上下文压缩
            compressed_context = self._dynamic_context_compression(
                weighted_results + character_context + foreshadowing_context
            )
            
            return {
                "vector_results": vector_results,
                "weighted_results": weighted_results,
                "character_context": character_context,
                "foreshadowing_context": foreshadowing_context,
                "compressed_context": compressed_context
            }
            
        except Exception as e:
            logging.error(f"Failed to get enhanced context: {e}")
            return {"error": str(e)}
    
    def _vector_search(self, query: str, k: int) -> List[ContextItem]:
        """执行向量检索"""
        results = []
        
        try:
            if not self.vector_store:
                return results
            
            # 执行相似性搜索
            docs = self.vector_store.similarity_search(query, k=k)
            
            for doc in docs:
                # 获取嵌入
                embedding = None
                if self.embedding_adapter:
                    embeddings = self.embedding_adapter.embed_documents([doc.page_content])
                    if embeddings and len(embeddings) > 0:
                        embedding = embeddings[0]
                
                # 创建上下文项
                context_item = ContextItem(
                    content=doc.page_content,
                    metadata=doc.metadata,
                    embedding=embedding,
                    source_type=doc.metadata.get("source_type", "general"),
                    timestamp=datetime.fromisoformat(doc.metadata.get("timestamp", datetime.now().isoformat()))
                )
                results.append(context_item)
                
        except Exception as e:
            logging.error(f"Vector search failed: {e}")
        
        return results
    
    def _apply_temporal_weighting(self, results: List[ContextItem], current_chapter: int) -> List[ContextItem]:
        """应用时间衰减加权"""
        weighted_results = []
        
        for item in results:
            # 计算时间距离（基于章节号）
            item_chapter = item.metadata.get("chapter", current_chapter)
            try:
                item_chapter_num = int(item_chapter)
                time_distance = abs(current_chapter - item_chapter_num)
            except:
                time_distance = 10  # 默认值
            
            # 应用衰减函数（指数衰减）
            decay_factor = np.exp(-time_distance * 0.3)  # 衰减系数
            item.weight = item.weight * decay_factor
            
            weighted_results.append(item)
        
        # 按权重排序
        weighted_results.sort(key=lambda x: x.weight, reverse=True)
        return weighted_results
    
    def _get_character_context(self, chapter_num: int) -> List[ContextItem]:
        """获取角色相关上下文"""
        character_context = []
        
        try:
            # 获取与当前章节相关的角色
            filepath = self.config.get("filepath", "./output")
            chapter_file = os.path.join(filepath, "chapters", f"chapter_{chapter_num}.txt")
            
            if os.path.exists(chapter_file):
                chapter_content = open(chapter_file, "r", encoding="utf-8").read()
                
                # 提取角色名称（简化处理）
                characters_in_chapter = self._extract_characters(chapter_content)
                
                # 为每个角色创建上下文项
                for char_name in characters_in_chapter:
                    if char_name in self.character_graph:
                        char_data = self.character_graph.nodes[char_name]
                        context_item = ContextItem(
                            content=f"角色 {char_name}: {char_data}",
                            metadata={
                                "character_name": char_name,
                                "chapter": chapter_num,
                                "relationship_strength": 1.0
                            },
                            source_type="character",
                            weight=0.8
                        )
                        character_context.append(context_item)
        
        except Exception as e:
            logging.warning(f"Failed to get character context: {e}")
        
        return character_context
    
    def _extract_characters(self, text: str) -> List[str]:
        """从文本中提取角色名称（简化实现）"""
        # 这里应该使用更复杂的NLP技术
        characters = []
        # 简单的启发式规则
        lines = text.split('\n')
        for line in lines:
            if "说" in line or "道" in line:
                # 可能包含角色对话
                pass
        return characters
    
    def _get_foreshadowing_context(self, chapter_num: int) -> List[ContextItem]:
        """获取伏笔相关上下文"""
        foreshadowing_context = []
        
        try:
            # 查找相关的伏笔
            related_foreshadowing = []
            
            # 检查之前的伏笔是否在当前章节解决
            for prev_chapter, foreshadowings in self.foreshadowing_tracker.items():
                if prev_chapter < chapter_num:
                    for f in foreshadowings:
                        if not f["resolved"]:
                            # 检查是否在当前章节解决
                            if self._is_foreshadowing_resolved(f, chapter_num):
                                f["resolved"] = True
                                related_foreshadowing.append(f)
            
            # 创建上下文项
            for f in related_foreshadowing:
                context_item = ContextItem(
                    content=f"伏笔: {f['content']} (已解决)",
                    metadata={
                        "foreshadowing": True,
                        "original_chapter": f["metadata"].get("chapter"),
                        "resolved_chapter": chapter_num
                    },
                    source_type="plot",
                    weight=0.9
                )
                foreshadowing_context.append(context_item)
            
            # 添加当前章节的新伏笔
            if chapter_num in self.foreshadowing_tracker:
                for f in self.foreshadowing_tracker[chapter_num]:
                    context_item = ContextItem(
                        content=f"伏笔: {f['content']}",
                        metadata={
                            "foreshadowing": True,
                            "chapter": chapter_num,
                            "resolved": False
                        },
                        source_type="plot",
                        weight=0.7
                    )
                    foreshadowing_context.append(context_item)
        
        except Exception as e:
            logging.warning(f"Failed to get foreshadowing context: {e}")
        
        return foreshadowing_context
    
    def _is_foreshadowing_resolved(self, foreshadowing: Dict, current_chapter: int) -> bool:
        """检查伏笔是否在当前章节解决（简化实现）"""
        # 这里应该使用更复杂的文本匹配技术
        return False
    
    def _dynamic_context_compression(self, context_items: List[ContextItem]) -> str:
        """动态上下文压缩"""
        if not context_items:
            return ""
        
        # 按权重和类型分组
        grouped_items = defaultdict(list)
        for item in context_items:
            grouped_items[item.source_type].append(item)
        
        # 构建压缩的上下文
        compressed_parts = []
        
        # 优先处理重要类型
        priority_order = ["setting", "character", "plot", "chapter", "knowledge", "general"]
        
        for source_type in priority_order:
            if source_type in grouped_items:
                items = grouped_items[source_type]
                # 按权重排序，取前N个
                items.sort(key=lambda x: x.weight, reverse=True)
                top_items = items[:3]  # 每种类型最多3个
                
                for item in top_items:
                    if item.weight > 0.3:  # 权重阈值
                        compressed_parts.append(f"[{source_type.upper()}] {item.content[:500]}...")
        
        # 合并并限制总长度
        compressed_context = "\n\n".join(compressed_parts)
        max_length = 4000  # 限制总长度
        if len(compressed_context) > max_length:
            compressed_context = compressed_context[:max_length] + "..."
        
        return compressed_context
    
    def update_from_chapter(self, chapter_num: int, chapter_content: str):
        """
        从章节更新向量存储
        
        Args:
            chapter_num: 章节号
            chapter_content: 章节内容
        """
        try:
            # 分割文本
            segments = split_text_for_vectorstore(chapter_content)
            
            # 为每个片段创建文档
            for i, segment in enumerate(segments):
                metadata = {
                    "chapter": chapter_num,
                    "segment": i,
                    "total_segments": len(segments),
                    "timestamp": datetime.now().isoformat()
                }
                
                self.add_context(
                    content=segment,
                    metadata=metadata,
                    source_type="chapter"
                )
            
            logging.info(f"Updated vector store from chapter {chapter_num}")
            
        except Exception as e:
            logging.error(f"Failed to update from chapter {chapter_num}: {e}")
    
    def get_statistics(self) -> Dict:
        """获取统计信息"""
        stats = {
            "total_documents": 0,
            "documents_by_type": defaultdict(int),
            "character_graph_stats": {},
            "foreshadowing_stats": {}
        }
        
        try:
            if self.vector_store:
                # 获取文档数量
                stats["total_documents"] = self.vector_store._collection.count()
                
                # 按类型统计（需要遍历所有文档）
                # 这里简化处理，实际应该更高效
                
            # 角色图谱统计
            stats["character_graph_stats"] = {
                "nodes": len(self.character_graph.nodes),
                "edges": len(self.character_graph.edges)
            }
            
            # 伏笔统计
            total_foreshadowing = sum(len(f) for f in self.foreshadowing_tracker.values())
            resolved_foreshadowing = sum(
                len([f for f in foreshadowings if f["resolved"]])
                for foreshadowings in self.foreshadowing_tracker.values()
            )
            stats["foreshadowing_stats"] = {
                "total": total_foreshadowing,
                "resolved": resolved_foreshadowing,
                "pending": total_foreshadowing - resolved_foreshadowing
            }
        
        except Exception as e:
            logging.warning(f"Failed to get statistics: {e}")
        
        return stats


# 使用示例
if __name__ == "__main__":
    config = {
        "embedding_api_key": "your_api_key",
        "embedding_url": "https://api.openai.com/v1",
        "embedding_model_name": "text-embedding-ada-002",
        "filepath": "./output"
    }
    
    enhanced_store = EnhancedVectorStore(config)
    
    # 添加一些示例上下文
    enhanced_store.add_context(
        content="这是一个关于科幻冒险的故事",
        metadata={"chapter": 1, "importance": "high"},
        source_type="setting"
    )
    
    # 获取增强上下文
    context = enhanced_store.get_enhanced_context(
        query="科幻冒险",
        chapter_num=1,
        k=5
    )
    
    print(f"Compressed context: {context.get('compressed_context', 'No context')}")
    print(f"Statistics: {enhanced_store.get_statistics()}")