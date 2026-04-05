# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- 三层配置系统（个人 > 项目 > 系统）
- 结构化状态管理系统（7个JSON状态文件）
- 多模型智能路由系统（支持LongCat优先）
- 33维度审计系统
- AI痕迹检测与消痕功能
- 完整自动化管线
- 守护进程模式
- Web界面（FastAPI + WebSocket）
- 平台集成（番茄作家助手、炼字工坊）

### Changed
- 重构配置管理器，支持嵌套配置访问
- 升级状态管理从txt到JSON格式
- 优化模型选择策略，添加熔断器机制

### Fixed
- 修复状态数据一致性问题
- 修复模型选择失败时的降级问题

## [1.0.0] - 2025-09-24

### Added
- 基础小说生成功能
- GUI界面（CustomTkinter）
- 向量检索系统（ChromaDB + LangChain）
- 基础一致性检查功能
- 多模型支持（OpenAI、DeepSeek、Gemini等）
- 状态追踪系统（角色状态、全局摘要）
- WebDAV同步支持

### Note
- 项目初始版本发布
- 基础功能完整可用

---

## 版本说明

### [Unreleased] - 当前开发版本
包含所有最新的优化和功能增强，包括架构重构、质量控制系统、自动化能力等。

### [1.0.0] - 2025-09-24
项目初始发布版本，包含基础的小说生成功能。

---

## 升级指南

### 从 1.0.0 升级到 Unreleased

1. **备份现有配置**
```bash
cp config.json config.json.backup
```

2. **更新代码**
```bash
git pull origin main
pip install -r requirements.txt --upgrade
```

3. **迁移状态文件**
```python
from state_manager import StateMigrator

migrator = StateMigrator("path/to/your/story")
migrator.migrate_all()
```

4. **更新配置文件**
- 参考 `config.example.json` 更新你的 `config.json`
- 添加新的配置项（audit_config、ai_detection_config等）

5. **验证升级**
```bash
python test_state_manager.py
python test_model_router.py
python test_audit_system.py
```

---

## 路线图

### v1.1.0 (计划中)
- [ ] 完整的Vue 3前端界面
- [ ] 单元测试覆盖率 > 70%
- [ ] 完整的API文档
- [ ] 性能优化（缓存机制）

### v1.2.0 (计划中)
- [ ] 分布式部署支持
- [ ] 本地模型微调支持
- [ ] 监控告警系统
- [ ] 日志收集和分析

### v2.0.0 (长期规划)
- [ ] 多租户支持
- [ ] 商业化功能
- [ ] 社区生态建设

---

## 贡献

如果你想为新版本做贡献，请查看 [CONTRIBUTING.md](CONTRIBUTING.md)。
