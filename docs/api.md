# API文档

本文档介绍 AI Novel Generator 的 RESTful API 接口。

## 📋 目录

- [API概述](#api概述)
- [认证](#认证)
- [基础端点](#基础端点)
- [配置管理](#配置管理)
- [小说生成](#小说生成)
- [状态查询](#状态查询)
- [平台集成](#平台集成)
- [WebSocket](#websocket)
- [错误处理](#错误处理)

---

## API概述

### 基础URL

```
http://localhost:8000
```

### API版本

当前版本：`v1.0`

所有API端点都以 `/api` 为前缀。

---

## 认证

当前版本暂不需要认证。未来版本将支持API密钥认证。

---

## 基础端点

### 获取API信息

```http
GET /
```

**响应示例**：
```json
{
  "message": "AI Novel Generator API",
  "version": "1.0.0"
}
```

---

## 配置管理

### 获取配置

```http
GET /api/config
```

**响应示例**：
```json
{
  "llm_configs": {
    "LongCatChat": {...}
  },
  "audit_config": {
    "enabled": true
  }
}
```

### 更新配置

```http
POST /api/config
```

**请求体**：
```json
{
  "audit_config.enabled": false,
  "ai_detection_config.detection_threshold": 0.5
}
```

**响应示例**：
```json
{
  "message": "Config updated successfully"
}
```

---

## 小说生成

### 创建小说项目

```http
POST /api/novels/create
```

**请求体**：
```json
{
  "title": "我的小说",
  "genre": "玄幻",
  "num_chapters": 100,
  "word_number": 3000,
  "topic": "一个少年的修仙之旅"
}
```

**响应示例**：
```json
{
  "novel_id": "novel_20260405_143022",
  "config": {
    "title": "我的小说",
    "genre": "玄幻",
    "num_chapters": 100,
    "word_number": 3000,
    "topic": "一个少年的修仙之旅"
  },
  "created_at": "2026-04-05T14:30:22"
}
```

### 启动生成任务

```http
POST /api/novels/{novel_id}/generate
```

**请求体**：
```json
{
  "novel_id": "novel_20260405_143022",
  "start_chapter": 1,
  "end_chapter": 10,
  "auto_mode": false
}
```

**响应示例**：
```json
{
  "task_id": "task_20260405_143025",
  "novel_id": "novel_20260405_143022",
  "status": "started",
  "started_at": "2026-04-05T14:30:25"
}
```

---

## 状态查询

### 获取小说状态

```http
GET /api/novels/{novel_id}/status
```

**响应示例**：
```json
{
  "novel_id": "novel_20260405_143022",
  "statistics": {
    "current_chapter": 5,
    "total_chapters": 100,
    "total_characters": 15,
    "active_characters": 8,
    "pending_hooks": 3,
    "resolved_hooks": 2,
    "total_word_count": 15000,
    "average_word_count": 3000
  },
  "timestamp": "2026-04-05T14:35:00"
}
```

### 获取可用模型

```http
GET /api/models
```

**响应示例**：
```json
{
  "models": [
    "LongCatChat",
    "LongcatLite",
    "gpt-4"
  ],
  "longcat_models": [
    "LongCatChat",
    "LongcatLite"
  ]
}
```

---

## 平台集成

### 注册平台

```http
POST /api/platforms/register
```

**请求体**：
```json
{
  "platform": "fanqie",
  "credentials": {
    "api_key": "your_key",
    "author_id": "your_id"
  }
}
```

**响应示例**：
```json
{
  "message": "Platform registered successfully",
  "platform": "fanqie"
}
```

### 发布章节

```http
POST /api/platforms/publish
```

**请求体**：
```json
{
  "novel_id": "novel_20260405_143022",
  "chapter_num": 1,
  "title": "第一章 开始",
  "content": "章节内容...",
  "platforms": ["fanqie", "lianzi"]
}
```

**响应示例**：
```json
{
  "fanqie": {
    "success": true,
    "chapter_id": "12345",
    "message": "上传成功"
  },
  "lianzi": {
    "success": true,
    "chapter_id": "67890",
    "message": "上传成功"
  }
}
```

---

## WebSocket

### 连接WebSocket

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/novel_id');
```

### 接收消息

**进度更新**：
```json
{
  "type": "progress",
  "task_id": "task_20260405_143025",
  "current": 5,
  "total": 10,
  "percentage": 50.0
}
```

**任务完成**：
```json
{
  "type": "task_complete",
  "task_id": "task_20260405_143025",
  "completed_at": "2026-04-05T15:00:00"
}
```

**错误消息**：
```json
{
  "type": "task_error",
  "task_id": "task_20260405_143025",
  "error": "API调用失败"
}
```

---

## 错误处理

### 错误响应格式

```json
{
  "detail": "错误描述",
  "status_code": 400,
  "timestamp": "2026-04-05T14:30:00"
}
```

### 常见错误码

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

---

## 使用示例

### Python示例

```python
import requests

# 创建小说
response = requests.post(
    'http://localhost:8000/api/novels/create',
    json={
        'title': '我的小说',
        'genre': '玄幻',
        'num_chapters': 100,
        'word_number': 3000,
        'topic': '一个少年的修仙之旅'
    }
)
novel_id = response.json()['novel_id']

# 启动生成
response = requests.post(
    f'http://localhost:8000/api/novels/{novel_id}/generate',
    json={
        'novel_id': novel_id,
        'start_chapter': 1,
        'end_chapter': 10,
        'auto_mode': False
    }
)
task_id = response.json()['task_id']
```

### JavaScript示例

```javascript
// 创建小说
const response = await fetch('http://localhost:8000/api/novels/create', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    title: '我的小说',
    genre: '玄幻',
    num_chapters: 100,
    word_number: 3000,
    topic: '一个少年的修仙之旅'
  })
});
const data = await response.json();
const novelId = data.novel_id;

// WebSocket连接
const ws = new WebSocket(`ws://localhost:8000/ws/${novelId}`);
ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log('收到消息:', message);
};
```

---

## 速率限制

当前版本暂无速率限制。未来版本将根据API密钥设置不同的速率限制。

---

## 版本控制

API版本通过URL前缀控制：

- `v1`: `/api/v1/...` (当前版本)
- `v2`: `/api/v2/...` (未来版本)

---

## 更多信息

- [GitHub仓库](https://github.com/YILING0013/AI_NovelGenerator)
- [问题反馈](https://github.com/YILING0013/AI_NovelGenerator/issues)
