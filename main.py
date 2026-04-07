import ctypes
import time
import os
import sys
import winreg
import subprocess
import json
import logging
import threading
from datetime import datetime


# ==================== 配置区 ====================
# 以下变量用于生成 config.json 模板
REMOTE_HOST = "http://localhost:8000"  # 基础服务器地址（不含路径）
CURRENT_VERSION = "1.2.1"  # 当前版本号
# ===============================================


# 初始化日志系统
def setup_logger():
    """配置主程序日志"""
    logger = logging.getLogger('WallpaperGuardian')
    logger.setLevel(logging.DEBUG)
    
    # 创建日志目录
    if getattr(sys, 'frozen', False):
        log_dir = os.path.join(os.path.dirname(sys.executable), 'logs')
    else:
        log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # 日志文件名（带日期）
    log_file = os.path.join(log_dir, f'main_{datetime.now().strftime("%Y%m%d")}.log')
    
    # 文件处理器
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    
    # 控制台处理器（仅开发环境）
    if not getattr(sys, 'frozen', False):
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        
        # 添加颜色支持
        class ColorFormatter(logging.Formatter):
            """彩色日志格式化器"""
            # ANSI 颜色代码
            LEVEL_COLORS = {
                'DEBUG': '\033[36m',      # 青色
                'INFO': '\033[32m',       # 绿色
                'WARNING': '\033[33m',    # 黄色
                'ERROR': '\033[31m',      # 红色
                'CRITICAL': '\033[1;31m'  # 亮红色
            }
            UPDATER_COLOR = '\033[35m'    # 紫色 - UPDATE 前缀
            RESET = '\033[0m'             # 重置颜色
            
            def format(self, record):
                # 获取对应级别的颜色
                level_color = self.LEVEL_COLORS.get(record.levelname, '')
                
                # 保存原始消息
                original_msg = record.getMessage()
                
                # 检查是否是 UPDATE 的日志（来自 update.py）
                is_updater = '[UPDATE]' in original_msg
                
                # 如果是 UPDATE 日志，给 [UPDATE] 添加紫色
                if is_updater:
                    colored_msg = original_msg.replace('[UPDATE]', f'{self.UPDATER_COLOR}[UPDATE]{self.RESET}')
                    # 临时修改消息
                    record.msg = colored_msg
                    record.args = ()
                
                # 先调用父类格式化，生成 asctime
                formatted = super().format(record)
                
                # 保存原始级别名称
                original_levelname = record.levelname
                
                # 给级别名称和方括号都添加颜色
                colored_levelname = f"{level_color}[{original_levelname}]{self.RESET}"
                
                # 替换格式化后的级别名称
                formatted = formatted.replace(f'[{original_levelname}]', colored_levelname)
                
                # 给整行添加颜色（除了重置部分）
                if is_updater:
                    # UPDATE 日志：整行用级别颜色，[UPDATE] 保持紫色
                    formatted = f"{level_color}{formatted}{self.RESET}"
                else:
                    # 普通日志：整行用级别颜色
                    formatted = f"{level_color}{formatted}{self.RESET}"
                
                # 恢复原始值
                record.levelname = original_levelname
                if is_updater:
                    record.msg = original_msg
                
                return formatted
        
        color_formatter = ColorFormatter(
            '%(asctime)s [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(color_formatter)
        logger.addHandler(console_handler)
    
    # 日志格式（文件使用普通格式）
    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    return logger


logger = setup_logger()


def cleanup_old_logs(log_dir, days=30):
    """清理超过指定天数的日志文件"""
    import glob
    from datetime import datetime, timedelta
    
    try:
        # 查找所有日志文件
        log_pattern = os.path.join(log_dir, 'main_*.log')
        log_files = glob.glob(log_pattern)
        
        if not log_files:
            logger.debug("没有发现日志文件，无需清理")
            return
        
        # 计算截止日期
        cutoff_date = datetime.now() - timedelta(days=days)
        deleted_count = 0
        
        for log_file in log_files:
            try:
                # 从文件名提取日期（格式：main_YYYYMMDD.log）
                filename = os.path.basename(log_file)
                date_str = filename.replace('main_', '').replace('.log', '')
                
                # 解析日期
                file_date = datetime.strptime(date_str, '%Y%m%d')
                
                # 如果文件日期早于截止日期，删除
                if file_date < cutoff_date:
                    os.remove(log_file)
                    deleted_count += 1
                    logger.info(f"已删除过期日志: {filename}")
            except Exception as e:
                logger.warning(f"处理日志文件失败 {log_file}: {e}")
        
        if deleted_count > 0:
            logger.info(f"日志清理完成，共删除 {deleted_count} 个文件")
        else:
            logger.debug("没有过期的日志文件需要清理")
            
    except Exception as e:
        logger.error(f"日志清理失败: {e}")


WIN_VER = sys.getwindowsversion().major


def show_error(msg):
    """显示错误消息框"""
    ctypes.windll.user32.MessageBoxW(0, msg, "Wallpaper Guardian Error", 0x10)


def ensure_single_instance():
    mutex_name = "WallpaperGuardian_SingleInstance"

    try:
        # 尝试创建命名互斥锁
        logger.debug("检查单实例锁...")
        mutex = ctypes.windll.kernel32.CreateMutexW(
            None,
            True,
            mutex_name
        )

        last_error = ctypes.windll.kernel32.GetLastError()
        if last_error == 183:  # ERROR_ALREADY_EXISTS
            # 互斥锁已存在，说明已有实例在运行
            logger.debug("检测到已有实例在运行")
            ctypes.windll.user32.MessageBoxW(0, "程序已在运行中", "Wallpaper Guardian", 0x40)

            return False
        else:
            # 成功创建互斥锁，允许运行
            logger.debug("单实例锁创建成功")
            return True

    except Exception as e:
        logger.debug(f"互斥锁检查失败: {e}")
        return True


def set_autostart():
    """设置开机自启动"""
    try:
        exe_path = sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(sys.argv[0])
        logger.debug(f"设置开机自启动: {exe_path}")

        # 添加注册表自启动项
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0, winreg.KEY_WRITE
            )
            winreg.SetValueEx(key, "WallpaperGuardian", 0, winreg.REG_SZ, f'"{exe_path}"')
            winreg.CloseKey(key)
            logger.info("注册表自启动设置成功")
        except Exception as e:
            logger.error(f"注册表设置失败: {str(e)}")
            show_error(f"注册表设置失败: {str(e)}")

        return True
    except Exception as e:
        logger.error(f"自启动设置异常: {str(e)}")
        show_error(f"自启动设置失败: {str(e)}")
        return False


def get_wallpaper():
    """获取当前壁纸路径"""
    try:
        SPI_GETDESKWALLPAPER = 0x0073
        buf = ctypes.create_unicode_buffer(512)
        
        if ctypes.windll.user32.SystemParametersInfoW(SPI_GETDESKWALLPAPER, 512, buf, 0):
            current_wallpaper = buf.value
            logger.debug(f"当前壁纸: {current_wallpaper}")
            return current_wallpaper
        
        logger.warning("获取壁纸路径失败")
        return None
    except Exception as e:
        logger.error(f"壁纸检测失败: {str(e)}")
        show_error(f"壁纸检测失败: {str(e)}")
        return None


def set_wallpaper(path):
    """设置壁纸（带重试机制）"""
    # 开发环境：只打印提示，不实际修改壁纸
    # if not getattr(sys, 'frozen', False):
    #     logger.info(f"[DEV MODE] 跳过壁纸设置: {path}")
    #     return

    logger.info(f"开始设置壁纸: {path}")
    SPI_SETDESKWALLPAPER = 0x0014
    
    for i in range(3):
        try:
            logger.debug(f"尝试设置壁纸 ({i+1}/3)...")
            
            if ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, path, 3):
                logger.info("壁纸设置成功")
                return
            
            logger.warning(f"第 {i+1} 次尝试失败，等待1秒后重试...")
            time.sleep(1)
        except Exception as e:
            logger.error(f"壁纸设置错误: {str(e)}")
            show_error(f"壁纸设置错误: {str(e)}")
            time.sleep(1)
    
    logger.error("壁纸设置失败，已达最大重试次数")
    show_error("壁纸设置失败，请检查文件权限")


def resource_path(relative):
    """获取资源文件路径（兼容开发模式和打包模式）"""
    try:
        base = sys._MEIPASS
        logger.debug(f"打包模式，资源基础路径: {base}")
    except AttributeError:
        base = os.path.abspath(".")
        logger.debug(f"开发模式，资源基础路径: {base}")

    full_path = os.path.join(base, relative)
    logger.debug(f"资源完整路径: {full_path}")
    
    if not os.path.exists(full_path):
        logger.error(f"资源文件不存在: {full_path}")
        show_error(f"缺少资源文件: {relative}")
        sys.exit(1)
    
    return full_path


def get_exe_dir():
    """获取程序真实运行目录"""
    if getattr(sys, 'frozen', False):
        # 打包后：返回 exe 所在目录
        exe_dir = os.path.dirname(sys.executable)
        logger.debug(f"打包模式，程序目录: {exe_dir}")
    else:
        # 开发环境：返回脚本所在目录
        exe_dir = os.path.dirname(os.path.abspath(__file__))
        logger.debug(f"开发模式，程序目录: {exe_dir}")
    
    return exe_dir


def ensure_config_exists():
    """检查并自动生成 config.json（如果不存在）"""
    try:
        exe_dir = get_exe_dir()
        config_path = os.path.join(exe_dir, 'config.json')
        
        logger.debug(f"检查配置文件: {config_path}")
        
        # 如果已存在，直接返回
        if os.path.exists(config_path):
            logger.debug("config.json 已存在，跳过生成")
            return
        
        # 不存在则自动生成
        logger.info("config.json 不存在，开始生成...")
        config_data = {
            "remote_host": REMOTE_HOST,
            "current_version": CURRENT_VERSION
        }
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"config.json 生成成功: {config_data}")
    except Exception as e:
        # 生成失败静默跳过，不影响主程序运行
        logger.warning(f"config.json 生成失败: {e}")


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
        
        logger.debug(f"检查更新程序: {update_program}")
        
        # 检查更新程序是否存在
        if os.path.exists(update_program):
            logger.info("发现更新程序，准备启动...")
            
            # 以独立进程方式后台启动，重定向输出到主进程
            process = subprocess.Popen(
                cmd,
                cwd=exe_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                bufsize=0,  # 无缓冲
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            
            # 启动线程读取更新程序的输出并转发到主程序日志
            def forward_output():
                try:
                    while True:
                        line = process.stdout.readline()
                        if not line:
                            break
                        
                        # 解码并记录日志
                        try:
                            text = line.decode('utf-8', errors='ignore').rstrip()
                            if text:
                                # 根据内容判断日志级别
                                if any(keyword in text for keyword in ['失败', '错误', '异常', 'Error', 'Exception']):
                                    logger.error(f"[UPDATE] {text}")
                                elif any(keyword in text for keyword in ['警告', 'Warning', '不存在']):
                                    logger.warning(f"[UPDATE] {text}")
                                else:
                                    logger.info(f"[UPDATE] {text}")
                        except Exception:
                            pass
                except Exception as e:
                    logger.error(f"输出转发线程异常: {e}")
            
            output_thread = threading.Thread(target=forward_output, daemon=True)
            output_thread.start()
            logger.debug("输出转发线程已启动")
            logger.debug("更新程序已启动（输出将转发到主日志）")
        else:
            logger.debug("更新程序不存在，跳过更新")
    except Exception as e:
        # 更新程序不存在或启动失败，静默跳过
        logger.debug(f"启动更新程序失败: {e}")


def main():
    """主程序 - 壁纸监控循环"""
    logger.info("="*50)
    logger.info("WallpaperGuardian 主程序启动")
    logger.info("="*50)
    
    original = resource_path('resources/wallpaper.jpg')
    logger.debug(f"目标壁纸路径: {original}")

    if not set_autostart():
        logger.warning("自启动设置失败，但继续运行")
        show_error("警告：未能设置自启动，程序将继续运行但不会开机自启")

    logger.info("进入壁纸监控循环...")
    loop_count = 0
    
    while True:
        loop_count += 1
        logger.debug(f"--- 监控循环 #{loop_count} ---")
        
        current = get_wallpaper()
        
        if current and current != original:
            logger.info("检测到壁纸变更！")
            logger.debug(f"当前壁纸: {current}")
            logger.debug(f"目标壁纸: {original}")
            set_wallpaper(original)
        else:
            if current:
                logger.debug("壁纸未变更，无需操作")
            else:
                logger.warning("无法获取当前壁纸路径")
        
        logger.debug("等待10秒后下次检测...")
        time.sleep(10)


if __name__ == '__main__':
    logger.info("#" * 60)
    logger.info("# WallpaperGuardian 程序入口")
    logger.info("#" * 60)
    
    # 检查单实例
    if not ensure_single_instance():
        logger.warning("已有实例在运行，退出")
        sys.exit(0)

    # 隐藏控制台窗口（Windows）
    if sys.platform.startswith('win'):
        logger.debug("隐藏控制台窗口")
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

    # Windows 7 兼容处理
    if WIN_VER == 6:
        logger.debug("Windows 7 环境，设置 PATH")
        os.environ['PATH'] = os.path.dirname(sys.executable) + ';' + os.environ.get('PATH', '')

    # 步骤1: 优先检查并生成 config.json
    logger.info("步骤1: 检查配置文件")
    ensure_config_exists()

    # 步骤2: 检测启动参数，如果没有 --no-update 则启动更新程序
    logger.info("步骤2: 检查启动参数")
    logger.debug(f"启动参数: {sys.argv}")
    
    if '--no-update' not in sys.argv:
        logger.info("未检测到 --no-update 参数，准备启动更新程序")
        launch_update()
    else:
        logger.info("检测到 --no-update 参数，跳过更新程序启动")

    # 步骤3: 清理过期日志
    logger.info("步骤3: 清理过期日志")
    if getattr(sys, 'frozen', False):
        log_dir = os.path.join(os.path.dirname(sys.executable), 'logs')
    else:
        log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
    cleanup_old_logs(log_dir, days=30)

    # 步骤4: 正常运行主程序
    logger.info("步骤4: 启动主程序")
    main()