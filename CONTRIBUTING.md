# 贡献指南

感谢你考虑为 AI Novel Generator 做贡献！🎉

## 📋 目录

- [行为准则](#行为准则)
- [如何贡献](#如何贡献)
- [开发流程](#开发流程)
- [代码规范](#代码规范)
- [提交规范](#提交规范)
- [Pull Request 流程](#pull-request-流程)
- [报告问题](#报告问题)
- [功能建议](#功能建议)

---

## 行为准则

本项目采用贡献者公约作为行为准则。参与此项目即表示你同意遵守其条款。请阅读 [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) 了解详情。

---

## 如何贡献

### 报告Bug

如果你发现了bug，请通过 [GitHub Issues](https://github.com/YILING0013/AI_NovelGenerator/issues) 提交报告。

提交Bug报告时，请包含：

1. **清晰的标题和描述**
2. **复现步骤** - 详细的步骤让我们能重现问题
3. **预期行为** - 你期望发生什么
4. **实际行为** - 实际发生了什么
5. **环境信息**:
   - 操作系统和版本
   - Python版本
   - 依赖版本
6. **截图** - 如果适用，添加截图帮助解释问题
7. **日志** - 相关的错误日志或输出

### 建议新功能

我们欢迎新功能建议！请通过 [GitHub Issues](https://github.com/YILING0013/AI_NovelGenerator/issues) 提交。

功能建议应包含：

1. **清晰的标题**
2. **详细描述** - 功能应该如何工作
3. **用例** - 为什么需要这个功能
4. **替代方案** - 你考虑过的其他解决方案
5. **额外信息** - 相关的截图、草图等

### 改进文档

文档改进包括：

- 修正拼写或语法错误
- 添加缺失的文档
- 改进现有文档的清晰度
- 翻译文档

### 提交代码

详见下方的 [开发流程](#开发流程)。

---

## 开发流程

### 1. Fork 并克隆仓库

```bash
# Fork 后克隆你的仓库
git clone https://github.com/your-username/Novel_Writer.git
cd Novel_Writer

# 添加上游仓库
git remote add upstream https://github.com/Pigeon111111/Novel_Writer.git
```

### 2. 创建分支

```bash
# 创建并切换到新分支
git checkout -b feature/your-feature-name

# 或修复bug
git checkout -b fix/your-bug-fix
```

分支命名规范：
- `feature/` - 新功能
- `fix/` - Bug修复
- `docs/` - 文档改进
- `refactor/` - 代码重构
- `test/` - 测试相关
- `chore/` - 其他杂项

### 3. 设置开发环境

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装开发依赖
pip install -r requirements-dev.txt

# 安装pre-commit hooks
pre-commit install
```

### 4. 进行更改

- 编写代码
- 添加测试
- 更新文档
- 确保所有测试通过

### 5. 提交更改

```bash
# 查看更改
git status
git diff

# 添加更改
git add .

# 提交（遵循提交规范）
git commit -m "feat: add amazing feature"
```

### 6. 推送到GitHub

```bash
git push origin feature/your-feature-name
```

### 7. 创建Pull Request

在GitHub上创建Pull Request，填写PR模板。

---

## 代码规范

### Python代码规范

我们遵循 [PEP 8](https://www.python.org/dev/peps/pep-0008/) 规范：

```python
# 好的示例
def calculate_quality_score(issues: List[AuditIssue]) -> float:
    """
    计算质量评分
    
    Args:
        issues: 审计问题列表
        
    Returns:
        质量评分（0-100）
    """
    if not issues:
        return 100.0
    
    penalty = sum(SEVERITY_WEIGHTS[issue.severity] * 5 for issue in issues)
    return max(0.0, 100.0 - penalty)
```

### 代码风格

- 使用 **4个空格** 缩进
- 最大行长度：**100字符**
- 使用 **UTF-8** 编码
- 文件末尾保留一个空行
- 使用 **中文注释**（遵循项目规则）

### 类型注解

我们鼓励使用类型注解：

```python
from typing import Dict, List, Optional

def process_chapter(
    chapter_num: int,
    content: str,
    config: Optional[Dict] = None
) -> Dict[str, Any]:
    """处理章节"""
    pass
```

### 文档字符串

使用Google风格的文档字符串：

```python
def function_name(param1: str, param2: int) -> bool:
    """
    函数简短描述
    
    详细描述（可选）
    
    Args:
        param1: 参数1说明
        param2: 参数2说明
        
    Returns:
        返回值说明
        
    Raises:
        ValueError: 异常说明
        
    Example:
        >>> function_name("test", 42)
        True
    """
    pass
```

### 导入顺序

```python
# 标准库
import os
import sys
from typing import Dict, List

# 第三方库
import requests
from fastapi import FastAPI

# 本地模块
from config_manager import ConfigManager
from state_manager import StateManager
```

---

## 提交规范

我们使用 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

### 提交格式

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type类型

- `feat`: 新功能
- `fix`: Bug修复
- `docs`: 文档更新
- `style`: 代码格式（不影响代码运行的变动）
- `refactor`: 重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动
- `perf`: 性能优化

### 示例

```bash
# 新功能
git commit -m "feat(audit): add 33-dimensional audit system"

# Bug修复
git commit -m "fix(router): fix model selection fallback logic"

# 文档
git commit -m "docs(readme): update installation guide"

# 重构
git commit -m "refactor(config): implement three-layer config system"
```

---

## Pull Request 流程

### PR检查清单

在提交PR之前，请确保：

- [ ] 代码遵循项目的代码规范
- [ ] 已添加必要的测试
- [ ] 所有测试都通过
- [ ] 已更新相关文档
- [ ] 提交信息遵循提交规范
- [ ] PR标题清晰描述更改内容

### PR标题格式

```
<type>(<scope>): <description>
```

示例：
- `feat(audit): add AI trace detection`
- `fix(router): fix circuit breaker logic`
- `docs(api): add FastAPI documentation`

### PR描述模板

```markdown
## 更改类型
- [ ] Bug修复
- [ ] 新功能
- [ ] 重构
- [ ] 文档更新
- [ ] 其他

## 描述
清晰描述你的更改

## 相关Issue
Fixes #123

## 测试
描述你如何测试这些更改

## 截图
如果适用，添加截图

## 检查清单
- [ ] 代码遵循规范
- [ ] 已添加测试
- [ ] 文档已更新
```

### 代码审查

- 所有PR都需要至少一位维护者的审查
- 审查者会提供反馈和建议
- 请及时响应审查意见
- 通过审查后，维护者会合并你的PR

---

## 报告问题

### 安全问题

如果你发现了安全漏洞，**请不要通过GitHub Issues报告**。请发送邮件至 security@example.com。

### 一般问题

通过 [GitHub Issues](https://github.com/YILING0013/AI_NovelGenerator/issues) 报告问题。

使用问题模板：
- [Bug报告](.github/ISSUE_TEMPLATE/bug_report.md)
- [功能建议](.github/ISSUE_TEMPLATE/feature_request.md)

---

## 功能建议

我们欢迎功能建议！请通过 [GitHub Issues](https://github.com/YILING0013/AI_NovelGenerator/issues) 提交。

好的功能建议包括：
1. 清晰的标题
2. 详细的功能描述
3. 使用场景
4. 预期效果
5. 可选的实现建议

---

## 获取帮助

- 💬 [GitHub Discussions](https://github.com/Pigeon111111/Novel_Writer/discussions)
- 📧 [Email](mailto:your-email@example.com) - 私人问题
- 📖 [文档](docs/) - 查阅文档

---

## 许可证

通过贡献代码，你同意你的贡献将根据项目的 [AGPL v3 许可证](LICENSE) 进行许可。

---

<div align="center">

**再次感谢你的贡献！❤️**

</div>
