import tkinter as tk
from tkinter import messagebox
import numpy as np
from scipy.interpolate import make_interp_spline
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.widgets import Cursor
from matplotlib.offsetbox import AnnotationBbox, TextArea


class PlottingApp:
    def __init__(self, root):
        # 设置 matplotlib 支持中文
        plt.rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体字体，可根据系统情况调整
        plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

        # 创建一个新的 Toplevel 窗口
        self.window = tk.Toplevel(root)
        self.window.title("数据绘图工具")

        # 输入框和标签
        tk.Label(self.window, text="X坐标 (用空格分隔，未知数据用 + 替代):").pack(pady=5)
        self.x_entry = tk.Entry(self.window, width=50)
        self.x_entry.pack(pady=5)

        tk.Label(self.window, text="Y坐标 (用空格分隔，未知数据用 + 替代):").pack(pady=5)
        self.y_entry = tk.Entry(self.window, width=50)
        self.y_entry.pack(pady=5)

        # 创建按钮框架
        self.button_frame1 = tk.Frame(self.window)
        self.button_frame1.pack(pady=5)
        self.button_frame2 = tk.Frame(self.window)
        self.button_frame2.pack(pady=5)

        # 第一行按钮
        draw_points_button = tk.Button(self.button_frame1, text="绘制数据点", command=self.draw_points,
                                     fg="white", bg="#4a7dff", font=("Microsoft YaHei", 10, "bold"))
        draw_points_button.pack(side=tk.LEFT, padx=5)

        # 第二行按钮 (拟合按钮)
        self.linear_fit_button = tk.Button(self.button_frame2, text="直线拟合", command=self.toggle_linear_fit,
                                         fg="white", bg="#4a7dff", font=("Microsoft YaHei", 10, "bold"))
        self.linear_fit_button.pack(side=tk.LEFT, padx=5)

        self.curve_fit_button = tk.Button(self.button_frame2, text="曲线拟合", command=self.toggle_curve_fit,
                                        fg="white", bg="#4a7dff", font=("Microsoft YaHei", 10, "bold"))
        self.curve_fit_button.pack(side=tk.LEFT, padx=5)

        # 第三行按钮 (图表类型)
        self.button_frame3 = tk.Frame(self.window)
        self.button_frame3.pack(pady=5)
        
        self.scatter_button = tk.Button(self.button_frame3, text="散点图", 
                                      command=lambda: self.set_chart_type('scatter'),
                                      fg="white", bg="#4a7dff", font=("Microsoft YaHei", 10, "bold"))
        self.scatter_button.pack(side=tk.LEFT, padx=5)
        
        self.bar_button = tk.Button(self.button_frame3, text="柱状图", 
                                  command=lambda: self.set_chart_type('bar'),
                                  fg="white", bg="#4a7dff", font=("Microsoft YaHei", 10, "bold"))
        self.bar_button.pack(side=tk.LEFT, padx=5)
        
        self.pie_button = tk.Button(self.button_frame3, text="饼状图", 
                                  command=lambda: self.set_chart_type('pie'),
                                  fg="white", bg="#4a7dff", font=("Microsoft YaHei", 10, "bold"))
        self.pie_button.pack(side=tk.LEFT, padx=5)

        # 创建 matplotlib 图形和坐标轴
        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.window)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # 创建 Annotation 对象用于显示坐标
        self.annotation = None
        self.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)

        # 创建十字光标
        self.cursor = Cursor(self.ax, useblit=True, color='red', linewidth=0.5)

        # 记录原始数据点和拟合状态
        self.raw_x = None
        self.raw_y = None
        self.linear_fit_line = None
        self.curve_fit_line = None
        self.show_linear_fit = False
        self.show_curve_fit = False
        self.chart_type = 'scatter'  # 默认散点图

    def process_input(self):
        """处理用户输入数据
        输入参数: 无
        返回值: (x, y) - 处理后的数据点数组，或 (None, None) 如果输入无效
        功能描述: 从输入框获取数据并处理成可用的数值数组
        """
        try:
            x_str = self.x_entry.get()
            y_str = self.y_entry.get()
            x_data = x_str.split()
            y_data = y_str.split()

            if len(x_data) != len(y_data):
                messagebox.showerror("输入错误", "X 和 Y 坐标的数据量必须相等。")
                return None, None

            x = []
            y = []
            for i in range(len(x_data)):
                if x_data[i] != '+' and y_data[i] != '+':
                    x.append(float(x_data[i]))
                    y.append(float(y_data[i]))

            if len(x) < 2:
                messagebox.showerror("输入错误", "有效数据点不足，无法绘图。")
                return None, None

            return np.array(x), np.array(y)
        except ValueError as e:
            messagebox.showerror("输入错误", f"输入数据格式错误: {e}")
            return None, None

    def draw_points(self):
        """绘制原始数据点
        输入参数: 无
        返回值: 无
        功能描述: 清除图形并绘制原始数据点
        """
        try:
            x, y = self.process_input()
            if x is None or y is None:
                return

            self.raw_x, self.raw_y = x, y
            self.redraw_plot()
        except Exception as e:
            messagebox.showerror("绘图错误", f"绘制数据点时出现错误: {e}")

    def toggle_linear_fit(self):
        """切换直线拟合显示状态
        输入参数: 无
        返回值: 无
        功能描述: 切换直线拟合的显示/隐藏状态
        """
        if self.raw_x is None or self.raw_y is None:
            messagebox.showwarning("警告", "请先绘制数据点")
            return

        self.show_linear_fit = not self.show_linear_fit
        self.redraw_plot()

    def toggle_curve_fit(self):
        """切换曲线拟合显示状态
        输入参数: 无
        返回值: 无
        功能描述: 切换曲线拟合的显示/隐藏状态
        """
        if self.raw_x is None or self.raw_y is None:
            messagebox.showwarning("警告", "请先绘制数据点")
            return

        self.show_curve_fit = not self.show_curve_fit
        self.redraw_plot()

    def set_chart_type(self, chart_type):
        """设置图表类型
        输入参数: chart_type - 图表类型字符串 ('scatter', 'bar', 'pie')
        返回值: 无
        功能描述: 设置当前图表类型并重绘
        """
        self.chart_type = chart_type
        self.redraw_plot()

    def draw_bar_chart(self):
        """绘制柱状图
        输入参数: 无
        返回值: 无
        功能描述: 根据当前数据绘制柱状图
        """
        if len(self.raw_x) != len(self.raw_y):
            messagebox.showerror("错误", "X和Y数据数量不匹配")
            return

        # 使用X值作为标签，Y值作为高度
        self.ax.bar(range(len(self.raw_x)), self.raw_y, tick_label=self.raw_x)
        self.ax.set_xlabel('类别')
        self.ax.set_ylabel('数值')

    def draw_pie_chart(self):
        """绘制饼状图
        输入参数: 无
        返回值: 无
        功能描述: 根据当前数据绘制饼状图
        """
        if len(self.raw_x) != len(self.raw_y):
            messagebox.showerror("错误", "X和Y数据数量不匹配")
            return

        # 使用X值作为标签，Y值作为大小
        self.ax.pie(self.raw_y, labels=self.raw_x, autopct='%1.1f%%')
        self.ax.axis('equal')  # 保证饼图是圆形

    def redraw_plot(self):
        """重绘整个图形
        输入参数: 无
        返回值: 无
        功能描述: 根据当前设置重绘所有可见元素
        """
        self.ax.clear()

        if self.raw_x is None or self.raw_y is None:
            self.canvas.draw()
            return

        # 根据图表类型绘制
        if self.chart_type == 'scatter':
            self.ax.scatter(self.raw_x, self.raw_y, color='b', label='数据点')
            
            # 绘制直线拟合
            if self.show_linear_fit:
                A = np.vstack([self.raw_x, np.ones(len(self.raw_x))]).T
                m, c = np.linalg.lstsq(A, self.raw_y, rcond=None)[0]
                x_min = self.raw_x.min()
                x_max = self.raw_x.max()
                y_min = m * x_min + c
                y_max = m * x_max + c
                self.ax.plot([x_min, x_max], [y_min, y_max], 'r-', label='直线拟合')

            # 绘制曲线拟合
            if self.show_curve_fit:
                x_new = np.linspace(self.raw_x.min(), self.raw_x.max(), 300)
                spl = make_interp_spline(self.raw_x, self.raw_y, k=3)
                y_new = spl(x_new)
                self.ax.plot(x_new, y_new, 'g-', label='曲线拟合')

        elif self.chart_type == 'bar':
            self.draw_bar_chart()
        elif self.chart_type == 'pie':
            self.draw_pie_chart()

        # 更新图例和画布
        if self.chart_type == 'scatter':
            self.ax.legend()
        self.canvas.draw()

    def on_mouse_move(self, event):
        """鼠标移动事件处理
        输入参数: event - 鼠标事件对象
        返回值: 无
        功能描述: 在鼠标位置显示当前坐标
        """
        if event.inaxes == self.ax:
            x, y = event.xdata, event.ydata
            if self.annotation is not None:
                self.annotation.remove()
            if x is not None and y is not None:
                # 创建文本区域
                text_area = TextArea(f'({x:.2f}, {y:.2f})', textprops=dict(color='black'))
                # 创建 AnnotationBbox
                self.annotation = AnnotationBbox(text_area, (x, y),
                                                 xybox=(30, 30),
                                                 xycoords='data',
                                                 boxcoords="offset points",
                                                 arrowprops=dict(arrowstyle="->"))
                self.ax.add_artist(self.annotation)
                self.canvas.draw_idle()
        else:
            if self.annotation is not None:
                self.annotation.remove()
                self.annotation = None
                self.canvas.draw_idle()
