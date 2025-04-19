@echo off
echo 正在使用阿里云镜像安装依赖库...
pip install opencv-python numpy matplotlib Pillow imageio pandas -i https://mirrors.aliyun.com/pypi/simple/
if errorlevel 1 (
    echo 依赖库安装失败，请检查网络连接
    pause
    exit /b
)

echo 正在打包程序...
pyinstaller --onefile --windowed --icon=icno.ico --add-data "*;." --hidden-import PIL._tkinter_finder OpenCv_cell.py
if errorlevel 1 (
    echo 打包失败，请检查错误信息
    pause
    exit /b
)

echo 打包成功！EXE文件位于 dist 文件夹中
pause