<div align="center">

# AI Novel Generator

**基于大语言模型的智能小说创作工具**

[![License](https://img.shields.io/badge/license-AGPL%20v3-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9%2B-brightgreen.svg)](https://www.python.org/)
[![GitHub Stars](https://img.shields.io/github/stars/Pigeon111111/Novel_Writer.svg)](https://github.com/Pigeon111111/Novel_Writer/stargazers)
[![GitHub Issues](https://img.shields.io/github/issues/Pigeon111111/Novel_Writer.svg)](https://github.com/Pigeon111111/Novel_Writer/issues)

[English](README_EN.md) | 简体中文

</div>

---

## 📖 项目简介

AI Novel Generator 是一款基于大语言模型的多功能小说生成工具，旨在帮助作者高效创作逻辑严谨、设定统一的长篇故事。通过智能化的状态追踪、语义检索和自动审校机制，确保小说创作的一致性和连贯性。

### ✨ 核心特性

- 🎨 **小说设定工坊** - 世界观架构、角色设定、剧情蓝图一站式管理
- 📖 **智能章节生成** - 多阶段生成流程，保障剧情连贯性
- 🧠 **状态追踪系统** - 角色发展轨迹、伏笔管理、资源账本
- 🔍 **语义检索引擎** - 基于向量的长程上下文一致性维护
- ✅ **自动审校机制** - 33维度审计系统，检测剧情矛盾与逻辑冲突
- 🤖 **AI痕迹消痕** - 自动检测和消除AI生成痕迹
- 🚀 **自动化管线** - 端到端自动化生成，支持守护进程模式
- 🌐 **Web界面** - FastAPI后端 + RESTful API + WebSocket实时推送
- 🔗 **平台集成** - 支持番茄作家助手、炼字工坊等平台自动投稿

---

## 🚀 快速开始

### 环境要求

- Python 3.9+ (推荐 3.10-3.12)
- pip 包管理工具
- 有效的API密钥（OpenAI / DeepSeek / LongCat 等）

### 安装步骤

```bash
# 克隆仓库
git clone https://github.com/Pigeon111111/Novel_Writer.git
cd Novel_Writer

# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 配置

1. 复制配置模板：
```bash
cp config.example.json config.json
```

2. 编辑 `config.json`，填入你的API密钥：
```json
{
  "llm_configs": {
    "LongCatChat": {
      "api_key": "your_api_key_here",
      "base_url": "https://api.longcat.chat/openai",
      "model_name": "LongCat-Flash-Chat",
      "temperature": 0.7,
      "max_tokens": 65536
    }
  }
}
```

### 运行

#### GUI模式
```bash
python main.py
```

#### Web模式
```bash
# 启动Web服务
python web_backend/main.py

# 访问 http://localhost:8000
```

#### 命令行模式
```bash
# 使用自动化管线
python -c "from automation import AutomatedPipeline; ..."
```

---

## 📚 文档

- [安装指南](docs/installation.md)
- [配置说明](docs/configuration.md)
- [使用教程](docs/tutorial.md)
- [API文档](docs/api.md)
- [开发指南](docs/development.md)
- [常见问题](docs/faq.md)

---

## ⚙️ 配置说明

### 三层配置优先级

本项目采用三层配置系统，优先级从高到低：

1. **个人配置** (`config.json`) - 最高优先级
2. **项目配置** (`config.default.json`) - 中等优先级
3. **系统默认配置** - 最低优先级

### 主要配置项

```json
{
  "llm_configs": {
    "LongCatChat": {...},
    "gpt-4": {...}
  },
  "audit_config": {
    "enabled": true,
    "auto_fix": false,
    "quality_threshold": 80.0
  },
  "ai_detection_config": {
    "enabled": true,
    "auto_remove_traces": true,
    "detection_threshold": 0.3
  },
  "automation_config": {
    "enabled": true,
    "auto_mode": false,
    "human_review_gate": true
  }
}
```

详细配置说明请参考 [配置文档](docs/configuration.md)。

---

## 🏗️ 项目架构

```
AI_NovelGenerator/
├── config_manager.py          # 三层配置管理器
├── state_manager/              # 状态管理模块
│   ├── models.py              # Pydantic数据模型
│   ├── manager.py             # 状态管理器
│   └── migration.py           # 迁移工具
├── model_router/               # 模型路由模块
│   ├── router.py              # 模型路由器
│   └── adaptive_selector.py   # 自适应选择器
├── audit_system/               # 审计系统模块
│   ├── dimensions.py          # 33维度定义
│   ├── result.py              # 审计结果模型
│   └── auditor.py             # 审计引擎
├── ai_detection/               # AI检测模块
│   ├── detector.py            # AI痕迹检测器
│   └── remover.py             # AI痕迹消除器
├── automation/                 # 自动化模块
│   ├── pipeline.py            # 自动化管线
│   └── daemon.py              # 守护进程
├── web_backend/                # Web后端
│   └── main.py                # FastAPI应用
└── platform_integration/       # 平台集成
    ├── adapter.py             # 平台适配器基类
    ├── fanqie.py              # 番茄作家助手
    ├── lianzi.py              # 炼字工坊
    └── manager.py             # 平台管理器
```

---

## 🎯 使用示例

### 基础使用

```python
from config_manager import ConfigManager
from automation import AutomatedPipeline

# 初始化
config = ConfigManager("config.json")
pipeline = AutomatedPipeline(config)

# 运行自动化生成
await pipeline.run_full_pipeline(
    start_chapter=1,
    end_chapter=10,
    auto_mode=False  # True为全自动模式
)
```

### 平台投稿

```python
from platform_integration import PlatformManager

# 初始化平台管理器
manager = PlatformManager(config)

# 注册番茄作家助手
manager.register_platform("fanqie", {
    "api_key": "your_key",
    "author_id": "your_id"
})

# 发布章节
results = await manager.publish_to_multiple(
    novel_id="novel_001",
    chapter_num=1,
    title="第一章 开始",
    content="章节内容...",
    platforms=["fanqie", "lianzi"]
)
```

---

## 🤝 贡献指南

我们欢迎所有形式的贡献！请查看 [贡献指南](CONTRIBUTING.md) 了解详情。

### 如何贡献

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

### 开发环境设置

```bash
# 安装开发依赖
pip install -r requirements-dev.txt

# 运行测试
pytest tests/

# 代码格式化
black .
isort .

# 类型检查
mypy .
```

---

## 📝 更新日志

查看 [CHANGELOG.md](CHANGELOG.md) 了解版本更新历史。

---

## 📄 许可证

本项目采用 GNU Affero General Public License v3.0 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

---

## 🙏 致谢

感谢以下开源项目的启发：

- [LangChain](https://github.com/langchain-ai/langchain) - LLM应用框架
- [ChromaDB](https://github.com/chroma-core/chroma) - 向量数据库
- [FastAPI](https://github.com/tiangolo/fastapi) - Web框架
- [Pydantic](https://github.com/pydantic/pydantic) - 数据验证

---

## 📞 联系方式

- 项目主页: https://github.com/Pigeon111111/Novel_Writer
- 问题反馈: https://github.com/Pigeon111111/Novel_Writer/issues
- 讨论区: https://github.com/Pigeon111111/Novel_Writer/discussions

---

## ⚠️ 免责声明

本项目仅供学习和研究使用。使用本工具生成的内容应遵守相关平台的规定和法律法规。开发者不对使用本工具产生的任何后果负责。

---

<div align="center">

**如果这个项目对你有帮助，请给一个 ⭐️ Star！**

Made with ❤️ by Pigeon111111

</div>
