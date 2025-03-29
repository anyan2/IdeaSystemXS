import os
import tkinter as tk
from tkinter import filedialog, messagebox


def search_text_in_files(folder_path, search_text):
    results = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if search_text in content:
                        results.append(file_path)
            except Exception as e:
                print(f"读取文件 {file_path} 时出错: {e}")
    return results


def browse_folder():
    folder_path = filedialog.askdirectory()
    folder_entry.delete(0, tk.END)
    folder_entry.insert(0, folder_path)


def perform_search():
    folder_path = folder_entry.get()
    search_text = text_entry.get()
    if not folder_path or not search_text:
        messagebox.showerror("错误", "请输入文件夹路径和搜索文本！")
        return
    results = search_text_in_files(folder_path, search_text)
    if results:
        result_text.delete(1.0, tk.END)
        for result in results:
            result_text.insert(tk.END, f"{result}\n")
    else:
        messagebox.showinfo("结果", "未找到匹配内容。")


# 创建主窗口
root = tk.Tk()
root.title("文本搜索程序")

# 文件夹路径输入框和按钮
folder_label = tk.Label(root, text="文件夹路径:")
folder_label.pack()
folder_entry = tk.Entry(root, width=50)
folder_entry.pack()
browse_button = tk.Button(root, text="浏览", command=browse_folder)
browse_button.pack()

# 搜索文本输入框
text_label = tk.Label(root, text="搜索文本:")
text_label.pack()
text_entry = tk.Entry(root, width=50)
text_entry.pack()

# 搜索按钮
search_button = tk.Button(root, text="搜索", command=perform_search)
search_button.pack()

# 结果显示框
result_text = tk.Text(root, height=10, width=50)
result_text.pack()

# 运行主循环
root.mainloop()
    
