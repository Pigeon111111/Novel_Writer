# web_backend/main.py
# -*- coding: utf-8 -*-
"""
FastAPI Web后端
提供RESTful API和WebSocket支持
"""
from fastapi import FastAPI, WebSocket, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Optional
import logging
import asyncio
from datetime import datetime
from pathlib import Path

from config_manager import ConfigManager
from automation import AutomatedPipeline

app = FastAPI(title="AI Novel Generator API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

config_manager = ConfigManager("config.json")
pipeline = AutomatedPipeline(config_manager)

active_websockets = []


class NovelConfig(BaseModel):
    title: str
    genre: str
    num_chapters: int
    word_number: int
    topic: str


class GenerationTask(BaseModel):
    novel_id: str
    start_chapter: int
    end_chapter: int
    auto_mode: bool = False


@app.get("/")
async def root():
    """根路径"""
    return {"message": "AI Novel Generator API", "version": "1.0.0"}


@app.get("/api/config")
async def get_config():
    """获取配置"""
    return config_manager.get_all()


@app.post("/api/config")
async def update_config(config: Dict):
    """更新配置"""
    for key, value in config.items():
        config_manager.set(key, value, save=False)
    config_manager.save_user_config()
    return {"message": "Config updated successfully"}


@app.post("/api/novels/create")
async def create_novel(novel_config: NovelConfig):
    """创建新小说项目"""
    novel_id = f"novel_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    config_manager.set("other_params.topic", novel_config.title, save=False)
    config_manager.set("other_params.genre", novel_config.genre, save=False)
    config_manager.set("other_params.num_chapters", novel_config.num_chapters, save=False)
    config_manager.set("other_params.word_number", novel_config.word_number, save=False)
    config_manager.save_user_config()
    
    return {
        "novel_id": novel_id,
        "config": novel_config.dict(),
        "created_at": datetime.now().isoformat()
    }


@app.post("/api/novels/{novel_id}/generate")
async def start_generation(
    novel_id: str,
    task: GenerationTask,
    background_tasks: BackgroundTasks
):
    """启动生成任务"""
    task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    background_tasks.add_task(
        run_generation_task,
        task_id,
        task.start_chapter,
        task.end_chapter,
        task.auto_mode
    )
    
    return {
        "task_id": task_id,
        "novel_id": novel_id,
        "status": "started",
        "started_at": datetime.now().isoformat()
    }


async def run_generation_task(task_id: str, start: int, end: int, auto_mode: bool):
    """运行生成任务"""
    try:
        await pipeline.run_full_pipeline(
            start_chapter=start,
            end_chapter=end,
            auto_mode=auto_mode,
            progress_callback=lambda curr, total: broadcast_progress(task_id, curr, total)
        )
        
        await broadcast_message({
            "type": "task_complete",
            "task_id": task_id,
            "completed_at": datetime.now().isoformat()
        })
    except Exception as e:
        logging.error(f"Generation task failed: {e}")
        await broadcast_message({
            "type": "task_error",
            "task_id": task_id,
            "error": str(e)
        })


async def broadcast_progress(task_id: str, current: int, total: int):
    """广播进度"""
    await broadcast_message({
        "type": "progress",
        "task_id": task_id,
        "current": current,
        "total": total,
        "percentage": (current / total * 100) if total > 0 else 0
    })


async def broadcast_message(message: dict):
    """广播消息到所有WebSocket连接"""
    for websocket in active_websockets:
        try:
            await websocket.send_json(message)
        except:
            active_websockets.remove(websocket)


@app.websocket("/ws/{novel_id}")
async def websocket_endpoint(websocket: WebSocket, novel_id: str):
    """WebSocket端点"""
    await websocket.accept()
    active_websockets.append(websocket)
    
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_json({
                "type": "echo",
                "message": data,
                "timestamp": datetime.now().isoformat()
            })
    except:
        active_websockets.remove(websocket)


@app.get("/api/novels/{novel_id}/status")
async def get_novel_status(novel_id: str):
    """获取小说状态"""
    stats = pipeline.state_manager.get_statistics()
    
    return {
        "novel_id": novel_id,
        "statistics": stats,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/models")
async def get_available_models():
    """获取可用模型列表"""
    models = pipeline.model_router.available_models
    
    return {
        "models": list(models.keys()),
        "longcat_models": pipeline.model_router.get_longcat_models()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
