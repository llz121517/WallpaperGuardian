#!/usr/bin/env python
# main.py

import ctypes
import time
import os
import sys
import glob
import time
import winreg
import subprocess
import json
import threading
from datetime import datetime, timedelta

# ==================== 配置区 ====================
# 以下变量用于生成 config.json 模板
REMOTE_HOST = "http://localhost:8000"  # 基础服务器地址（不含路径）
CURRENT_VERSION = "1.2.1"  # 当前版本号
# ===============================================


class log:
    DEBUG, INFO, WARN, ERROR = range(4)

    level = INFO
    dir = "logs"
    keep = 7
    flush = True

    @classmethod
    def _write(cls, lv, tag, msg):
        if cls.level > lv:
            return
        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{ts}] [{tag}] {msg}"
        print(line, flush=cls.flush)

        os.makedirs(cls.dir, exist_ok=True)
        fname = time.strftime("%Y-%m-%d.log")
        with open(os.path.join(cls.dir, fname), "a", encoding="utf-8") as f:
            f.write(line + "\n")

        cutoff = datetime.now() - timedelta(days=cls.keep)
        for fn in glob.glob(os.path.join(cls.dir, "*.log")):
            if datetime.fromtimestamp(os.path.getmtime(fn)) < cutoff:
                os.remove(fn)

    @classmethod
    def debug(cls, msg): cls._write(cls.DEBUG, "DEBUG", msg)
    @classmethod
    def info(cls, msg):  cls._write(cls.INFO, "INFO", msg)
    @classmethod
    def warn(cls, msg):  cls._write(cls.WARN, "WARN", msg)
    @classmethod
    def error(cls, msg): cls._write(cls.ERROR, "ERROR", msg)
    @classmethod
    def update(cls, msg): cls._write(cls.INFO, "UPDATE", msg)

log = log


WIN_VER = sys.getwindowsversion().major

def show_error(msg):
    """显示错误消息框"""
    ctypes.windll.user32.MessageBoxW(0, msg, "Wallpaper Guardian Error", 0x10)


def ensure_single_instance():
    mutex_name = "WallpaperGuardian_SingleInstance"

    try:
        # 尝试创建命名互斥锁
        log.debug("检查单实例锁...")
        mutex = ctypes.windll.kernel32.CreateMutexW(
            None,
            True,
            mutex_name
        )

        last_error = ctypes.windll.kernel32.GetLastError()
        if last_error == 183:  # ERROR_ALREADY_EXISTS
            # 互斥锁已存在，说明已有实例在运行
            log.debug("检测到已有实例在运行")
            ctypes.windll.user32.MessageBoxW(0, "程序已在运行中", "Wallpaper Guardian", 0x40)

            return False
        else:
            # 成功创建互斥锁，允许运行
            log.debug("单实例锁创建成功")
            return True

    except Exception as e:
        log.debug(f"互斥锁检查失败: {e}")
        return True


def set_autostart():
    """设置开机自启动"""
    try:
        exe_path = sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(sys.argv[0])
        log.debug(f"设置开机自启动: {exe_path}")

        # 添加注册表自启动项
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0, winreg.KEY_WRITE
            )
            winreg.SetValueEx(key, "WallpaperGuardian", 0, winreg.REG_SZ, f'"{exe_path}"')
            winreg.CloseKey(key)
            log.info("注册表自启动设置成功")
        except Exception as e:
            log.error(f"注册表设置失败: {str(e)}")
            show_error(f"注册表设置失败: {str(e)}")

        return True
    except Exception as e:
        log.error(f"自启动设置异常: {str(e)}")
        show_error(f"自启动设置失败: {str(e)}")
        return False


def get_wallpaper():
    """获取当前壁纸路径"""
    try:
        SPI_GETDESKWALLPAPER = 0x0073
        buf = ctypes.create_unicode_buffer(512)
        
        if ctypes.windll.user32.SystemParametersInfoW(SPI_GETDESKWALLPAPER, 512, buf, 0):
            current_wallpaper = buf.value
            log.debug(f"当前壁纸: {current_wallpaper}")
            return current_wallpaper
        
        log.warn("获取壁纸路径失败")
        return None
    except Exception as e:
        log.error(f"壁纸检测失败: {str(e)}")
        show_error(f"壁纸检测失败: {str(e)}")
        return None


def set_wallpaper(path):
    """设置壁纸（带重试机制）"""
    # 开发环境：只打印提示，不实际修改壁纸
    # if not getattr(sys, 'frozen', False):
    #     logger.info(f"[DEV MODE] 跳过壁纸设置: {path}")
    #     return

    log.info(f"开始设置壁纸: {path}")
    SPI_SETDESKWALLPAPER = 0x0014
    
    for i in range(3):
        try:
            log.debug(f"尝试设置壁纸 ({i + 1}/3)...")
            
            if ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, path, 3):
                log.info("壁纸设置成功")
                return
            
            log.warn(f"第 {i + 1} 次尝试失败，等待1秒后重试...")
            time.sleep(1)
        except Exception as e:
            log.error(f"壁纸设置错误: {str(e)}")
            show_error(f"壁纸设置错误: {str(e)}")
            time.sleep(1)
    
    log.error("壁纸设置失败，已达最大重试次数")
    show_error("壁纸设置失败，请检查文件权限")


def resource_path(relative):
    """获取资源文件路径（兼容开发模式和打包模式）"""
    try:
        base = sys._MEIPASS
        log.debug(f"打包模式，资源基础路径: {base}")
    except AttributeError:
        base = os.path.abspath(".")
        log.debug(f"开发模式，资源基础路径: {base}")

    full_path = os.path.join(base, relative)
    log.debug(f"资源完整路径: {full_path}")
    
    if not os.path.exists(full_path):
        log.error(f"资源文件不存在: {full_path}")
        show_error(f"缺少资源文件: {relative}")
        sys.exit(1)
    
    return full_path


def get_exe_dir():
    """获取程序真实运行目录"""
    if getattr(sys, 'frozen', False):
        # 打包后：返回 exe 所在目录
        exe_dir = os.path.dirname(sys.executable)
        log.debug(f"打包模式，程序目录: {exe_dir}")
    else:
        # 开发环境：返回脚本所在目录
        exe_dir = os.path.dirname(os.path.abspath(__file__))
        log.debug(f"开发模式，程序目录: {exe_dir}")
    
    return exe_dir


def ensure_config_exists():
    """检查并自动生成 config.json（如果不存在）"""
    try:
        exe_dir = get_exe_dir()
        config_path = os.path.join(exe_dir, 'config.json')
        
        log.debug(f"检查配置文件: {config_path}")
        
        # 如果已存在，直接返回
        if os.path.exists(config_path):
            log.debug("config.json 已存在，跳过生成")
            return
        
        # 不存在则自动生成
        log.info("config.json 不存在，开始生成...")
        config_data = {
            "remote_host": REMOTE_HOST,
            "current_version": CURRENT_VERSION
        }
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, ensure_ascii=False, indent=2)
        
        log.info(f"config.json 生成成功: {config_data}")
    except Exception as e:
        # 生成失败静默跳过，不影响主程序运行
        log.warn(f"config.json 生成失败: {e}")


def launch_update():
    """启动更新程序，并捕获其 print 输出转发到 LLog"""
    try:
        exe_dir = get_exe_dir()

        # 选择启动文件
        if getattr(sys, 'frozen', False):
            update_exe = os.path.join(exe_dir, "Update.exe")
            cmd = [update_exe]
        else:
            update_exe = os.path.join(exe_dir, "update.py")
            cmd = [sys.executable, "-u", update_exe]

        log.debug(f"检查更新程序: {update_exe}")

        if not os.path.exists(update_exe):
            log.debug("更新程序不存在，跳过")
            return

        log.info("发现更新程序，正在后台启动...")

        # 启动更新程序，捕获 stdout
        process = subprocess.Popen(
            cmd,
            cwd=exe_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
        )

        # 线程：实时捕获 Update.exe 的 print
        def forward_output():
            if not show_update_log:
                log.debug("更新程序日志已被屏蔽")
                return

            while True:
                line = process.stdout.readline()
                if not line:
                    break

                try:
                    text = line.decode("utf-8", errors="ignore").strip()
                    if not text:
                        continue

                    log.update(text)
                except:
                    pass

        # 启动守护线程
        t = threading.Thread(target=forward_output, daemon=True)
        t.start()
        log.debug("更新程序已启动")

    except Exception as e:
        log.debug(f"启动更新失败: {e}")


def main():
    """主程序 - 壁纸监控循环"""
    log.info("=" * 50)
    log.info("WallpaperGuardian 主程序启动")
    log.info("=" * 50)
    
    original = resource_path('resources/wallpaper.jpg')
    log.debug(f"目标壁纸路径: {original}")

    if not set_autostart():
        log.warn("自启动设置失败，但继续运行")
        show_error("警告：未能设置自启动，程序将继续运行但不会开机自启")

    log.info("进入壁纸监控循环...")
    loop_count = 0
    
    while True:
        loop_count += 1
        log.debug(f"--- 监控循环 #{loop_count} ---")
        
        current = get_wallpaper()
        
        if current and current != original:
            log.info("检测到壁纸变更！")
            log.debug(f"当前壁纸: {current}")
            log.debug(f"目标壁纸: {original}")
            set_wallpaper(original)
        else:
            if current:
                log.debug("壁纸未变更，无需操作")
            else:
                log.warn("无法获取当前壁纸路径")
        
        log.debug("等待10秒后下次检测...")
        time.sleep(10)


if __name__ == '__main__':
    # 初始化日志参数
    log.level = log.DEBUG
    log.dir = "logs"
    log.keep = 7
    log.flush = True
    show_update_log = True

    log.info("=" * 60)
    log.info("程序入口")
    log.info("=" * 60)
    
    # 检查单实例
    if not ensure_single_instance():
        log.warn("\n已有实例在运行，退出")
        sys.exit(0)

    # 隐藏控制台窗口（Windows）
    if sys.platform.startswith('win'):
        log.debug("隐藏控制台窗口")
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

    # Windows 7 兼容处理
    if WIN_VER == 6:
        log.debug("Windows 7 环境，设置 PATH")
        os.environ['PATH'] = os.path.dirname(sys.executable) + ';' + os.environ.get('PATH', '')

    # 步骤1: 检查并生成 config.json
    log.info("步骤1: 检查配置文件")
    ensure_config_exists()

    log.info("步骤2: 启动更新程序")
    launch_update()

    log.info("步骤3: 启动主程序")
    main()