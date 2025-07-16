import base64
import os
from openai import OpenAI

# 初始化OpenAI客户端
client = OpenAI(
    api_key="2aa89cd6-014e-40e3-ac0a-1a45d6df0eae",  # 从环境变量获取API密钥
    base_url="https://ark.cn-beijing.volces.com/api/v3",  # API基础地址
)


def call_data_recognition_api(image_path):
    """调用视觉多模态API（图片识别）"""
    try:
        # 将本地图片转换为base64格式
        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode("utf-8")

        # 构造请求体，开启流式响应
        response = client.chat.completions.create(
            model="doubao-1-5-vision-pro-32k-250115",  # 模型名称
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text",
                         "text": "识别并提取图片中的实验数据，将其数字化。如果图片中包含科学仪器，也请识别并描述。回答中不要用到制表符。"},
                        # 文本提示
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"  # base64格式图片
                            },
                        },
                    ],
                }
            ],
            stream=True  # 开启流式响应
        )

        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content
    except Exception as e:
        # 处理API调用失败的情况
        yield f"API调用失败：{str(e)}"


def call_ai_assistant_api(query):
    """调用智能助手API（使用官方SDK）"""
    try:
        # 开启流式请求
        response = client.chat.completions.create(
            model="deepseek-v3-250324",  # 模型名称
            messages=[
                {"role": "system",
                 "content": "你是专注于物理实验辅助的通用计算助手，负责检查实验数据的合理性并进行计算。常见计算包括标准差、平均数、误差值等。如果不清楚计算内容，请向用户确认。尽量避免出现需要渲染的数学公式，最终计算结果要明显。回复保持简洁。"},
                # 系统提示
                {"role": "user", "content": query},  # 用户输入
            ],
            stream=True  # 开启流式响应
        )

        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content
    except Exception as e:
        # 处理API调用失败的情况
        yield f"API调用失败：{str(e)}"