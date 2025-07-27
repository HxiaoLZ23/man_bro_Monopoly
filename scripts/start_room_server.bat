@echo off
echo ========================================
echo 🎮 大富翁房间管理服务器启动器
echo ========================================

:: 检查虚拟环境是否存在
if not exist "DaFuWeng\Scripts\activate.bat" (
    echo ❌ 找不到虚拟环境 DaFuWeng
    echo 请确保虚拟环境已正确创建
    pause
    exit /b 1
)

:: 激活虚拟环境
echo 🔄 激活虚拟环境...
call DaFuWeng\Scripts\activate.bat

:: 检查websockets是否已安装
echo 🔍 检查websockets模块...
python -c "import websockets; print('✅ websockets已安装，版本:', websockets.__version__)" 2>nul
if %errorlevel% neq 0 (
    echo ⚠️ websockets未安装，正在安装...
    pip install websockets
    if %errorlevel% neq 0 (
        echo ❌ websockets安装失败
        pause
        exit /b 1
    )
    echo ✅ websockets安装成功
)

:: 启动房间管理服务器
echo 🚀 启动房间管理服务器...
if exist "room_server.py" (
    python room_server.py
) else (
    echo ❌ 找不到房间管理服务器文件
    echo 请确保 room_server.py 文件存在
    pause
    exit /b 1
)

pause 