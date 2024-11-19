在以下代码的基础上，根据这个 agent 的交互方式，在 gui 中增加一个按钮表示暂停或启动 agent 进行游戏，同时显示 agent 的每一步操作，再增加一个时延选项，控制 agent 执行一次操作后等待的秒数，默认0.5s。

agent 交互代码如下：

```python
from dqn_agent import DQNAgent
agent = DQNAgent(game.board_size, input_channels, action_size)
agent.multi_channel_init(game.board_size, len(game.notion))

state = agent.multi_channel_divide(game.board, game.step)
action = agent.select_action(state)
game.game_step(action_num[int(action)])
```

目前的 gui 框架代码如下：

```python
import tkinter as tk
from tkinter import messagebox
from game.game import Game
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
            tk.PhotoImage(file=f"./assets/images/notion_{i}.png")  # 调整图片大小
            for i in range(len(self.game.notion))
        ]

        # 主框架
        self.frame = tk.Frame(self.root, bg="#2b2b2b", padx=10, pady=10)
        self.frame.pack(fill="both", expand=True)

        # 分数与步数
        self.info_frame = tk.Frame(self.frame, bg="#2b2b2b")
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
        self.grid_frame = tk.Frame(self.frame, bg="#2b2b2b")
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

        # 重置按钮
        self.reset_button = tk.Button(
            self.frame,
            text="Restart Game",
            font=("Helvetica", 9),
            bg="#ff5722",
            fg="#ffffff",
            command=self.reset_game,
        )
        self.reset_button.pack(pady=10)

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


# 运行游戏
if __name__ == "__main__":
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
    ScaleFactor = ctypes.windll.shcore.GetScaleFactorForDevice(0)

    root = tk.Tk()
    root.tk.call("tk", "scaling", ScaleFactor / 75)
    gui = GameGUI(root)
    root.mainloop()

```

