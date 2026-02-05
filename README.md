# Wallpaper Guardian - 壁纸守护工具

一个轻量级的 Windows 桌面壁纸守护程序，自动监控并恢复指定的壁纸设置，防止壁纸被意外更改。

## 功能特性

- 🖼️ **自动壁纸锁定**：持续监控桌面壁纸状态，检测到更改时自动恢复
- 🚀 **开机自启动**：自动配置注册表实现开机自启
- 🔒 **单实例运行**：防止程序重复启动，确保系统资源合理使用
- 🎯 **静默后台运行**：无界面干扰，在后台默默工作
- 📦 **独立可执行文件**：无需安装 Python 环境即可运行
- ♻️ **重试机制**：壁纸设置失败时自动重试，提高成功率

## 系统要求

- **操作系统**：Windows 7/8/10/11
- **磁盘空间**：约 20MB（包含打包后的程序）
- **权限**：需要当前用户权限以修改注册表和设置壁纸

## 快速开始

### 方式一：直接运行可执行文件

1. 从 `dist` 目录中找到 `WallpaperGuardian.exe`
2. 双击运行即可
3. 程序会自动将 `resources/wallpaper.jpg` 设置为桌面壁纸
4. 程序将在后台持续运行，保护壁纸不被更改

### 方式二：从源码运行

#### 安装依赖

```bash
pip install -r requirements.txt
```

#### 运行程序

```bash
python main.py
```

## 项目结构

```
wallpaper_guard/
├── main.py                 # 主程序入口
├── requirements.txt        # Python 依赖包列表
├── resources/
│   └── wallpaper.jpg      # 默认壁纸文件
├── dist/                   # 打包后的可执行文件
│   └── WallpaperGuardian.exe
├── build/                  # PyInstaller 构建临时文件
├── uninstall.bat          # 卸载脚本
└── README.md              # 项目说明文档
```

## 打包说明

如需重新打包程序，使用以下命令：

```bash
pyinstaller --onefile --windowed --name=WallpaperGuardian --add-data "resources;resources" main.py
```

参数说明：
- `--onefile`：打包为单个可执行文件
- `--windowed`：不显示控制台窗口
- `--name`：指定输出文件名
- `--add-data`：添加资源文件到打包程序中

## 使用说明

### 首次运行

1. 运行程序后，会自动将 `resources/wallpaper.jpg` 设置为桌面壁纸
2. 程序会自动添加到开机启动项
3. 程序窗口会自动隐藏，在后台运行

### 更换壁纸

如需更换守护的壁纸：

1. 替换 `resources/wallpaper.jpg` 文件为你想要的壁纸
2. 重新打包程序或从源码运行

### 停止程序

通过任务管理器结束 `WallpaperGuardian.exe` 进程即可。

### 卸载

运行 `uninstall.bat` 脚本，或手动执行以下操作：

1. 结束程序进程
2. 删除注册表启动项：`HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run` 中的 `WallpaperGuardian`
3. 删除程序文件

## 技术实现

### 核心技术

- **Python**：主要开发语言
- **PyInstaller**：打包为 Windows 可执行文件
- **Windows API**：通过 `ctypes` 调用系统 API 进行壁纸管理
- **Windows 注册表**：实现开机自启动功能

### 关键功能实现

- **单实例控制**：使用 Windows 命名互斥锁（Mutex）
- **壁纸监控**：每 10 秒检测一次当前壁纸路径
- **壁纸设置**：调用 `SystemParametersInfoW` API，带 3 次重试机制
- **资源管理**：兼容开发模式和打包模式的资源路径获取

## 注意事项

⚠️ **重要提示**：

1. 程序会持续运行并监控壁纸状态，可能占用少量系统资源
2. 如需临时更换壁纸，请先退出程序
3. 确保 `resources/wallpaper.jpg` 文件存在且格式正确
4. 某些安全软件可能会拦截注册表修改操作，请添加信任

## 常见问题

### Q: 程序运行后没有效果？
A: 检查 `resources/wallpaper.jpg` 是否存在，以及是否有权限修改桌面壁纸。

### Q: 如何确认程序正在运行？
A: 打开任务管理器，在进程列表中查找 `WallpaperGuardian.exe`。

### Q: 开机没有自动启动？
A: 检查注册表项 `HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run` 中是否存在 `WallpaperGuardian`。

### Q: 如何临时禁用壁纸保护？
A: 通过任务管理器结束程序进程即可。

## 许可证

本项目仅供学习和个人使用。

## 更新日志

详细的更新记录请查看 [CHANGELOG.md](CHANGELOG.md)
