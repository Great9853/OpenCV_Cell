@echo off
echo ����ʹ�ð����ƾ���װ������...
pip install opencv-python numpy matplotlib Pillow imageio pandas -i https://mirrors.aliyun.com/pypi/simple/
if errorlevel 1 (
    echo �����ⰲװʧ�ܣ�������������
    pause
    exit /b
)

echo ���ڴ������...
pyinstaller --onefile --windowed --icon=icno.ico --add-data "*;." --hidden-import PIL._tkinter_finder OpenCv_cell.py
if errorlevel 1 (
    echo ���ʧ�ܣ����������Ϣ
    pause
    exit /b
)

echo ����ɹ���EXE�ļ�λ�� dist �ļ�����
pause