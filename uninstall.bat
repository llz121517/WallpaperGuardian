@echo off
:: WallpaperGuardian 卸载脚本
:: 作者: li, 邮箱: q1qaz2wsx91@outlook.com
:: 功能: 完整清理自启动项、进程和临时文件

color 0a
cls
echo.
echo ==============================================
echo    WallpaperGuardian 卸载程序
echo ==============================================
echo.

set "APP_NAME=WallpaperGuardian"
set "REG_PATH=HKCU\Software\Microsoft\Windows\CurrentVersion\Run"
set "SHORTCUT=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\%APP_NAME%.lnk"
set "PROCESS_NAME=%APP_NAME%.exe"

:: 提示用户
echo 此脚本将执行以下操作：
echo 1. 结束正在运行的 %PROCESS_NAME% 进程
echo 2. 删除注册表自启动项
echo 3. 删除启动目录快捷方式
echo 4. 清理临时文件（如果存在）
echo.
choice /c YN /n /m "确定要继续吗? [Y/N]: "
if not "%errorlevel%"=="1" (
    echo.
    echo 操作已取消。
    timeout /t 2 >nul
    exit /b
)

echo.
echo ==============================================
echo   正在清理 WallpaperGuardian...
echo ==============================================

:: 1. 结束进程
echo [步骤1/4] 结束进程...
taskkill /f /im "%PROCESS_NAME%" 2>nul
if "%errorlevel%"=="0" (
    echo     ? 成功结束 %PROCESS_NAME%
) else (
    echo     ○ %PROCESS_NAME% 未运行或已结束
)

:: 等待片刻确保进程完全退出
timeout /t 1 >nul

:: 2. 删除注册表项
echo [步骤2/4] 清理注册表...
reg query "%REG_PATH%" /v "%APP_NAME%" >nul 2>&1
if "%errorlevel%"=="0" (
    reg delete "%REG_PATH%" /v "%APP_NAME%" /f >nul
    if "%errorlevel%"=="0" (
        echo     ? 注册表自启动项已删除
    ) else (
        echo     ? 注册表项删除失败
    )
) else (
    echo     ○ 注册表项不存在
)

:: 3. 删除快捷方式
echo [步骤3/4] 删除快捷方式...
if exist "%SHORTCUT%" (
    del /q "%SHORTCUT%" >nul 2>&1
    if not exist "%SHORTCUT%" (
        echo     ? 启动目录快捷方式已删除
    ) else (
        echo     ? 快捷方式删除失败
    )
) else (
    echo     ○ 快捷方式不存在
)

:: 4. 清理PyInstaller临时文件
echo [步骤4/4] 清理临时文件...
for /f "tokens=*" %%i in ('wmic process where "name='%PROCESS_NAME%'" get ExecutablePath /value 2^>nul ^| findstr "="') do (
    for /f "delims== tokens=2" %%j in ("%%i") do (
        set "EXE_PATH=%%j"
    )
)
if defined EXE_PATH (
    set "TEMP_DIR=%TEMP%\_MEI*"
    pushd "%TEMP%" >nul 2>&1
    for /d %%d in (_MEI*) do (
        if exist "%%d\%PROCESS_NAME%" (
            echo     ? 发现并清理临时目录: %%d
            rd /s /q "%%d" >nul 2>&1
        )
    )
    popd >nul
) else (
    echo     ○ 无法确定程序路径，跳过临时文件清理
)

echo.
echo ==============================================
echo             卸载完成！
echo ==============================================
echo.
echo 所有相关项目已清理完毕。
echo 如果需要重新安装，请重启电脑后操作。
echo.
pause