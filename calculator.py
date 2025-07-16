import tkinter as tk
from tkinter import simpledialog, messagebox, scrolledtext
import numpy as np
import re


class ExperimentDataProcessor:
    def __init__(self, root):
        self.root = root
        self.root.title("实验数据处理")
        self.root.geometry("950x500")
        self.std_dev = None
        self.records = []

        # 主框架，设置内边距
        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.pack(expand=True, fill='both')

        # 左侧框架，包含按钮和使用说明
        left_frame = tk.Frame(main_frame)
        left_frame.pack(side='left', fill='y', padx=10)

        # 按钮框架
        button_frame = tk.Frame(left_frame)
        button_frame.pack(side='top', fill='y')

        # 标准差计算按钮
        self.std_button = tk.Button(button_frame, text="标准差计算", command=self.calculate_std_dev,
                                    width=20, font=('Arial', 10))
        self.std_button.pack(pady=10)

        # 平均数计算按钮
        self.mean_button = tk.Button(button_frame, text="平均数计算", command=self.calculate_mean,
                                     width=20, font=('Arial', 10))
        self.mean_button.pack(pady=10)

        # U偏差计算按钮
        self.u_button = tk.Button(button_frame, text="U偏差计算", command=self.calculate_u_deviation,
                                  width=20, font=('Arial', 10))
        self.u_button.pack(pady=10)

        # 普通计算器按钮
        self.calc_button = tk.Button(button_frame, text="普通计算器", command=self.calculate_expression,
                                     width=20, font=('Arial', 10))
        self.calc_button.pack(pady=10)

        # 使用说明标签
        instruction_text = (
            "使用说明：\n"
            "1. 进行标准差、平均数计算时，请用空格分割数据。\n"
            "2. 若此前已计算过标准差，在计算U偏差时无需再次输入标准差。\n"
            "3. 普通计算器中，使用 ^ 表示指数运算。"
        )
        self.instruction_label = tk.Label(left_frame, text=instruction_text, justify=tk.LEFT, font=('Arial', 10))
        self.instruction_label.pack(side='bottom', padx=10, pady=10, fill='x')

        # 记录显示框
        self.records_text = scrolledtext.ScrolledText(main_frame, width=40, height=20, wrap='word',
                                                      font=('Arial', 10))
        self.records_text.pack(side='right', padx=10, pady=10, fill='both', expand=True)

    def add_record(self, function_name, expression, result):
        record = f"功能: {function_name}, 表达式: {expression}, 结果: {result}"
        self.records.append(record)
        self.records_text.insert(tk.END, record + "\n")
        self.records_text.see(tk.END)

    def calculate_std_dev(self):
        data = simpledialog.askstring("标准差计算", "请输入以空格分隔的数据：")
        if data:
            try:
                data_list = list(map(float, data.split()))
                self.std_dev = np.std(data_list, ddof=1)
                result = f"标准差：{self.std_dev:.4f}"
                messagebox.showinfo("标准差计算结果", result)
                self.add_record("标准差计算", data, result)
            except ValueError:
                messagebox.showerror("输入错误", "请输入有效的数字数据。")

    def calculate_mean(self):
        data = simpledialog.askstring("平均数计算", "请输入以空格分隔的数据：")
        if data:
            try:
                data_list = list(map(float, data.split()))
                mean_value = np.mean(data_list)
                result = f"平均数：{mean_value:.4f}"
                messagebox.showinfo("平均数计算结果", result)
                self.add_record("平均数计算", data, result)
            except ValueError:
                messagebox.showerror("输入错误", "请输入有效的数字数据。")

    def calculate_u_deviation(self):
        if self.std_dev is None:
            std_dev_input = simpledialog.askstring("标准差输入", "请输入标准差值（若未计算过）：")
            if std_dev_input:
                try:
                    self.std_dev = float(std_dev_input)
                except ValueError:
                    messagebox.showerror("输入错误", "请输入有效的标准差值。")
                    return

        instrument_error = simpledialog.askstring("仪器误差输入", "请输入仪器误差值：")
        if instrument_error:
            try:
                instrument_error = float(instrument_error)
                u_value = np.sqrt(self.std_dev ** 2 + (instrument_error / 3) ** 2)
                result = f"U偏差：{u_value:.4f}"
                messagebox.showinfo("U偏差计算结果", result)
                self.add_record("U偏差计算", f"标准差: {self.std_dev}, 仪器误差: {instrument_error}", result)
            except ValueError:
                messagebox.showerror("输入错误", "请输入有效的仪器误差值。")

    def calculate_expression(self):
        expression = simpledialog.askstring("普通计算器", "请输入数学表达式（使用^表示指数）：")
        if expression:
            try:
                expression_eval = re.sub(r'\^', '**', expression)
                result = eval(expression_eval)
                result_str = f"计算结果：{result:.4f}"
                messagebox.showinfo("计算结果", result_str)
                self.add_record("普通计算器", expression, result_str)
            except (ValueError, SyntaxError, ZeroDivisionError) as e:
                messagebox.showerror("输入错误", "请输入有效的数学表达式。")


def open_calculator(root):
    top = tk.Toplevel(root)
    app = ExperimentDataProcessor(top)


if __name__ == "__main__":
    root = tk.Tk()
    app = ExperimentDataProcessor(root)
    root.mainloop()
