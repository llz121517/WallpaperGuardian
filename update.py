import json
import os
import sys
import time
import ctypes
import subprocess


def get_exe_dir():
    """获取 Update.exe 自身所在目录"""
    if getattr(sys, 'frozen', False):
        exe_dir = os.path.dirname(sys.executable)
    else:
        exe_dir = os.path.dirname(os.path.abspath(__file__))
    
    print(f"[UPDATE] 程序目录: {exe_dir}")
    print(f"[UPDATE] 运行模式: {'开发环境' if not getattr(sys, 'frozen', False) else '打包环境'}")
    return exe_dir


def kill_wallpaper_guardian():
    """强制杀死所有正在运行的 WallpaperGuardian.exe 进程"""
    try:
        print("[UPDATE] 正在杀死 WallpaperGuardian.exe 进程...")
        result = subprocess.run(
            ['taskkill', '/F', '/IM', 'WallpaperGuardian.exe'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=10
        )
        if not getattr(sys, 'frozen', False):
            print(f"[UPDATE] taskkill 返回码: {result.returncode}")
            if result.stdout:
                print(f"[UPDATE] stdout: {result.stdout.decode('gbk', errors='ignore')}")
        time.sleep(1)
        print("[UPDATE] 进程杀死完成")
    except Exception as e:
        print(f"[UPDATE] 杀死进程失败: {e}")


def download_file(url, dest_path):
    """下载文件到指定路径"""
    try:
        print(f"[UPDATE] 开始下载: {url}")
        print(f"[UPDATE] 保存路径: {dest_path}")
        import urllib.request
        urllib.request.urlretrieve(url, dest_path)
        print("[UPDATE] 下载成功")
        return True
    except Exception as e:
        print(f"[UPDATE] 下载失败: {e}")
        return False


def main():
    try:
        print("[UPDATE] " + "="*50)
        print("[UPDATE] Update.exe 启动")
        print("[UPDATE] " + "="*50)
        
        exe_dir = get_exe_dir()
        config_path = os.path.join(exe_dir, 'config.json')

        # 1. 检查 config.json 是否存在
        if not os.path.exists(config_path):
            print("[UPDATE] config.json 不存在，退出")
            sys.exit(0)
        
        print("[UPDATE] config.json 存在")

        # 2. 读取 config.json
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            print(f"[UPDATE] 配置内容: {json.dumps(config_data, ensure_ascii=False)}")
        except Exception as e:
            print(f"[UPDATE] 读取 config.json 失败: {e}")
            sys.exit(0)

        remote_host = config_data.get('remote_host', '')
        current_version = config_data.get('current_version', '')
        
        print(f"[UPDATE] 远程主机: {remote_host}")
        print(f"[UPDATE] 当前版本: {current_version}")

        if not remote_host:
            print("[UPDATE] remote_host 为空，退出")
            sys.exit(0)

        # 3. 发送 HTTP POST 请求
        try:
            import urllib.request
            import urllib.error

            post_data = json.dumps(config_data).encode('utf-8')
            print(f"[UPDATE] 发送 POST 请求到: {remote_host}")
            print(f"[UPDATE] 请求数据: {post_data.decode('utf-8')}")
            
            req = urllib.request.Request(
                remote_host,
                data=post_data,
                headers={'Content-Type': 'application/json'},
                method='POST'
            )

            response = urllib.request.urlopen(req, timeout=10)
            response_data = json.loads(response.read().decode('utf-8'))
            print(f"[UPDATE] 服务器响应: {json.dumps(response_data, ensure_ascii=False)}")
        except Exception as e:
            print(f"[UPDATE] 网络请求失败: {e}")
            sys.exit(0)

        # 4. 解析响应
        if not response_data or response_data.get('exit', False):
            print("[UPDATE] 收到退出指令或空响应，退出")
            sys.exit(0)

        # 5. 执行更新指令
        # 5.1 更新主机地址
        new_host = response_data.get('new_host')
        if new_host:
            print(f"[UPDATE] 更新主机地址: {new_host}")
            config_data['remote_host'] = new_host
            try:
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump(config_data, f, ensure_ascii=False, indent=2)
                print("[UPDATE] 主机地址更新成功")
            except Exception as e:
                print(f"[UPDATE] 写入 config.json 失败: {e}")

        # 5.2 更新主程序
        new_version = response_data.get('new_version')
        if new_version and new_version != current_version:
            print(f"[UPDATE] 检测到新版本: {new_version}")
            try:
                # 拼接下载地址
                download_url = f"{remote_host}/download/{new_version}"
                temp_exe = os.path.join(exe_dir, 'WallpaperGuardian_new.exe')
                main_exe = os.path.join(exe_dir, 'WallpaperGuardian.exe')
                
                print(f"[UPDATE] 下载地址: {download_url}")
                print(f"[UPDATE] 临时文件: {temp_exe}")
                print(f"[UPDATE] 主程序: {main_exe}")

                # 下载新版程序
                if download_file(download_url, temp_exe):
                    # 强制杀死所有正在运行的 WallpaperGuardian.exe 进程
                    kill_wallpaper_guardian()

                    # 替换旧版程序
                    if os.path.exists(main_exe):
                        print("[UPDATE] 删除旧版主程序...")
                        try:
                            os.remove(main_exe)
                            print("[UPDATE] 删除成功")
                        except Exception as e:
                            print(f"[UPDATE] 删除失败: {e}，等待2秒后重试...")
                            time.sleep(2)
                            try:
                                os.remove(main_exe)
                                print("[UPDATE] 重试删除成功")
                            except Exception as e2:
                                print(f"[UPDATE] 重试删除失败: {e2}")
                                sys.exit(0)

                    # 重命名新程序
                    print("[UPDATE] 重命名新程序...")
                    try:
                        os.rename(temp_exe, main_exe)
                        print("[UPDATE] 重命名成功")
                    except Exception as e:
                        print(f"[UPDATE] 重命名失败: {e}，等待2秒后重试...")
                        time.sleep(2)
                        try:
                            os.rename(temp_exe, main_exe)
                            print("[UPDATE] 重试重命名成功")
                        except Exception as e2:
                            print(f"[UPDATE] 重试重命名失败: {e2}")
                            sys.exit(0)

                    # 更新版本号
                    print(f"[UPDATE] 更新版本号: {current_version} -> {new_version}")
                    config_data['current_version'] = new_version
                    try:
                        with open(config_path, 'w', encoding='utf-8') as f:
                            json.dump(config_data, f, ensure_ascii=False, indent=2)
                        print("[UPDATE] 版本号更新成功")
                    except Exception as e:
                        print(f"[UPDATE] 写入版本号失败: {e}")

                    # 启动新版程序，传递 --no-update 参数
                    print(f"[UPDATE] 启动新版程序: {main_exe} --no-update")
                    try:
                        subprocess.Popen(
                            [main_exe, '--no-update'],
                            cwd=exe_dir,
                            creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
                        )
                        print("[UPDATE] 新版程序启动成功")
                    except Exception as e:
                        print(f"[UPDATE] 启动新版程序失败: {e}")
                else:
                    print("[UPDATE] 下载失败，跳过更新")
            except Exception as e:
                print(f"[UPDATE] 更新过程出错: {e}")
        elif new_version == current_version:
            print(f"[UPDATE] 已是最新版本: {current_version}")
        
        print("[UPDATE] " + "="*50)
        print("[UPDATE] Update.exe 退出")
        print("[UPDATE] " + "="*50)

    except Exception as e:
        print(f"[UPDATE] 未捕获的异常: {e}")
        import traceback
        print(traceback.format_exc())
    finally:
        sys.exit(0)


if __name__ == '__main__':
    # 隐藏控制台窗口
    if sys.platform.startswith('win'):
        try:
            ctypes.windll.user32.ShowWindow(
                ctypes.windll.kernel32.GetConsoleWindow(), 
                0
            )
        except Exception:
            pass

    main()
