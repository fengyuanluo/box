import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog
from PIL import Image, ImageTk
import os
import pyperclip


def save_last_used_background(file_path):
    # 保存当前使用的壁纸路径到程序所在目录
    current_directory = os.getcwd()
    with open(os.path.join(current_directory, 'background_path.txt'), 'w') as f:
        f.write(file_path)


def load_last_used_background():
    # 从程序所在目录加载上次使用的壁纸路径
    current_directory = os.getcwd()
    try:
        with open(os.path.join(current_directory, 'background_path.txt'), 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return None


def set_background_image():
    # 用户选择图片设置背景和保存路径
    file_path = filedialog.askopenfilename(
        title="选择背景图片",
        filetypes=[("Image files", "*.jpg *.jpeg *.png")]
    )
    if file_path:
        update_background(file_path)
        save_last_used_background(file_path)


def update_background(file_path=None):
    # 根据给定的文件路径更新背景，如果没有提供路径，那么尝试加载上次的背景
    if not file_path:
        file_path = load_last_used_background()
    if file_path:
        # 设置背景图片
        image = Image.open(file_path)
        image = image.resize((root.winfo_width(), root.winfo_height()), Image.Resampling.LANCZOS)
        bg_image = ImageTk.PhotoImage(image)
        background_label.config(image=bg_image)
        background_label.image = bg_image


def format_text():
    # 提取书摘的功能
    input_text = input_text_box.get("1.0", tk.END)
    lines = input_text.split('\n')

    # 标记是否开始遇到一个书摘段落
    in_excerpt = False
    formatted_lines = []

    for line in lines:
        if line.strip().startswith('▪'):
            in_excerpt = True
            line = line.strip()[1:].strip()
        elif line.strip().startswith('◆'):
            in_excerpt = False

        if in_excerpt:
            formatted_lines.append(line)

    formatted_text = "\n".join(formatted_lines)

    output_text_box.delete("1.0", tk.END)
    output_text_box.insert(tk.END, formatted_text)


def copy_to_clipboard():
    # 复制输出框的内容到剪贴板
    output_text = output_text_box.get("1.0", tk.END)
    pyperclip.copy(output_text)
    messagebox.showinfo("操作成功", "文本已复制到剪贴板")


root = tk.Tk()
root.title("沉浸式书摘提取工具")
root.geometry("800x400+100+100")
root.attributes('-alpha', 0.95)

background_label = tk.Label(root)
background_label.pack(fill=tk.BOTH, expand=True)

top_frame = tk.Frame(background_label)
top_frame.pack(side=tk.TOP, pady=5, expand=True, fill=tk.BOTH)

input_text_box = scrolledtext.ScrolledText(top_frame, wrap=tk.WORD, width=80, height=20)
input_text_box.pack(side=tk.LEFT, padx=10, pady=10)

output_text_box = scrolledtext.ScrolledText(top_frame, wrap=tk.WORD, width=80, height=20)
output_text_box.pack(side=tk.RIGHT, padx=10, pady=10)

button_frame = tk.Frame(background_label)
button_frame.pack(side=tk.TOP, pady=5)

extract_button = tk.Button(button_frame, text="提取书摘", command=format_text)
extract_button.pack(side=tk.LEFT, padx=5)

copy_button = tk.Button(button_frame, text="复制", command=copy_to_clipboard)
copy_button.pack(side=tk.LEFT, padx=5)

set_bg_button = tk.Button(button_frame, text="选择背景图片", command=set_background_image)
set_bg_button.pack(side=tk.LEFT, padx=5)

update_background()

root.mainloop()