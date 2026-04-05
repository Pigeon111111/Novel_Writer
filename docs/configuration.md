# 配置说明

本文档详细介绍 AI Novel Generator 的配置系统。

## 📋 目录

- [配置系统概述](#配置系统概述)
- [配置文件结构](#配置文件结构)
- [核心配置项](#核心配置项)
- [高级配置](#高级配置)
- [配置示例](#配置示例)

---

## 配置系统概述

### 三层配置优先级

AI Novel Generator 采用三层配置系统，优先级从高到低：

1. **个人配置** (`config.json`) - 最高优先级
   - 用户自定义配置
   - 包含敏感信息（API密钥等）
   - 不应提交到版本控制

2. **项目配置** (`config.default.json`) - 中等优先级
   - 项目默认配置
   - 团队共享配置
   - 可以提交到版本控制

3. **系统默认配置** - 最低优先级
   - 代码中定义的默认值
   - 作为兜底配置

### 配置合并规则

系统会自动合并三层配置，后者的配置会覆盖前者：

```python
merged_config = deep_merge(
    system_default,    # 系统默认
    project_config,    # 项目配置
    user_config        # 用户配置（最高优先级）
)
```

---

## 配置文件结构

### config.json 结构

```json
{
  "llm_configs": {...},
  "embedding_configs": {...},
  "choose_configs": {...},
  "audit_config": {...},
  "ai_detection_config": {...},
  "automation_config": {...},
  "other_params": {...},
  "proxy_setting": {...},
  "webdav_config": {...}
}
```

---

## 核心配置项

### 1. LLM配置 (`llm_configs`)

定义可用的LLM模型：

```json
{
  "llm_configs": {
    "LongCatChat": {
      "api_key": "your_api_key",
      "base_url": "https://api.longcat.chat/openai",
      "model_name": "LongCat-Flash-Chat",
      "temperature": 0.7,
      "max_tokens": 65536,
      "timeout": 600,
      "interface_format": "OpenAI"
    },
    "gpt-4": {
      "api_key": "your_openai_key",
      "base_url": "https://api.openai.com/v1",
      "model_name": "gpt-4",
      "temperature": 0.7,
      "max_tokens": 4096,
      "timeout": 600,
      "interface_format": "OpenAI"
    },
    "deepseek-chat": {
      "api_key": "your_deepseek_key",
      "base_url": "https://api.deepseek.com/v1",
      "model_name": "deepseek-chat",
      "temperature": 0.7,
      "max_tokens": 4096,
      "timeout": 600,
      "interface_format": "OpenAI"
    }
  }
}
```

**参数说明**：

- `api_key`: API密钥
- `base_url`: API基础URL
- `model_name`: 模型名称
- `temperature`: 温度参数（0-2，越高越随机）
- `max_tokens`: 最大生成token数
- `timeout`: 请求超时时间（秒）
- `interface_format`: 接口格式（OpenAI/Azure/Custom）

### 2. 模型选择配置 (`choose_configs`)

为不同任务指定使用的模型：

```json
{
  "choose_configs": {
    "prompt_draft_llm": "LongCatChat",
    "chapter_outline_llm": "LongCat-Flash-Thinking-2601",
    "architecture_llm": "LongCat-Flash-Thinking-2601",
    "final_chapter_llm": "LongcatLite",
    "consistency_review_llm": "LongCat-Flash-Thinking-2601"
  }
}
```

**任务类型**：

- `prompt_draft_llm`: 草稿撰写
- `chapter_outline_llm`: 章节大纲
- `architecture_llm`: 架构规划
- `final_chapter_llm`: 最终定稿
- `consistency_review_llm`: 一致性检查

### 3. 审计配置 (`audit_config`)

```json
{
  "audit_config": {
    "enabled": true,
    "auto_fix": false,
    "quality_threshold": 80.0,
    "critical_threshold": 0,
    "major_threshold": 2
  }
}
```

**参数说明**：

- `enabled`: 是否启用审计系统
- `auto_fix`: 是否自动修复问题
- `quality_threshold`: 质量评分阈值（0-100）
- `critical_threshold`: 允许的严重问题数
- `major_threshold`: 允许的重要问题数

### 4. AI检测配置 (`ai_detection_config`)

```json
{
  "ai_detection_config": {
    "enabled": true,
    "auto_remove_traces": true,
    "detection_threshold": 0.3,
    "max_iterations": 3
  }
}
```

**参数说明**：

- `enabled`: 是否启用AI痕迹检测
- `auto_remove_traces`: 是否自动消除痕迹
- `detection_threshold`: 检测阈值（0-1，越低越严格）
- `max_iterations`: 最大迭代次数

### 5. 自动化配置 (`automation_config`)

```json
{
  "automation_config": {
    "enabled": true,
    "auto_mode": false,
    "human_review_gate": true,
    "batch_size": 10,
    "retry_on_failure": 3
  }
}
```

**参数说明**：

- `enabled`: 是否启用自动化
- `auto_mode`: 是否全自动模式（无需人工干预）
- `human_review_gate`: 是否需要人工审核
- `batch_size`: 批量处理大小
- `retry_on_failure`: 失败重试次数

---

## 高级配置

### Embedding配置

```json
{
  "embedding_configs": {
    "openai": {
      "api_key": "your_key",
      "base_url": "https://api.openai.com/v1",
      "model_name": "text-embedding-ada-002"
    },
    "local": {
      "model_name": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    }
  }
}
```

### 代理配置

```json
{
  "proxy_setting": {
    "proxy_url": "127.0.0.1",
    "proxy_port": "7890",
    "enabled": true
  }
}
```

### WebDAV同步配置

```json
{
  "webdav_config": {
    "webdav_url": "https://your-webdav-server.com",
    "webdav_username": "your_username",
    "webdav_password": "your_password"
  }
}
```

---

## 配置示例

### 完整配置示例

```json
{
  "last_interface_format": "OpenAI",
  "last_embedding_interface_format": "OpenAI",
  
  "llm_configs": {
    "LongCatChat": {
      "api_key": "your_longcat_key",
      "base_url": "https://api.longcat.chat/openai",
      "model_name": "LongCat-Flash-Chat",
      "temperature": 0.7,
      "max_tokens": 65536,
      "timeout": 600,
      "interface_format": "OpenAI"
    },
    "gpt-4": {
      "api_key": "your_openai_key",
      "base_url": "https://api.openai.com/v1",
      "model_name": "gpt-4",
      "temperature": 0.7,
      "max_tokens": 4096,
      "timeout": 600,
      "interface_format": "OpenAI"
    }
  },
  
  "embedding_configs": {
    "openai": {
      "api_key": "your_openai_key",
      "base_url": "https://api.openai.com/v1",
      "model_name": "text-embedding-ada-002"
    }
  },
  
  "choose_configs": {
    "prompt_draft_llm": "LongCatChat",
    "chapter_outline_llm": "LongCatChat",
    "architecture_llm": "LongCatChat",
    "final_chapter_llm": "LongCatChat",
    "consistency_review_llm": "LongCatChat"
  },
  
  "audit_config": {
    "enabled": true,
    "auto_fix": false,
    "quality_threshold": 80.0,
    "critical_threshold": 0,
    "major_threshold": 2
  },
  
  "ai_detection_config": {
    "enabled": true,
    "auto_remove_traces": true,
    "detection_threshold": 0.3,
    "max_iterations": 3
  },
  
  "automation_config": {
    "enabled": true,
    "auto_mode": false,
    "human_review_gate": true,
    "batch_size": 10,
    "retry_on_failure": 3
  },
  
  "other_params": {
    "topic": "",
    "genre": "",
    "num_chapters": 0,
    "word_number": 0,
    "filepath": "",
    "chapter_num": "120",
    "user_guidance": "",
    "characters_involved": "",
    "key_items": "",
    "scene_location": "",
    "time_constraint": ""
  },
  
  "proxy_setting": {
    "proxy_url": "127.0.0.1",
    "proxy_port": "",
    "enabled": false
  },
  
  "webdav_config": {
    "webdav_url": "",
    "webdav_username": "",
    "webdav_password": ""
  }
}
```

---

## 配置管理

### 通过代码管理配置

```python
from config_manager import ConfigManager

# 初始化
config = ConfigManager("config.json")

# 获取配置
api_key = config.get("llm_configs.LongCatChat.api_key")
audit_enabled = config.get("audit_config.enabled", True)

# 设置配置
config.set("audit_config.quality_threshold", 85.0)
config.set("ai_detection_config.enabled", True)

# 保存配置
config.save_user_config()

# 重新加载
config.reload()

# 重置为默认值
config.reset_to_default("audit_config.auto_fix")
```

---

## 配置最佳实践

1. **API密钥安全**
   - 不要将 `config.json` 提交到版本控制
   - 使用环境变量存储敏感信息
   - 定期更换API密钥

2. **配置文件管理**
   - 使用 `config.example.json` 作为模板
   - 为不同环境创建不同配置文件
   - 定期备份配置文件

3. **性能优化**
   - 根据任务类型选择合适的模型
   - 调整 `max_tokens` 控制成本
   - 合理设置 `timeout` 避免长时间等待

---

## 下一步

- 📖 [快速开始指南](quickstart.md)
- 🎯 [基础使用教程](basic-usage.md)
- 🚀 [高级功能](advanced-features.md)
