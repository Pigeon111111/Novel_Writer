# 安装指南

本指南将帮助你快速安装和配置 AI Novel Generator。

## 📋 目录

- [系统要求](#系统要求)
- [安装步骤](#安装步骤)
- [环境配置](#环境配置)
- [验证安装](#验证安装)
- [下一步](#下一步)

---

## 系统要求

### 操作系统

- Windows 10/11
- macOS 10.15+
- Linux (Ubuntu 18.04+, CentOS 7+)

### Python版本

- **最低要求**: Python 3.9
- **推荐版本**: Python 3.10 - 3.12

### 硬件要求

- **CPU**: 双核及以上
- **内存**: 4GB RAM（推荐8GB+）
- **硬盘**: 至少2GB可用空间

### 网络要求

- 稳定的互联网连接（用于API调用）
- 访问LLM API服务（OpenAI、DeepSeek、LongCat等）

---

## 安装步骤

### 1. 获取项目代码

#### 方式一：Git克隆（推荐）

```bash
git clone https://github.com/YILING0013/AI_NovelGenerator.git
cd AI_NovelGenerator
```

#### 方式二：下载压缩包

1. 访问 [GitHub仓库](https://github.com/YILING0013/AI_NovelGenerator)
2. 点击 "Code" -> "Download ZIP"
3. 解压到本地目录

### 2. 创建虚拟环境（推荐）

#### Windows

```powershell
python -m venv venv
.\venv\Scripts\activate
```

#### Linux/macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. 安装依赖

#### 基础依赖

```bash
pip install -r requirements.txt
```

#### 开发依赖（可选）

如果你要参与开发，安装额外的开发工具：

```bash
pip install -r requirements-dev.txt
```

### 4. 配置API密钥

#### 创建配置文件

```bash
# 复制配置模板
cp config.example.json config.json
```

#### 编辑配置文件

打开 `config.json`，填入你的API密钥：

```json
{
  "llm_configs": {
    "LongCatChat": {
      "api_key": "your_longcat_api_key_here",
      "base_url": "https://api.longcat.chat/openai",
      "model_name": "LongCat-Flash-Chat",
      "temperature": 0.7,
      "max_tokens": 65536,
      "timeout": 600,
      "interface_format": "OpenAI"
    },
    "gpt-4": {
      "api_key": "your_openai_api_key_here",
      "base_url": "https://api.openai.com/v1",
      "model_name": "gpt-4",
      "temperature": 0.7,
      "max_tokens": 4096,
      "timeout": 600,
      "interface_format": "OpenAI"
    }
  }
}
```

---

## 环境配置

### 配置LLM服务

AI Novel Generator 支持多种LLM服务：

#### LongCat（推荐）

```json
{
  "LongCatChat": {
    "api_key": "your_key",
    "base_url": "https://api.longcat.chat/openai",
    "model_name": "LongCat-Flash-Chat",
    "temperature": 0.7,
    "max_tokens": 65536
  }
}
```

#### OpenAI

```json
{
  "gpt-4": {
    "api_key": "your_openai_key",
    "base_url": "https://api.openai.com/v1",
    "model_name": "gpt-4",
    "temperature": 0.7,
    "max_tokens": 4096
  }
}
```

#### DeepSeek

```json
{
  "deepseek-chat": {
    "api_key": "your_deepseek_key",
    "base_url": "https://api.deepseek.com/v1",
    "model_name": "deepseek-chat",
    "temperature": 0.7,
    "max_tokens": 4096
  }
}
```

#### 本地模型（Ollama）

```json
{
  "ollama-llama2": {
    "api_key": "ollama",
    "base_url": "http://localhost:11434/v1",
    "model_name": "llama2",
    "temperature": 0.7,
    "max_tokens": 4096
  }
}
```

### 配置Embedding服务

用于语义检索功能：

```json
{
  "embedding_configs": {
    "openai": {
      "api_key": "your_openai_key",
      "base_url": "https://api.openai.com/v1",
      "model_name": "text-embedding-ada-002"
    }
  }
}
```

### 配置代理（可选）

如果需要使用代理：

```json
{
  "proxy_setting": {
    "proxy_url": "127.0.0.1",
    "proxy_port": "7890",
    "enabled": true
  }
}
```

---

## 验证安装

### 1. 检查Python版本

```bash
python --version
# 应显示 Python 3.9.x 或更高版本
```

### 2. 检查依赖安装

```bash
python -c "import customtkinter; import langchain; import chromadb; print('依赖安装成功')"
```

### 3. 测试配置

```bash
python test_model_router.py
```

预期输出：
```
测试模型路由系统
==================================================
可用模型数量: X
...
模型路由器测试通过！
```

### 4. 启动应用

#### GUI模式

```bash
python main.py
```

#### Web模式

```bash
python web_backend/main.py
# 访问 http://localhost:8000
```

---

## 常见安装问题

### 问题1：依赖安装失败

**解决方案**：
```bash
# 升级pip
python -m pip install --upgrade pip

# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 问题2：ChromaDB安装失败

**解决方案**：
```bash
# Windows可能需要安装Visual C++ Build Tools
# 下载地址：https://visualstudio.microsoft.com/visual-cpp-build-tools/

# 或使用预编译版本
pip install chromadb --prefer-binary
```

### 问题3：CustomTkinter显示异常

**解决方案**：
```bash
# 重新安装CustomTkinter
pip uninstall customtkinter
pip install customtkinter --upgrade
```

### 问题4：API连接失败

**解决方案**：
1. 检查网络连接
2. 验证API密钥是否正确
3. 检查代理配置
4. 确认base_url是否正确

---

## 下一步

安装完成后，你可以：

1. 📖 阅读 [快速开始指南](quickstart.md)
2. ⚙️ 查看 [配置说明](configuration.md)
3. 🎯 尝试 [基础使用教程](basic-usage.md)
4. 🚀 探索 [高级功能](advanced-features.md)

---

## 获取帮助

如果遇到安装问题：

- 💬 [GitHub Discussions](https://github.com/YILING0013/AI_NovelGenerator/discussions)
- 🐛 [提交Issue](https://github.com/YILING0013/AI_NovelGenerator/issues)
- 📖 [常见问题](faq.md)
