import tkinter as tk
from tkinter import messagebox
from game.game import Game
from dqn_agent import DQNAgent
import time
import threading
import ctypes

class GameGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Push&Pop")
        self.root.configure(bg="#2b2b2b")  # 设置背景色

        self.game = Game()
        self.game.board_init_rand()
        self.board_size = self.game.board_size

        # 加载图片并调整大小
        self.image_size = 60  # 每个单元格图片的大小
        self.images = [
            tk.PhotoImage(file=f"./assets/images/notion_{i}.png")
            for i in range(len(self.game.notion))
        ]

        # DQN Agent 初始化
        self.agent = DQNAgent(self.game.board_size, input_channels=7, action_size=4)
        self.agent.multi_channel_init(self.game.board_size, len(self.game.notion))

        # 状态
        self.running = False
        self.delay = 0.5  # 默认时延

        # 主框架：左侧和右侧
        self.main_frame = tk.Frame(self.root, bg="#2b2b2b")
        self.main_frame.pack(fill="both", expand=True)

        # 左侧框架
        self.left_frame = tk.Frame(self.main_frame, bg="#2b2b2b", padx=10, pady=10)
        self.left_frame.pack(side="left", fill="both", expand=True)

        # 右侧框架 (Agent Log)
        self.right_frame = tk.Frame(self.main_frame, bg="#2b2b2b", padx=10, pady=10)
        self.right_frame.pack(side="right", fill="y")

        # 分数与步数
        self.info_frame = tk.Frame(self.left_frame, bg="#2b2b2b")
        self.info_frame.pack(pady=10)

        self.score_label = tk.Label(
            self.info_frame,
            text="Score: 0",
            font=("Helvetica", 7),
            bg="#2b2b2b",
            fg="#ffffff",
        )
        self.score_label.pack(side="left", padx=20)
        self.step_label = tk.Label(
            self.info_frame,
            text="Step: 0",
            font=("Helvetica", 7),
            bg="#2b2b2b",
            fg="#ffffff",
        )
        self.step_label.pack(side="left", padx=20)

        # 游戏网格
        self.grid_frame = tk.Frame(self.left_frame, bg="#2b2b2b")
        self.grid_frame.pack(fill="both", expand=True)
        self.cells = []
        for row in range(self.board_size):
            row_cells = []
            for col in range(self.board_size):
                canvas = tk.Canvas(
                    self.grid_frame,
                    width=self.image_size,
                    height=self.image_size,
                    bg="#444444",
                    highlightthickness=2,
                    highlightbackground="#2b2b2b",
                )
                canvas.grid(row=row, column=col, padx=0, pady=0, sticky="nsew")
                row_cells.append(canvas)
            self.cells.append(row_cells)

        # 让网格始终保持正方形
        for i in range(self.board_size):
            self.grid_frame.grid_rowconfigure(i, weight=0, uniform="cell")
            self.grid_frame.grid_columnconfigure(i, weight=0, uniform="cell")

        # 按钮和选项
        self.control_frame = tk.Frame(self.left_frame, bg="#2b2b2b")
        self.control_frame.pack(pady=10)

        self.reset_button = tk.Button(
            self.control_frame,
            text="Restart Game",
            font=("Helvetica", 9),
            bg="#ff5722",
            fg="#ffffff",
            command=self.reset_game,
        )
        self.reset_button.pack(side="left", padx=10)

        self.toggle_button = tk.Button(
            self.control_frame,
            text="Start Agent",
            font=("Helvetica", 9),
            bg="#4caf50",
            fg="#ffffff",
            command=self.toggle_agent,
        )
        self.toggle_button.pack(side="left", padx=10)

        tk.Label(
            self.control_frame,
            text="Delay (s):",
            font=("Helvetica", 7),
            bg="#2b2b2b",
            fg="#ffffff",
        ).pack(side="left", padx=5)
        self.delay_slider = tk.Scale(
            self.control_frame,
            from_=0.1,
            to=2.0,
            resolution=0.1,
            orient="horizontal",
            bg="#2b2b2b",
            fg="#ffffff",
            troughcolor="#555555",
            command=self.update_delay,
        )
        self.delay_slider.set(self.delay)
        self.delay_slider.pack(side="left", padx=10)

        # 操作日志框 (在右侧)
        tk.Label(
            self.right_frame,
            text="Agent Log",
            font=("Helvetica", 9),
            bg="#2b2b2b",
            fg="#ffffff",
        ).pack(pady=5)
        self.log_text = tk.Text(
            self.right_frame,
            width=40,
            height=20,
            bg="#2b2b2b",
            fg="#ffffff",
            state="disabled",
        )
        self.log_text.pack(fill="y", expand=True)

        # 键盘绑定
        self.root.bind("<Key>", self.handle_keypress)

        # 初始化网格显示
        self.update_board()

    def update_board(self):
        """
        更新界面网格
        """
        for row in range(self.board_size):
            for col in range(self.board_size):
                value = self.game.board[row][col]
                canvas = self.cells[row][col]
                canvas.delete("all")  # 清空画布
                if value < len(self.images):
                    canvas.create_image(
                        self.image_size // 2,
                        self.image_size // 2,
                        image=self.images[value],
                        anchor="center",
                    )
                else:
                    canvas.create_rectangle(
                        0, 0, self.image_size, self.image_size, fill="#444444"
                    )

        # 更新分数和步数
        self.score_label.config(text=f"Score: {self.game.score}")
        self.step_label.config(text=f"Step: {self.game.step}")

    def log_action(self, action):
        """
        记录 Agent 的操作
        """
        self.log_text.config(state="normal")
        self.log_text.insert("end", f"Action: {action}\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")

    def update_delay(self, value):
        """
        更新时延
        """
        self.delay = float(value)

    def handle_keypress(self, event):
        """
        处理键盘输入
        """
        key = event.keysym.lower()
        if key in ["a", "w", "s", "d"]:
            self.game.game_step(key)
            self.game.game_level()
            self.update_board()

            # 检查游戏状态
            if self.game.game_status() == "over":
                self.show_game_over()

    def show_game_over(self):
        """
        显示游戏结束提示
        """
        result = messagebox.askyesno("GAME OVER")
        if result:
            self.reset_game()
        else:
            self.root.destroy()

    def reset_game(self):
        """
        重新开始游戏
        """
        self.game.game_reset()
        self.update_board()

    def toggle_agent(self):
        """
        切换 Agent 运行状态
        """
        self.running = not self.running
        if self.running:
            self.toggle_button.config(text="Pause Agent", bg="#f44336")
            threading.Thread(target=self.run_agent).start()
        else:
            self.toggle_button.config(text="Start Agent", bg="#4caf50")

    def run_agent(self):
        """
        运行 Agent 的游戏逻辑
        """
        while self.running:
            state = self.agent.multi_channel_divide(self.game.board, self.game.step)
            action = self.agent.select_action_test(state)
            self.game.game_step(self.action_num[int(action)])
            self.log_action(self.action_num[int(action)])
            self.update_board()
            if self.game.game_status() == "over":
                self.show_game_over()
                break
            time.sleep(self.delay)


# 运行游戏
if __name__ == "__main__":
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
    ScaleFactor = ctypes.windll.shcore.GetScaleFactorForDevice(0)

    root = tk.Tk()
    root.tk.call("tk", "scaling", ScaleFactor / 75)
    gui = GameGUI(root)
    root.mainloop()