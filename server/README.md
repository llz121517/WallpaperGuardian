# Wallpaper Guardian 更新服务器

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)

基于 FastAPI 的自动更新服务器，为 Wallpaper Guardian 客户端提供版本检查和文件下载服务。

**当前版本**: v1.0.1 (2026-04-07)

## 📋 功能特性

- ✅ 版本检查接口（POST /updater）
- ✅ 文件下载接口（GET /download/{version}）
- ✅ 智能响应策略（无需更新/仅改主机/仅更版本/同时更新）
- ✅ 详细的控制台日志输出
- ✅ 健康检查接口
- ✅ 自动创建版本目录
- ✅ 配置化管理（v1.0.1 新增）
- ✅ 动态文件名返回（v1.0.1 修复）

## 🚀 快速开始

### 1. 安装依赖

```bash
cd server
```

### 2. 准备版本文件

在 `server/versions/` 目录下放置各版本的 exe 文件，命名格式为：`{版本号}.exe`

例如：
```
server/
└── versions/
    ├── 1.0.0.exe
    ├── 1.1.0.exe
    └── 1.2.0.exe
```

### 3. 配置服务器

编辑 `server/main.py` 顶部的配置区：

```python
# 服务器信息
TITLE = "Wallpaper Guardian Update Server"
DESCRIPTION = "壁纸守护程序自动更新服务器"
VERSION = "1.0.1"  # 服务端版本号

# 服务器监听地址及端口
HOST = "0.0.0.0"
PORT = 8000

# 最新版本号（客户端版本）
LATEST_VERSION = "1.2.1"

# 新版本下载地址（可选，用于动态切换服务器）
NEW_HOST = None  # 例如: "http://new-server.com"
```

### 4. 启动服务器

```bash
python main.py
```

服务器将在 `http://0.0.0.0:8000` 启动。

## 📡 API 接口

### 1. 版本检查接口

**请求**
```
POST /updater
Content-Type: application/json

{
  "remote_host": "http://your-server.com/api/updater",
  "current_version": "1.0.0"
}
```

**响应规则**

#### 情况1：无需任何操作
```json
{
  "exit": true
}
```

#### 情况2：仅改主机
```json
{
  "new_host": "http://new-server.com/api/updater"
}
```

#### 情况3：仅更版本
```json
{
  "new_version": "1.1.0"
}
```

#### 情况4：同时改主机 + 更版本
```json
{
  "new_host": "http://new-server.com/api/updater",
  "new_version": "1.1.0"
}
```

### 2. 文件下载接口

**请求**
```
GET /download/{version}
```

**示例**
```
GET /download/1.1.0
```

**响应**
- 成功：返回 `WallpaperGuardian.exe` 文件流
- 失败：返回 404 错误

### 3. 服务器状态

**请求**
```
GET /
```

**响应**
```json
{
  "service": "Wallpaper Guardian Update Server",
  "version": "1.0.1",
  "latest_version": "1.2.1",
  "status": "running",
  "new_host": null
}
```

### 4. 健康检查

**请求**
```
GET /health
```

**响应**
```json
{
  "status": "healthy"
}
```

## 🔧 配置说明

### 修改最新版本

编辑 `main.py`：
```python
LATEST_VERSION = "1.2.1"  # 改为新的客户端版本号
```

### 修改服务端版本

编辑 `main.py`：
```python
VERSION = "1.0.2"  # 改为新的服务端版本号
```

### 动态切换服务器地址

编辑 `main.py`：
```python
NEW_HOST = "http://new-server.com/api/updater"  # 设置新地址
```

设置为 `None` 则不返回新主机地址。

### 添加新版本

1. 将新版 `WallpaperGuardian.exe` 复制到 `versions/` 目录
2. 重命名为 `{版本号}.exe`（例如：`1.2.0.exe`）
3. 更新 `LATEST_VERSION` 配置

## 📝 使用示例

### 测试版本检查

```bash
curl -X POST http://localhost:8000/updater \
  -H "Content-Type: application/json" \
  -d '{"remote_host": "http://localhost:8000/updater", "current_version": "1.0.0"}'
```

### 测试文件下载

```bash
curl -O http://localhost:8000/download/1.1.0
```

### Python 测试脚本

```python
import requests

# 测试版本检查
response = requests.post(
    "http://localhost:8000/updater",
    json={
        "remote_host": "http://localhost:8000/updater",
        "current_version": "1.0.0"
    }
)
print(response.json())

# 测试文件下载
response = requests.get("http://localhost:8000/download/1.1.0")
with open("1.1.0.exe", "wb") as f:
    f.write(response.content)
```

## 📂 项目结构

```
server/
├── main.py              # 服务器主程序
├── requirements.txt     # Python 依赖
├── versions/            # 版本文件存储目录
│   ├── 1.0.0.exe
│   └── 1.1.0.exe
└── README.md           # 说明文档
```

## ⚙️ 部署建议

### 开发环境
```bash
python main.py
```

### 生产环境（使用 Gunicorn）

```bash
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000
```

### 使用 Nginx 反向代理

```nginx
server {
    listen 80;
    server_name update.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 🔍 控制台日志

服务器会输出详细的日志信息：

```
[UPDATE CHECK] 收到更新请求
[UPDATE CHECK] 客户端版本: 1.0.0
[UPDATE CHECK] 客户端服务器: http://localhost:8000/updater
[UPDATE CHECK] 返回新版本号: 1.1.0
[UPDATE CHECK] 响应数据: {'new_version': '1.1.0'}

[DOWNLOAD] 请求下载版本: 1.1.0
[DOWNLOAD] 开始传输文件: D:\server\versions\1.1.0.exe
[DOWNLOAD] 文件大小: 15.23 MB
```

## ⚠️ 注意事项

1. **文件命名**：版本文件必须严格按照 `{版本号}.exe` 格式命名
2. **版本目录**：确保 `versions/` 目录存在且有读写权限
3. **网络安全**：生产环境建议启用 HTTPS
4. **访问控制**：可添加 API Key 或 IP 白名单增强安全性
5. **文件完整性**：建议添加文件哈希校验

## 🛠️ 故障排除

### Q: 启动时提示端口被占用？
A: 修改 `main.py` 中的端口号，或关闭占用 8000 端口的程序。

### Q: 下载返回 404？
A: 检查 `versions/` 目录下是否存在对应版本的文件，文件名是否正确。

### Q: 如何查看服务器是否正常运行？
A: 访问 `http://localhost:8000/health` 查看健康状态。

## 📄 许可证

本项目采用 [MIT 许可证](../LICENSE) - 详情请查看 [LICENSE](../LICENSE) 文件。

## 📝 更新日志

### v1.0.1 (2026-04-07)

**Fixed**:
- 修复下载接口文件名硬编码问题
  - `filename="1.1.0.exe"` → `filename=f"{version}.exe"`
  - 现在下载的文件名与请求的版本号一致
- 修复配置变量拼写错误
  - `DeSCRIPTION` → `DESCRIPTION`

**Changed**:
- 配置化改造
  - 新增 TITLE、DESCRIPTION、VERSION、HOST、PORT 配置变量
  - FastAPI 初始化使用配置变量
  - root 接口响应使用配置变量
  - 启动信息使用配置变量
  - 提高代码可维护性和灵活性
- 更新最新客户端版本号
  - `LATEST_VERSION`: "1.1.1" → "1.2.1"
- root 接口新增 `new_host` 字段
  - 用于动态切换服务器地址

### v1.0.0 (2026-04-06)

**Initial Release**:
- 版本检查接口（POST /updater）
- 文件下载接口（GET /download/{version}）
- 健康检查接口（GET /health）
- 服务器状态接口（GET /）
