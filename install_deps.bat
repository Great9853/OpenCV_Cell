@echo off
echo ���ڸ���pip...
python -m pip install --upgrade pip -i https://mirrors.aliyun.com/pypi/simple/
if errorlevel 1 (
    echo pip����ʧ�ܣ�������������
    pause
    exit /b
)

echo ����ʹ�ð����ƾ���װ������...
pip install opencv-python numpy matplotlib Pillow imageio pandas -i https://mirrors.aliyun.com/pypi/simple/
if errorlevel 1 (
    echo �����ⰲװʧ�ܣ�������������
    pause
    exit /b
)

echo �����������Ѱ�װ��ɣ�
pause