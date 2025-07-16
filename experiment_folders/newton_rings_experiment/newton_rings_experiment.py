import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import re

class NewtonRingsExperimentWindow(tk.Toplevel):
    def open_image_enhance(self):
        """函数模块名称: 打开图片增强窗口
        输入参数: 无
        返回值: 无
        功能描述: 打开图片增强工具窗口
        """
        from image_enhance import ImageEnhanceWindow
        ImageEnhanceWindow(self)
    def __init__(self, parent):
        super().__init__(parent)
        self.title("牛顿环曲率半径计算")
        self.geometry("1000x700")
        self.configure(bg="#f0f0f0")
        
        self.pixel_to_real_ratio = None
        self.circle_data = []
        self.delta_n = tk.IntVar(value=5)
        self.wavelength = tk.DoubleVar(value=589)
        self.auto_fill_var = tk.BooleanVar(value=True)  # 新增自动推算开关
        
        self.create_ui()

    def create_ui(self):
        main_frame = ttk.Frame(self)
        main_frame.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)
        
        # 左侧面板
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 右侧面板
        right_frame = ttk.Frame(main_frame, width=300)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10)
        
        # 按钮区域
        button_frame = ttk.Frame(left_frame)
        button_frame.pack(pady=10)
        
        # MODIFIED: 调整按钮顺序，图片增强按钮放在最左侧
        ttk.Button(
            button_frame,
            text="图片增强",
            command=self.open_image_enhance
        ).pack(side=tk.LEFT, padx=(0, 10))  # MODIFIED: 移到最左侧并添加右边距
        
        ttk.Button(
            button_frame,
            text="生成圆数据文件",
            command=self.generate_circle_file
        ).pack(side=tk.LEFT, padx=(0, 10))  # MODIFIED: 调整位置
        
        ttk.Button(
            button_frame, 
            text="选择圆数据文件", 
            command=self.select_and_load_file
        ).pack(side=tk.LEFT)  # MODIFIED: 调整位置
        
        # 以下原有代码保持不变
        self.data_frame = ttk.Frame(left_frame)
        self.data_frame.pack(fill=tk.BOTH, expand=True)
        
        self.status_label = ttk.Label(left_frame, text="请选择包含圆数据的txt文件", foreground="blue")
        self.status_label.pack(pady=10)
        
        # 右侧内容
        params_frame = ttk.LabelFrame(right_frame, text="计算参数", padding=10)
        params_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(params_frame, text="环数差Δn:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(params_frame, textvariable=self.delta_n, width=8).grid(row=0, column=1, sticky=tk.E)
        
        ttk.Label(params_frame, text="波长λ(nm):").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(params_frame, textvariable=self.wavelength, width=8).grid(row=1, column=1, sticky=tk.E)
        
        # 新增自动推算开关
        ttk.Checkbutton(
            params_frame, 
            text="自动推算直径", 
            variable=self.auto_fill_var
        ).grid(row=2, column=0, columnspan=2, pady=5, sticky=tk.W)
        
        ttk.Button(
            params_frame, 
            text="计算比例并推算", 
            command=self.calculate_and_fill
        ).grid(row=3, column=0, columnspan=2, pady=5)
        
        ttk.Button(
            params_frame, 
            text="计算曲率半径", 
            command=self.calculate_radius
        ).grid(row=4, column=0, columnspan=2, pady=10)
        
        # 比例显示
        self.ratio_label = ttk.Label(params_frame, text="像素比例: 未计算")
        self.ratio_label.grid(row=5, column=0, columnspan=2)
        
        # 结果区域
        result_frame = ttk.LabelFrame(right_frame, text="计算结果", padding=10)
        result_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.result_text = tk.Text(result_frame, height=15, wrap=tk.WORD)
        self.result_text.pack(fill=tk.BOTH, expand=True)
        
        ttk.Button(
            result_frame, 
            text="复制结果", 
            command=self.copy_results
        ).pack(pady=5)


    def generate_circle_file(self):
        """函数模块名称: 生成圆数据文件
        输入参数: 无
        返回值: 无
        功能描述: 运行drawing_circle.py脚本来生成圆数据文件
        """
        try:
            script_path = os.path.join("experiment_folders", "newton_rings_experiment", "drawing_circle.py")
            if os.path.exists(script_path):
                os.system(f"python {script_path}")
                self.status_label.config(text="已运行圆数据生成脚本", foreground="green")
            else:
                messagebox.showerror("错误", f"未找到脚本文件: {script_path}")
                self.status_label.config(text="脚本文件不存在", foreground="red")
        except Exception as e:
            messagebox.showerror("错误", f"运行脚本时出错: {e}")
            self.status_label.config(text="脚本运行失败", foreground="red")

    def select_and_load_file(self):
        """文件选择函数保持不变"""
        file_path = filedialog.askopenfilename(
            title="选择圆数据文件",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                self.load_circle_data(file_path)
                self.show_data_table()
                self.status_label.config(text=f"已加载文件: {os.path.basename(file_path)}", foreground="green")
            except Exception as e:
                messagebox.showerror("错误", f"加载文件时出错: {e}")
                self.status_label.config(text="文件加载失败", foreground="red")

    def load_circle_data(self, file_path):
        """加载圆数据函数保持不变"""
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        pattern = r"圆(\d+):\s*圆心坐标:\s*\(([\d.]+),\s*([\d.]+)\)\s*半径:\s*([\d.]+)px"
        matches = re.findall(pattern, content)
        
        self.circle_data = []
        for match in matches:
            self.circle_data.append({
                'number': int(match[0]),
                'center': (float(match[1]), float(match[2])),
                'radius': float(match[3]),
                'diameter': float(match[3]) * 2
            })
        
        self.circle_data.sort(key=lambda x: x['radius'])

    def show_data_table(self):
        for widget in self.data_frame.winfo_children():
            widget.destroy()
        
        if not self.circle_data:
            ttk.Label(self.data_frame, text="没有找到圆数据").pack()
            return
        
        headers = ["环编号", "半径(px)", "直径(px)", "实际直径(mm)"]
        for col, header in enumerate(headers):
            ttk.Label(self.data_frame, text=header, font=("Arial", 10, "bold")).grid(row=0, column=col, padx=5, pady=5)
        
        self.entry_widgets = []
        for row, circle in enumerate(self.circle_data, start=1):
            ttk.Label(self.data_frame, text=f"环{row}").grid(row=row, column=0, padx=5, pady=5)
            ttk.Label(self.data_frame, text=f"{circle['radius']:.2f}").grid(row=row, column=1, padx=5, pady=5)
            ttk.Label(self.data_frame, text=f"{circle['diameter']:.2f}").grid(row=row, column=2, padx=5, pady=5)
            
            entry_var = tk.StringVar()
            entry = ttk.Entry(self.data_frame, textvariable=entry_var)
            entry.grid(row=row, column=3, padx=5, pady=5)
            self.entry_widgets.append((entry, entry_var))  # 存储Entry和StringVar
            
            # 如果已有计算值，自动填充
            if 'real_diameter' in circle:
                entry_var.set(f"{circle['real_diameter']:.4f}")
        
        ttk.Button(
            self.data_frame, 
            text="计算比例", 
            command=self.calculate_ratio
        ).grid(row=len(self.circle_data)+1, column=0, columnspan=4, pady=20)

    def calculate_and_fill(self):
        """新增方法：计算比例并自动推算所有直径"""
        self.calculate_ratio()
        if self.pixel_to_real_ratio and self.auto_fill_var.get():
            self.auto_fill_diameters()

    def auto_fill_diameters(self):
        """新增方法：自动推算所有直径并填充"""
        if not self.pixel_to_real_ratio:
            return
            
        try:
            for i, (entry, entry_var) in enumerate(self.entry_widgets):
                pixel_diameter = self.circle_data[i]['diameter']
                real_diameter = pixel_diameter / self.pixel_to_real_ratio
                entry_var.set(f"{real_diameter:.4f}")
                # 更新数据到circle_data
                self.circle_data[i]['real_diameter'] = real_diameter
            
            messagebox.showinfo("完成", "已自动推算并填充所有直径数据")
        except Exception as e:
            messagebox.showerror("错误", f"自动推算直径时出错: {e}")

    def calculate_ratio(self):
        """修改后的计算比例方法，同时更新数据"""
        try:
            ratios = []
            valid_inputs = 0
            
            for i, (entry, entry_var) in enumerate(self.entry_widgets):
                value = entry_var.get()
                if value:
                    try:
                        real_diameter = float(value)
                        pixel_diameter = self.circle_data[i]['diameter']
                        ratios.append(pixel_diameter / real_diameter)
                        valid_inputs += 1
                        # 更新数据到circle_data
                        self.circle_data[i]['real_diameter'] = real_diameter
                    except ValueError:
                        continue
            
            if valid_inputs == 0:
                raise ValueError("至少需要输入一个环的实际直径")
            
            self.pixel_to_real_ratio = sum(ratios) / len(ratios)
            self.ratio_label.config(text=f"像素比例: {self.pixel_to_real_ratio:.4f} px/mm")
            
        except Exception as e:
            messagebox.showerror("错误", f"计算比例时出错: {e}")

    def calculate_radius(self):
        """修改后的计算曲率半径方法，使用所有有效数据"""
        try:
            delta_n = self.delta_n.get()
            wavelength = self.wavelength.get()
            
            if delta_n <= 0:
                raise ValueError("环数差必须为正整数")
            if wavelength <= 0:
                raise ValueError("波长必须为正数")
            if not self.pixel_to_real_ratio:
                raise ValueError("请先计算像素与实际尺寸比例")
            
            # 获取所有有效直径数据（包括自动推算的）
            real_diameters = []
            for i, (entry, entry_var) in enumerate(self.entry_widgets):
                value = entry_var.get()
                if value:
                    try:
                        real_diameter = float(value)
                        real_diameters.append((i+1, real_diameter))
                    except ValueError:
                        continue
            
            available_pairs = len(real_diameters) - delta_n
            if available_pairs <= 0:
                raise ValueError(f"需要至少 {delta_n+1} 个有效输入，当前只有 {len(real_diameters)} 个")
            
            wavelength_m = wavelength * 1e-9  # nm -> m
            
            results = []
            for i in range(available_pairs):
                m_ring, D_m = real_diameters[i + delta_n]
                n_ring, D_n = real_diameters[i]
                
                D_m_m = D_m * 1e-3  # mm -> m
                D_n_m = D_n * 1e-3  # mm -> m
                
                R = (D_m_m**2 - D_n_m**2) / (4 * delta_n * wavelength_m)
                results.append({
                    'pair': f"环{n_ring}-环{m_ring}",
                    'R': R
                })
            
            avg_R = sum(r['R'] for r in results) / len(results)
            std_dev = (sum((r['R'] - avg_R)**2 for r in results) / (len(results)-1))**0.5
            
            output = [f"{r['pair']}  R值: {r['R']:.5g}m" for r in results]
            output.append("\n统计结果:")
            output.append(f"平均值: R_avg = {avg_R:.5g}m")
            output.append(f"标准差: σ = {std_dev:.5g}m")
            output.append(f"使用数据对数: {len(results)}")
            output.append(f"总有效数据: {len(real_diameters)}个")
            
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, "\n".join(output))
            
        except Exception as e:
            messagebox.showerror("计算错误", f"计算曲率半径时出错: {e}")

    def copy_results(self):
        result = self.result_text.get(1.0, tk.END)
        if result.strip():
            self.clipboard_clear()
            self.clipboard_append(result)
            messagebox.showinfo("复制成功", "结果已复制到剪贴板")