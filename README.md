# Wallpaper Guardian - 壁纸守护工具

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)](https://www.microsoft.com/windows)

一个功能完善的 Windows 桌面壁纸守护程序，自动监控并恢复指定的壁纸设置，支持远程自动更新和智能日志管理。

## ✨ 功能特性

### 核心功能
- 🖼️ **自动壁纸锁定**：持续监控桌面壁纸状态（每10秒检测），检测到更改时自动恢复
- 🔄 **自动更新系统**：支持远程版本检测、自动下载并更新主程序（v1.1.0 新增）
- 🚀 **开机自启动**：自动配置 Windows 注册表实现开机自启
- 🔒 **单实例运行**：使用命名互斥锁防止程序重复启动
- 🎯 **静默后台运行**：无界面干扰，在后台默默工作

### 高级特性
- 📦 **独立可执行文件**：无需安装 Python 环境即可运行
- ♻️ **重试机制**：壁纸设置失败时自动重试最多3次
- 🔧 **智能配置**：首次启动自动生成配置文件（v1.1.0 新增）
- 🛡️ **进程隔离**：更新程序与主程序完全独立，互不影响（v1.1.0 新增）
- 🎨 **彩色日志系统**：控制台彩色输出，智能级别分类，自动清理旧日志（v1.2.0 新增）

## 📋 系统要求

- **操作系统**：Windows 7/8/10/11
- **磁盘空间**：约 25MB（包含主程序和更新程序）
- **权限**：需要当前用户权限以修改注册表和设置壁纸
- **网络**：自动更新功能需要网络连接（可选）

## 🚀 快速开始

### 方式一：直接运行可执行文件（推荐）

1. 确保以下文件在同一目录：
   - `WallpaperGuardian.exe` - 主程序
   - `Update.exe` - 更新程序（可选，用于自动更新）
   - ~~`resources/wallpaper.jpg` - 默认壁纸~~
   - 默认壁纸已内置到`WallpaperGuardian.exe\resources/wallpaper.jpg`

2. 双击运行 `WallpaperGuardian.exe`

3. 程序会自动：
   - 生成 `config.json` 配置文件
   - 将 `wallpaper.jpg` 设置为桌面壁纸
   - 启动更新检查（如果 Update.exe 存在）
   - 在后台持续监控壁纸状态

### 方式二：从源码运行（开发模式）

#### 1. 安装依赖

```bash
pip install -r requirements.txt
```

#### 2. 运行程序

```bash
python main.py
```

## 📁 项目结构

```
wallpaper_guard/
├── main.py                 # 主程序入口
├── update.py               # 更新程序入口
├── requirements.txt        # Python 依赖包列表
├── config.json             # 配置文件（自动生成）
├── resources/
│   └── wallpaper.jpg      # 默认壁纸文件
├── dist/                   # 打包后的可执行文件
│   ├── WallpaperGuardian.exe
│   └── Update.exe
├── build/                  # PyInstaller 构建临时文件
├── uninstall.bat          # 卸载脚本
├── README.md              # 项目说明文档
└── CHANGELOG.md           # 更新日志
```

## 🔨 打包说明

### 打包主程序

```bash
pyinstaller --onefile --windowed --name=WallpaperGuardian --add-data "resources;resources" main.py
```

### 打包更新程序

```bash
pyinstaller --onefile --windowed --name=Update update.py
```

### 参数说明

- `--onefile`：打包为单个可执行文件
- `--windowed`：不显示控制台窗口（生产环境）
- `--name`：指定输出文件名
- `--add-data`：添加资源文件到打包程序中

**注意**：开发调试时可以移除 `--windowed` 参数以查看控制台输出。

## ⚙️ 配置说明

### config.json（v1.1.0 新增，v1.1.1 优化）

程序首次启动时会自动生成配置文件：

```json
{
  "remote_host": "http://localhost:8000",
  "current_version": "1.2.0"
}
```

**字段说明**：
- `remote_host`：基础服务器地址（不含路径），客户端会自动拼接：
  - 版本检查：`{remote_host}/updater`
  - 文件下载：`{remote_host}/download/{version}`
- `current_version`：当前版本号

**配置示例**：
```json
{
  "remote_host": "http://your-server.com",  // 生产环境
  "current_version": "1.2.0"
}
```

**注意**：
- 配置文件位于程序所在目录，不使用临时目录
- 仅需配置基础 URL，无需指定具体接口路径
- 如需重置配置，删除此文件后重启程序即可自动生成

### 修改默认配置

编辑 `main.py` 顶部的配置区：

```python
# ==================== 配置区 ====================
REMOTE_HOST = "http://your-server.com/api/check"  # 默认服务地址
CURRENT_VERSION = "1.0.0"  # 初始版本号
# ===============================================
```

## 📖 使用说明

### 首次运行

1. 运行程序后，会自动生成 `config.json`
2. 程序会将 `resources/wallpaper.jpg` 设置为桌面壁纸
3. 自动添加到开机启动项
4. 后台启动更新程序检查更新（如果 Update.exe 存在）
5. 程序窗口自动隐藏，在后台运行

### 启动参数

- **正常启动**：`WallpaperGuardian.exe` - 自动检查更新
- **跳过更新**：`WallpaperGuardian.exe --no-update` - 不启动更新程序

### 更换壁纸

如需更换守护的壁纸：

1. 替换 `resources/wallpaper.jpg` 文件为你想要的壁纸
2. 重新打包程序或从源码运行

### 停止程序

通过任务管理器结束 `WallpaperGuardian.exe` 进程即可。

### 卸载

运行 `uninstall.bat` 脚本，或手动执行以下操作：

1. 结束程序进程（WallpaperGuardian.exe 和 Update.exe）
2. 删除注册表启动项：`HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run` 中的 `WallpaperGuardian`
3. 删除程序文件和配置文件

## 🔄 自动更新机制（v1.1.0 新增）

### 工作原理

1. **启动阶段**：主程序启动时自动后台启动更新程序
2. **配置读取**：更新程序读取 `config.json` 获取服务器地址和当前版本
3. **版本检测**：向远程服务器发送 POST 请求（携带完整配置）
4. **响应处理**：解析服务器返回的 JSON 数据
5. **执行更新**：如有新版本，下载并替换主程序
6. **重启程序**：启动新版程序并传递 `--no-update` 参数

### 服务器响应格式

#### 标准响应
```json
{
  "new_host": "http://new-server.com/api/check",  // 可选：更新服务器地址
  "new_version": "1.1.0"                           // 可选：新版本号
}
```

#### 仅退出
```json
{
  "exit": true
}
```

#### 空响应
服务器返回空对象 `{}` 或无 `new_version` 字段时，跳过更新。

### 更新流程详解

1. **下载阶段**
   - 拼接下载地址：`remote_host + /download/ + new_version`
   - 下载到临时文件：`WallpaperGuardian_new.exe`

2. **替换阶段**
   - 强制杀死所有正在运行的 `WallpaperGuardian.exe` 进程
   - 删除旧版主程序文件
   - 重命名临时文件为主程序

3. **配置更新**
   - 更新 `config.json` 中的 `current_version` 字段

4. **启动新版**
   - 启动新版 `WallpaperGuardian.exe --no-update`
   - 更新程序自动退出

### 进程隔离设计

- ✅ 更新程序以独立进程运行
- ✅ 主程序退出不影响更新进程
- ✅ 更新程序完成后自动退出
- ✅ 无窗口、无日志、无弹窗，完全静默

## 🛠️ 技术实现

### 核心技术栈

- **Python**：主要开发语言
- **PyInstaller**：打包为 Windows 可执行文件
- **Windows API**：通过 `ctypes` 调用系统 API
- **Windows 注册表**：实现开机自启动
- **subprocess**：进程管理和通信

### 关键功能实现

- **单实例控制**：使用 Windows 命名互斥锁（Mutex）
- **壁纸监控**：每 10 秒检测一次当前壁纸路径
- **壁纸设置**：调用 `SystemParametersInfoW` API，带 3 次重试机制
- **资源管理**：兼容开发模式和打包模式的资源路径获取
- **进程隔离**：更新程序以独立进程运行，主程序退出不影响更新
- **日志转发**：开发环境下更新程序输出实时转发到主控制台

### 开发环境特性（v1.1.0 增强）

- 自动检测开发/生产环境
- 开发环境下跳过实际壁纸修改，只输出调试信息
- 详细的控制台日志输出：
  - `[DEBUG]` - 主程序调试信息
  - `[UPDATE]` - 更新程序输出（实时转发）
- 启动 `update.py` 而非 `Update.exe`，便于调试
- 支持通过 PyInstaller 参数控制是否显示控制台

### 日志系统（v1.2.0 新增）

#### 彩色控制台输出
- **DEBUG** (青色)：调试信息、配置详情、网络请求参数
- **INFO** (绿色)：正常流程、操作成功、状态变更
- **WARNING** (黄色)：需要注意但不影响运行
- **ERROR** (红色)：错误和失败
- **CRITICAL** (亮红色)：严重错误
- **[UPDATE]** (紫色)：来自更新程序的日志标识

#### 日志文件管理
- 按日期分割：`logs/main_YYYYMMDD.log`
- UTF-8 编码，确保中文正常显示
- 打包后写入 `exe目录/logs/` 文件夹
- 开发环境同时输出到控制台和文件

#### 智能日志清理
- 启动时自动清理 30 天前的旧日志
- 智能识别日志文件名中的日期
- 安全的异常处理，单个文件失败不影响其他
- 详细的清理过程记录

#### 日志转发机制
- update.py 日志回传到主程序统一管理
- 子进程输出通过 PIPE 捕获，daemon 线程实时转发
- 主程序根据内容智能判断日志级别：
  - 包含“失败/错误/异常/Error/Exception” → ERROR
  - 包含“警告/Warning/不存在” → WARNING
  - 其他 → INFO

## ⚠️ 注意事项

1. **壁纸保护**：程序会持续监控并恢复壁纸，如需临时更换壁纸，请先退出程序
2. **文件权限**：确保程序有权限修改注册表和设置壁纸
3. **网络安全**：某些安全软件可能会拦截注册表修改或网络连接，请添加信任
4. **配置文件**：不要手动删除 `config.json`，除非需要重置配置
5. **资源文件**：确保 `resources/wallpaper.jpg` 存在且格式正确
6. **更新服务器**：建议配置可信的更新服务器地址

## ❓ 常见问题

### Q: 程序运行后没有效果？
A: 检查 `resources/wallpaper.jpg` 是否存在，以及是否有权限修改桌面壁纸。查看控制台是否有错误信息。

### Q: 如何确认程序正在运行？
A: 打开任务管理器，在进程列表中查找 `WallpaperGuardian.exe` 和 `Update.exe`。

### Q: 开机没有自动启动？
A: 检查注册表项 `HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run` 中是否存在 `WallpaperGuardian`。

### Q: 如何临时禁用壁纸保护？
A: 通过任务管理器结束 `WallpaperGuardian.exe` 进程即可。

### Q: 如何跳过自动更新？
A: 使用命令行参数启动：`WallpaperGuardian.exe --no-update`

### Q: 开发环境下如何查看调试信息？
A: 直接运行 `python main.py`，控制台会输出详细的 `[DEBUG]` 和 `[UPDATE]` 日志。

### Q: 如何查看自动更新的日志？
A: 开发环境下运行 `python main.py`，控制台会显示 `[UPDATE]` 前缀的更新程序输出。生产环境下更新程序静默运行，无日志输出。

### Q: 自动更新安全吗？
A: 更新程序仅在检测到新版本时才会下载，且下载后会验证文件完整性。建议配置可信的更新服务器。

### Q: 更新失败怎么办？
A: 检查网络连接，确认 `config.json` 中的 `remote_host` 配置正确。查看控制台日志了解具体错误。

## 📝 更新日志

详细的更新记录请查看 [CHANGELOG.md](CHANGELOG.md)

### 最新版本：v1.2.1 (2026-04-07)

**Bug 修复**：
- 修复 Windows 打包后 update.py 日志中文乱码问题
- 修复服务端下载接口文件名硬编码问题
- 修复配置变量拼写错误

**服务端优化**：
- 配置化改造，提高可维护性
- 更新最新版本号到 1.2.0

### 历史版本

**v1.2.0 (2026-04-07)**：
- 完整的彩色日志系统，支持智能级别分类
- [UPDATE] 前缀紫色标识，快速区分来源
- 自动日志清理功能，保持目录整洁
- 优化函数排版和代码结构
- 修复退出提示重复显示问题

**v1.1.0 (2026-04-06)**：
- 完整的自动更新系统
- 配置文件自动生成和管理
- 开发环境调试支持增强
- 进程隔离设计

**v1.0.0 (2026-02-05)**：
- 初始版本发布
- 壁纸守护核心功能

## 📄 许可证

本项目采用 [MIT 许可证](LICENSE) - 详情请查看 [LICENSE](LICENSE) 文件。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

### 贡献指南

1. Fork 本仓库
2. 创建你的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交你的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启一个 Pull Request

## 联系方式

如有问题或建议，请通过以下方式联系：
- 提交 [Issue](https://github.com/llz121517/WallpaperGuard/issues)

## ⭐ 支持项目

如果你觉得这个项目对你有帮助，请给个 Star ⭐ 支持一下！

---

**提示**：本项目使用了静默运行机制，所有操作均在后台完成，不会产生弹窗干扰。
