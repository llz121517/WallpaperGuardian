# Changelog

All notable changes to this project will be documented in this file.
This changelog follows the [Keep a Changelog](https://keepachangelog.com/) standard, and version numbers follow [Semantic Versioning (SemVer)](https://semver.org/lang/zh-CN/).

所有重要变更将记录在此文件中。
本 changelog 遵循 [Keep a Changelog](https://keepachangelog.com/) 标准，版本号遵循 [语义化版本（SemVer）](https://semver.org/lang/zh-CN/)。

## [Unreleased] - 未发布

> 此部分用于记录**已合并但尚未发布**的变更。发布新版本时，将其内容移入新版本条目并清空。

### Added
- （新增功能）

### Changed
- （已有功能的非破坏性修改）

### Deprecated
- （标记为废弃的功能，未来可能移除）

### Removed
- （已彻底移除的功能）

### Fixed
- （bug 修复）

### Security
- （安全相关修复，如 XSS、路径穿越等）


> **注**：所有日期格式为 YYYY-MM-DD

---

## [v1.0.0] - 2026-04-06

### Added
- 实现壁纸自动锁定功能
  - 持续监控桌面壁纸状态（每10秒检测一次）
  - 检测到壁纸更改时自动恢复为指定壁纸
- 支持开机自启动
  - 自动配置 Windows 注册表实现开机自启
  - 注册表路径：`HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run`
- 单实例运行控制
  - 使用 Windows 命名互斥锁（Mutex）防止重复启动
  - 检测到已运行实例时显示提示并退出
- 壁纸设置重试机制
  - 壁纸设置失败时自动重试最多3次
  - 每次重试间隔1秒，提高成功率
- 静默后台运行，无界面干扰
- 通过 PyInstaller 打包为独立可执行文件
- 兼容开发模式和打包模式的资源路径管理
- 增强的错误处理和用户提示


