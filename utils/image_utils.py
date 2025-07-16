from PIL import Image, ImageEnhance

def process_image(image, value):
    """根据滑块值处理图片（示例：调整亮度）"""
    enhancer = ImageEnhance.Brightness(image)
    return enhancer.enhance(value / 100)
