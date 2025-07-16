import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from scipy import optimize
import tkinter.messagebox as messagebox
from pathlib import Path
import os

# 设置中文显示
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']  # 备选字体
plt.rcParams['axes.unicode_minus'] = False

class ArcToCircle:
    def __init__(self):
        self.fig, self.ax = plt.subplots(figsize=(10, 8))
        plt.subplots_adjust(bottom=0.2)
        self.image_path = None
        self.gray_image = None
        self.binary_image = None
        self.sampled_points = []
        self.circle_params = None
        self.threshold = 30
        self.max_samples = 20
        self.current_click_handler = None
        
        # 创建中文按钮
        self.ax_load = plt.axes([0.2, 0.05, 0.1, 0.075])
        self.ax_sample = plt.axes([0.35, 0.05, 0.15, 0.075]) 
        self.ax_fit = plt.axes([0.55, 0.05, 0.1, 0.075])
        self.btn_load = Button(self.ax_load, '加载图像')
        self.btn_sample = Button(self.ax_sample, '添加采样点')
        self.btn_fit = Button(self.ax_fit, '拟合圆形')
        
        self.btn_load.on_clicked(self.load_image)
        self.btn_sample.on_clicked(self.enable_sample_mode)
        self.btn_fit.on_clicked(self.fit_circle)
        
        self.ax.set_title('圆弧补全工具')
        plt.show()
    
    def load_image(self, event):
        """改进的图像加载函数，完全支持中文路径"""
        from tkinter import filedialog
        
        try:
            # 使用Tkinter文件对话框
            root = filedialog.Tk()
            root.withdraw()
            self.image_path = filedialog.askopenfilename(
                title="选择图像文件",
                filetypes=[("图像文件", "*.jpg;*.jpeg;*.png")]
            )
            
            if not self.image_path:
                return
                
            # 使用PIL读取图像（解决OpenCV中文路径问题）
            from PIL import Image
            img = np.array(Image.open(self.image_path).convert('RGB'))
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            
            # 图像处理
            self.gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            _, self.binary_image = cv2.threshold(
                self.gray_image, 0, 255, 
                cv2.THRESH_BINARY+cv2.THRESH_OTSU
            )
            
            # 显示图像
            self.ax.clear()
            self.ax.imshow(self.gray_image, cmap='gray')
            self.ax.set_title(f'已加载: {os.path.basename(self.image_path)}')
            self.sampled_points = []
            self.fig.canvas.draw()
            
        except Exception as e:
            messagebox.showerror("错误", f"图像加载失败:\n{str(e)}")
    
    def enable_sample_mode(self, event):
        """启用采样模式"""
        if not hasattr(self, 'gray_image'):
            messagebox.showwarning("警告", "请先加载图像")
            return
            
        if self.current_click_handler:
            self.fig.canvas.mpl_disconnect(self.current_click_handler)
            
        self.current_click_handler = self.fig.canvas.mpl_connect(
            'button_press_event', self.add_sample_point
        )
        messagebox.showinfo("提示", "请在图像上点击选择采样点")
    
    def add_sample_point(self, event):
        """改进的采样点添加方法，解决数值溢出问题"""
        if event.inaxes != self.ax or not hasattr(self, 'gray_image'):
            return
            
        try:
            x, y = int(round(event.xdata)), int(round(event.ydata))
            if x < 0 or y < 0 or x >= self.gray_image.shape[1] or y >= self.gray_image.shape[0]:
                return
                
            L0 = int(self.gray_image[y, x])
            directions = [(1,0), (-1,0), (0,1), (0,-1)]
            
            for dx, dy in directions:
                nx, ny = x, y
                while True:
                    nx += dx
                    ny += dy
                    
                    # 边界检查
                    if nx < 0 or ny < 0 or nx >= self.gray_image.shape[1] or ny >= self.gray_image.shape[0]:
                        break
                        
                    # 安全计算亮度差
                    try:
                        L = int(self.gray_image[ny, nx])
                        if abs(int(L) - int(L0)) > self.threshold:
                            self.sampled_points.append((nx, ny))
                            self.ax.plot(nx, ny, 'ro', markersize=4)
                            self.fig.canvas.draw()
                            break
                    except:
                        break
                        
        except Exception as e:
            messagebox.showerror("错误", f"采样时出错:\n{str(e)}")
    
    def fit_circle(self, event):
        """圆拟合算法"""
        if len(self.sampled_points) < 5:
            messagebox.showwarning("警告", "采样点不足，至少需要5个点")
            return
            
        points = np.array(self.sampled_points)
        x = points[:, 0].astype(np.float64)  # 确保使用浮点数
        y = points[:, 1].astype(np.float64)
        
        # 代数法拟合
        def algebraic_circle_fit(x, y):
            A = np.vstack([x, y, np.ones(len(x))]).T
            b = x**2 + y**2
            c = np.linalg.lstsq(A, b, rcond=None)[0]
            xc = c[0]/2
            yc = c[1]/2
            R = np.sqrt(c[2] + xc**2 + yc**2)
            return xc, yc, R
        
        # 几何法拟合
        def geometric_circle_fit(x, y):
            def calc_R(xc, yc):
                return np.sqrt((x-xc)**2 + (y-yc)**2)
                
            def error_func(c):
                Ri = calc_R(*c)
                return Ri - Ri.mean()
                
            xc_guess, yc_guess, _ = algebraic_circle_fit(x, y)
            center, _ = optimize.leastsq(error_func, (xc_guess, yc_guess))
            xc, yc = center
            Ri = calc_R(xc, yc)
            R = Ri.mean()
            return xc, yc, R
        
        try:
            xc, yc, R = geometric_circle_fit(x, y)
            self.circle_params = (xc, yc, R)
            self.draw_circle()
        except Exception as e:
            messagebox.showerror("错误", f"拟合失败:\n{str(e)}")
    
    def draw_circle(self):
        """绘制拟合结果"""
        if not self.circle_params:
            return
            
        xc, yc, R = self.circle_params
        
        # 绘制完整圆
        theta = np.linspace(0, 2*np.pi, 100)
        x = xc + R * np.cos(theta)
        y = yc + R * np.sin(theta)
        self.ax.plot(x, y, 'g--', linewidth=2, label='拟合圆')
        
        # 绘制圆心
        self.ax.plot(xc, yc, 'bx', markersize=10, label='圆心')
        
        # 计算并显示误差
        points = np.array(self.sampled_points)
        distances = np.sqrt((points[:,0]-xc)**2 + (points[:,1]-yc)**2)
        error = np.mean(np.abs(distances - R))
        self.ax.set_title(f'拟合结果 半径={R:.1f}px 误差={error:.2f}px')
        
        self.ax.legend()
        self.fig.canvas.draw()

if __name__ == "__main__":
    try:
        app = ArcToCircle()
    except Exception as e:
        messagebox.showerror("程序错误", f"程序初始化失败:\n{str(e)}")
