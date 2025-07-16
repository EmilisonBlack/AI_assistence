import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import markdown  # 确保已安装markdown库: pip install markdown
from tkhtmlview import HTMLLabel
from utils.api_utils import call_data_recognition_api, call_ai_assistant_api
from calculator import open_calculator
from experiment_selection import ExperimentSelectionWindow
from drawing_interface import PlottingApp
from image_enhance import ImageEnhanceWindow
import threading
import time
from queue import Queue
import os

class MainApplication(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("大学物理实验工具V1.0")
        self.geometry("1200x700")
        self.configure(bg="#f0f0f0")

        # 用于存储当前HTML内容和消息历史
        self.data_recognition_html = ""
        self.ai_response_html = ""
        self.data_messages = []  # 存储图片识别对话历史
        self.ai_messages = []    # 存储AI助手对话历史

        # 双缓冲变量
        self.data_buffer = ""
        self.ai_buffer = ""
        
        # 消息队列用于线程间通信
        self.data_message_queue = Queue()
        self.ai_message_queue = Queue()
        
        # 上次更新时间
        self.last_data_update = 0
        self.last_ai_update = 0
        
        # 最小更新间隔（毫秒）
        self.MIN_UPDATE_INTERVAL = 100  

        # 标志变量，用于记录是否为第一次发送消息
        self.first_data_query = True
        self.first_ai_query = True

        # 当前处理状态
        self.is_processing_data = False
        self.is_processing_ai = False

        # 左侧工具栏
        self.toolbar = ttk.Frame(self, width=100, style="Toolbar.TFrame")
        self.toolbar.pack(side=tk.LEFT, fill=tk.Y)

        # 右侧主界面
        self.main_frame = ttk.Frame(self, style="MainFrame.TFrame")
        self.main_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # 初始化工具栏按钮
        self.init_toolbar()

        # 初始化主界面
        self.init_main_frame()

        # 设置样式
        self.init_styles()
        
        # 启动消息处理循环
        self.after(100, self.process_message_queues)

    def init_styles(self):
        # 自定义样式
        style = ttk.Style()
        style.configure("Toolbar.TFrame", background="#333333")
        style.configure("MainFrame.TFrame", background="#f0f0f0")
        # 修改按钮背景色为更深的蓝色，文字保持白色
        style.configure("Toolbar.TButton",
                        background="#2A4F7C",
                        foreground="#FFFFFF",
                        font=("Arial", 12, "bold"),
                        padding=8,
                        borderwidth=2,
                        relief="raised")
        # 按钮悬停状态样式
        style.map("Toolbar.TButton",
                  background=[('active', '#3A6F9C')],
                  relief=[('active', 'sunken')])
        style.configure("Dialog.TFrame", background="#f9f9f9")
        style.configure("Input.TFrame", background="#e0e0e0")
        # 添加用户消息和AI回复的样式
        style.configure("UserMessage.TLabel", background="#e6f7ff", foreground="#000000")
        style.configure("AIMessage.TLabel", background="#f0f0f0", foreground="#000000")

    def init_toolbar(self):
        # 新增选择实验按钮
        btn_select_experiment = ttk.Button(
            self.toolbar,
            text="选择实验",
            command=self.open_experiment_selection,
            style="Toolbar.TButton"
        )
        btn_select_experiment.pack(pady=10, padx=5, fill=tk.X)

        # 图片增强按钮
        btn_image_enhance = ttk.Button(
            self.toolbar,
            text="图片增强",
            command=self.open_image_enhance,
            style="Toolbar.TButton"
        )
        btn_image_enhance.pack(pady=10, padx=5, fill=tk.X)

        # 高级计算器按钮
        btn_advanced_calculator = ttk.Button(
            self.toolbar,
            text="高级计算器",
            command=lambda: open_calculator(self),
            style="Toolbar.TButton"
        )
        btn_advanced_calculator.pack(pady=10, padx=5, fill=tk.X)

        # 新增智能绘图按钮
        btn_smart_drawing = ttk.Button(
            self.toolbar,
            text="智能绘图",
            command=self.open_drawing_interface,
            style="Toolbar.TButton"
        )
        btn_smart_drawing.pack(pady=10, padx=5, fill=tk.X)

    def init_main_frame(self):
        # 分割主界面为左右两部分
        self.paned_window = ttk.PanedWindow(self.main_frame, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True)

        # 图片识别对话框
        self.data_recognition_frame = ttk.Frame(self.paned_window, style="Dialog.TFrame")
        self.paned_window.add(self.data_recognition_frame, weight=1)

        # 智能助手对话框
        self.ai_assistant_frame = ttk.Frame(self.paned_window, style="Dialog.TFrame")
        self.paned_window.add(self.ai_assistant_frame, weight=1)

        # 初始化图片识别和智能助手界面
        self.init_data_recognition()
        self.init_ai_assistant()

    def init_data_recognition(self):
        # 图片识别对话框布局
        dialog_label = ttk.Label(
            self.data_recognition_frame,
            text="AI图片识别-Vision-Pro-32K",
            font=("Arial", 12),
            background="#f9f9f9"
        )
        dialog_label.pack(pady=10)

        # 上传图片按钮
        btn_upload = ttk.Button(self.data_recognition_frame, text="添加图片", command=self.upload_image)
        btn_upload.pack(pady=10)

        # 显示识别结果的HTMLLabel
        self.data_recognition_text = HTMLLabel(
            self.data_recognition_frame,
            html="",
            height=8,
            font=("Arial", 10)
        )
        self.data_recognition_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # 输入框和发送按钮的容器
        self.data_input_frame = ttk.Frame(self.data_recognition_frame, style="Input.TFrame")
        self.data_input_frame.pack(fill=tk.X, padx=10, pady=10)

        # 输入框
        self.data_entry = tk.Text(
            self.data_input_frame,
            height=3,
            wrap=tk.WORD,
            font=("Arial", 12),
            width=30
        )
        self.data_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)

        # 添加滚动条
        data_scrollbar = ttk.Scrollbar(
            self.data_input_frame,
            orient=tk.VERTICAL,
            command=self.data_entry.yview
        )
        data_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.data_entry.config(yscrollcommand=data_scrollbar.set)

        # 发送按钮
        btn_send = ttk.Button(self.data_input_frame, text="发送", command=self.send_data_query)
        btn_send.pack(side=tk.RIGHT, padx=5, pady=5)

    def init_ai_assistant(self):
        # 智能助手对话框布局
        dialog_label = ttk.Label(
            self.ai_assistant_frame,
            text="通用智能助手-Deepseek-V3",
            font=("Arial", 12),
            background="#f9f9f9"
        )
        dialog_label.pack(pady=10)

        # 显示助手回复的HTMLLabel
        self.ai_response_text = HTMLLabel(
            self.ai_assistant_frame,
            html="",
            height=15,
            font=("Arial", 10)
        )
        self.ai_response_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 输入框和发送按钮的容器
        self.ai_input_frame = ttk.Frame(self.ai_assistant_frame, style="Input.TFrame")
        self.ai_input_frame.pack(fill=tk.X, padx=10, pady=10)

        # 输入框
        self.ai_entry = tk.Text(
            self.ai_input_frame,
            height=3,
            wrap=tk.WORD,
            font=("Arial", 12),
            width=30
        )
        self.ai_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)

        # 添加滚动条
        ai_scrollbar = ttk.Scrollbar(
            self.ai_input_frame,
            orient=tk.VERTICAL,
            command=self.ai_entry.yview
        )
        ai_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.ai_entry.config(yscrollcommand=ai_scrollbar.set)

        # 发送按钮
        btn_send = ttk.Button(self.ai_input_frame, text="发送", command=self.send_ai_query)
        btn_send.pack(side=tk.RIGHT, padx=5, pady=5)

    def upload_image(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.image_path = file_path
            self.process_image_recognition(file_path)

    def process_image_recognition(self, file_path):
        if self.is_processing_data:
            return  # 正在处理中，不重复处理
        
        self.is_processing_data = True
        self.data_recognition_html = ""
        
        # 添加用户消息到历史
        user_message = f"用户：上传了图片 {os.path.basename(file_path)}"
        self.data_messages.append({"role": "user", "content": user_message})
        self.update_data_display(force=True)
        
        # 开始流式响应
        threading.Thread(target=self._process_image_recognition_thread, args=(file_path,)).start()

    def _process_image_recognition_thread(self, file_path):
        try:
            # 创建新的AI回复容器
            self.current_ai_response = ""
            self.data_messages.append({"role": "ai", "content": ""})
            
            for chunk in call_data_recognition_api(file_path):
                self.current_ai_response += chunk
                # 更新最后一条消息
                self.data_messages[-1]["content"] = self.current_ai_response
                # 将更新请求放入队列，而不是直接更新
                self.data_message_queue.put("update")
                time.sleep(0.01)  # 控制更新频率
                
            # 处理完成，强制更新一次
            self.data_message_queue.put("update_force")
                
        except Exception as e:
            error_msg = f"处理出错: {str(e)}"
            self.data_messages.append({"role": "system", "content": error_msg})
            self.data_message_queue.put("update_force")
        finally:
            self.is_processing_data = False

    def send_data_query(self):
        query = self.data_entry.get("1.0", tk.END).strip()
        if query and hasattr(self, 'image_path'):
            self.process_image_recognition(self.image_path)
            self.data_entry.delete("1.0", tk.END)

    def send_ai_query(self):
        query = self.ai_entry.get("1.0", tk.END).strip()
        if query:
            if self.is_processing_ai:
                return  # 正在处理中，不重复处理
                
            self.is_processing_ai = True
            self.ai_response_html = ""
            
            # 添加用户消息到历史
            user_message = f"用户：{query}"
            self.ai_messages.append({"role": "user", "content": user_message})
            self.update_ai_display(force=True)
            
            # 开始流式响应
            threading.Thread(target=self._process_ai_response_thread, args=(query,)).start()
            self.ai_entry.delete("1.0", tk.END)

    def _process_ai_response_thread(self, query):
        try:
            # 创建新的AI回复容器
            self.current_ai_response = ""
            self.ai_messages.append({"role": "ai", "content": ""})
            
            for chunk in call_ai_assistant_api(query):
                self.current_ai_response += chunk
                # 更新最后一条消息
                self.ai_messages[-1]["content"] = self.current_ai_response
                # 将更新请求放入队列
                self.ai_message_queue.put("update")
                time.sleep(0.01)  # 控制更新频率
                
            # 处理完成，强制更新一次
            self.ai_message_queue.put("update_force")
                
        except Exception as e:
            error_msg = f"处理出错: {str(e)}"
            self.ai_messages.append({"role": "system", "content": error_msg})
            self.ai_message_queue.put("update_force")
        finally:
            self.is_processing_ai = False

    def update_data_display(self, force=False):
        current_time = time.time() * 1000  # 转换为毫秒
        
        # 如果不是强制更新，检查是否达到最小更新间隔
        if not force and (current_time - self.last_data_update < self.MIN_UPDATE_INTERVAL):
            return
            
        self.last_data_update = current_time
        
        # 构建HTML内容，区分不同消息
        html = ""
        for message in self.data_messages:
            if message["role"] == "user":
                html += f'<div style="background-color: #e6f7ff; padding: 8px; margin: 5px; border-radius: 5px;">'
                html += f'<p style="font-weight: bold; margin: 0;">用户</p>'
                html += f'<p style="margin: 0;">{message["content"]}</p>'
                html += '</div>'
            elif message["role"] == "ai":
                # 将Markdown转换为HTML
                markdown_content = message["content"]
                html_content = markdown.markdown(markdown_content)
                
                html += f'<div style="background-color: #f0f0f0; padding: 8px; margin: 5px; border-radius: 5px;">'
                html += f'<p style="font-weight: bold; margin: 0;">AI</p>'
                html += f'<div style="margin: 0;">{html_content}</div>'
                html += '</div>'
            elif message["role"] == "system":
                html += f'<div style="background-color: #ffe6e6; padding: 8px; margin: 5px; border-radius: 5px;">'
                html += f'<p style="font-weight: bold; margin: 0;">系统</p>'
                html += f'<p style="margin: 0;">{message["content"]}</p>'
                html += '</div>'
        
        self.data_recognition_html = html
        
        # 使用双缓冲技术减少闪烁
        self.data_buffer = html
        self.data_recognition_text.set_html(self.data_buffer)
        self.update_idletasks()

    def update_ai_display(self, force=False):
        current_time = time.time() * 1000  # 转换为毫秒
        
        # 如果不是强制更新，检查是否达到最小更新间隔
        if not force and (current_time - self.last_ai_update < self.MIN_UPDATE_INTERVAL):
            return
            
        self.last_ai_update = current_time
        
        # 构建HTML内容，区分不同消息
        html = ""
        for message in self.ai_messages:
            if message["role"] == "user":
                html += f'<div style="background-color: #e6f7ff; padding: 8px; margin: 5px; border-radius: 5px;">'
                html += f'<p style="font-weight: bold; margin: 0;">用户</p>'
                html += f'<p style="margin: 0;">{message["content"]}</p>'
                html += '</div>'
            elif message["role"] == "ai":
                # 将Markdown转换为HTML
                markdown_content = message["content"]
                html_content = markdown.markdown(markdown_content)
                
                html += f'<div style="background-color: #f0f0f0; padding: 8px; margin: 5px; border-radius: 5px;">'
                html += f'<p style="font-weight: bold; margin: 0;">AI</p>'
                html += f'<div style="margin: 0;">{html_content}</div>'
                html += '</div>'
            elif message["role"] == "system":
                html += f'<div style="background-color: #ffe6e6; padding: 8px; margin: 5px; border-radius: 5px;">'
                html += f'<p style="font-weight: bold; margin: 0;">系统</p>'
                html += f'<p style="margin: 0;">{message["content"]}</p>'
                html += '</div>'
        
        self.ai_response_html = html
        
        # 使用双缓冲技术减少闪烁
        self.ai_buffer = html
        self.ai_response_text.set_html(self.ai_buffer)
        self.update_idletasks()

    def process_message_queues(self):
        # 处理数据识别消息队列
        while not self.data_message_queue.empty():
            msg = self.data_message_queue.get()
            if msg == "update":
                self.update_data_display(force=False)
            elif msg == "update_force":
                self.update_data_display(force=True)
        
        # 处理AI助手消息队列
        while not self.ai_message_queue.empty():
            msg = self.ai_message_queue.get()
            if msg == "update":
                self.update_ai_display(force=False)
            elif msg == "update_force":
                self.update_ai_display(force=True)
        
        # 继续循环处理消息
        self.after(50, self.process_message_queues)

    def open_image_enhance(self):
        ImageEnhanceWindow(self)

    def open_experiment_selection(self):
        ExperimentSelectionWindow(self)

    def open_drawing_interface(self):
        try:
            PlottingApp(self)
        except Exception as e:
            messagebox.showerror("错误", f"打开智能绘图窗口时出错: {e}")


if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()