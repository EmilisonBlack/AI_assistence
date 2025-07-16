import tkinter as tk
from tkinter import ttk, filedialog
from utils.api_utils import call_data_recognition_api  # API调用工具函数

class DataRecognitionFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        # 对话框
        self.dialog_frame = ttk.Frame(self)
        self.dialog_frame.pack(fill=tk.BOTH, expand=True)

        # 输入栏
        self.input_frame = ttk.Frame(self)
        self.input_frame.pack(fill=tk.X)

        # 上传图片按钮
        btn_upload = ttk.Button(self.input_frame, text="上传图片", command=self.upload_image)
        btn_upload.pack(side=tk.LEFT, padx=5, pady=5)

        # 发送按钮
        btn_send = ttk.Button(self.input_frame, text="发送", command=self.send_query)
        btn_send.pack(side=tk.RIGHT, padx=5, pady=5)

    def send_query(self):
        if hasattr(self, 'image_path'):
            response = call_data_recognition_api(self.image_path)
            for chunk in response:
                self.display_response(chunk)

    def display_response(self, response):
        # 在对话框中显示API返回的数据
        label = ttk.Label(self.dialog_frame, text=response)
        label.pack()
        self.dialog_frame.update_idletasks()  # 更新界面

    def display_response(self, response):
        # 在对话框中显示API返回的数据
        label = ttk.Label(self.dialog_frame, text=response)
        label.pack()
