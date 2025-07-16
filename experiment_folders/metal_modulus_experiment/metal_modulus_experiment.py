import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import math

class MetalModulusExperimentWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("拉伸法测金属丝杨氏模量")
        self.geometry("700x950")
        self.configure(bg="#f0f0f0")
        
        # 创建主框架
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 数据输入区域
        self.create_data_input_section()
        
        # 计算按钮区域
        self.create_calculation_buttons()
        
        # 结果显示区域
        self.create_result_display()
        
        # 实验知识查询区域
        self.create_knowledge_query_buttons()
        
        # 初始化数据存储
        self.measurements = []
        self.parameters = {}
        self.errors = {}
        self.results = {}
    
    def create_data_input_section(self):
        """创建数据输入区域"""
        input_frame = ttk.LabelFrame(self.main_frame, text="数据输入", padding=10)
        input_frame.pack(fill=tk.X, pady=5)
        
        # 创建选项卡
        self.notebook = ttk.Notebook(input_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # 测量数据选项卡
        self.create_measurement_tab()
        
        # 参数输入选项卡
        self.create_parameter_tab()
        
        # 误差输入选项卡
        self.create_error_tab()
    
    def create_measurement_tab(self):
        """创建测量数据输入选项卡
        函数模块名称: 测量数据输入选项卡
        输入参数: 无
        返回值: 无
        功能描述: 创建包含4列10行的测量数据输入表格，自动计算平均值和差值
        """
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="测量数据")
        
        # 标尺读数输入
        ttk.Label(tab, text="荷重砝码变化量 ΔP (kg):").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.delta_p_entry = ttk.Entry(tab)
        self.delta_p_entry.grid(row=0, column=1, padx=5, pady=5)
        self.delta_p_entry.insert(0, "5")  # 默认值
        
        # 标尺读数输入表格标题
        ttk.Label(tab, text="标尺读数 (cm):").grid(row=1, column=0, columnspan=5, pady=5, sticky=tk.W)
        
        # 列标题（调整对齐）
        headers = ["序号", "P增加时 S", "P减小时 S'", "平均值 (S+S')/2", "差值 ΔS (S6-S1)"]
        for col, header in enumerate(headers):
            ttk.Label(tab, text=header).grid(row=2, column=col, padx=5, pady=2, sticky=tk.W if col > 0 else tk.E)
        
        # 创建10行5列的输入表格（包含序号列）
        self.reading_entries = []
        for row in range(10):
            row_entries = []
            # 序号列
            ttk.Label(tab, text=f"S{row+1}:").grid(row=row+3, column=0, padx=5, pady=2, sticky=tk.E)
            
            # 前两列为可编辑输入框（P增加和P减少）
            for col in range(1, 3):
                entry = ttk.Entry(tab, width=10)
                entry.grid(row=row+3, column=col, padx=5, pady=2, sticky=tk.W)
                row_entries.append(entry)
            
            # 后两列为自动计算的只读文本框（平均值和差值）
            for col in range(3, 5):
                entry = ttk.Entry(tab, width=12, state='readonly')
                entry.grid(row=row+3, column=col, padx=5, pady=2, sticky=tk.W)
                row_entries.append(entry)
            
            self.reading_entries.append(row_entries)
        
        # 添加确认按钮（调整位置到表格下方居中）
        ttk.Button(tab, text="确认输入", command=self.validate_measurements).grid(
            row=14, column=0, columnspan=5, pady=10)

    def create_parameter_tab(self):
        """创建参数输入选项卡"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="实验参数")
        
        parameters = [
            ("钢丝长度 L (cm):", "L"),
            ("光杠杆到标尺距离 D (cm):", "D"),
            ("钢丝直径 ρ (mm):", "rho"),
            ("光杠杆后脚尖间距 b (cm):", "b")
        ]
        
        self.parameter_entries = {}
        for i, (label_text, param_name) in enumerate(parameters):
            ttk.Label(tab, text=label_text).grid(row=i, column=0, padx=5, pady=5, sticky=tk.W)
            entry = ttk.Entry(tab)
            entry.grid(row=i, column=1, padx=5, pady=5)
            self.parameter_entries[param_name] = entry
        
        # 添加确认按钮
        ttk.Button(tab, text="确认参数", command=self.validate_parameters).grid(row=4, column=0, columnspan=2, pady=10)
    
    def create_error_tab(self):
        """创建误差输入选项卡"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="误差参数")
        
        errors = [
            ("钢丝长度误差 ΔL (cm):", "Delta_L"),
            ("光杠杆距离误差 ΔD (cm):", "Delta_D"),
            ("钢丝直径误差 Δρ (mm):", "Delta_rho"),
            ("光杠杆间距误差 Δb (cm):", "Delta_b"),
            ("砝码误差 ΔP (kg):", "Delta_delta_P"),
            ("标尺读数误差 ΔS (cm):", "Delta_Delta_S")
        ]
        
        self.error_entries = {}
        for i, (label_text, error_name) in enumerate(errors):
            ttk.Label(tab, text=label_text).grid(row=i, column=0, padx=5, pady=5, sticky=tk.W)
            entry = ttk.Entry(tab)
            entry.grid(row=i, column=1, padx=5, pady=5)
            self.error_entries[error_name] = entry
        
        # 添加确认按钮
        ttk.Button(tab, text="确认误差", command=self.validate_errors).grid(row=6, column=0, columnspan=2, pady=10)
    
    def create_calculation_buttons(self):
        """创建计算按钮区域"""
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        # 确保所有按钮命令对应的方法都已定义
        ttk.Button(button_frame, text="逐差法计算", command=self.calculate_difference_method).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="计算杨氏弹性模量", command=self.calculate_modulus).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="误差分析计算", command=self.calculate_error).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="结果分析", command=self.analyze_results).pack(side=tk.LEFT, padx=5)
    
    def create_result_display(self):
        """创建结果显示区域"""
        result_frame = ttk.LabelFrame(self.main_frame, text="计算结果与过程", padding=10)
        result_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.result_text = tk.Text(result_frame, wrap=tk.WORD, height=15)
        scrollbar = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=scrollbar.set)
        
        self.result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 关键结果显示区域
        key_result_frame = ttk.Frame(self.main_frame)
        key_result_frame.pack(fill=tk.X, pady=5)
        
        self.modulus_label = ttk.Label(key_result_frame, text="杨氏弹性模量: 未计算", font=("Arial", 12, "bold"), foreground="red")
        self.modulus_label.pack(pady=5)
        
        self.error_label = ttk.Label(key_result_frame, text="相对误差: 未计算", font=("Arial", 12))
        self.error_label.pack(pady=5)
    
    def create_knowledge_query_buttons(self):
        """创建实验知识查询按钮"""
        query_frame = ttk.Frame(self.main_frame)
        query_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(query_frame, text="实验原理查询", command=self.show_experiment_principle).pack(side=tk.LEFT, padx=5)
        ttk.Button(query_frame, text="公式查询", command=self.show_formulas).pack(side=tk.LEFT, padx=5)
        ttk.Button(query_frame, text="仪器操作查询", command=self.show_operation_steps).pack(side=tk.LEFT, padx=5)
    
    def validate_measurements(self):
        """验证测量数据输入"""
        try:
            delta_p = float(self.delta_p_entry.get())
            if delta_p <= 0:
                raise ValueError("砝码变化量必须为正数")
            
            readings = []
            avg_readings = []
            delta_readings = []
            
            # 验证并获取前两列数据（注意索引已调整）
            for row in range(10):
                s = self.reading_entries[row][0].get()  # 列1: P增加时S
                s_prime = self.reading_entries[row][1].get()  # 列2: P减小时S'
                
                if not s or not s_prime:
                    continue  # 允许部分数据为空
                
                s_val = float(s)
                s_prime_val = float(s_prime)
                readings.append((s_val, s_prime_val))
                
                # 计算平均值
                avg = (s_val + s_prime_val) / 2
                avg_readings.append(avg)
                
                # 更新平均值显示（列3）
                self.reading_entries[row][2].config(state='normal')
                self.reading_entries[row][2].delete(0, tk.END)
                self.reading_entries[row][2].insert(0, f"{avg:.4f}")
                self.reading_entries[row][2].config(state='readonly')
            
            if len(readings) < 10:
                raise ValueError("需要完整输入10组数据")
            
            # 计算差值列（列4）
            for row in range(5):
                delta = avg_readings[row+5] - avg_readings[row]
                delta_readings.append(delta)
                
                # 更新差值显示（只显示前5行）
                self.reading_entries[row][3].config(state='normal')
                self.reading_entries[row][3].delete(0, tk.END)
                self.reading_entries[row][3].insert(0, f"{delta:.4f}")
                self.reading_entries[row][3].config(state='readonly')
            
            self.measurements = {
                'delta_p': delta_p,
                'readings': readings,
                'avg_readings': avg_readings,
                'delta_readings': delta_readings
            }
            messagebox.showinfo("成功", "测量数据验证通过并已自动计算")
        except ValueError as e:
            messagebox.showerror("输入错误", f"测量数据输入有误: {str(e)}")

            
    def validate_parameters(self):
        """验证实验参数输入"""
        try:
            parameters = {}
            for param_name, entry in self.parameter_entries.items():
                value = entry.get()
                if not value:
                    raise ValueError(f"参数 {param_name} 不能为空")
                
                float_value = float(value)
                if float_value <= 0:
                    raise ValueError(f"参数 {param_name} 必须为正数")
                
                # 单位转换
                if param_name == 'rho':
                    float_value /= 1000  # mm转m
                elif param_name == 'L' or param_name == 'D' or param_name == 'b':
                    float_value /= 100  # cm转m
                
                parameters[param_name] = float_value
            
            self.parameters = parameters
            messagebox.showinfo("成功", "实验参数验证通过")
        except ValueError as e:
            messagebox.showerror("输入错误", f"实验参数输入有误: {str(e)}")
    
    def validate_errors(self):
        """验证误差参数输入"""
        try:
            errors = {}
            for error_name, entry in self.error_entries.items():
                value = entry.get()
                if not value:
                    errors[error_name] = 0.0  # 允许误差为空，默认为0
                    continue
                
                float_value = float(value)
                if float_value < 0:
                    raise ValueError(f"误差 {error_name} 不能为负数")
                
                # 单位转换
                if 'rho' in error_name:
                    float_value /= 1000  # mm转m
                elif 'Delta_L' in error_name or 'Delta_D' in error_name or 'Delta_b' in error_name:
                    float_value /= 100  # cm转m
                elif 'Delta_S' in error_name:
                    float_value /= 100  # cm转m
                
                errors[error_name] = float_value
            
            self.errors = errors
            messagebox.showinfo("成功", "误差参数验证通过")
        except ValueError as e:
            messagebox.showerror("输入错误", f"误差参数输入有误: {str(e)}")
    
    def calculate_difference_method(self):
        """逐差法计算
        函数模块名称: 逐差法计算
        输入参数: 无
        返回值: 无
        功能描述: 使用逐差法计算平均读数差，基于新的10行4列数据结构
        """
        if not self.measurements or 'avg_readings' not in self.measurements:
            messagebox.showerror("错误", "请先输入并确认测量数据")
            return
        
        avg_readings = self.measurements['avg_readings']
        delta_readings = self.measurements['delta_readings']
        
        if len(avg_readings) < 10:
            messagebox.showerror("错误", "需要完整输入10组数据")
            return
        
        # 计算平均读数差 (使用已计算好的差值)
        avg_delta_s = sum(delta_readings) / len(delta_readings)
        
        # 保存结果
        self.results['delta_s_list'] = delta_readings
        self.results['avg_delta_s'] = avg_delta_s
        
        # 显示计算过程
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, "逐差法计算过程:\n\n")
        self.result_text.insert(tk.END, f"标尺读数平均值: {avg_readings}\n")
        
        for i in range(5):
            self.result_text.insert(tk.END, 
                f"ΔS{i+1} = S{i+6} - S{i+1} = {avg_readings[i+5]:.4f} - {avg_readings[i]:.4f} = {delta_readings[i]:.4f} cm\n")
        
        self.result_text.insert(tk.END, 
            f"\n平均读数差 ΔS = ({' + '.join([f'{x:.4f}' for x in delta_readings])}) / {len(delta_readings)} = {avg_delta_s:.4f} cm\n")
        self.result_text.insert(tk.END, f"\n注意: 计算杨氏模量时请将单位转换为米(m)\n")

    
    def calculate_modulus(self):
        """计算杨氏弹性模量
        函数模块名称: 杨氏弹性模量计算
        输入参数: 无
        返回值: 无
        功能描述: 计算杨氏弹性模量，使用新的测量数据结构
        """
        if not self.measurements or 'avg_delta_s' not in self.results:
            messagebox.showerror("错误", "请先完成逐差法计算")
            return
        
        if not self.parameters:
            messagebox.showerror("错误", "请先输入实验参数")
            return
        
        try:
            # 获取参数
            L = self.parameters['L']
            D = self.parameters['D']
            rho = self.parameters['rho']
            b = self.parameters['b']
            
            # 获取测量数据
            delta_p = self.measurements['delta_p']
            avg_delta_s = self.results['avg_delta_s'] / 100  # cm转m
            
            # 计算杨氏模量
            numerator = 8 * L * D * delta_p * 9.8
            denominator = math.pi * (rho ** 2) * b * avg_delta_s
            E = numerator / denominator
            
            # 保存结果
            self.results['E'] = E
            
            # 显示计算过程
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, "杨氏弹性模量计算过程:\n\n")
            self.result_text.insert(tk.END, "使用的测量数据:\n")
            for i in range(10):
                s, s_prime = self.measurements['readings'][i]
                self.result_text.insert(tk.END, 
                    f"S{i+1}: {s:.4f} cm, S'{i+1}: {s_prime:.4f} cm → 平均: {self.measurements['avg_readings'][i]:.4f} cm\n")
            
            self.result_text.insert(tk.END, "\n逐差法计算结果:\n")
            for i in range(5):
                self.result_text.insert(tk.END, 
                    f"ΔS{i+1} = {self.results['delta_s_list'][i]:.4f} cm\n")
            
            self.result_text.insert(tk.END, 
                f"\n平均读数差 ΔS = {self.results['avg_delta_s']:.4f} cm → {avg_delta_s} m\n\n")
            
            self.result_text.insert(tk.END, f"使用公式: E = (8 * L * D * ΔP * g) / (π * ρ² * b * ΔS)\n\n")
            self.result_text.insert(tk.END, f"参数值:\n")
            self.result_text.insert(tk.END, f"L = {L} m\n")
            self.result_text.insert(tk.END, f"D = {D} m\n")
            self.result_text.insert(tk.END, f"ρ = {rho*1000:.4f} mm (输入值) → {rho} m\n")
            self.result_text.insert(tk.END, f"b = {b*1000:.4f} mm (输入值) → {b} m\n")
            self.result_text.insert(tk.END, f"ΔP = {delta_p} kg\n")
            self.result_text.insert(tk.END, f"g = 9.8 N/kg\n")
            self.result_text.insert(tk.END, f"ΔS = {avg_delta_s} m\n\n")
            self.result_text.insert(tk.END, f"计算过程:\n")
            self.result_text.insert(tk.END, f"分子 = 8 * {L} * {D} * {delta_p} * 9.8 = {numerator:.4f}\n")
            self.result_text.insert(tk.END, f"分母 = π * ({rho})² * {b} * {avg_delta_s} = {denominator:.4f}\n")
            self.result_text.insert(tk.END, f"\n杨氏弹性模量 E = {numerator:.4f} / {denominator:.4f} = {E:.2e} Pa\n")
            
            # 更新关键结果
            self.modulus_label.config(text=f"杨氏弹性模量: {E:.2e} Pa")
        except Exception as e:
            messagebox.showerror("计算错误", f"计算杨氏模量时出错: {str(e)}")


    def calculate_error(self):
        """误差分析计算"""
        if 'E' not in self.results:
            messagebox.showerror("错误", "请先计算杨氏弹性模量")
            return
        
        if not self.errors:
            messagebox.showerror("错误", "请先输入误差参数")
            return
        
        try:
            # 获取参数和误差
            L = self.parameters['L']
            D = self.parameters['D']
            rho = self.parameters['rho']
            b = self.parameters['b']
            delta_p = self.measurements['delta_p']
            avg_delta_s = self.results['avg_delta_s'] / 100  # cm转m
            
            Delta_L = self.errors['Delta_L']
            Delta_D = self.errors['Delta_D']
            Delta_rho = self.errors['Delta_rho']
            Delta_b = self.errors['Delta_b']
            Delta_delta_P = self.errors['Delta_delta_P']
            Delta_Delta_S = self.errors['Delta_Delta_S']
            
            # 计算各项相对误差
            rel_L = Delta_L / L
            rel_D = Delta_D / D
            rel_rho = 2 * (Delta_rho / rho)  # 注意公式中有2倍
            rel_b = Delta_b / b
            rel_delta_P = Delta_delta_P / delta_p
            rel_Delta_S = Delta_Delta_S / avg_delta_s
            
            # 计算总相对误差
            total_rel_error = rel_L + rel_D + rel_rho + rel_b + rel_delta_P + rel_Delta_S
            Delta_E = total_rel_error * self.results['E']
            
            # 保存结果
            self.results['relative_errors'] = {
                'rel_L': rel_L,
                'rel_D': rel_D,
                'rel_rho': rel_rho,
                'rel_b': rel_b,
                'rel_delta_P': rel_delta_P,
                'rel_Delta_S': rel_Delta_S,
                'total_rel_error': total_rel_error,
                'Delta_E': Delta_E
            }
            
            # 显示计算过程
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, "误差分析计算过程:\n\n")
            self.result_text.insert(tk.END, "使用公式: (ΔE/E) = (ΔL/L) + (ΔD/D) + 2*(Δρ/ρ) + (Δb/b) + (ΔΔP/ΔP) + (ΔΔS/ΔS)\n\n")
            
            self.result_text.insert(tk.END, "各项相对误差:\n")
            self.result_text.insert(tk.END, f"(ΔL/L) = {Delta_L} / {L} = {rel_L:.4f} ({rel_L*100:.2f}%)\n")
            self.result_text.insert(tk.END, f"(ΔD/D) = {Delta_D} / {D} = {rel_D:.4f} ({rel_D*100:.2f}%)\n")
            self.result_text.insert(tk.END, f"2*(Δρ/ρ) = 2 * {Delta_rho} / {rho} = {rel_rho:.4f} ({rel_rho*100:.2f}%)\n")
            self.result_text.insert(tk.END, f"(Δb/b) = {Delta_b} / {b} = {rel_b:.4f} ({rel_b*100:.2f}%)\n")
            self.result_text.insert(tk.END, f"(ΔΔP/ΔP) = {Delta_delta_P} / {delta_p} = {rel_delta_P:.4f} ({rel_delta_P*100:.2f}%)\n")
            self.result_text.insert(tk.END, f"(ΔΔS/ΔS) = {Delta_Delta_S} / {avg_delta_s} = {rel_Delta_S:.4f} ({rel_Delta_S*100:.2f}%)\n\n")
            
            self.result_text.insert(tk.END, f"总相对误差 = {rel_L:.4f} + {rel_D:.4f} + {rel_rho:.4f} + {rel_b:.4f} + {rel_delta_P:.4f} + {rel_Delta_S:.4f}\n")
            self.result_text.insert(tk.END, f"            = {total_rel_error:.4f} ({total_rel_error*100:.2f}%)\n\n")
            
            self.result_text.insert(tk.END, f"绝对误差 ΔE = E * (ΔE/E) = {self.results['E']:.2e} * {total_rel_error:.4f}\n")
            self.result_text.insert(tk.END, f"            = {Delta_E:.2e} Pa\n")
            
            # 更新关键结果
            self.error_label.config(text=f"相对误差: {total_rel_error*100:.2f}%")
        except Exception as e:
            messagebox.showerror("计算错误", f"误差分析时出错: {str(e)}")
    
    def analyze_results(self):
        """结果分析"""
        if 'E' not in self.results:
            messagebox.showerror("错误", "请先计算杨氏弹性模量")
            return
        
        # 理论值范围 (假设钢的杨氏模量约为 2.0×10^11 Pa)
        theoretical_min = 1.8e11
        theoretical_max = 2.2e11
        E = self.results['E']
        
        # 分析结果
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, "结果分析:\n\n")
        self.result_text.insert(tk.END, f"您计算的杨氏弹性模量 E = {E:.2e} Pa\n")
        self.result_text.insert(tk.END, f"钢的理论杨氏模量范围: {theoretical_min:.2e} ~ {theoretical_max:.2e} Pa\n\n")
        
        if E < theoretical_min * 0.9 or E > theoretical_max * 1.1:
            self.result_text.insert(tk.END, "警告: 您的计算结果超出理论范围±10%!\n\n")
            self.result_text.insert(tk.END, "可能原因分析:\n")
            
            if 'relative_errors' in self.results:
                errors = self.results['relative_errors']
                max_error = max(errors['rel_L'], errors['rel_D'], errors['rel_rho'], 
                            errors['rel_b'], errors['rel_delta_P'], errors['rel_Delta_S'])
                
                if max_error == errors['rel_rho']:
                    self.result_text.insert(tk.END, "1. 钢丝直径测量误差较大 (因为 E ∝ 1/ρ²)\n")
                    self.result_text.insert(tk.END, "   - 建议使用更精确的螺旋测微器测量钢丝直径\n")
                    self.result_text.insert(tk.END, "   - 在不同位置多次测量取平均值\n\n")
                
                if max_error == errors['rel_Delta_S']:
                    self.result_text.insert(tk.END, "2. 标尺读数误差较大\n")
                    self.result_text.insert(tk.END, "   - 检查光杠杆和望远镜调节是否准确\n")
                    self.result_text.insert(tk.END, "   - 确保实验过程中仪器稳定，避免振动\n\n")
                
                if max_error == errors['rel_D'] or max_error == errors['rel_b']:
                    self.result_text.insert(tk.END, "3. 光杠杆参数测量误差较大\n")
                    self.result_text.insert(tk.END, "   - 重新测量光杠杆到标尺的距离 D\n")
                    self.result_text.insert(tk.END, "   - 精确测量光杠杆后脚尖间距 b\n\n")
            else:
                self.result_text.insert(tk.END, "- 请检查测量数据是否准确\n")
                self.result_text.insert(tk.END, "- 检查仪器调节是否正确\n")
                self.result_text.insert(tk.END, "- 确保实验环境稳定\n")
        else:
            self.result_text.insert(tk.END, "您的计算结果在理论范围内，实验数据可靠!\n")
            if 'relative_errors' in self.results:
                self.result_text.insert(tk.END, "\n误差分析显示主要误差来源:\n")
                errors = self.results['relative_errors']
                sorted_errors = sorted([('钢丝长度', errors['rel_L']),
                                    ('光杠杆距离', errors['rel_D']),
                                    ('钢丝直径', errors['rel_rho']),
                                    ('光杠杆间距', errors['rel_b']),
                                    ('砝码质量', errors['rel_delta_P']),
                                    ('标尺读数', errors['rel_Delta_S'])], 
                                    key=lambda x: x[1], reverse=True)
                
                for name, error in sorted_errors[:3]:
                    self.result_text.insert(tk.END, f"- {name}: {error*100:.2f}%\n")
    
    def show_experiment_principle(self):
        """显示实验原理"""
        principle_window = tk.Toplevel(self)
        principle_window.title("实验原理")
        principle_window.geometry("600x400")
        
        text = tk.Text(principle_window, wrap=tk.WORD, padx=10, pady=10)
        scrollbar = ttk.Scrollbar(principle_window, orient=tk.VERTICAL, command=text.yview)
        text.configure(yscrollcommand=scrollbar.set)
        
        text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        principle_text = """
        金属丝杨氏弹性模量测定实验原理
        
        1. 基本概念
        杨氏弹性模量(Young's modulus)是描述固体材料抵抗弹性形变能力的物理量，是材料在弹性限度内应力与应变的比值。
        
        2. 胡克定律
        对于连续、均匀、各向同性的材料制成的细丝，在弹性限度内，应变与应力成正比：
        
            (ΔP / A) = E * (Δl / l)
        
        其中：
        - ΔP: 外力变化量 (N)
        - A: 钢丝横截面积 (m²)
        - E: 杨氏弹性模量 (Pa)
        - Δl: 伸长量 (m)
        - l: 钢丝原长 (m)
        
        3. 光杠杆放大原理
        由于钢丝伸长量Δl非常微小，直接测量困难，本实验采用光杠杆放大法进行测量：
        
            Δl = (b / 2D) * ΔS
        
        其中：
        - b: 光杠杆后脚尖间距 (m)
        - D: 光杠杆到标尺的距离 (m)
        - ΔS: 标尺读数变化量 (m)
        
        4. 最终计算公式
        综合以上原理，得到杨氏弹性模量计算公式：
        
            E = (8 * L * D * ΔP * g) / (π * ρ² * b * ΔS)
        
        其中：
        - L: 钢丝长度 (m)
        - ρ: 钢丝直径 (m)
        - g: 重力加速度 (9.8 m/s²)
        """
        text.insert(tk.END, principle_text)
        text.config(state=tk.DISABLED)
    
    def show_formulas(self):
        """显示公式说明"""
        formula_window = tk.Toplevel(self)
        formula_window.title("公式查询")
        formula_window.geometry("600x400")
        
        text = tk.Text(formula_window, wrap=tk.WORD, padx=10, pady=10)
        scrollbar = ttk.Scrollbar(formula_window, orient=tk.VERTICAL, command=text.yview)
        text.configure(yscrollcommand=scrollbar.set)
        
        text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        formula_text = """
        实验相关公式及说明
        
        1. 胡克定律公式
        (ΔP / A) = E * (Δl / l)
        
        参数说明：
        - ΔP: 外力变化量 (单位: N)
        - A: 钢丝横截面积 (单位: m²)
        - E: 杨氏弹性模量 (单位: Pa)
        - Δl: 钢丝伸长量 (单位: m)
        - l: 钢丝原长 (单位: m)
        
        应用场景：描述材料在弹性限度内应力与应变的关系。
        
        2. 光杠杆放大公式
        Δl = (b / 2D) * ΔS
        
        参数说明：
        - b: 光杠杆后脚尖间距 (单位: m)
        - D: 光杠杆到标尺的距离 (单位: m)
        - ΔS: 标尺读数变化量 (单位: m)
        
        应用场景：将微小的钢丝伸长量Δl放大为可测量的标尺读数变化ΔS。
        
        3. 横截面积公式
        A = (π * ρ²) / 4
        
        参数说明：
        - ρ: 钢丝直径 (单位: m)
        
        应用场景：计算钢丝的横截面积。
        
        4. 杨氏模量计算公式
        E = (8 * L * D * ΔP * g) / (π * ρ² * b * ΔS)
        
        参数说明：
        - L: 钢丝长度 (单位: m)
        - D: 光杠杆到标尺的距离 (单位: m)
        - ΔP: 砝码质量变化量 (单位: kg)
        - g: 重力加速度 (9.8 m/s²)
        - ρ: 钢丝直径 (单位: m)
        - b: 光杠杆后脚尖间距 (单位: m)
        - ΔS: 标尺读数平均变化量 (单位: m)
        
        应用场景：综合计算金属丝的杨氏弹性模量。
        """
        text.insert(tk.END, formula_text)
        text.config(state=tk.DISABLED)
    
    def show_operation_steps(self):
        """显示仪器操作步骤"""
        operation_window = tk.Toplevel(self)
        operation_window.title("仪器操作步骤")
        operation_window.geometry("600x500")
        
        text = tk.Text(operation_window, wrap=tk.WORD, padx=10, pady=10)
        scrollbar = ttk.Scrollbar(operation_window, orient=tk.VERTICAL, command=text.yview)
        text.configure(yscrollcommand=scrollbar.set)
        
        text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        operation_text = """
        仪器操作步骤指引
        
        1. 仪器安装与调节
        (1) 调节杨氏模量仪器支架成铅直：
            - 使用水平仪检查支架是否垂直
            - 调整支架底部的调节旋钮，直至支架处于铅直状态
            - 确保钢丝自然下垂，无弯曲或扭曲
        
        (2) 安装光杠杆：
            - 将光杠杆前脚放在固定平台上
            - 后脚尖轻轻放在与钢丝连接的圆形托盘上
            - 确保光杠杆镜面垂直于水平面
        
        2. 望远镜调节
        (1) 粗调：
            - 将望远镜置于距光杠杆约1-2米处
            - 调节望远镜高度和角度，使眼睛能大致从望远镜中看到标尺的像
            - 通过光杠杆镜面观察，应能看到标尺
        
        (2) 细调：
            - 通过望远镜的调焦旋钮，使标尺刻度清晰成像
            - 微调光杠杆和望远镜的位置，确保能准确读取标尺读数
            - 记录初始标尺读数S₀
        
        3. 数据测量步骤
        (1) 逐次增加砝码(如每次增加5kg)：
            - 每次增加砝码后，等待约1分钟使系统稳定
            - 记录对应的标尺读数S₁, S₂, ..., Sₙ
        
        (2) 逐次减少砝码：
            - 按相同间隔减少砝码
            - 记录对应的标尺读数Sₙ', ..., S₂', S₁'
            - 检查增减砝码时的读数是否一致，评估测量可靠性
        
        4. 参数测量
        (1) 测量钢丝长度L：
            - 用钢卷尺测量钢丝上夹头到下夹头之间的长度
            - 多次测量取平均值
        
        (2) 测量光杠杆距离D：
            - 用钢卷尺测量光杠杆镜面到标尺的垂直距离
            - 确保测量时卷尺保持水平
        
        (3) 测量钢丝直径ρ：
            - 用螺旋测微器在不同位置测量钢丝直径
            - 至少测量5次取平均值
            - 注意消除零点误差
        
        (4) 测量光杠杆后脚尖间距b：
            - 将光杠杆三脚在白纸上压出痕迹
            - 用游标卡尺测量两后脚尖之间的距离
        
        5. 注意事项
        - 实验过程中避免触碰仪器，防止振动影响读数
        - 增减砝码时要轻拿轻放
        - 读数时眼睛要平视，避免视差
        - 保持光杠杆镜面清洁
        """
        text.insert(tk.END, operation_text)
        text.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = MetalModulusExperimentWindow(root)
    root.mainloop()
