import tkinter as tk
from tkinter import font
from tkinter import messagebox
from game.game import Game
import os
import sys
import ctypes


class GameGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Push&Pop")
        self.root.configure(bg="#2b2b2b")  # 设置背景色

        self.game = Game()
        self.game.board_init_rand()
        self.board_size = self.game.board_size
        self.action_num = ["a", "w", "s", "d"]

        self.history = []  # 保存历史记录，每个元素为 (board, score, step, log)
        self.max_history_len = 80
        self.current_time_index = 0  # 当前历史位置
        self.max_time_index = 0

        # 加载图片并调整大小
        self.image_size = 60  # 每个单元格图片的大小
        if hasattr(sys, '_MEIPASS'):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath(".")
        self.images = [
            tk.PhotoImage(file=os.path.join(base_path, f"assets/images/notion_{i}.png"))
            for i in range(len(self.game.notion))
        ]

        # 主框架：左侧和右侧
        self.main_frame = tk.Frame(self.root, bg="#2b2b2b")
        self.main_frame.pack(fill="both", expand=True)

        # 左侧框架
        self.left_frame = tk.Frame(self.main_frame, bg="#2b2b2b", padx=10, pady=10)
        self.left_frame.pack(side="left", fill="both", expand=True)

        # 右侧框架 (Agent Log)
        self.right_frame = tk.Frame(self.main_frame, bg="#2b2b2b", padx=10, pady=10)
        self.right_frame.pack(side="right", fill="y")

        # 在右侧日志框区域添加滚动条和动态调整宽度功能
        self.log_frame = tk.Frame(self.right_frame, bg="#2b2b2b")
        self.log_frame.pack(fill="both", expand=True)

        # 滚动条
        self.scrollbar = tk.Scrollbar(
            self.log_frame, bg="#2b2b2b", troughcolor="#444444"
        )
        self.scrollbar.pack(side="right", fill="y")

        # 滚动条与时间回溯

        self.time_scroll = tk.Scale(
            self.right_frame,
            from_=0,
            to=0,
            resolution=1,
            orient="horizontal",
            bg="#2b2b2b",
            fg="#ffffff",
            troughcolor="#555555",
            highlightthickness=0,  # 去除高亮边框
            command=self.update_time,
            length=150,
        )
        self.time_scroll.pack(side="left", fill="x", expand=True, pady=10)

        # 分数与步数
        self.info_frame = tk.Frame(self.left_frame, bg="#2b2b2b")
        self.info_frame.pack(pady=10)

        self.score_label = tk.Label(
            self.info_frame,
            text="Score: 0",
            font=("JetBrains Mono", 7),
            bg="#2b2b2b",
            fg="#ffffff",
        )
        self.score_label.pack(side="left", padx=20)
        self.step_label = tk.Label(
            self.info_frame,
            text="Step: 0",
            font=("JetBrains Mono", 7),
            bg="#2b2b2b",
            fg="#ffffff",
        )
        self.step_label.pack(side="left", padx=20)

        # 游戏网格
        self.grid_frame = tk.Frame(self.left_frame, bg="#2b2b2b")
        self.grid_frame.pack(fill="both", expand=True, pady=10, padx=10)
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
        self.agent_frame = tk.Frame(self.left_frame, bg="#2b2b2b")
        self.agent_frame.pack(pady=5)
        self.agent_delay_frame = tk.Frame(self.left_frame, bg="#2b2b2b")
        self.agent_delay_frame.pack(pady=5)

        self.reset_button = tk.Button(
            self.control_frame,
            text="Restart Game",
            font=("JetBrains Mono", 9),
            bg="#616161",
            fg="#ffffff",
            command=self.reset_game,
        )
        self.reset_button.pack(side="left", padx=10)

        # 操作日志框 (在右侧)
        tk.Label(
            self.log_frame,
            text="Agent Log",
            font=("JetBrains Mono", 7),
            bg="#2b2b2b",
            fg="#ffffff",
        ).pack(pady=5)
        self.log_text = tk.Text(
            self.log_frame,
            width=20,
            height=20,
            bg="#2b2b2b",
            fg="#ffffff",
            state="disabled",
            yscrollcommand=self.scrollbar.set,
            wrap="none",
            font=font.Font(family="JetBrains Mono", size=6),
        )
        self.log_text.pack(side="left", fill="y", expand=True)
        # 绑定滚动条
        self.scrollbar.config(command=self.log_text.yview)

        # 键盘绑定
        self.root.bind("<Key>", self.handle_keypress)

        # 初始化网格显示
        self.update_board()

        self.save_history()
        
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

    def log_action(self, action, role):
        """
        记录操作
        """
        self.log_text.config(state="normal")
        message = f"[{self.game.step}]: {role} {action}\n"
        self.log_text.config(width=max(self.log_text.cget("width"), len(message)))
        self.log_text.insert("end", message)
        self.log_text.see("end")
        self.log_text.config(state="disabled")

    def save_history(self):
        """
        保存当前游戏状态到历史记录
        """
        # 深拷贝当前状态
        history_entry = {
            "board": [row[:] for row in self.game.board],  # 保存棋盘状态
            "score": self.game.score,  # 游戏得分
            "step": self.game.step,  # 当前步数
            "last_status": self.game.last_status[:],  # 上一步得分与步数
            "valid_step": self.game.valid_step,  # 当前步是否有效
            "player_position": self.game.player_position[:],  # 玩家的位置
            "player_move_history": [
                moves[:] for moves in self.game.player_move_history
            ],  # 玩家的移动历史
            "log": self.log_text.get("1.0", "end-1c"),  # 保存日志内容
        }
        self.history = self.history[: self.current_time_index - max(0, self.max_time_index-self.max_history_len)]
        self.history.append(history_entry)
        self.history = self.history[-self.max_history_len :]
        self.current_time_index += 1
        self.max_time_index = self.current_time_index

        # 更新滚动条范围
        self.time_scroll.config(
            from_=max(0, self.max_time_index - self.max_history_len),
            to=self.max_time_index - 1,
        )
        self.time_scroll.set(self.max_time_index - 1)

    def restore_history(self, index):
        """
        恢复历史记录中的游戏状态
        """
        if index < max(0, self.max_time_index-self.max_history_len) or index > self.max_time_index-1:
            return

        self.current_time_index = index + 1
        history_entry = self.history[index - max(0, self.max_time_index-min(len(self.history), self.max_history_len))]

        # 恢复游戏状态
        self.game.board = [row[:] for row in history_entry["board"]]
        self.game.score = history_entry["score"]
        self.game.step = history_entry["step"]
        self.game.last_status = history_entry["last_status"][:]
        self.game.valid_step = history_entry["valid_step"]
        self.game.player_position = history_entry["player_position"][:]
        self.game.player_move_history = [
            moves[:] for moves in history_entry["player_move_history"]
        ]

        # 更新界面显示
        self.update_board()

        # 恢复日志显示
        self.log_text.config(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.insert("1.0", history_entry["log"])
        self.log_text.see("end")
        self.log_text.config(state="disabled")

    def update_time(self, value):
        """
        滚动条更新历史状态
        """
        index = int(value)
        self.restore_history(index)

    def handle_keypress(self, event):
        """
        处理键盘输入，将上下左右映射为 awsd
        """
        # 定义箭头键到 aws 键的映射
        key_mapping = {
            "Up": "w",
            "Down": "s",
            "Left": "a",
            "Right": "d",
            "8": "w",
            "2": "s",
            "4": "a",
            "6": "d",
        }

        # 获取按键名称并转换
        key = event.keysym

        if key in key_mapping:  # 如果是箭头键，映射到 awsd
            key = key_mapping[key]

        key = key.lower()  # 转为小写，确保一致性

        if key in ["a", "w", "s", "d"]:
            self.game.game_step(key)
            self.log_action(key, "player")
            self.game.game_level()
            self.update_board()
            self.save_history()

            # 检查游戏状态
            if self.game.game_status() == "over":
                self.show_game_over()

    def show_game_over(self):
        """
        显示游戏结束提示
        """
        result = messagebox.askyesno(
            title="GAME OVER", message="Would you like to continue?"
        )
        if result:
            pass
        else:
            self.root.destroy()

    def reset_game(self):
        """
        重新开始游戏
        """
        self.game.game_reset()
        self.update_board()

        # 清理历史记录和日志
        self.history = []
        self.max_time_index = 0
        self.current_time_index = 0
        self.time_scroll.config(from_=0, to=0)
        self.time_scroll.set(0)

        # 清理日志
        self.log_text.config(state="normal")  # 允许修改日志
        self.log_text.delete("1.0", "end")  # 删除所有内容
        self.log_text.config(state="disabled")  # 恢复只读状态


# 运行游戏
if __name__ == "__main__":
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
    ScaleFactor = ctypes.windll.shcore.GetScaleFactorForDevice(0)

    root = tk.Tk()
    root.tk.call("tk", "scaling", ScaleFactor / 75)
    gui = GameGUI(root)
    root.mainloop()
