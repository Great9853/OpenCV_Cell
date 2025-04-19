@echo off
echo 正在更新pip...
python -m pip install --upgrade pip -i https://mirrors.aliyun.com/pypi/simple/
if errorlevel 1 (
    echo pip更新失败，请检查网络连接
    pause
    exit /b
)

echo 正在使用阿里云镜像安装依赖库...
pip install opencv-python numpy matplotlib Pillow imageio pandas -i https://mirrors.aliyun.com/pypi/simple/
if errorlevel 1 (
    echo 依赖库安装失败，请检查网络连接
    pause
    exit /b
)

echo 所有依赖库已安装完成！
pause