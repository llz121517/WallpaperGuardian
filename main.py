import ctypes
import time
import os
import sys
import winreg
import subprocess
import json


# ==================== 配置区 ====================
# 以下变量用于生成 config.json 模板
REMOTE_HOST = "http://localhost:8000"  # 基础服务器地址（不含路径）
CURRENT_VERSION = "1.1.1"  # 当前版本号
# ===============================================


WIN_VER = sys.getwindowsversion().major


def show_error(msg):
    ctypes.windll.user32.MessageBoxW(0, msg, "Wallpaper Guardian Error", 0x10)



def ensure_single_instance():
    mutex_name = "WallpaperGuardian_SingleInstance"

    try:
        # 尝试创建命名互斥锁
        print("[DEBUG] 检查单实例锁...")
        mutex = ctypes.windll.kernel32.CreateMutexW(
            None,
            True,
            mutex_name
        )

        last_error = ctypes.windll.kernel32.GetLastError()
        if last_error == 183:  # ERROR_ALREADY_EXISTS
            # 互斥锁已存在，说明已有实例在运行
            print("[DEBUG] 检测到已有实例在运行")
            ctypes.windll.user32.MessageBoxW(0, "程序已在运行中", "Wallpaper Guardian", 0x40)

            return False
        else:
            # 成功创建互斥锁，允许运行
            print("[DEBUG] 单实例锁创建成功")
            return True

    except Exception as e:
        print(f"[DEBUG] 互斥锁检查失败: {e}")
        return True


def set_autostart():
    try:
        exe_path = sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(sys.argv[0])
        print(f"[DEBUG] 设置开机自启动: {exe_path}")

        # 添加注册表自启动项
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                 r"Software\Microsoft\Windows\CurrentVersion\Run",
                                 0, winreg.KEY_WRITE)
            winreg.SetValueEx(key, "WallpaperGuardian", 0, winreg.REG_SZ, f'"{exe_path}"')
            winreg.CloseKey(key)
            print("[DEBUG] 注册表自启动设置成功")
        except Exception as e:
            print(f"[DEBUG] 注册表设置失败: {str(e)}")
            show_error(f"注册表设置失败: {str(e)}")

        return True
    except Exception as e:
        print(f"[DEBUG] 自启动设置异常: {str(e)}")
        show_error(f"自启动设置失败: {str(e)}")
        return False


def get_wallpaper():
    """获取当前壁纸路径（增强兼容性）"""
    try:
        SPI_GETDESKWALLPAPER = 0x0073
        buf = ctypes.create_unicode_buffer(512)
        if ctypes.windll.user32.SystemParametersInfoW(SPI_GETDESKWALLPAPER, 512, buf, 0):
            current_wallpaper = buf.value
            print(f"[DEBUG] 当前壁纸: {current_wallpaper}")
            return current_wallpaper
        print("[DEBUG] 获取壁纸路径失败")
        return None
    except Exception as e:
        print(f"[DEBUG] 壁纸检测失败: {str(e)}")
        show_error(f"壁纸检测失败: {str(e)}")
        return None


def set_wallpaper(path):
    """设置壁纸（带重试机制）"""
    # 开发环境：只打印提示，不实际修改壁纸
    if not getattr(sys, 'frozen', False):
        print(f"[DEV MODE] 跳过壁纸设置: {path}")
        return
    
    print(f"[DEBUG] 开始设置壁纸: {path}")
    SPI_SETDESKWALLPAPER = 0x0014
    for i in range(3):
        try:
            print(f"[DEBUG] 尝试设置壁纸 ({i+1}/3)...")
            if ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, path, 3):
                print("[DEBUG] 壁纸设置成功")
                return
            print(f"[DEBUG] 第 {i+1} 次尝试失败，等待1秒后重试...")
            time.sleep(1)
        except Exception as e:
            print(f"[DEBUG] 壁纸设置错误: {str(e)}")
            show_error(f"壁纸设置错误: {str(e)}")
            time.sleep(1)
    print("[DEBUG] 壁纸设置失败，已达最大重试次数")
    show_error("壁纸设置失败，请检查文件权限")


def resource_path(relative):
    """获取资源文件路径（兼容开发模式和打包模式）"""
    try:
        base = sys._MEIPASS
        print(f"[DEBUG] 打包模式，资源基础路径: {base}")
    except AttributeError:
        base = os.path.abspath(".")
        print(f"[DEBUG] 开发模式，资源基础路径: {base}")

    full_path = os.path.join(base, relative)
    print(f"[DEBUG] 资源完整路径: {full_path}")
    if not os.path.exists(full_path):
        print(f"[DEBUG] 资源文件不存在: {full_path}")
        show_error(f"缺少资源文件: {relative}")
        sys.exit(1)
    return full_path


def get_exe_dir():
    """获取程序真实运行目录（禁止使用临时目录）"""
    if getattr(sys, 'frozen', False):
        # 打包后：返回 exe 所在目录
        exe_dir = os.path.dirname(sys.executable)
        print(f"[DEBUG] 打包模式，程序目录: {exe_dir}")
    else:
        # 开发环境：返回脚本所在目录
        exe_dir = os.path.dirname(os.path.abspath(__file__))
        print(f"[DEBUG] 开发模式，程序目录: {exe_dir}")
    return exe_dir


def ensure_config_exists():
    """检查并自动生成 config.json（如果不存在）"""
    try:
        exe_dir = get_exe_dir()
        config_path = os.path.join(exe_dir, 'config.json')
        
        print(f"[DEBUG] 检查配置文件: {config_path}")
        # 如果已存在，直接返回
        if os.path.exists(config_path):
            print("[DEBUG] config.json 已存在，跳过生成")
            return
        
        # 不存在则自动生成
        print("[DEBUG] config.json 不存在，开始生成...")
        config_data = {
            "remote_host": REMOTE_HOST,
            "current_version": CURRENT_VERSION
        }
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, ensure_ascii=False, indent=2)
        print(f"[DEBUG] config.json 生成成功: {config_data}")
    except Exception as e:
        # 生成失败静默跳过，不影响主程序运行
        print(f"[DEBUG] config.json 生成失败: {e}")
        pass


def launch_update():
    """后台静默启动 Update.exe/update.py（不阻塞主程序）"""
    try:
        exe_dir = get_exe_dir()
        
        # 根据运行环境选择不同的更新程序
        if getattr(sys, 'frozen', False):
            # 打包后：启动 Update.exe
            update_program = os.path.join(exe_dir, 'Update.exe')
            cmd = [update_program]
        else:
            # 开发环境：启动 update.py
            update_program = os.path.join(exe_dir, 'update.py')
            cmd = [sys.executable, '-u', update_program]  # -u 强制无缓冲输出
        
        print(f"[DEBUG] 检查更新程序: {update_program}")
        # 检查更新程序是否存在
        if os.path.exists(update_program):
            print(f"[DEBUG] 发现更新程序，准备启动...")
            
            # 以独立进程方式后台启动，重定向输出到主进程
            process = subprocess.Popen(
                cmd,
                cwd=exe_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                bufsize=0,  # 无缓冲
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            
            # 启动线程读取更新程序的输出并转发到主程序控制台
            import threading
            def forward_output():
                try:
                    while True:
                        line = process.stdout.readline()
                        if not line:
                            break
                        # 解码并打印
                        try:
                            text = line.decode('utf-8', errors='ignore').rstrip()
                            if text:
                                print(f"[UPDATE] {text}", flush=True)
                        except Exception:
                            pass
                except Exception as e:
                    print(f"[DEBUG] 输出转发线程异常: {e}")
            
            output_thread = threading.Thread(target=forward_output, daemon=True)
            output_thread.start()
            print("[DEBUG] 输出转发线程已启动")
            
            print("[DEBUG] 更新程序已启动（输出将转发到主控制台）")
        else:
            print("[DEBUG] 更新程序不存在，跳过更新")
    except Exception as e:
        # 更新程序不存在或启动失败，静默跳过
        print(f"[DEBUG] 启动更新程序失败: {e}")
        import traceback
        traceback.print_exc()
        pass


def main():
    print("[DEBUG] " + "="*50)
    print("[DEBUG] WallpaperGuardian 主程序启动")
    print("[DEBUG] " + "="*50)
    
    original = resource_path('resources/wallpaper.jpg')
    print(f"[DEBUG] 目标壁纸路径: {original}")

    if not set_autostart():
        print("[DEBUG] 自启动设置失败，但继续运行")
        show_error("警告：未能设置自启动，程序将继续运行但不会开机自启")

    print("[DEBUG] 进入壁纸监控循环...")
    loop_count = 0
    while True:
        loop_count += 1
        print(f"\n[DEBUG] --- 监控循环 #{loop_count} ---")
        current = get_wallpaper()
        if current and current != original:
            print(f"[DEBUG] 检测到壁纸变更！")
            print(f"[DEBUG] 当前壁纸: {current}")
            print(f"[DEBUG] 目标壁纸: {original}")
            set_wallpaper(original)
        else:
            if current:
                print("[DEBUG] 壁纸未变更，无需操作")
            else:
                print("[DEBUG] 无法获取当前壁纸路径")
        print(f"[DEBUG] 等待10秒后下次检测...")
        time.sleep(10)


if __name__ == '__main__':
    print("\n[DEBUG] " + "#"*60)
    print("[DEBUG] # WallpaperGuardian 程序入口")
    print("[DEBUG] " + "#"*60)
    
    if not ensure_single_instance():
        print("[DEBUG] 已有实例在运行，退出")
        sys.exit(0)

    if sys.platform.startswith('win'):
        print("[DEBUG] 隐藏控制台窗口")
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

    if WIN_VER == 6:
        print("[DEBUG] Windows 7 环境，设置 PATH")
        os.environ['PATH'] = os.path.dirname(sys.executable) + ';' + os.environ.get('PATH', '')

    # 1. 优先检查并生成 config.json
    print("\n[DEBUG] >>> 步骤1: 检查配置文件")
    ensure_config_exists()

    # 2. 检测启动参数，如果没有 --no-update 则启动更新程序
    print("\n[DEBUG] >>> 步骤2: 检查启动参数")
    print(f"[DEBUG] 启动参数: {sys.argv}")
    if '--no-update' not in sys.argv:
        print("[DEBUG] 未检测到 --no-update 参数，准备启动更新程序")
        launch_update()
    else:
        print("[DEBUG] 检测到 --no-update 参数，跳过更新程序启动")

    # 3. 正常运行主程序
    print("\n[DEBUG] >>> 步骤3: 启动主程序")
    main()