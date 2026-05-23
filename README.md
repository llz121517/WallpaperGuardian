# Wallpaper Guardian - 壁纸守护工具
[![stars](https://img.shields.io/github/stars/llz121517/WallpaperGuardian)](https://github.com/llz121517/WallpaperGuardian/stargazers)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)](https://www.microsoft.com/windows)

一款 Windows 壁纸守护工具，自动锁定并恢复桌面壁纸，支持后台静默运行、开机自启与远程自动更新。

![](resources/wallpaper.jpg)

• 默认壁纸


## ✨ 功能特性
### 核心功能
- 🖼️ 壁纸自动守护：定时检测壁纸变更，自动还原预设壁纸
- 🔄 远程自动更新：独立更新进程，无感升级主程序
- 🚀 开机自启：注册表静默配置，无需手动设置
- 🔒 单实例锁：互斥进程保护，防止重复运行
- 🧘 后台静默运行：无窗口、无弹窗，常驻后台

### 进阶能力
- 📦 单文件打包：免 Python 环境，直接双击运行
- 🔁 壁纸设置重试：失败自动重试，提升稳定性
- ⚙️ 自动生成配置：首次运行创建 `config.json`
- 📝 轻量自研日志：分级输出、按天分割、自动清理
- 🛡️ 进程隔离：更新程序与主程序完全解耦

> ### 注
> 无法肘击非正版Win7定期将壁纸修改为黑色的机制（改不了纯色 ╮(╯_╰)╭）

## 💻 系统要求
- 系统：Windows 7 / 8 / 10 / 11
- 占用：约 25MB（主程序+更新程序）
- 权限：普通用户权限（需读写注册表、设置壁纸）
- 网络：可选，仅自动更新功能需要

> ### ⚠️ Windows 7 兼容提示
> 如需适配 Win7，打包 Python 版本**必须 ≤3.8**（推荐 3.8.10）。
> 高版本打包会出现缺失系统 DLL、`_winapi` 加载失败等问题。

### ⚠️ 重要安全提示
目前客户端与更新服务端均未实现任何鉴权与校验机制，存在服务器地址被劫持、伪造返回恶意安装包的风险；请务必保证更新服务器完全可信，建议仅在**内网局域网**环境内部署使用，若自行使用非可信公网服务器产生安全风险与相关损失，作者不承担任何责任。

## 🚀 快速开始
### 正式版运行
同一目录保留以下文件：
- `WallpaperGuardian.exe` 主程序
- `Update.exe` 自动更新程序（可选）

双击主程序即可，自动生成配置、设置壁纸、开启守护与更新检测。

### 源码运行
```bash
pip install -r requirements.txt
```
```bash
python main.py
```

## 📁 项目结构
```
wallpaper_guard/
├── main.py            # 主程序入口
├── update.py          # 更新程序入口
├── requirements.txt   # 依赖列表
├── config.json        # 自动生成配置
├── resources/         # 默认壁纸资源
├── dist/              # 打包输出
├── build/             # 打包临时文件
└── uninstall.bat      # 卸载脚本
```

## 🔨 打包命令
主程序：
```bash
pyinstaller --onefile --windowed --name=WallpaperGuardian --add-data "resources;resources" main.py
```
更新程序：
```bash
pyinstaller --onefile --windowed --name=Update update.py
```
开发调试可去掉 `--windowed` 查看控制台日志。

## ⚙️ 配置说明
首次启动自动生成 `config.json`：
```json
{
  "remote_host": "http://localhost:8000",
  "current_version": "1.2.0"
}
```
- `remote_host`：更新服务根地址
- `current_version`：本地版本号

如需重置配置，直接删除文件重启即可自动重建。

## 🧩 使用说明
- 更换壁纸：替换 `resources/wallpaper.jpg` 后重新打包
- 停止程序：任务管理器结束对应进程，或使用`uninstall.bat`杀死
- 卸载：运行 `uninstall.bat`，会自动杀死进程、清理注册表，随后需手动删除程序文件

## 🔄 自动更新流程
1. 主程序后台拉起独立更新进程
2. 读取本地配置，请求服务端版本接口
3. 比对版本，有新版自动下载临时文件
4. 终止旧进程、替换程序文件、更新配置版本
5. 拉起新版主程序，更新进程自动退出

服务端支持返回新版本地址、版本号或仅退出指令，适配自建更新服务。

## 🛠️ 技术亮点
- 基于 Windows 互斥锁实现单实例
- Ctypes 调用系统 API 设置/读取壁纸
- Subprocess 管道捕获子进程日志，统一转发
- 自定义轻量日志：分级打印、按天分文件、自动清旧日志
- 自动区分开发/打包环境，路径与日志目录自适应

## ⚠️ 注意事项
- 守护期间会强制还原壁纸，临时更换请先退出程序
- 安全软件若拦截注册表/网络请求，建议加入信任列表
- 请勿随意删除配置文件与资源目录

## ❓ 常见问题
- 无效果：检查资源完整性、文件权限与控制台日志
- 不开机自启：核对注册表 Run 项是否生成
- 更新失败：检查网络、服务地址配置与防火墙拦截

## 📋 更新日志
### v1.3.0
- 日志系统重构，替换原生 logging 为自定义轻量日志
- 精简代码、降低资源占用与磁盘 I/O
- 优化启动流程与进程日志转发逻辑

其余历史版本迭代详见 [CHANGELOG.md](CHANGELOG.md)

## 📄 开源许可
本项目采用 [MIT](LICENSE) 开源协议，可自由使用与二次开发。

## ⭐ 支持与贡献
欢迎提交 [Issue](https://github.com/llz121517/WallpaperGuard/issues) 与 [PR](https://github.com/llz121517/WallpaperGuard/pulls)，觉得好用可以点 Star 支持！