import tkinter as tk
from tkinter import ttk, scrolledtext
from utils.api_utils import call_ai_assistant_api  # API调用工具函数
import markdown
from tkhtmlview import HTMLLabel

class AIAssistantFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        # 对话框
        self.dialog_frame = ttk.Frame(self)
        self.dialog_frame.pack(fill=tk.BOTH, expand=True)

        # 显示回复的滚动文本框
        self.response_text = HTMLLabel(self.dialog_frame, html="", height=15, font=("Arial", 10))
        self.response_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 输入栏
        self.input_frame = ttk.Frame(self)
        self.input_frame.pack(fill=tk.X)

        # 输入框
        self.entry = tk.Text(self.input_frame, height=3, wrap=tk.WORD, font=("Arial", 12), width=30)
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)

        # 添加滚动条
        scrollbar = ttk.Scrollbar(self.input_frame, orient=tk.VERTICAL, command=self.entry.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.entry.config(yscrollcommand=scrollbar.set)

        # 发送按钮
        btn_send = ttk.Button(self.input_frame, text="发送", command=self.send_query)
        btn_send.pack(side=tk.RIGHT, padx=5, pady=5)

    def send_query(self):
        query = self.entry.get("1.0", tk.END).strip()  # 获取输入框内容
        if query:
            response = call_ai_assistant_api(query)
            html_response = markdown.markdown(response)
            self.display_response(html_response)
            self.entry.delete("1.0", tk.END)  # 清空输入框

    def display_response(self, response):
        # 在对话框中显示API返回的数据
        current_html = self.response_text.html
        new_html = current_html + response
        self.response_text.set_html(new_html)
        self.dialog_frame.update_idletasks()  # 更新界面
