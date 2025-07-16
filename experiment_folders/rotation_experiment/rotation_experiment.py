import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from rotation_experiment_method2 import RotationExperimentMethod2

GRAVITY = 980  # 重力加速度 (cm/s²)

class DataInputTable(ttk.Frame):
    """通用数据输入表格组件（2行7列，含平均值）"""
    def __init__(self, parent, rows, cols, title=""):
        super().__init__(parent, borderwidth=1, relief="solid", padding=5)
        self.entries = {}
        
        # 表格标题
        if title:
            ttk.Label(self, text=title, font=('Arial', 10, 'bold')).grid(row=0, column=0, columnspan=len(cols), pady=5)
        
        # 列标题
        for j, col in enumerate(cols):
            ttk.Label(self, text=col, width=12).grid(row=1, column=j, padx=2, pady=2)
        
        # 行标签和输入框
        for i, row in enumerate(rows, 2):
            ttk.Label(self, text=row).grid(row=i, column=0, padx=2, pady=2, sticky="w")
            for j, _ in enumerate(cols[1:], 1):  # 跳过第一列（行标签）
                entry = ttk.Entry(self, width=10)
                entry.grid(row=i, column=j, padx=2, pady=2)
                entry.bind("<FocusOut>", lambda event, r=row, c=j: self.update_average(r))
                self.entries[(row, j)] = entry
            
            # 平均值列
            avg_entry = ttk.Entry(self, width=10, state="readonly")
            avg_entry.grid(row=i, column=len(cols)-1, padx=2, pady=2)
            self.entries[(row, "avg")] = avg_entry
    
    def get_data(self):
        """获取表格数据并转换为数值"""
        data = {}
        for (row, col), entry in self.entries.items():
            if col != "avg":  # 跳过平均值列
                try:
                    data[(row, col)] = float(entry.get())
                except ValueError:
                    data[(row, col)] = 0.0
        return data
    
    def update_average(self, row):
        """更新指定行的平均值"""
        # 获取该行所有数据列的值
        values = []
        for col in range(1, len(self.entries)//2):  # 排除行标签和平均值列
            try:
                values.append(float(self.entries[(row, col)].get()))
            except ValueError:
                pass
        
        # 计算并更新平均值
        if len(values) > 0:
            avg = sum(values) / len(values)
            avg_entry = self.entries[(row, "avg")]
            avg_entry.configure(state="normal")
            avg_entry.delete(0, tk.END)
            avg_entry.insert(0, f"{avg:.2f}")
            avg_entry.configure(state="readonly")

class RotationExperimentApp:
    def __init__(self, root):
        self.root = root
        self.root.title("转动惯量实验数据处理系统")
        self.root.geometry("1200x800")
        
        # 数据存储
        self.current_method = "method1"
        self.params = {
            "m1": 0.0,       # 砝码质量 (g)
            "r": 0.0,        # 绕线轮半径 (cm)
            "m_ring": 0.0,   # 铝环质量 (g)
            "r_inner": 0.0,  # 铝环内径 (cm)
            "r_outer": 0.0   # 铝环外径 (cm)
        }
        
        # 创建界面
        self.create_widgets()
        self.show_method1_interface()
        
        # 延迟初始化实验二功能
        self.method2 = None

    def create_widgets(self):
        """创建界面组件"""
        # 配置主窗口的网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(2, weight=1)
        self.root.rowconfigure(3, weight=1)
        
        # 顶部控制栏
        control_frame = ttk.Frame(self.root)
        control_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        
        ttk.Button(control_frame, text="实验一：直接计算法", command=self.show_method1_interface).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(control_frame, text="实验二：作图法", 
                 command=lambda: self.init_method2().show_method2_interface()).grid(row=0, column=1, padx=5, pady=5)
        
        # 参数输入区
        param_frame = ttk.LabelFrame(self.root, text="基础实验参数", padding=10)
        param_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        
        # 配置参数区的网格
        for i in range(7):
            param_frame.columnconfigure(i, weight=1)
        
        # 砝码质量
        ttk.Label(param_frame, text="砝码质量 m1 (g):").grid(row=0, column=0, sticky="w")
        self.m1_entry = ttk.Entry(param_frame, width=10)
        self.m1_entry.grid(row=0, column=1, padx=5, pady=2)
        
        # 绕线轮半径
        ttk.Label(param_frame, text="绕线轮半径 r (cm):").grid(row=0, column=2, sticky="w")
        self.r_entry = ttk.Entry(param_frame, width=10)
        self.r_entry.grid(row=0, column=3, padx=5, pady=2)
        
        # 铝环质量
        ttk.Label(param_frame, text="铝环质量 m (g):").grid(row=0, column=4, sticky="w")
        self.m_entry = ttk.Entry(param_frame, width=10)
        self.m_entry.grid(row=0, column=5, padx=5, pady=2)
        
        # 计算按钮
        self.calculate_btn = ttk.Button(param_frame, text="执行计算", command=self.perform_calculation)
        self.calculate_btn.grid(row=0, column=6, padx=10, pady=2)
        
        # 主内容区
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(0, weight=1)
        
        # 结果显示区
        self.result_area = ttk.LabelFrame(self.root, text="计算结果", padding=10)
        self.result_area.grid(row=3, column=0, sticky="nsew", padx=10, pady=5)
        self.result_area.columnconfigure(0, weight=1)
        self.result_area.rowconfigure(0, weight=1)

    def show_method1_interface(self):
        """实验一界面：直接计算法（2行7列表格）"""
        self.current_method = "method1"
        self.clear_interface()
        
        # 创建主表格
        self.method1_table = DataInputTable(
            self.main_frame,
            rows=["β (有铝环)", "β' (有铝环)", "β0 (无铝环)", "β0' (无铝环)"],
            cols=["测量次数", "第1次", "第2次", "第3次", "第4次", "第5次", "平均值"],
            title="实验一：角加速度测量数据"
        )
        self.method1_table.grid(row=0, column=0, sticky="nsew", pady=5)
        
        # 创建参数输入子框架
        params_subframe = ttk.Frame(self.main_frame)
        params_subframe.grid(row=1, column=0, sticky="ew", pady=5)
        
        # 内径/外径输入
        ttk.Label(params_subframe, text="铝环内径 r_inner (cm):").grid(row=0, column=0, sticky="w", pady=2)
        self.r_inner_entry = ttk.Entry(params_subframe, width=10)
        self.r_inner_entry.grid(row=0, column=1, sticky="w", padx=5, pady=2)
        
        ttk.Label(params_subframe, text="铝环外径 r_outer (cm):").grid(row=0, column=2, sticky="w", pady=2, padx=10)
        self.r_outer_entry = ttk.Entry(params_subframe, width=10)
        self.r_outer_entry.grid(row=0, column=3, sticky="w", padx=5, pady=2)
        
        # 配置行权重
        self.main_frame.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=1)
        
        # 配置参数子框架的列权重
        for i in range(4):
            params_subframe.columnconfigure(i, weight=1)
        
        self.update_status("请输入实验一的角加速度数据和几何参数")

    def clear_interface(self):
        """清除当前界面内容"""
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        for widget in self.result_area.winfo_children():
            widget.destroy()
        self.result_area.configure(text="计算结果")

    def update_status(self, message):
        """更新状态栏信息"""
        self.root.title(f"转动惯量实验数据处理系统 - {message}")

    def perform_calculation(self):
        """执行计算逻辑"""
        try:
            # 获取基础参数
            self.params["m1"] = float(self.m1_entry.get())
            self.params["r"] = float(self.r_entry.get())
            self.params["m_ring"] = float(self.m_entry.get())
            
            if self.current_method == "method1":
                # 确保实验一的参数获取
                self.params["r_inner"] = float(self.r_inner_entry.get())
                self.params["r_outer"] = float(self.r_outer_entry.get())
                self.calculate_method1()
            else:
                if self.method2 is None:
                    self.init_method2()
                self.method2.calculate_method2()
                
        except ValueError as e:
            messagebox.showerror("输入错误", f"请检查参数输入：{str(e)}")
            return

    def calculate_method1(self):
        """实验一计算逻辑"""
        # 获取表格数据
        data = self.method1_table.get_data()
        
        # 提取β和β'值（有铝环）
        beta_values = [data[("β (有铝环)", i)] for i in range(1, 7)]  # 第1-6列是测量值
        beta_prime_values = [data[("β' (有铝环)", i)] for i in range(1, 7)]
        # 提取β0和β0'值（无铝环）
        beta0_values = [data[("β0 (无铝环)", i)] for i in range(1, 7)]
        beta0_prime_values = [data[("β0' (无铝环)", i)] for i in range(1, 7)]
        
        # 计算平均值
        beta_avg = np.mean(beta_values)
        beta_prime_avg = np.mean(beta_prime_values)
        beta0_avg = np.mean(beta0_values)
        beta0_prime_avg = np.mean(beta0_prime_values)
        
        # 计算转动惯量
        numerator = self.params["m1"] * GRAVITY * self.params["r"]
        denominator_with = beta_avg - beta_prime_avg
        denominator_without = beta0_avg - beta0_prime_avg
        
        # 总转动惯量（有铝环时）
        J = numerator / denominator_with
        # 系统本底转动惯量（无铝环时）
        J0 = numerator / denominator_without
        # 铝环转动惯量
        J_ring = J - J0
        
        # 计算理论值
        J_theory = 0.5 * self.params["m_ring"] * (
            self.params["r_inner"]**2 + self.params["r_outer"]**2
        )
        
        # 计算误差
        error = abs(J_ring - J_theory) / J_theory * 100
        
        # 显示结果
        self.display_result(f"""
实验一计算结果：
-----------------------------------
β (有铝环) 平均值 = {beta_avg:.2f} rad/s²
β' (有铝环) 平均值 = {beta_prime_avg:.2f} rad/s²
β0 (无铝环) 平均值 = {beta0_avg:.2f} rad/s²
β0' (无铝环) 平均值 = {beta0_prime_avg:.2f} rad/s²
总转动惯量 J = {J:.2f} g·cm²
本底转动惯量 J0 = {J0:.2f} g·cm²
铝环转动惯量 J_ring = {J_ring:.2f} g·cm²
铝环转动惯量（理论值） = {J_theory:.2f} g·cm²
相对误差 = {error:.2f}%
""")

    def init_method2(self):
        """延迟初始化实验二功能"""
        if self.method2 is None:
            self.method2 = RotationExperimentMethod2()
            # 绑定方法
            self.method2.main_frame = self.main_frame
            self.method2.result_area = self.result_area
            self.method2.params = self.params
            self.method2.current_method = self.current_method
            self.method2.clear_interface = self.clear_interface
            self.method2.update_status = self.update_status
            self.method2.display_result = self.display_result
        return self.method2

    def display_result(self, text):
        """显示计算结果"""
        for widget in self.result_area.winfo_children():
            widget.destroy()
        
        result_label = ttk.Label(self.result_area, text=text, justify="left", font=('Arial', 10))
        result_label.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = RotationExperimentApp(root)
    root.mainloop()
