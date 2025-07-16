import numpy as np
import tkinter.messagebox as messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from tkinter import ttk

GRAVITY = 980  # 重力加速度 (cm/s²)

class RotationExperimentMethod2:
    """实验二：作图法相关功能"""
    
    def __init__(self):
        # 实验二参数
        self.m2_config = {
            "start": 12.5,   # 默认起始值10+2.5=12.5g
            "step": 5.0,     # 默认步长5g
            "count": 6       # 默认6组数据
        }
        # 必要的属性占位
        self.main_frame = None
        self.result_area = None
        self.params = None
        self.current_method = None
        self.method2_table = None
        self.m2_start_entry = None
        self.m2_step_entry = None
        self.m2_count_entry = None

    def show_method2_interface(self):
        """实验二界面：作图法"""
        self.current_method = "method2"
        self.clear_interface()
        
        # 创建参数输入子框架
        params_subframe = ttk.Frame(self.main_frame)
        params_subframe.grid(row=1, column=0, sticky="ew", pady=5)
        
        # m1参数设置
        ttk.Label(params_subframe, text="m1起始值 (g):").grid(row=0, column=0, sticky="w")
        self.m2_start_entry = ttk.Entry(params_subframe, width=10)
        self.m2_start_entry.insert(0, str(self.m2_config["start"]))
        self.m2_start_entry.grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(params_subframe, text="m1步长 (g):").grid(row=0, column=2, sticky="w")
        self.m2_step_entry = ttk.Entry(params_subframe, width=10)
        self.m2_step_entry.insert(0, str(self.m2_config["step"]))
        self.m2_step_entry.grid(row=0, column=3, padx=5, pady=2)
        
        ttk.Label(params_subframe, text="测量次数:").grid(row=0, column=4, sticky="w")
        self.m2_count_entry = ttk.Entry(params_subframe, width=10)
        self.m2_count_entry.insert(0, str(self.m2_config["count"]))
        self.m2_count_entry.grid(row=0, column=5, padx=5, pady=2)
        
        ttk.Button(params_subframe, text="更新表格", command=self.update_method2_table).grid(row=0, column=6, padx=10, pady=2)
        
        # 初始化表格
        self.update_method2_table()
        
        # 配置行权重
        self.main_frame.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=1)
        
        # 配置参数子框架的列权重
        for i in range(7):
            params_subframe.columnconfigure(i, weight=1)
        
        self.update_status("请输入实验二的角加速度数据（有/无铝环）")

    def update_method2_table(self):
        """更新实验二表格"""
        try:
            start = float(self.m2_start_entry.get())
            step = float(self.m2_step_entry.get())
            count = int(self.m2_count_entry.get())
            if count <= 0:
                raise ValueError("测量次数必须大于0")
            self.m2_config = {"start": start, "step": step, "count": count}
            
            # 生成m1标签（动态列标题）
            m1_labels = [f"测量{i+1} (m1={start + i*step:.1f}g)" for i in range(count)]
            
            # 添加平均值列
            cols = ["测量次数"] + m1_labels + ["平均值"]
            
            # 清除旧表格
            if hasattr(self, 'method2_table') and self.method2_table:
                self.method2_table.destroy()
            
            # 创建新表格（2行7列：β(有铝环), β0(无铝环), 平均值）
            from rotation_experiment import DataInputTable
            self.method2_table = DataInputTable(
                self.main_frame,
                rows=["β (有铝环)", "β' (有铝环)", "β0 (无铝环)", "β0' (无铝环)"],
                cols=cols,
                title="实验二：不同砝码质量下的角加速度"
            )
            self.method2_table.grid(row=0, column=0, sticky="nsew", pady=5)
            
        except ValueError as e:
            messagebox.showerror("输入错误", f"请检查m1参数设置：{str(e)}")

    def calculate_method2(self):
        """实验二计算逻辑"""
        if not hasattr(self, 'method2_table') or not self.method2_table:
            messagebox.showerror("错误", "请先设置实验参数并输入数据")
            return
            
        data = self.method2_table.get_data()
        count = self.m2_config["count"]
        
        # 生成m1值数组
        m1_values = np.array([
            self.m2_config["start"] + i * self.m2_config["step"] 
            for i in range(count)
        ])
        
        # 提取有铝环数据
        beta_with = np.array([data[("β (有铝环)", i)] for i in range(1, count+1)])
        beta_prime_with = np.array([data[("β' (有铝环)", i)] for i in range(1, count+1)])
        # 提取无铝环数据
        beta_without = np.array([data[("β0 (无铝环)", i)] for i in range(1, count+1)])
        beta_prime_without = np.array([data[("β0' (无铝环)", i)] for i in range(1, count+1)])
        
        # 计算平均角加速度
        beta_avg_with = (beta_with + beta_prime_with) / 2
        beta_avg_without = (beta_without + beta_prime_without) / 2
        
        # 线性拟合
        slope_with, intercept_with = np.polyfit(beta_avg_with, m1_values, 1)
        slope_without, intercept_without = np.polyfit(beta_avg_without, m1_values, 1)
        
        # 计算转动惯量
        J_total = slope_with * GRAVITY * self.params["r"]
        J0 = slope_without * GRAVITY * self.params["r"]
        J_ring = J_total - J0
        
        # 计算摩擦力矩
        Mu_with = -intercept_with * GRAVITY * self.params["r"]
        Mu_without = -intercept_without * GRAVITY * self.params["r"]
        
        # 计算理论值
        J_theory = 0.5 * self.params["m_ring"] * (
            self.params["r_inner"]**2 + self.params["r_outer"]**2
        )
        
        # 计算误差
        error = abs(J_ring - J_theory) / J_theory * 100
        
        # 显示结果
        self.display_result(f"""
实验二计算结果：
-----------------------------------
有铝环转动惯量 J_total = {J_total:.2f} g·cm²
无铝环转动惯量 J0 = {J0:.2f} g·cm²
铝环转动惯量 J_ring = {J_ring:.2f} g·cm²
铝环转动惯量（理论值） = {J_theory:.2f} g·cm²
相对误差 = {error:.2f}%
有铝环摩擦力矩 Mu = {Mu_with:.2f} dyn·cm
无铝环摩擦力矩 Mu0 = {Mu_without:.2f} dyn·cm
拟合斜率（有铝环） = {slope_with:.4f} g/(rad/s²)
拟合斜率（无铝环） = {slope_without:.4f} g/(rad/s²)
""")
        
        # 绘制拟合曲线
        self.plot_fitting(beta_avg_with, beta_avg_without, m1_values, slope_with, slope_without)

    def plot_fitting(self, beta_with, beta_without, m1_values, slope_with, slope_without):
        """绘制双拟合曲线"""
        for widget in self.result_area.winfo_children():
            widget.destroy()
        
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.scatter(beta_with, m1_values, color='blue', label='有铝环数据', zorder=2)
        ax.scatter(beta_without, m1_values, color='red', label='无铝环数据', zorder=2)
        
        # 生成拟合线
        x_min = min(beta_with.min(), beta_without.min())
        x_max = max(beta_with.max(), beta_without.max())
        x_range = np.linspace(x_min, x_max, 100)
        
        y_fit_with = slope_with * x_range + (np.mean(m1_values) - slope_with * np.mean(beta_with))
        y_fit_without = slope_without * x_range + (np.mean(m1_values) - slope_without * np.mean(beta_without))
        
        ax.plot(x_range, y_fit_with, 'b--', label=f'有铝环拟合 (k={slope_with:.4f})', zorder=1)
        ax.plot(x_range, y_fit_without, 'r--', label=f'无铝环拟合 (k={slope_without:.4f})', zorder=1)
        
        ax.set_xlabel('角加速度 β (rad/s²)', fontsize=12)
        ax.set_ylabel('砝码质量 m1 (g)', fontsize=12)
        ax.set_title('实验二：m1 - β 线性拟合曲线', fontsize=14)
        ax.grid(True, linestyle='--', alpha=0.7)
        ax.legend()
        
        # 嵌入Tkinter界面
        canvas = FigureCanvasTkAgg(fig, master=self.result_area)
        canvas.draw()
        canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
