import cv2
import pytesseract
import time
import numpy as np
import pyautogui
import tkinter as tk
import re
import keyboard  # 用于检测键盘按键

# 设置 Tesseract 的路径（根据你的安装路径进行修改）
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class TransparentWindow:
    def __init__(self, prompt=""):
        self.root = tk.Tk()
        self.root.attributes('-alpha', 0.3)  # 设置窗口透明度
        self.root.overrideredirect(True)  # 去掉窗口边框
        self.root.geometry(f"{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}+0+0")
        self.rect = (0, 0, 0, 0)
        self.drag_start = None
        self.canvas = tk.Canvas(self.root, bg='gray')
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind('<Button-1>', self.on_click)
        self.canvas.bind('<B1-Motion>', self.on_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_release)
        self.root.bind('<KeyPress-q>', self.quit)  # 按 'q' 键退出选择
        self.prompt = prompt
        self.text_id = None

    def on_click(self, event):
        self.drag_start = (event.x, event.y)

    def on_drag(self, event):
        if self.drag_start:
            self.rect = (self.drag_start[0], self.drag_start[1], event.x - self.drag_start[0], event.y - self.drag_start[1])
            self.canvas.delete('all')
            self.canvas.create_rectangle(self.rect[0], self.rect[1], self.rect[0] + self.rect[2], self.rect[1] + self.rect[3], outline='red', width=2)
            if self.text_id:
                self.canvas.delete(self.text_id)
            self.text_id = self.canvas.create_text(50, 10, anchor="nw", text=self.prompt, fill="black", font=("Arial", 16))

    def on_release(self, event):
        self.drag_start = None

    def quit(self, event=None):
        self.root.destroy()

    def get_rect(self):
        return self.rect

    def run(self):
        self.root.mainloop()

def capture_text_from_region(region):
    screenshot = pyautogui.screenshot(region=region)
    img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    text = pytesseract.image_to_string(img)
    return text

def calculate_expression(expression):
    expression = expression.replace('x', '*').replace('X', '*')
    match = re.match(r'([0-9\+\-\*/\.\s]+)=', expression)
    if match:
        try:
            result = eval(match.group(1))
            return result
        except Exception as e:
            print(f"无法计算表达式: {expression}")
            return None
    return None

# 数字轨迹定义 (每个数字由一系列鼠标移动坐标表示)
digit_paths = {
    '0': [(0, 0), (1, 0), (1, 1), (0, 1), (0 ,0)],  # 圆形轨迹
    '1': [(0.5, 0), (0.5, 1)],  # 直线
    '2': [(0, 0), (1, 0), (0, 1), (1, 1)],  # “2”的轨迹
    '3': [(0, 0), (1, 0.5), (0, 0.5), (1, 1), (0, 1)],  # “3”的轨迹
    '4': [(1, 1), (1, 0), (0, 0.5), (1, 0.5)],  # “4”的轨迹
    '5': [(1, 0), (0, 0), (1, 1), (0, 1)],  # “5”的轨迹
    '6': [(0.5, 0), (0, 0.5), (0.5, 1), (1, 0.5), (0, 0.5)],  # “6”的轨迹
    '7': [(0, 0), (1, 0), (1, 1)],  # “7”的轨迹
    '8': [(0, 0), (1, 0), (0, 1), (1, 1), (0, 0)],  # “8”的轨迹
    '9': [(1, 1), (1, 0), (0, 0), (1, 0.4)],  # “9”的轨迹
    '.': [(0.5, 1)], #"."的轨迹
}

def draw_large_text_in_region(region, text):
    start_x = region[0] + 50
    start_y = region[1] + 50
    font_size = 70  # 增大字体大小

    for char in text:
        if char in digit_paths:
            # 获取字符的轨迹并插值
            path = digit_paths[char]

            # 第一步：将鼠标移到字符起点的初始位置（不按下鼠标）
            pyautogui.moveTo(start_x + path[0][0] * font_size, start_y + path[0][1] * font_size, duration=0)  # 不延迟

            # 第二步：移动到字符的第一笔画开始点位，按下鼠标
            pyautogui.mouseDown()

            # 第三步：依次移动到路径中的每一个点，模拟书写过程
            for point in path:
                x = start_x + point[0] * font_size
                y = start_y + point[1] * font_size
                pyautogui.mouseDown()
                pyautogui.moveTo(x, y, duration=0.15)  # 将duration设置为0加速绘画

                pyautogui.mouseUp()

            # 第四步：完成当前字符的笔画，松开鼠标
            pyautogui.mouseUp()

        # 移动到下一个字符位置（开始新字符前，不连笔）
        start_x += font_size + 20

def main():
    print("请选择第一个区域用于识别内容，按回车键确认选择")
    transparent_window_1 = TransparentWindow(prompt="选择第一个区域用于识别内容")
    transparent_window_1.run()

    x1, y1, width1, height1 = transparent_window_1.get_rect()
    if width1 <= 0 or height1 <= 0:
        print("未选择有效区域。")
        return
    region1 = (x1, y1, width1, height1)
    print(f"选择的第一个区域: {region1}")

    print("请选择第二个区域用于绘制结果，按回车键确认选择")
    transparent_window_2 = TransparentWindow(prompt="选择第二个区域用于绘制结果")
    transparent_window_2.run()

    x2, y2, width2, height2 = transparent_window_2.get_rect()
    if width2 <= 0 or height2 <= 0:
        print("未选择有效区域。")
        return
    region2 = (x2, y2, width2, height2)
    print(f"选择的第二个区域: {region2}")

    try:
        while True:
            if keyboard.is_pressed('esc'):  # 检查是否按下了 Esc 键
                print("程序已终止。")
                break

            text = capture_text_from_region(region1)
            print(f"识别的文字内容: {text.strip()}")

            result = calculate_expression(text.strip())
            if result is not None:
                print(f"算式结果: {result}")
                draw_large_text_in_region(region2, str(result))

            print("按下 Enter 键继续识别...")
            keyboard.wait('enter')  # 等待按下 Enter 键以继续识别
    except KeyboardInterrupt:
        print("程序已手动停止。")


if __name__ == "__main__":
    #time.sleep(2)
    main()
