import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from matplotlib.image import AxesImage
from scipy import optimize
import tkinter.messagebox as messagebox
from pathlib import Path
import os
import logging
import datetime

# 调试日志配置 [DEBUG]标记方便后期删除
logging.basicConfig(
    level=logging.DEBUG,
    format='[DEBUG] %(asctime)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def debug_log(msg):
    """调试日志记录函数 [DEBUG]标记方便后期删除"""
    logger.debug(msg)

# [DEBUG] 添加调试信息函数
def debug_info(func_name, **kwargs):
    """[DEBUG] 记录函数调试信息"""
    debug_msg = f"[{func_name}] "
    for k, v in kwargs.items():
        debug_msg += f"{k}={v} "
    logger.debug(debug_msg)

# 设置中文显示
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

class ArcToCircle:
    def __init__(self):
        debug_log("初始化ArcToCircle类")  # [DEBUG]
        self.fig, self.ax = plt.subplots(figsize=(10, 8))
        debug_info("axes_initialized",
                   figure_size=self.fig.get_size_inches(),
                   axes_position=self.ax.get_position().bounds)  # [DEBUG] 记录坐标轴信息
        plt.subplots_adjust(bottom=0.2)
        self.image_path = None
        self.gray_image = None
        self.binary_image = None
        self.sampled_points = []  # 当前采样点
        self.temp_circle = None   # 当前临时圆（拟合中）
        self.confirmed_circles = []  # 已确认的圆
        self.base_center = None    # 基准圆心（用于同心圆）
        self.threshold = 30
        self.max_samples = 20

        # 半自动标记相关状态
        self.semi_auto_mode = False
        self.scan_paths = []  # 扫描路径 [(起点, 终点)]
        self.current_ring = 0  # 当前处理的牛顿环编号
        self.trigger_ready = False  # 标记触发准备状态
        self.is_scanning = False  # 标记是否处于扫描阶段

        # 新增：用于记录每个点的标记信息
        self.point_mark_info = []

        # 创建按钮
        self.ax_load = plt.axes([0.1, 0.05, 0.1, 0.075])
        self.ax_sample = plt.axes([0.21, 0.05, 0.12, 0.075])
        self.ax_concentric = plt.axes([0.34, 0.05, 0.12, 0.075])
        self.ax_semi_auto = plt.axes([0.47, 0.05, 0.12, 0.075])
        self.ax_save = plt.axes([0.6, 0.05, 0.1, 0.075])
        self.btn_load = Button(self.ax_load, '加载图像')
        self.btn_sample = Button(self.ax_sample, '添加采样点')
        self.btn_concentric = Button(self.ax_concentric, '确认同心圆')
        self.btn_semi_auto = Button(self.ax_semi_auto, '半自动标记')
        self.btn_save = Button(self.ax_save, '保存结果')

        self.btn_load.on_clicked(self.load_image)
        self.btn_sample.on_clicked(self.enable_sample_mode)
        self.btn_concentric.on_clicked(self.confirm_circle)
        self.btn_semi_auto.on_clicked(self.enable_semi_auto_mode)
        self.btn_save.on_clicked(self.save_results)

        self.ax.set_title('圆弧补全工具')
        plt.show()

    def load_image(self, event):
        """加载图像: 清除所有状态并加载新图像"""
        debug_log("开始加载图像")  # [DEBUG]
        from tkinter import filedialog

        try:
            root = filedialog.Tk()
            root.withdraw()
            self.image_path = filedialog.askopenfilename(
                title="选择图像文件",
                filetypes=[("图像文件", "*.jpg;*.jpeg;*.png")]
            )

            if not self.image_path:
                debug_log("用户取消选择图像")  # [DEBUG]
                return

            from PIL import Image
            debug_info("load_image", image_path=self.image_path)  # [DEBUG]
            img = np.array(Image.open(self.image_path).convert('RGB'))
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

            self.gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            _, self.binary_image = cv2.threshold(
                self.gray_image, 0, 255,
                cv2.THRESH_BINARY + cv2.THRESH_OTSU
            )

            # 重置所有状态
            self.ax.clear()
            self.sampled_points = []
            self.temp_circle = None
            self.confirmed_circles = []
            self.base_center = None
            # 新增：重置点标记信息
            self.point_mark_info = []

            # 显示图像
            self.ax.imshow(self.gray_image, cmap='gray')
            self.ax.set_title(f'已加载: {os.path.basename(self.image_path)}')
            self.initial_xlim = self.ax.get_xlim()
            self.initial_ylim = self.ax.get_ylim()
            self.fig.canvas.draw()
            debug_log("图像加载成功")  # [DEBUG]

        except Exception as e:
            debug_log(f"图像加载失败: {str(e)}")  # [DEBUG]
            messagebox.showerror("错误", f"图像加载失败:\n{str(e)}")

    def enable_sample_mode(self, event):
        """启用采样模式: 准备接收新的采样点"""
        debug_log("启用采样模式")  # [DEBUG]
        if not hasattr(self, 'gray_image'):
            debug_log("未加载图像，无法启用采样模式")  # [DEBUG]
            messagebox.showwarning("警告", "请先加载图像")
            return

        # 确保图像显示
        if not any(isinstance(artist, AxesImage) for artist in self.ax.get_children()):  # 修改这里
            self.ax.imshow(self.gray_image, cmap='gray')

        # 连接点击事件
        self.fig.canvas.mpl_connect('button_press_event', self.add_sample_point)
        debug_log("采样模式已启用，等待用户点击")  # [DEBUG]
        messagebox.showinfo("提示", "请点击图像添加采样点")

    def add_sample_point(self, event):
        """添加采样点: 根据点击位置添加点并实时更新圆"""
        debug_info("add_sample_point",
                   event_inaxes=event.inaxes,
                   has_gray_image=hasattr(self, 'gray_image'),
                   is_scanning=self.is_scanning)  # [DEBUG] 增加is_scanning状态

        if event.inaxes != self.ax:
            debug_info("click_outside_image",
                       click_coords=(event.xdata, event.ydata),
                       inaxes=str(event.inaxes),
                       expected_axes=str(self.ax))  # [DEBUG] 增加更详细的点击位置信息
            return

        if not hasattr(self, 'gray_image'):
            debug_log("未加载图像，拒绝添加采样点")  # [DEBUG] 更明确的拒绝原因
            messagebox.showwarning("操作拒绝", "请先加载图像后再添加采样点")
            return

        try:
            x, y = int(round(event.xdata)), int(round(event.ydata))
            debug_info("add_sample_point", click_coords=(x, y))  # [DEBUG]

            if x < 0 or y < 0 or x >= self.gray_image.shape[1] or y >= self.gray_image.shape[0]:
                debug_log(f"坐标超出范围: ({x},{y})")  # [DEBUG]
                return

            # 修改点1：增加对扫描模式的判断
            if hasattr(self, 'semi_auto_mode') and self.semi_auto_mode and hasattr(self, 'click_counter') and self.click_counter < 2 and not self.is_scanning:
                debug_log("半自动模式前两次点击(非扫描模式)，跳过采样")  # [DEBUG]
                self.click_counter += 1
                return

            # 扫描模式下生成1+4个点
            if self.is_scanning:
                debug_log("扫描模式下添加采样点")  # [DEBUG]
                # 1. 添加中心点
                self.sampled_points.append((x, y))
                self.ax.plot(x, y, 'ro', markersize=4)
                # 新增：记录中心点标记信息
                self.point_mark_info.append({'type': 'center', 'coords': (x, y)})

                # 2. 向四周发散4个边缘点
                directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
                for dx, dy in directions:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.gray_image.shape[1] and 0 <= ny < self.gray_image.shape[0]:
                        self.sampled_points.append((nx, ny))
                        self.ax.plot(nx, ny, 'ro', markersize=4)
                        # 新增：记录边缘点标记信息
                        self.point_mark_info.append({'type': 'edge', 'coords': (nx, ny), 'center': (x, y)})
            else:
                debug_log("普通模式下添加采样点")  # [DEBUG]
                # 普通模式下使用原有边缘检测逻辑
                self.sampled_points.append((x, y))
                self.ax.plot(x, y, 'ro', markersize=4)
                # 新增：记录中心点标记信息
                self.point_mark_info.append({'type': 'center', 'coords': (x, y)})

                L0 = int(self.gray_image[y, x])
                directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

                for dx, dy in directions:
                    nx, ny = x, y
                    while True:
                        nx += dx
                        ny += dy
                        if nx < 0 or ny < 0 or nx >= self.gray_image.shape[1] or ny >= self.gray_image.shape[0]:
                            break

                        L = int(self.gray_image[ny, nx])
                        if abs(L - L0) > self.threshold:
                            self.sampled_points.append((nx, ny))
                            self.ax.plot(nx, ny, 'ro', markersize=4)
                            # 新增：记录边缘点标记信息
                            self.point_mark_info.append({'type': 'edge', 'coords': (nx, ny), 'center': (x, y)})
                            break

            debug_info("add_sample_point", sampled_points_count=len(self.sampled_points))  # [DEBUG]
            # 新增：记录点标记信息数量
            debug_info("add_sample_point", point_mark_info_count=len(self.point_mark_info))

            # 实时更新圆
            self.update_circle()
            self.fig.canvas.draw()

        except Exception as e:
            debug_log(f"采样时出错: {str(e)}")  # [DEBUG]
            messagebox.showerror("错误", f"采样时出错:\n{str(e)}")

    def update_circle(self):
        """更新当前圆: 根据采样点拟合新圆"""
        debug_info("update_circle", sampled_points_count=len(self.sampled_points))  # [DEBUG]

        if len(self.sampled_points) < 3:  # 至少需要3个点
            debug_log("采样点不足3个，无法拟合圆")  # [DEBUG]
            return

        points = np.array(self.sampled_points)
        x = points[:, 0].astype(np.float64)
        y = points[:, 1].astype(np.float64)

        # 清除临时圆
        self.clear_temp_circle()

        # 拟合圆
        if self.base_center is None:
            debug_log("初始圆拟合(圆心和半径都变化)")  # [DEBUG]
            # 初始圆拟合（圆心和半径都变化）
            xc, yc, R = self.geometric_circle_fit(x, y)
        else:
            debug_log("同心圆模式(固定圆心，仅拟合半径)")  # [DEBUG]
            # 同心圆模式（固定圆心，仅拟合半径）
            xc, yc = self.base_center
            R = np.mean(np.sqrt((x - xc) ** 2 + (y - yc) ** 2))

        self.temp_circle = (xc, yc, R)
        debug_info("update_circle", temp_circle=self.temp_circle)  # [DEBUG]
        self.draw_temp_circle()

    def geometric_circle_fit(self, x, y):
        """几何圆拟合: 返回圆心(xc,yc)和半径R"""
        debug_log("开始几何圆拟合")  # [DEBUG]

        def calc_R(xc, yc):
            return np.sqrt((x - xc) ** 2 + (y - yc) ** 2)

        def error_func(c):
            Ri = calc_R(*c)
            return Ri - Ri.mean()

        # 初始猜测（使用代数法）
        A = np.vstack([x, y, np.ones(len(x))]).T
        b = x ** 2 + y ** 2
        c = np.linalg.lstsq(A, b, rcond=None)[0]
        xc_guess, yc_guess = c[0] / 2, c[1] / 2
        debug_info("geometric_circle_fit", initial_guess=(xc_guess, yc_guess))  # [DEBUG]

        # 优化圆心
        center, _ = optimize.leastsq(error_func, (xc_guess, yc_guess))
        xc, yc = center
        R = calc_R(xc, yc).mean()
        debug_info("geometric_circle_fit", fitted_circle=(xc, yc, R))  # [DEBUG]
        return xc, yc, R

    def clear_temp_circle(self):
        """清除临时圆: 移除绿色虚线和蓝色圆心标记"""
        debug_log("清除临时圆")  # [DEBUG]
        for line in self.ax.lines[:]:
            if (line.get_linestyle() == '--' and line.get_color() == 'g') or \
                    (line.get_marker() == 'x' and line.get_color() == 'b'):
                line.remove()

    def draw_temp_circle(self):
        """绘制临时圆: 绿色虚线圆和蓝色圆心标记"""
        debug_info("draw_temp_circle", temp_circle=self.temp_circle)  # [DEBUG]

        if not self.temp_circle:
            debug_log("没有临时圆需要绘制")  # [DEBUG]
            return

        xc, yc, R = self.temp_circle

        # 绘制圆
        theta = np.linspace(0, 2 * np.pi, 100)
        x = xc + R * np.cos(theta)
        y = yc + R * np.sin(theta)
        self.ax.plot(x, y, 'g--', linewidth=2)

        # 绘制圆心
        self.ax.plot(xc, yc, 'bx', markersize=10)

        # 更新标题显示误差
        points = np.array(self.sampled_points)
        distances = np.sqrt((points[:, 0] - xc) ** 2 + (points[:, 1] - yc) ** 2)
        error = np.mean(np.abs(distances - R))
        self.ax.set_title(f'当前圆 半径={R:.1f}px 误差={error:.2f}px')

        # 保持视图范围
        self.ax.set_xlim(self.initial_xlim)
        self.ax.set_ylim(self.initial_ylim)

    def confirm_circle(self, event):
        """确认同心圆: 将当前圆固定并准备绘制下一个同心圆"""
        debug_log("确认同心圆")  # [DEBUG]

        if not self.temp_circle:
            debug_log("没有临时圆可确认")  # [DEBUG]
            messagebox.showwarning("警告", "请先拟合圆")
            return

        # 如果是第一个圆，设置基准圆心
        if self.base_center is None:
            debug_log("设置基准圆心")  # [DEBUG]
            self.base_center = (self.temp_circle[0], self.temp_circle[1])

        # 保存当前圆
        self.confirmed_circles.append(self.temp_circle)
        debug_info("confirm_circle", confirmed_circles_count=len(self.confirmed_circles))  # [DEBUG]

        # 清除临时状态（保留已确认的圆）
        self.sampled_points = []
        self.temp_circle = None
        # 新增：可选择是否清空点标记信息，这里暂时不清空
        # self.point_mark_info = []

        # 重绘所有已确认的圆
        self.redraw_confirmed_circles()
        debug_log("同心圆已确认")  # [DEBUG]
        messagebox.showinfo("提示", "已确认当前圆，请添加新的采样点绘制同心圆")

    def redraw_confirmed_circles(self):
        """重绘所有已确认的圆: 确保它们始终可见"""
        debug_info("redraw_confirmed_circles", confirmed_circles_count=len(self.confirmed_circles))  # [DEBUG]

        # 清除所有内容（保留图像）
        self.ax.clear()
        if hasattr(self, 'gray_image'):
            self.ax.imshow(self.gray_image, cmap='gray')

        # 重绘所有已确认的圆
        for i, (xc, yc, R) in enumerate(self.confirmed_circles):
            theta = np.linspace(0, 2 * np.pi, 100)
            x = xc + R * np.cos(theta)
            y = yc + R * np.sin(theta)
            self.ax.plot(x, y, 'g-', linewidth=2)  # 实线表示已确认
            self.ax.plot(xc, yc, 'bx', markersize=10)

        # 恢复视图
        if hasattr(self, 'initial_xlim'):
            self.ax.set_xlim(self.initial_xlim)
            self.ax.set_ylim(self.initial_ylim)

        self.fig.canvas.draw()

    def enable_semi_auto_mode(self, event):
        """启用半自动标记模式"""
        debug_log("启用半自动标记模式")  # [DEBUG]

        if not hasattr(self, 'gray_image'):
            debug_log("未加载图像，无法启用半自动模式")  # [DEBUG]
            messagebox.showwarning("警告", "请先加载图像")
            return

        if self.base_center is None:
            debug_log("未设置基准圆心，无法启用半自动模式")  # [DEBUG]
            messagebox.showwarning("警告", "请先确定基准圆心")
            return

        # 确保断开所有现有点击事件
        self.fig.canvas.mpl_disconnect('button_press_event')

        # 设置半自动模式状态
        self.semi_auto_mode = True
        self.scan_paths = []
        self.current_ring = 0
        self.trigger_ready = False
        self.click_counter = 0  # 初始化点击计数器
        debug_info("enable_semi_auto_mode",
                   semi_auto_mode=self.semi_auto_mode,
                   base_center=self.base_center)  # [DEBUG]

        # 连接专用点击事件用于确定扫描路径
        self.scan_path_cid = self.fig.canvas.mpl_connect('button_press_event', self.set_scan_path)
        debug_log("等待用户设置扫描路径")  # [DEBUG]
        messagebox.showinfo("提示", "请在最外层牛顿环上点击两个点确定扫描路径")

    def set_scan_path(self, event):
        """用户手动设置扫描路径（起点和终点）"""
        debug_info("set_scan_path",
                   semi_auto_mode=self.semi_auto_mode,
                   event_inaxes=event.inaxes,
                   has_gray_image=hasattr(self, 'gray_image'))  # [DEBUG]

        if not self.semi_auto_mode or event.inaxes != self.ax or not hasattr(self, 'gray_image'):
            debug_log("无效的扫描路径设置请求")  # [DEBUG]
            return

        try:
            x, y = int(round(event.xdata)), int(round(event.ydata))
            debug_info("set_scan_path", click_coords=(x, y))  # [DEBUG]

            if x < 0 or y < 0 or x >= self.gray_image.shape[1] or y >= self.gray_image.shape[0]:
                debug_log(f"坐标超出范围: ({x},{y})")  # [DEBUG]
                return

            # 记录路径点（不参与拟合）
            if len(self.scan_paths) < 2:
                self.scan_paths.append((x, y))
                debug_info("set_scan_path", scan_paths=self.scan_paths)  # [DEBUG]
                # 绘制蓝色标记点(仅可视化，不加入采样点)
                point = self.ax.plot(x, y, 'bo', markersize=4, label='scan_path_point')
                self.fig.canvas.draw()

            # 第二个终点点击后，立即开始扫描
            if len(self.scan_paths) == 2:
                debug_log("扫描路径设置完成，开始扫描")  # [DEBUG]
                self.fig.canvas.mpl_disconnect(self.scan_path_cid)
                # 清除所有蓝色临时标记点
                for line in self.ax.lines[:]:
                    if line.get_label() == 'scan_path_point':
                        line.remove()
                self.fig.canvas.draw()
                self.is_scanning = True  # 进入扫描模式
                debug_info("start_scanning", scan_paths=self.scan_paths)  # [DEBUG]
                self.start_scanning()    # 启动自动扫描

        except Exception as e:
            debug_log(f"设置扫描路径时出错: {str(e)}")  # [DEBUG]
            messagebox.showerror("错误", f"设置扫描路径时出错:\n{str(e)}")

    def start_scanning(self):
        """沿两条路径扫描，生成模拟点击数据点"""
        debug_log("开始自动扫描")  # [DEBUG]
        self.sampled_points = []  # 清空旧数据
        self.is_scanning = True   # 标记扫描状态
        self.click_counter = 2    # 跳过前两次点击的限制 [MODIFIED]
        debug_info("start_scanning",
                   scan_paths=self.scan_paths,
                   is_scanning=self.is_scanning)  # [DEBUG]

        if len(self.scan_paths) != 2:
            pass  # 这里原代码未完成，可根据需求补充

    def save_results(self, event):
        """保存结果，可将点标记信息保存到文件"""
        import json
        try:
            with open('point_mark_info.json', 'w') as f:
                json.dump(self.point_mark_info, f, indent=4)
            messagebox.showinfo("提示", "点标记信息已保存到 point_mark_info.json")
        except Exception as e:
            messagebox.showerror("错误", f"保存点标记信息时出错:\n{str(e)}")

if __name__ == "__main__":
    app = ArcToCircle()