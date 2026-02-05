import ctypes
import time
import os
import sys
import winreg


WIN_VER = sys.getwindowsversion().major


def show_error(msg):
    ctypes.windll.user32.MessageBoxW(0, msg, "Wallpaper Guardian Error", 0x10)



def ensure_single_instance():
    mutex_name = "WallpaperGuardian_SingleInstance"

    try:
        # 尝试创建命名互斥锁
        mutex = ctypes.windll.kernel32.CreateMutexW(
            None,
            True,
            mutex_name
        )

        last_error = ctypes.windll.kernel32.GetLastError()
        if last_error == 183:  # ERROR_ALREADY_EXISTS
            # 互斥锁已存在，说明已有实例在运行
            ctypes.windll.user32.MessageBoxW(0, "程序已在运行中", "Wallpaper Guardian", 0x40)

            return False
        else:
            # 成功创建互斥锁，允许运行
            return True

    except Exception as e:
        print(f"互斥锁检查失败: {e}")
        return True


def set_autostart():
    try:
        exe_path = sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(sys.argv[0])

        # 添加注册表自启动项
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                 r"Software\Microsoft\Windows\CurrentVersion\Run",
                                 0, winreg.KEY_WRITE)
            winreg.SetValueEx(key, "WallpaperGuardian", 0, winreg.REG_SZ, f'"{exe_path}"')
            winreg.CloseKey(key)
        except Exception as e:
            show_error(f"注册表设置失败: {str(e)}")

        return True
    except Exception as e:
        show_error(f"自启动设置失败: {str(e)}")
        return False


def get_wallpaper():
    """获取当前壁纸路径（增强兼容性）"""
    try:
        SPI_GETDESKWALLPAPER = 0x0073
        buf = ctypes.create_unicode_buffer(512)
        if ctypes.windll.user32.SystemParametersInfoW(SPI_GETDESKWALLPAPER, 512, buf, 0):
            return buf.value
        return None
    except Exception as e:
        show_error(f"壁纸检测失败: {str(e)}")
        return None


def set_wallpaper(path):
    """设置壁纸（带重试机制）"""
    SPI_SETDESKWALLPAPER = 0x0014
    for _ in range(3):
        try:
            if ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, path, 3):
                return
            time.sleep(1)
        except Exception as e:
            show_error(f"壁纸设置错误: {str(e)}")
            time.sleep(1)
    show_error("壁纸设置失败，请检查文件权限")


def resource_path(relative):
    """获取资源文件路径（兼容开发模式和打包模式）"""
    try:
        base = sys._MEIPASS
    except AttributeError:
        base = os.path.abspath(".")

    full_path = os.path.join(base, relative)
    if not os.path.exists(full_path):
        show_error(f"缺少资源文件: {relative}")
        sys.exit(1)
    return full_path


def main():
    original = resource_path('resources/wallpaper.jpg')

    if not set_autostart():
        show_error("警告：未能设置自启动，程序将继续运行但不会开机自启")

    while True:
        current = get_wallpaper()
        if current and current != original:
            set_wallpaper(original)
        time.sleep(10)


if __name__ == '__main__':
    if not ensure_single_instance():
        sys.exit(0)

    if sys.platform.startswith('win'):
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

    if WIN_VER == 6:
        os.environ['PATH'] = os.path.dirname(sys.executable) + ';' + os.environ.get('PATH', '')

    main()