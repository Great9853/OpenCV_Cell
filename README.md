
# Open_Cell 程序说明

## 原创声明
2025 Great9853(Logic)版权所有
本软件为原创作品，未经许可不得擅自修改、反编译或用于商业用途

## 引用说明
如使用本程序或代码片段，请注明出处：

## 功能概述
本程序是一个基于OpenCV的图像处理工具，主要功能包括：
- 图像文件批量处理
- 基础图像处理操作（如滤波、边缘检测等）
- 图像分析与特征提取
- 数据可视化与结果导出

## 程序结构
Open_Cell/
├── build.bat          # 程序打包脚本
├── install_deps.bat   # 依赖安装脚本
├── OpenCv_cell.py     # 主程序源代码
├── icno.ico           # 程序图标
└── README.md          # 说明文档

## 使用说明
1. 安装依赖：
   - 运行`install_deps.bat`自动安装所需Python库
2. 打包程序：
   - 运行`build.bat`生成可执行文件
3. 运行程序：
   - 生成的EXE文件位于`dist`目录下

## 开发环境
- Python 4.x
- 主要依赖库：
  - opencv-python
  - numpy
  - matplotlib
  - Pillow
  - imageio
  - pandas
