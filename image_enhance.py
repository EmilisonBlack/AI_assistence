import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk, ImageDraw
import numpy as np
import cv2
from utils.image_utils import process_image

class ImageEnhanceWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("牛顿环图像增强")
        self.geometry("1200x800")
        self.configure(bg="#f0f0f0")

        # 初始化变量
        self.color_tolerance = 30
        self.original_image = None
        self.processed_image = None
        self.erode_kernel_size = 1
        self.dilate_kernel_size = 1

        # 新增腐蚀和膨胀参数
        self.erode_iterations = 1  # 腐蚀迭代次数
        self.dilate_iterations = 1  # 膨胀迭代次数
        self.morph_kernel_size = 3  # 形态学操作核大小
        
        # 新增图像处理参数
        self.contrast_factor = 1.5
        self.brightness_offset = 0
        self.blur_size = 3
        self.adaptive_thresh = True
        self.brightness_low = 0
        self.brightness_high = 255
        self.invert_colors = False  # MODIFIED: 添加颜色反转标志
        
        # 新增去噪参数
        self.enable_median_blur = False
        self.median_blur_size = 3
        self.enable_connected_components = False
        self.min_component_area = 10

        # 主布局
        self.main_paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.main_paned.pack(fill=tk.BOTH, expand=True)

        # 左侧原图区域
        self.original_image_frame = ttk.Frame(self.main_paned, style="Dialog.TFrame")
        self.main_paned.add(self.original_image_frame, weight=2)

        # 右侧布局
        self.right_paned = ttk.PanedWindow(self.main_paned, orient=tk.VERTICAL)
        self.main_paned.add(self.right_paned, weight=1)

        # 预览图区域
        self.preview_image_frame = ttk.Frame(self.right_paned, style="Dialog.TFrame")
        self.right_paned.add(self.preview_image_frame, weight=3)

        # 参数调整区域
        self.slider_frame = ttk.Frame(self.right_paned, style="Input.TFrame")
        self.right_paned.add(self.slider_frame, weight=1)

        # 初始化界面
        self.init_image_enhance_interface()
        self.bind("<Configure>", self.on_window_resize)
        self.main_paned.bind("<B1-Motion>", self.on_paned_drag)

    def init_image_enhance_interface(self):
        """界面模块:初始化界面元素
        输入参数: 无
        返回值: 无
        功能描述: 初始化所有界面控件和布局
        """
        # 原图显示区域
        self.original_label = ttk.Label(self.original_image_frame)
        self.original_label.pack(fill=tk.BOTH, expand=True)

        # 预览图显示区域
        self.preview_label = ttk.Label(self.preview_image_frame)
        self.preview_label.pack(fill=tk.BOTH, expand=True)

        # 初始化控制滑块
        self.init_slider_controls()
        self.init_styles()

    def init_slider_controls(self):
        """界面模块:初始化滑块控件
        输入参数: 无
        返回值: 无
        功能描述: 初始化所有图像处理参数的控制滑块
        """
        # 创建主容器
        main_container = ttk.Frame(self.slider_frame)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # 按钮区域
        btn_frame = ttk.Frame(main_container)
        btn_frame.pack(fill=tk.X, pady=(0,10))
        
        # 功能按钮
        ttk.Button(btn_frame, text="导入图片", command=self.import_image).pack(side=tk.LEFT, expand=True)
        ttk.Button(btn_frame, text="下载图片", command=self.download_image).pack(side=tk.LEFT, expand=True)
        self.edge_detection_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            btn_frame, text="边缘检测", variable=self.edge_detection_var,
            command=self.update_preview
        ).pack(side=tk.LEFT, expand=True)

        # MODIFIED: 添加颜色反转按钮
        self.invert_var = tk.BooleanVar(value=self.invert_colors)
        ttk.Checkbutton(
            btn_frame, text="反转颜色", variable=self.invert_var,
            command=lambda: self.update_param('invert_colors', self.invert_var.get())
        ).pack(side=tk.LEFT, expand=True)

        # 分隔线
        ttk.Separator(main_container, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=5)

        # 滑块控制区域
        control_frame = ttk.Frame(main_container)
        control_frame.pack(fill=tk.BOTH, expand=True)

        # 分隔线
        ttk.Separator(main_container, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=5)

        # 预留扩展区域
        expand_frame = ttk.Frame(main_container, height=50)
        expand_frame.pack(fill=tk.X, pady=(5,0))

        # 第一列控制项
        col1 = ttk.Frame(control_frame)
        col1.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 对比度控制
        ttk.Label(col1, text="对比度").pack(anchor=tk.W)
        self.contrast_slider = ttk.Scale(
            col1, from_=0.1, to=3.0, value=self.contrast_factor,
            command=lambda v: self.update_param('contrast_factor', int(float(v))))
        self.contrast_slider.pack(fill=tk.X)

        # 亮度控制
        ttk.Label(col1, text="亮度偏移").pack(anchor=tk.W, pady=(10,0))
        self.brightness_slider = ttk.Scale(
            col1, from_=-50, to=50, value=self.brightness_offset,
            command=lambda v: self.update_param('brightness_offset', int(float(v))))
        self.brightness_slider.pack(fill=tk.X)

        # 明度下限控制
        ttk.Label(col1, text="明度下限").pack(anchor=tk.W, pady=(10,0))
        self.brightness_low_slider = ttk.Scale(
            col1, from_=0, to=255, value=self.brightness_low,
            command=lambda v: self.update_param('brightness_low', int(float(v))))
        self.brightness_low_slider.pack(fill=tk.X)

        # 明度上限控制
        ttk.Label(col1, text="明度上限").pack(anchor=tk.W, pady=(10,0))
        self.brightness_high_slider = ttk.Scale(
            col1, from_=0, to=255, value=self.brightness_high,
            command=lambda v: self.update_param('brightness_high', int(float(v))))
        self.brightness_high_slider.pack(fill=tk.X)

        # 第二列控制项
        col2 = ttk.Frame(control_frame)
        col2.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)

        # 自适应阈值控制
        self.thresh_var = tk.BooleanVar(value=self.adaptive_thresh)
        ttk.Checkbutton(
            col2, text="自适应阈值", variable=self.thresh_var,
            command=lambda: self.update_param('adaptive_thresh', self.thresh_var.get())
        ).pack(anchor=tk.W)

        # 第三列控制项 - 形态学操作和去噪
        col3 = ttk.Frame(control_frame)
        col3.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 中值滤波控制
        self.median_var = tk.BooleanVar(value=self.enable_median_blur)
        ttk.Checkbutton(
            col3, text="中值滤波", variable=self.median_var,
            command=lambda: self.update_param('enable_median_blur', self.median_var.get())
        ).pack(anchor=tk.W)
        
        ttk.Label(col3, text="中值滤波核大小(奇数)").pack(anchor=tk.W, pady=(5,0))
        self.median_slider = ttk.Scale(
            col3, from_=1, to=7, value=self.median_blur_size,
            command=lambda v: self.update_param('median_blur_size', int(float(v)) | 1))  # 确保为奇数
        self.median_slider.pack(fill=tk.X)
        
        # 连通域去噪控制
        self.cc_var = tk.BooleanVar(value=self.enable_connected_components)
        ttk.Checkbutton(
            col3, text="连通域去噪", variable=self.cc_var,
            command=lambda: self.update_param('enable_connected_components', self.cc_var.get())
        ).pack(anchor=tk.W, pady=(10,0))
        
        ttk.Label(col3, text="最小连通域面积").pack(anchor=tk.W, pady=(5,0))
        self.area_slider = ttk.Scale(
            col3, from_=1, to=50, value=self.min_component_area,
            command=lambda v: self.update_param('min_component_area', int(float(v))))
        self.area_slider.pack(fill=tk.X)
        
        # 腐蚀迭代次数控制
        ttk.Label(col3, text="腐蚀强度").pack(anchor=tk.W)
        self.erode_slider = ttk.Scale(
            col3, from_=0, to=5, value=self.erode_iterations,
            command=lambda v: self.update_param('erode_iterations', int(float(v))))
        self.erode_slider.pack(fill=tk.X)

        # 膨胀迭代次数控制
        ttk.Label(col3, text="膨胀强度").pack(anchor=tk.W, pady=(10,0))
        self.dilate_slider = ttk.Scale(
            col3, from_=0, to=5, value=self.dilate_iterations,
            command=lambda v: self.update_param('dilate_iterations', int(float(v))))
        self.dilate_slider.pack(fill=tk.X)
        
        # 核大小控制
        ttk.Label(col3, text="核大小(奇数)").pack(anchor=tk.W, pady=(10,0))
        self.kernel_slider = ttk.Scale(
            col3, from_=1, to=7, value=self.morph_kernel_size,
            command=lambda v: self.update_param('morph_kernel_size', int(float(v)) | 1))  # 确保为奇数
        self.kernel_slider.pack(fill=tk.X)

    def update_preview(self, value=None):
        if not self.original_image:
            return

        # 转换为灰度图
        gray = np.array(self.original_image.convert('L'))
        
        # 对比度增强
        enhanced = self.enhance_contrast(gray)
        # 明度拉伸
        enhanced = self.brightness_stretch(enhanced)
        
        # 二值化处理 (新增)
        _, binary = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        
        # 形态学操作 (新增)
        kernel = np.ones((self.morph_kernel_size, self.morph_kernel_size), np.uint8)
        if self.erode_iterations > 0:
            binary = cv2.erode(binary, kernel, iterations=self.erode_iterations)
        if self.dilate_iterations > 0:
            binary = cv2.dilate(binary, kernel, iterations=self.dilate_iterations)
        
        # 边缘检测
        if self.edge_detection_var.get():
            edges = self.detect_edges(binary)  # 修改为对二值化图像进行边缘检测
            # 合并边缘检测结果
            result = np.where(edges > 0, 255, binary)
        else:
            result = binary
        
        # 创建预览图
        preview_array = np.zeros((*result.shape, 3), dtype=np.uint8)
        preview_array[result == 0] = [0, 0, 0]      # 黑色表示边缘/暗区
        preview_array[result == 255] = [255, 255, 255]  # 白色表示背景/亮区
        
        if self.invert_colors:
            preview_array = 255 - preview_array
            
        self.processed_image = Image.fromarray(preview_array)
        self.display_preview_image(self.processed_image)


    def init_styles(self):
        """界面模块:初始化样式
        输入参数: 无
        返回值: 无
        功能描述: 设置界面控件的视觉样式
        """
        style = ttk.Style()
        style.configure("Dialog.TFrame", background="#ffffff", borderwidth=2, relief="ridge")
        style.configure("Input.TFrame", background="#f9f9f9", borderwidth=2, relief="ridge")
        style.configure("TButton", font=("Arial", 10), padding=5)
        style.configure("TLabel", background="#f9f9f9", font=("Arial", 10))

    def import_image(self):
        """文件模块:导入图片
        输入参数: 无
        返回值: 无
        功能描述: 从文件系统选择并加载图片
        """
        file_path = filedialog.askopenfilename()
        if file_path:
            self.original_image = Image.open(file_path)
            max_size = 2000
            if max(self.original_image.width, self.original_image.height) > max_size:
                self.original_image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            self.display_original_image()
            self.update_preview()

    def display_original_image(self):
        """显示模块:显示原图
        输入参数: 无
        返回值: 无
        功能描述: 在左侧面板显示原始图像
        """
        if self.original_image:
            frame_width = self.original_image_frame.winfo_width()
            frame_height = self.original_image_frame.winfo_height()
            resized_image = self.resize_image(self.original_image, (frame_width, frame_height))
            self.original_tk_image = ImageTk.PhotoImage(resized_image)
            self.original_label.config(image=self.original_tk_image)

    def update_param(self, param_name, value):
        """参数模块:更新参数
        输入参数: 
            param_name - 参数名称
            value - 参数值
        返回值: 无
        功能描述: 更新处理参数并刷新预览
        """
        setattr(self, param_name, value)
        self.update_preview()

    def enhance_contrast(self, image_array):
        """图像处理模块:增强对比度
        输入参数: image_array - 图像数组
        返回值: 增强后的图像数组
        功能描述: 应用对比度和亮度调整
        """
        img = image_array.astype(float)
        img = (img - 128) * self.contrast_factor + 128 + self.brightness_offset
        return np.clip(img, 0, 255).astype(np.uint8)

    def brightness_stretch(self, image_array):
        """图像处理模块:明度拉伸
        输入参数: image_array - 图像数组
        返回值: 处理后的图像数组
        功能描述: 根据设定的上下限拉伸明度
        """
        if self.brightness_high <= self.brightness_low:
            return image_array
            
        img = image_array.astype(float)
        # 低于下限设为0
        img[img < self.brightness_low] = 0
        # 高于上限设为255
        img[img > self.brightness_high] = 255
        # 中间值线性拉伸到[0,100]
        mask = (img >= self.brightness_low) & (img <= self.brightness_high)
        img[mask] = ((img[mask] - self.brightness_low) / 
                    (self.brightness_high - self.brightness_low)) * 100
        return img.astype(np.uint8)

    def detect_edges(self, image_array):
        """图像处理模块:边缘检测
        输入参数: image_array - 图像数组
        返回值: 边缘检测后的图像数组
        功能描述: 使用Canny算法进行边缘检测
        """
        # 高斯模糊降噪
        blurred = cv2.GaussianBlur(image_array, (5, 5), 0)
        # Canny边缘检测
        edges = cv2.Canny(blurred, 50, 150)
        return edges

    def update_preview(self, value=None):
        """图像处理模块:更新预览
        输入参数: value - 可选参数
        返回值: 无
        功能描述: 生成并显示处理后的预览图像
        """
        if not self.original_image:
            return

        # 转换为灰度图
        gray = np.array(self.original_image.convert('L'))
        
        # 对比度增强
        enhanced = self.enhance_contrast(gray)
        # 明度拉伸
        enhanced = self.brightness_stretch(enhanced)
        
        # 边缘检测
        if self.edge_detection_var.get():
            edges = self.detect_edges(enhanced)
            # 合并边缘检测结果
            result = np.where(edges > 0, 255, enhanced)
        else:
            result = enhanced
            
        # 二值化处理
        _, binary = cv2.threshold(result, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        
        # 形态学操作 (腐蚀膨胀)
        kernel = np.ones((self.morph_kernel_size, self.morph_kernel_size), np.uint8)
        if self.erode_iterations > 0:
            binary = cv2.erode(binary, kernel, iterations=self.erode_iterations)
        if self.dilate_iterations > 0:
            binary = cv2.dilate(binary, kernel, iterations=self.dilate_iterations)
        
        # 创建预览图
        preview_array = np.zeros((*binary.shape, 3), dtype=np.uint8)
        preview_array[binary == 0] = [0, 0, 0]      # 黑色表示边缘/暗区
        preview_array[binary == 255] = [255, 255, 255]  # 白色表示背景/亮区
        
        # 颜色反转处理
        if self.invert_colors:
            preview_array = 255 - preview_array
            
        # 中值滤波去噪
        if self.enable_median_blur:
            preview_array = cv2.medianBlur(preview_array, self.median_blur_size)
            
        # 连通域分析去噪
        if self.enable_connected_components:
            gray = cv2.cvtColor(preview_array, cv2.COLOR_BGR2GRAY)
            _, binary = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)
            num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(binary, 8, cv2.CV_32S)
            
            clean_img = np.zeros_like(binary)
            for i in range(1, num_labels):
                if stats[i, cv2.CC_STAT_AREA] >= self.min_component_area:
                    clean_img[labels == i] = 255
                    
            preview_array = cv2.cvtColor(clean_img, cv2.COLOR_GRAY2BGR)
            
        self.processed_image = Image.fromarray(preview_array)
        self.display_preview_image(self.processed_image)

    def display_preview_image(self, image):
        """显示模块:显示预览图
        输入参数: image - PIL图像对象
        返回值: 无
        功能描述: 在右侧面板显示处理后的图像
        """
        if self.processed_image:
            frame_width = self.preview_image_frame.winfo_width()
            frame_height = self.preview_image_frame.winfo_height()
            resized_image = self.resize_image(image, (frame_width, frame_height))
            self.preview_tk_image = ImageTk.PhotoImage(resized_image)
            self.preview_label.config(image=self.preview_tk_image)

    def resize_image(self, image, size):
        """工具模块:调整图像大小
        输入参数: 
            image - PIL图像对象
            size - 目标尺寸
        返回值: 调整后的图像
        功能描述: 保持宽高比调整图像大小
        """
        if image.width > 0 and image.height > 0:
            ratio = min(size[0] / image.width, size[1] / image.height)
            new_size = (int(image.width * ratio), int(image.height * ratio))
            return image.resize(new_size, Image.Resampling.LANCZOS)
        return image

    def on_window_resize(self, event):
        """事件模块:窗口大小变化
        输入参数: event - 事件对象
        返回值: 无
        功能描述: 响应窗口大小变化事件
        """
        if self.original_image:
            self.display_original_image()
        if self.processed_image:
            self.display_preview_image(self.processed_image)

    def on_paned_drag(self, event):
        """事件模块:分割线拖动
        输入参数: event - 事件对象
        返回值: 无
        功能描述: 响应分割线拖动事件
        """
        if self.original_image:
            self.display_original_image()
        if self.processed_image:
            self.display_preview_image(self.processed_image)

    def download_image(self):
        """文件模块:下载图片
        输入参数: 无
        返回值: 无
        功能描述: 保存处理后的图像到文件
        """
        if self.processed_image:
            file_path = filedialog.asksaveasfilename(defaultextension=".png")
            if file_path:
                self.processed_image.save(file_path, quality=95)
                print(f"图片已保存到: {file_path}")

    def display_preview_image(self, image):
        """显示模块:显示预览图
        输入参数: image - PIL图像对象
        返回值: 无
        功能描述: 在右侧面板显示处理后的图像
        """
        if self.processed_image:
            frame_width = self.preview_image_frame.winfo_width()
            frame_height = self.preview_image_frame.winfo_height()
            resized_image = self.resize_image(image, (frame_width, frame_height))
            self.preview_tk_image = ImageTk.PhotoImage(resized_image)
            self.preview_label.config(image=self.preview_tk_image)

    def resize_image(self, image, size):
        """工具模块:调整图像大小
        输入参数: 
            image - PIL图像对象
            size - 目标尺寸
        返回值: 调整后的图像
        功能描述: 保持宽高比调整图像大小
        """
        if image.width > 0 and image.height > 0:
            ratio = min(size[0] / image.width, size[1] / image.height)
            new_size = (int(image.width * ratio), int(image.height * ratio))
            return image.resize(new_size, Image.Resampling.LANCZOS)
        return image

    def on_window_resize(self, event):
        """事件模块:窗口大小变化
        输入参数: event - 事件对象
        返回值: 无
        功能描述: 响应窗口大小变化事件
        """
        if self.original_image:
            self.display_original_image()
        if self.processed_image:
            self.display_preview_image(self.processed_image)

    def on_paned_drag(self, event):
        """事件模块:分割线拖动
        输入参数: event - 事件对象
        返回值: 无
        功能描述: 响应分割线拖动事件
        """
        if self.original_image:
            self.display_original_image()
        if self.processed_image:
            self.display_preview_image(self.processed_image)

    def download_image(self):
        """文件模块:下载图片
        输入参数: 无
        返回值: 无
        功能描述: 保存处理后的图像到文件
        """
        if self.processed_image:
            file_path = filedialog.asksaveasfilename(defaultextension=".png")
            if file_path:
                self.processed_image.save(file_path, quality=95)
                print(f"图片已保存到: {file_path}")
