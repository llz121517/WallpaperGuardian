import json
import os
import sys
import time
import ctypes
import subprocess
import logging

# 强制设置 stdout 为 UTF-8 编码（解决 Windows 控制台乱码问题）
if sys.platform.startswith('win'):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 配置日志 - 输出到 stdout（会被主程序捕获）
logging.basicConfig(
    level=logging.DEBUG,
    format='%(message)s',  # 移除 [UPDATE] 前缀，由主程序统一添加
    stream=sys.stdout
)
logger = logging.getLogger('UpdateProgram')


def get_exe_dir():
    """获取 Update.exe 自身所在目录"""
    if getattr(sys, 'frozen', False):
        exe_dir = os.path.dirname(sys.executable)
    else:
        exe_dir = os.path.dirname(os.path.abspath(__file__))
    
    logger.debug(f"程序目录: {exe_dir}")
    logger.debug(f"运行模式: {'开发环境' if not getattr(sys, 'frozen', False) else '打包环境'}")
    return exe_dir


def kill_wallpaper_guardian():
    """强制杀死所有正在运行的 WallpaperGuardian.exe 进程"""
    try:
        logger.info("正在杀死 WallpaperGuardian.exe 进程...")
        result = subprocess.run(
            ['taskkill', '/F', '/IM', 'WallpaperGuardian.exe'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=10
        )
        if result.returncode == 0:
            logger.info("进程杀死成功")
        else:
            logger.warning(f"taskkill 返回码: {result.returncode}")
        time.sleep(1)
    except Exception as e:
        logger.error(f"杀死进程失败: {e}")


def download_file(url, dest_path):
    """下载文件到指定路径"""
    try:
        logger.info(f"开始下载: {url}")
        logger.debug(f"保存路径: {dest_path}")
        import urllib.request
        urllib.request.urlretrieve(url, dest_path)
        logger.info("下载成功")
        return True
    except Exception as e:
        logger.error(f"下载失败: {e}")
        return False


# 全局标志，防止重复退出
_exited = False

def app_exit():
    """安全退出，防止重复调用"""
    global _exited
    if _exited:
        return  # 已经退出过，直接返回
    
    _exited = True
    logger.info("=" * 50)
    logger.info("Update.exe 退出")
    logger.info("=" * 50)
    sys.exit(0)

def main():
    try:
        logger.info("="*50)
        logger.info("Update.exe 启动")
        logger.info("="*50)
        
        exe_dir = get_exe_dir()
        config_path = os.path.join(exe_dir, 'config.json')

        # 1. 检查 config.json 是否存在
        if not os.path.exists(config_path):
            logger.warning("config.json 不存在，退出")
            app_exit()
        
        logger.debug("config.json 存在")

        # 2. 读取 config.json
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            logger.debug(f"配置内容: {json.dumps(config_data, ensure_ascii=False)}")
        except Exception as e:
            logger.error(f"读取 config.json 失败: {e}")
            app_exit()

        remote_host = config_data.get('remote_host', '')
        current_version = config_data.get('current_version', '')
        
        logger.debug(f"服务器地址: {remote_host}")
        logger.debug(f"当前版本: {current_version}")

        if not remote_host:
            logger.error("remote_host 为空，退出")
            app_exit()

        # 3. 发送 HTTP POST 请求
        try:
            import urllib.request
            import urllib.error

            # 拼接 updater 接口地址
            updater_url = f"{remote_host}/updater"
            post_data = json.dumps(config_data).encode('utf-8')
            logger.debug(f"发送 POST 请求到: {updater_url}")
            logger.debug(f"请求数据: {post_data.decode('utf-8')}")
            
            req = urllib.request.Request(
                updater_url,
                data=post_data,
                headers={'Content-Type': 'application/json'},
                method='POST'
            )

            response = urllib.request.urlopen(req, timeout=10)
            response_data = json.loads(response.read().decode('utf-8'))
            logger.debug(f"服务器响应: {json.dumps(response_data, ensure_ascii=False)}")
        except Exception as e:
            logger.error(f"网络请求失败: {e}")
            app_exit()

        # 4. 解析响应
        if not response_data or response_data.get('exit', False):
            logger.info("收到退出指令或空响应，退出")
            app_exit()

        # 5. 执行更新指令
        # 5.1 更新主机地址
        new_host = response_data.get('new_host')
        if new_host:
            logger.warning(f"更新主机地址: {new_host}")
            config_data['remote_host'] = new_host
            try:
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump(config_data, f, ensure_ascii=False, indent=2)
                logger.info("主机地址更新成功")
            except Exception as e:
                logger.error(f"写入 config.json 失败: {e}")

        # 5.2 更新主程序
        new_version = response_data.get('new_version')
        if new_version and new_version != current_version:
            logger.warning(f"检测到新版本: {new_version}")
            try:
                # 拼接下载地址
                download_url = f"{remote_host}/download/{new_version}"
                temp_exe = os.path.join(exe_dir, 'WallpaperGuardian_new.exe')
                main_exe = os.path.join(exe_dir, 'WallpaperGuardian.exe')
                
                logger.info(f"下载地址: {download_url}")
                logger.debug(f"临时文件: {temp_exe}")
                logger.debug(f"主程序: {main_exe}")

                # 下载新版程序
                if download_file(download_url, temp_exe):
                    # 强制杀死所有正在运行的 WallpaperGuardian.exe 进程
                    kill_wallpaper_guardian()

                    # 替换旧版程序
                    if os.path.exists(main_exe):
                        logger.info("删除旧版主程序...")
                        try:
                            os.remove(main_exe)
                            logger.info("删除成功")
                        except Exception as e:
                            logger.warning(f"删除失败: {e}，等待2秒后重试...")
                            time.sleep(2)
                            try:
                                os.remove(main_exe)
                                logger.info("重试删除成功")
                            except Exception as e2:
                                logger.error(f"重试删除失败: {e2}")
                                app_exit()

                    # 重命名新程序
                    logger.info("重命名新程序...")
                    try:
                        os.rename(temp_exe, main_exe)
                        logger.info("重命名成功")
                    except Exception as e:
                        logger.warning(f"重命名失败: {e}，等待2秒后重试...")
                        time.sleep(2)
                        try:
                            os.rename(temp_exe, main_exe)
                            logger.info("重试重命名成功")
                        except Exception as e2:
                            logger.error(f"重试重命名失败: {e2}")
                            app_exit()

                    # 更新版本号
                    logger.info(f"更新版本号: {current_version} -> {new_version}")
                    config_data['current_version'] = new_version
                    try:
                        with open(config_path, 'w', encoding='utf-8') as f:
                            json.dump(config_data, f, ensure_ascii=False, indent=2)
                        logger.info("版本号更新成功")
                    except Exception as e:
                        logger.error(f"写入版本号失败: {e}")

                    # 启动新版程序，传递 --no-update 参数
                    logger.info(f"启动新版程序: {main_exe} --no-update")
                    try:
                        subprocess.Popen(
                            [main_exe, '--no-update'],
                            cwd=exe_dir,
                            creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
                        )
                        logger.info("新版程序启动成功")
                    except Exception as e:
                        logger.error(f"启动新版程序失败: {e}")
                else:
                    logger.error("下载失败，跳过更新")
            except Exception as e:
                logger.error(f"更新过程出错: {e}")
        elif new_version == current_version:
            logger.info(f"已是最新版本: {current_version}")


    except Exception as e:
        logger.error(f"未捕获的异常: {e}")
        import traceback
        logger.error(traceback.format_exc())
    finally:
        app_exit()


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
