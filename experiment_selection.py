import tkinter as tk
from tkinter import ttk

class ExperimentSelectionWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("选择实验")
        self.geometry("400x300")
        self.configure(bg="#f0f0f0")  # 设置背景颜色

        # 添加实验选择按钮
        button1 = ttk.Button(self, text="拉伸法测金属丝杨氏模量", command=self.open_metal_modulus_experiment)  # MODIFIED: 修改按钮文本
        button1.pack(pady=20)
        
        button2 = ttk.Button(self, text="牛顿环法测透镜曲率半径", command=self.open_newton_rings_experiment)  # MODIFIED: 修改按钮文本
        button2.pack(pady=20)
        
        button3 = ttk.Button(self, text="转动定律和转动惯量验证", command=self.open_rotation_experiment)  # MODIFIED: 新增按钮
        button3.pack(pady=20)

    def open_metal_modulus_experiment(self):
        """函数模块名称: 打开金属丝杨氏模量实验窗口
        输入参数: 无
        返回值: 无
        功能描述: 导入并打开金属丝杨氏模量实验界面
        """
        from experiment_folders.metal_modulus_experiment.metal_modulus_experiment import MetalModulusExperimentWindow
        MetalModulusExperimentWindow(self)

    def open_newton_rings_experiment(self):
        """函数模块名称: 打开牛顿环实验窗口
        输入参数: 无
        返回值: 无
        功能描述: 导入并打开牛顿环法测透镜曲率半径实验界面
        """
        from experiment_folders.newton_rings_experiment.newton_rings_experiment import NewtonRingsExperimentWindow
        NewtonRingsExperimentWindow(self)
        
    def open_rotation_experiment(self):  # MODIFIED: 新增函数
        """函数模块名称: 打开转动定律实验窗口
        输入参数: 无
        返回值: 无
        功能描述: 导入并打开转动定律和转动惯量验证实验界面
        """
        from experiment_folders.rotation_experiment.rotation_experiment import RotationExperimentWindow
        RotationExperimentWindow(self)


if __name__ == "__main__":
    root = tk.Tk()
    app = ExperimentSelectionWindow(root)
    root.mainloop()
