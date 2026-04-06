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

## [1.1.0] - 2026-04-06

### Added

#### 自动更新系统
- 完整的自动更新框架
  - 独立的更新程序（update.py / Update.exe）
  - 远程版本检测和配置管理
  - 支持动态更新服务器地址
  - 自动下载并替换主程序
- 智能更新流程
  - 强制杀死旧进程以解除文件锁
  - 原子性文件替换操作
  - 更新后自动启动新版程序
  - 传递 `--no-update` 参数避免循环更新
- 配置文件管理
  - 首次启动自动生成 config.json
  - 支持 remote_host 和 current_version 配置
  - 可配置的默认服务器地址和版本号
  - 基于 exe 真实目录，禁止使用临时目录
- 进程隔离设计
  - 更新程序与主程序完全独立
  - 主程序退出不影响更新进程
  - 后台静默运行，无窗口干扰

#### 开发支持增强
- 开发环境智能检测
  - 自动识别开发/生产环境
  - 开发环境下跳过实际壁纸修改，保护开发者桌面
  - 只输出调试信息，不执行危险操作
- 详细的调试日志系统
  - 主程序输出带 `[DEBUG]` 前缀
  - 更新程序输出带 `[UPDATE]` 前缀
  - 实时转发子进程输出到主控制台
  - 覆盖所有关键执行路径（启动、配置、监控、更新）
- 灵活的控制台管理
  - 生产环境隐藏控制台窗口
  - 开发环境可选择显示/隐藏
  - 支持通过 PyInstaller 参数控制

### Changed

- 优化程序启动流程
  - 优先检查并生成配置文件
  - 然后启动更新程序
  - 最后进入主循环
- 改进资源路径获取逻辑
  - 明确区分开发和打包环境
  - 所有操作基于 exe 真实目录
- 更新程序启动策略
  - 开发环境启动 update.py
  - 生产环境启动 Update.exe

### Fixed

- 修复开发环境下壁纸被频繁修改的问题
- 修复更新程序输出无法查看的问题
- 修复进程间通信的缓冲问题

---

## [1.0.0] - 2026-02-05

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


