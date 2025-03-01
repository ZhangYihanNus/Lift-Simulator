import tkinter as tk
from tkinter import messagebox

# 定义主应用程序类
class LiftSimulatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Lift Simulator")  # 设置窗口标题
        self.root.geometry("1000x600")  # 设置窗口大小为1000x600

        # 创建主框架，用于布局
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # 创建两个并列的文本区域
        self.label_abc = tk.Label(self.main_frame, text="ABC", font=("Arial", 24))
        self.label_abc.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        self.label_def = tk.Label(self.main_frame, text="def", font=("Arial", 24))
        self.label_def.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        # 创建文本输入区域
        self.input_entry = tk.Entry(self.main_frame, width=50, font=("Arial", 16))
        self.input_entry.grid(row=1, column=0, columnspan=2, padx=20, pady=20, sticky="ew")

        # 创建确认按钮
        self.confirm_button = tk.Button(
            self.main_frame, text="Confirm", font=("Arial", 20), command=self.on_confirm, height=3
        )
        self.confirm_button.grid(row=2, column=0, columnspan=2, padx=20, pady=20, sticky="ew")

        # 创建Next tick按钮
        self.next_tick_button = tk.Button(
            self.main_frame, text="Next tick", font=("Arial", 20), command=self.on_next_tick, height=3
        )
        self.next_tick_button.grid(row=3, column=0, columnspan=2, padx=20, pady=20, sticky="ew")

        # 配置网格布局的权重，使内容居中
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_rowconfigure(2, weight=1)
        self.main_frame.grid_rowconfigure(3, weight=1)

        # 绑定窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    # 确认按钮的回调函数
    def on_confirm(self):
        user_input = self.input_entry.get()
        if user_input:
            messagebox.showinfo("Input Received", f"You entered: {user_input}")
        else:
            messagebox.showwarning("No Input", "Please enter something!")

    # Next tick按钮的回调函数
    def on_next_tick(self):
        print("Next tick clicked")  # 这里可以替换为实际的逻辑

    # 窗口关闭的回调函数
    def on_close(self):
        self.root.destroy()
        # if messagebox.askokcancel("Quit", "Do you want to quit?"):
        #     self.root.destroy()

# 主程序入口
if __name__ == "__main__":
    root = tk.Tk()
    app = LiftSimulatorApp(root)
    root.mainloop()  # 进入主事件循环