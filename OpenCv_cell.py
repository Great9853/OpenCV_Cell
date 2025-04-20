import cv2
import numpy as np
import matplotlib.pyplot as plt
# 修改导入部分，在原有导入基础上添加LabelFrame
from tkinter import Tk, filedialog, messagebox, Toplevel, Canvas, Scrollbar
from tkinter import simpledialog
from tkinter import Label, Scale, Button, HORIZONTAL, Frame, LabelFrame  # 添加LabelFrame
from matplotlib import use as mpl_use
import imageio
import os
from PIL import Image, ImageDraw, ImageFont
from tkinter import Tk, Label, Scale, Button, HORIZONTAL, Frame, filedialog
import pandas as pd  # 新增导入

# 配置matplotlib后端
mpl_use('TkAgg')

class ParameterWindow:
    """参数调节窗口"""
    def __init__(self):
        self.root = Tk()
        self.root.title("参数调节")
        
        # 创建滑动条
        self.hmin = Scale(self.root, label="色相下限", from_=0, to=180, orient=HORIZONTAL)
        self.hmin.set(100)
        self.hmin.pack()
        
        self.hmax = Scale(self.root, label="色相上限", from_=0, to=180, orient=HORIZONTAL)
        self.hmax.set(180)
        self.hmax.pack()
        
        self.smin = Scale(self.root, label="饱和度下限", from_=0, to=255, orient=HORIZONTAL)
        self.smin.set(5)
        self.smin.pack()
        
        self.smax = Scale(self.root, label="饱和度上限", from_=0, to=255, orient=HORIZONTAL)
        self.smax.set(200)
        self.smax.pack()
        
        self.vmin = Scale(self.root, label="明度下限", from_=0, to=255, orient=HORIZONTAL)
        self.vmin.set(120)
        self.vmin.pack()
        
        self.vmax = Scale(self.root, label="明度上限", from_=0, to=255, orient=HORIZONTAL)
        self.vmax.set(255)
        self.vmax.pack()
        
        # 确认按钮
        Button(self.root, text="确认", command=self.root.destroy).pack()
    
    def get_params(self):
        """获取当前参数值"""
        return {
            'hmin': self.hmin.get(),
            'hmax': self.hmax.get(),
            'smin': self.smin.get(),
            'smax': self.smax.get(),
            'vmin': self.vmin.get(),
            'vmax': self.vmax.get()
        }
    
    def show(self):
        """显示窗口"""
        self.root.mainloop()

def select_image():
    """手动选择图片"""
    root = Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="选择细胞图像",
        filetypes=[("图像文件", "*.jpg *.jpeg *.png *.bmp"), ("所有文件", "*.*")]
    )
    root.destroy()
    return file_path

def process_image(img, params):
    # 新增: 使用CLAHE增强对比度
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    l = clahe.apply(l)
    lab = cv2.merge((l,a,b))
    img = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
    
    """处理图像并返回结果"""
    # 颜色空间转换
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower = np.array([params['hmin'], params['smin'], params['vmin']])
    upper = np.array([params['hmax'], params['smax'], params['vmax']])
    mask = cv2.inRange(hsv, lower, upper)

    # 图像处理
    masked = cv2.bitwise_and(img, img, mask=mask)
    gray = cv2.cvtColor(masked, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (7,7), 0)
    
    # 二值化
    _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    
    # 形态学操作
    # 在process_image函数中调整形态学参数
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7,7))  # 增大内核尺寸(原5,5)
    closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=3)  # 增加迭代次数(原2)
    
    # 查找轮廓
    contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # 查找轮廓后添加面积过滤
    min_cell_area = 50  # 最小细胞面积
    max_cell_area = 500  # 最大细胞面积
    valid_contours = []
    
    # 添加圆形度过滤
    valid_contours = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        perimeter = cv2.arcLength(cnt, True)
        if perimeter == 0:
            continue
        circularity = 4 * np.pi * area / (perimeter ** 2)
        
        # 细胞通常圆形度在0.7-1.3之间
        if 0.7 < circularity < 1.3 and min_cell_area < area < max_cell_area:
            valid_contours.append(cnt)
    
    # 使用过滤后的轮廓
    result_img = img.copy()
    cv2.drawContours(result_img, valid_contours, -1, (0,255,0), 2)
    
    # 标注细胞编号
    for i, cnt in enumerate(contours):
        M = cv2.moments(cnt)
        if M["m00"] != 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            cv2.putText(result_img, str(i+1), (cX, cY), 
                      cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    
    return result_img, len(contours)

def put_chinese_text(img, text, position, font_path, font_size, color):
    # 将 OpenCV 图像转换为 PIL 图像
    img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img_pil)
    
    # 加载字体
    try:
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        print(f"无法加载字体文件: {font_path}")
        return img
    
    # 绘制中文文本
    draw.text(position, text, font=font, fill=color)
    
    # 将 PIL 图像转换回 OpenCV 图像
    return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

class MainWindow:
    """主界面"""
    def __init__(self):
        self.root = Tk()
        self.root.title("细胞计数程序")
        self.root.geometry("500x700")  # 增大窗口尺寸
        
        # 主框架布局
        main_frame = Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 图片选择部分
        self.select_frame = LabelFrame(main_frame, text="图像选择", padx=5, pady=5)
        self.select_frame.pack(fill="x", pady=5)
        Button(self.select_frame, text="选择图片", command=self.select_image).pack(pady=5)
        
        # 颜色预设部分
        self.preset_frame = LabelFrame(main_frame, text="颜色预设", padx=5, pady=5)
        self.preset_frame.pack(fill="x", pady=5)
        
        # 修改颜色识别部分，优化蓝色染色细胞的HSV范围：
        colors = [
                 ("紫色", (130, 50, 50), (160, 255, 255)),
                 ("红色", (0, 50, 50), (10, 255, 255)),
                 ("蓝色", (100, 100, 50), (130, 255, 200)),  # 调整蓝色范围，提高饱和度下限
                 ("绿色", (40, 50, 50), (80, 255, 255))]
        
        for i, (name, lower, upper) in enumerate(colors):
            btn = Button(self.preset_frame, text=name, width=8,
                        command=lambda l=lower, u=upper: self.set_color_range(l, u))
            btn.grid(row=0, column=i, padx=5, pady=5)

        # 形态学参数部分 - 移动到颜色预设后面
        self.morph_frame = LabelFrame(main_frame, text="形态学参数", padx=5, pady=5)
        self.morph_frame.pack(fill="x", pady=5)
        
        Label(self.morph_frame, text="内核大小:").grid(row=0, column=0, sticky="e", padx=5)
        self.kernel_size = Scale(self.morph_frame, from_=1, to=15, orient=HORIZONTAL, command=self.update_image)
        self.kernel_size.set(5)
        self.kernel_size.grid(row=0, column=1, sticky="ew", padx=5)
        
        Label(self.morph_frame, text="迭代次数:").grid(row=0, column=2, sticky="e", padx=5)
        self.iterations = Scale(self.morph_frame, from_=1, to=5, orient=HORIZONTAL, command=self.update_image)
        self.iterations.set(2)
        self.iterations.grid(row=0, column=3, sticky="ew", padx=5)

        # 参数调节部分 - 现在放在形态学参数后面
        self.param_frame = LabelFrame(main_frame, text="HSV参数调节", padx=5, pady=5)
        self.param_frame.pack(fill="x", pady=5)
        
        # 使用grid布局使参数更整齐
        labels = ["色相下限", "色相上限", "饱和度下限", "饱和度上限", "明度下限", "明度上限"]
        scales = []
        for i, label in enumerate(labels):
            Label(self.param_frame, text=label).grid(row=i//2, column=(i%2)*2, sticky="e", padx=5)
            scale = Scale(self.param_frame, from_=0, to=255 if "度" in label else 180, 
                         orient=HORIZONTAL, command=self.update_image)
            scale.grid(row=i//2, column=(i%2)*2+1, sticky="ew", padx=5)
            scales.append(scale)
            
        self.hmin, self.hmax, self.smin, self.smax, self.vmin, self.vmax = scales
        
        # 设置默认值
        self.hmin.set(100)
        self.hmax.set(180)
        self.smin.set(5)
        self.smax.set(200)
        self.vmin.set(120)
        self.vmax.set(255)
        
        # 形态学参数部分
        self.morph_frame = LabelFrame(main_frame, text="形态学参数", padx=5, pady=5)
        self.morph_frame.pack(fill="x", pady=5)
        
        Label(self.morph_frame, text="内核大小:").grid(row=0, column=0, sticky="e", padx=5)
        self.kernel_size = Scale(self.morph_frame, from_=1, to=15, orient=HORIZONTAL, command=self.update_image)
        self.kernel_size.set(5)
        self.kernel_size.grid(row=0, column=1, sticky="ew", padx=5)
        
        Label(self.morph_frame, text="迭代次数:").grid(row=0, column=2, sticky="e", padx=5)
        self.iterations = Scale(self.morph_frame, from_=1, to=5, orient=HORIZONTAL, command=self.update_image)
        self.iterations.set(2)
        self.iterations.grid(row=0, column=3, sticky="ew", padx=5)
        
        # 计数结果显示
        self.result_label = Label(self.root, text="当前细胞总数: 0")
        self.result_label.pack(pady=10)
        
        # 操作按钮
        self.button_frame = Frame(self.root)
        self.button_frame.pack(fill="x", padx=10, pady=10)
        
        # 添加细胞参数控制
        self.cell_param_frame = LabelFrame(main_frame, text="细胞参数", padx=5, pady=5)
        self.cell_param_frame.pack(fill="x", pady=5)
        
        Label(self.cell_param_frame, text="最小面积:").grid(row=0, column=0)
        self.min_area = Scale(self.cell_param_frame, from_=10, to=200, orient=HORIZONTAL, command=self.update_image)
        self.min_area.set(50)
        self.min_area.grid(row=0, column=1)
        
        Label(self.cell_param_frame, text="最大面积:").grid(row=0, column=2)
        self.max_area = Scale(self.cell_param_frame, from_=100, to=1000, orient=HORIZONTAL, command=self.update_image)
        self.max_area.set(500)
        self.max_area.grid(row=0, column=3)
        
    def set_color_range(self, lower, upper):
        """根据预设颜色设置HSV范围"""
        self.hmin.set(lower[0])
        self.hmax.set(upper[0])
        self.smin.set(lower[1])
        self.smax.set(upper[1])
        self.vmin.set(lower[2])
        self.vmax.set(upper[2])
        self.update_image()

    def save_test_record(self):
        """保存当前测试记录到内存"""
        self.test_count += 1
        params = self.get_params()
        cell_count = self.result_label.cget("text").split(": ")[1]
        
        # 获取当前时间
        from datetime import datetime
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 创建记录字典
        record = {
            "测试序号": self.test_count,
            "测试时间": current_time,
            "色相下限": params['hmin'],
            "色相上限": params['hmax'],
            "饱和度下限": params['smin'],
            "饱和度上限": params['smax'],
            "明度下限": params['vmin'],
            "明度上限": params['vmax'],
            "细胞总数": cell_count
        }
        
        # 添加到记录列表
        self.test_records.append(record)
        messagebox.showinfo("保存成功", f"测试记录#{self.test_count}已保存!")

    def show_test_record(self):
        """显示所有测试记录"""
        if not self.test_records:
            messagebox.showinfo("提示", "暂无测试记录")
            return
            
        record_window = Toplevel(self.root)
        record_window.title(f"测试记录 (共{len(self.test_records)}条)")
        
        # 创建主框架
        main_frame = Frame(record_window)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 创建带滚动条的画布
        canvas = Canvas(main_frame)
        scrollbar = Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 显示所有记录
        for record in self.test_records:
            frame = Frame(scrollable_frame, bd=1, relief="solid", padx=5, pady=5)
            frame.pack(fill="x", padx=5, pady=5)
            
            # 显示完整记录信息
            Label(frame, text=f"记录#{record['测试序号']} - {record['测试时间']}", 
                 font=('Arial', 10, 'bold')).pack(anchor="w")
            Label(frame, text=f"细胞总数: {record['细胞总数']}").pack(anchor="w")
            
            # 创建参数框架
            param_frame = Frame(frame)
            param_frame.pack(anchor="w", padx=10)
            
            # 显示详细参数
            Label(param_frame, text=f"色相下限: {record['色相下限']}").grid(row=0, column=0, sticky="w")
            Label(param_frame, text=f"色相上限: {record['色相上限']}").grid(row=0, column=1, sticky="w")
            Label(param_frame, text=f"饱和度下限: {record['饱和度下限']}").grid(row=1, column=0, sticky="w")
            Label(param_frame, text=f"饱和度上限: {record['饱和度上限']}").grid(row=1, column=1, sticky="w")
            Label(param_frame, text=f"明度下限: {record['明度下限']}").grid(row=2, column=0, sticky="w")
            Label(param_frame, text=f"明度上限: {record['明度上限']}").grid(row=2, column=1, sticky="w")
        
        # 添加保存按钮
        btn_frame = Frame(record_window)
        btn_frame.pack(fill="x", padx=10, pady=5)
        Button(btn_frame, text="保存所有记录到Excel", command=self.save_all_records).pack(side="right")
        
        # 布局
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def save_all_records(self):
        """保存所有测试记录到Excel"""
        if not self.test_records:
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel文件", "*.xlsx")],
            initialfile="all_test_records.xlsx"
        )
        
        if file_path:
            # 转换记录格式为DataFrame
            data = {key: [record[key] for record in self.test_records] 
                   for key in self.test_records[0].keys()}
            df = pd.DataFrame(data)
            df.to_excel(file_path, index=False)
            messagebox.showinfo("保存成功", f"已保存{len(self.test_records)}条记录!")

    def show_help_manual(self):
        """显示帮助手册"""
        help_window = Tk()
        help_window.title("帮助手册")
        
        # 帮助内容
        help_text = """
        色相大小效果：
        - 色相下限：控制检测颜色的最低色相值
        - 色相上限：控制检测颜色的最高色相值
        
        饱和度大小效果：
        - 饱和度下限：控制检测颜色的最低饱和度
        - 饱和度上限：控制检测颜色的最高饱和度
        
        明度大小效果：
        - 明度下限：控制检测颜色的最低明度
        - 明度上限：控制检测颜色的最高明度
        紫色染色建议参数：
        - 色相范围：120-160
        - 饱和度范围：30-255
        - 明度范围：50-255
        - 形态学内核：7x7
        - 迭代次数：3次
        """
        Label(help_window, text=help_text, justify="left").pack()
    
    def save_results(self):
        """保存结果"""
        if hasattr(self, 'img'):
            params = self.get_params()
            result_img, cell_count = process_image(self.img, params)
            
            # 保存JPG
            jpg_path = filedialog.asksaveasfilename(
                defaultextension=".jpg",
                filetypes=[("JPEG文件", "*.jpg")],
                initialfile="cell_result.jpg"
            )
            if jpg_path:
                cv2.imwrite(jpg_path, result_img)
            
            # 保存GIF - 修改后的部分
            gif_path = filedialog.asksaveasfilename(
                defaultextension=".gif",
                filetypes=[("GIF文件", "*.gif")],
                initialfile="cell_process.gif"
            )
            if gif_path:
                # 创建GIF帧 - 使用更合理的动画效果
                frames = []
                for i in range(10):
                    alpha = i/10
                    beta = 1 - alpha
                    frame = cv2.addWeighted(result_img, alpha, cv2.cvtColor(result_img, cv2.COLOR_BGR2GRAY), beta, 0)
                    frames.append(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                
                # 保存GIF - 添加duration参数控制速度
                imageio.mimsave(gif_path, frames, duration=0.2)  # 每帧0.2秒
    
    def update_image(self, _=None):
        """更新图像处理结果"""
        if hasattr(self, 'img'):
            self.process_image()
    
    def select_image(self):
        """选择图片"""
        file_path = filedialog.askopenfilename(
            title="选择细胞图像",
            filetypes=[("图像文件", "*.jpg *.jpeg *.png *.bmp"), ("所有文件", "*.*")]
        )
        if file_path:
            try:
                # 使用numpy读取文件内容，再通过cv2解码
                img_array = np.fromfile(file_path, dtype=np.uint8)
                self.img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                if self.img is not None:
                    self.process_image()
                else:
                    messagebox.showerror("错误", "无法读取图像文件，请检查文件格式和路径")
            except Exception as e:
                messagebox.showerror("错误", f"加载图像失败: {str(e)}")
    
    def process_image(self):
        """处理图像并更新结果"""
        params = self.get_params()
        result_img, cell_count = process_image(self.img, params)
        self.result_label.config(text=f"当前细胞总数: {cell_count}")
        cv2.imshow("处理结果", result_img)
    
    def get_params(self):
        """获取当前参数值"""
        return {
            'hmin': self.hmin.get(),
            'hmax': self.hmax.get(),
            'smin': self.smin.get(),
            'smax': self.smax.get(),
            'vmin': self.vmin.get(),
            'vmax': self.vmax.get(),
            'kernel_size': self.kernel_size.get(),
            'iterations': self.iterations.get()
        }
    
    def show(self):
        """显示窗口"""
        self.root.mainloop()

def main():
    # 创建主窗口
    main_window = MainWindow()
    try:
        main_window.show()
    except KeyboardInterrupt:
        print("程序已退出")
        cv2.destroyAllWindows()
    finally:
        cv2.destroyAllWindows()  # 确保窗口被正确关闭

if __name__ == "__main__":
    main()