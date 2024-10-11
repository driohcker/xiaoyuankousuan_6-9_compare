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
        self.root.bind('<Button-3>', self.quit)  # 右键点击退出
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

def preprocess_image(img):
    # 将图像转换为灰度图像
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # 进行二值化处理
    _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    return binary

def capture_text_from_region(region):
    # 截取屏幕
    screenshot = pyautogui.screenshot(region=region)
    # 格式化图片
    img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    # 处理图片
    processed_img = preprocess_image(img)
    # 设置 Tesseract 的配置，使用单个文本块识别模式
    text = pytesseract.image_to_string(processed_img, config='--psm 6')
    return text

# 比较两个数字并返回大小关系符号
def compare_numbers(text):
    # 使用正则表达式匹配数字
    numbers = re.findall(r'\d+', text)

    if len(numbers) < 2:
        return False
    else:
        print("比较结果：")
        if numbers[0] > numbers[1]:
            print("大于")
            pyautogui.press(".")
        elif numbers[0] < numbers[1]:
            print("小于")
            pyautogui.press(",")
        else:
            print("等于")
            pyautogui.press("=")
        return True

# 修改 main 函数逻辑，加入 text 变化检测和连续未找到计数
def main():
    print("请选择第一个区域用于识别内容，按鼠标右键确认选择")
    transparent_window_1 = TransparentWindow(prompt="选择第一个区域用于识别内容")
    transparent_window_1.run()

    x1, y1, width1, height1 = transparent_window_1.get_rect()
    region1 = (x1, y1, width1, height1)
    print(f"选择的第一个区域: {region1}")

    previous_text = ""  # 保存前一次的 text 值
    no_number_count = 0  # 记录连续未找到数字的次数
    time.sleep(1)

    try:
        while True:
            if keyboard.is_pressed('esc'):
                print("程序已终止。")
                break

            # 获取当前截取区域的 text
            current_text = capture_text_from_region(region1)
            print(f"识别的文字内容: {current_text.strip()}")

            # 检查文本变化
            if current_text != previous_text:
                # 文本变化时才比较数字
                if not compare_numbers(current_text):
                    no_number_count += 1
                    print(f"未找到数字可比较，连续未找到次数: {no_number_count}")
                else:
                    no_number_count = 0  # 重置计数器
                previous_text = current_text  # 更新为新的 text
            else:
                # 如果文本未变化，增加未找到数字计数
                no_number_count += 1
                print(f"文本未变化，连续未找到次数: {no_number_count}")

            # 如果连续五次未找到数字，按下 "c" 键
            if no_number_count >= 5:
                print("连续五次未找到数字，按下c键")
                pyautogui.press("c")
                no_number_count = 0  # 重置计数器

            time.sleep(0.5)
    except KeyboardInterrupt:
        print("程序已手动停止。")

if __name__ == "__main__":
    main()
