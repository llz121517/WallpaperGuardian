"""
Wallpaper Guardian 更新服务器
提供版本检查和文件下载服务
"""
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
from typing import Optional

app = FastAPI(
    title="Wallpaper Guardian Update Server",
    description="壁纸守护程序自动更新服务器",
    version="1.0.0"
)

# ==================== 配置区 ====================
# 最新版本号
LATEST_VERSION = "1.1.1"

# 新版本下载地址（可选，用于动态切换服务器）
NEW_HOST = None  # 例如: "http://new-server.com"

# 程序文件存储目录
VERSIONS_DIR = os.path.join(os.path.dirname(__file__), "versions")

# 确保版本目录存在
os.makedirs(VERSIONS_DIR, exist_ok=True)
# ===============================================


class UpdateRequest(BaseModel):
    """客户端上传的配置信息"""
    remote_host: str
    current_version: str


class UpdateResponse(BaseModel):
    """服务器响应"""
    exit: Optional[bool] = None
    new_host: Optional[str] = None
    new_version: Optional[str] = None


@app.post("/updater", response_model=UpdateResponse)
async def check_update(request: UpdateRequest):
    """
    版本检查接口
    
    请求体：客户端上传完整 config.json
    响应规则：
    - 无需任何操作：返回 {"exit": true}
    - 仅改主机：{"new_host": "新地址"}
    - 仅更版本：{"new_version": "新版本号"}
    - 同时改主机 + 更版本：{"new_host":"...", "new_version":"..."}
    """
    print(f"[UPDATE CHECK] 收到更新请求")
    print(f"[UPDATE CHECK] 客户端版本: {request.current_version}")
    print(f"[UPDATE CHECK] 客户端服务器: {request.remote_host}")
    
    # 构建响应
    response_data = {}
    
    # 检查是否需要更新主机地址
    if NEW_HOST and NEW_HOST != request.remote_host:
        response_data["new_host"] = NEW_HOST
        print(f"[UPDATE CHECK] 返回新主机地址: {NEW_HOST}")
    
    # 检查是否需要更新版本
    if request.current_version != LATEST_VERSION:
        # 检查新版本文件是否存在
        version_file = os.path.join(VERSIONS_DIR, f"{LATEST_VERSION}.exe")
        if os.path.exists(version_file):
            response_data["new_version"] = LATEST_VERSION
            print(f"[UPDATE CHECK] 返回新版本号: {LATEST_VERSION}")
        else:
            print(f"[UPDATE CHECK] 警告: 新版本文件不存在: {version_file}")
    
    # 如果没有任何更新，返回 exit: true
    if not response_data:
        print(f"[UPDATE CHECK] 无需更新")
        return UpdateResponse(exit=True)
    
    print(f"[UPDATE CHECK] 响应数据: {response_data}")
    return UpdateResponse(**response_data)


@app.get("/download/{version}")
async def download_version(version: str):
    """
    下载指定版本的程序文件
    
    路径参数：
    - version: 版本号（例如: 1.1.0）
    
    返回：对应版本的 1.1.0.exe 文件流
    """
    print(f"[DOWNLOAD] 请求下载版本: {version}")
    
    # 构建文件路径
    file_path = os.path.join(VERSIONS_DIR, f"{version}.exe")
    
    # 检查文件是否存在
    if not os.path.exists(file_path):
        print(f"[DOWNLOAD] 文件不存在: {file_path}")
        raise HTTPException(
            status_code=404,
            detail=f"版本 {version} 的文件不存在"
        )
    
    # 检查是否为文件
    if not os.path.isfile(file_path):
        print(f"[DOWNLOAD] 路径不是文件: {file_path}")
        raise HTTPException(
            status_code=404,
            detail=f"版本 {version} 的路径不是有效文件"
        )
    
    print(f"[DOWNLOAD] 开始传输文件: {file_path}")
    print(f"[DOWNLOAD] 文件大小: {os.path.getsize(file_path) / 1024 / 1024:.2f} MB")
    
    # 返回文件流
    return FileResponse(
        path=file_path,
        filename="1.1.0.exe",
        media_type="application/octet-stream"
    )


@app.get("/")
async def root():
    """服务器状态检查"""
    return {
        "service": "Wallpaper Guardian Update Server",
        "version": "1.0.0",
        "latest_version": LATEST_VERSION,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    
    print("="*60)
    print("Wallpaper Guardian 更新服务器")
    print("="*60)
    print(f"最新版本: {LATEST_VERSION}")
    print(f"版本目录: {VERSIONS_DIR}")
    print(f"服务器地址: http://0.0.0.0:8000")
    print("="*60)
    print("\n可用接口:")
    print("  POST /updater       - 版本检查")
    print("  GET  /download/{v}  - 下载指定版本")
    print("  GET  /              - 服务器状态")
    print("  GET  /health        - 健康检查")
    print("="*60)
    
    # 启动服务器
    uvicorn.run(app, host="0.0.0.0", port=8000)
