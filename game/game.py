from random import random, randrange, choice, shuffle
from math import floor
import copy


class Game:
    def __init__(self):
        """
        初始化函数
        """
        self.board_size = 5  # 游戏棋盘大小
        self.board_center = floor(self.board_size / 2)
        self.board = [[0] * self.board_size for _ in range(self.board_size)]  # 游戏棋盘的状态
        self.notion = ['⬜', '🔲', '⬛', '🔹', '💠', '🔶']
        '''
        棋盘中, int 代表 state
            0-⬜-空
            1-🔲-可动块
            2-⬛-不可动块
            3-🔹-加分点
            4-💠-清除点
            5-🔶-玩家
        '''
        self.score = 0  # 游戏得分
        self.last_status = [0, 0]  # 游戏上一步得分与步数
        self.step = 0  # 游戏进行到的状态
        self.valid_step = False
        self.player_position = [self.board_center, self.board_center]  # 玩家的初始位置
        self.player_move_history = [[], [], []]  # 玩家的移动历史记录
        self.board[self.board_center][self.board_center] = 5

    def game_reset(self, rand=True):
        """
        重置游戏
        :return:
        """
        self.board = [[0] * self.board_size for _ in range(self.board_size)]  # 游戏棋盘的状态
        self.score = 0  # 游戏得分
        self.last_status = [0, 0]  # 游戏上一步得分与步数
        self.step = 0  # 游戏进行到的状态
        self.player_position = [self.board_center, self.board_center]  # 玩家的初始位置
        self.board[self.board_center][self.board_center] = 5
        if rand:
            self.board_init_rand()
        else:
            self.board = copy.deepcopy(self.setted_board)

    def console_show(self) -> object:
        """
        函数：在控制台查看游戏情况
        :return:
        """
        print("-------------------")
        print("{:>17}".format("⏩Step=" + str(self.step)))
        print("{:>17}".format("🆒Score=" + str(self.score)))
        print(f"Debug mode: the reward is {self.game_reward()}")
        print("-------------------")
        for row in range(self.board_size):
            print("| ", end='')
            for col in range(self.board_size):
                print('{: ^2}'.format(self.notion[self.board[row][col]]), end='')
            print("|")
        print("-------------------")
        print()
        print()

    def show_board(self, board) -> object:
        """
        函数：在控制台查看游戏情况
        :return:
        """
        print("-------------------")
        for row in range(self.board_size):
            print("| ", end='')
            for col in range(self.board_size):
                print('{: ^2}'.format(self.notion[board[row][col]]), end='')
            print("|")
        print("-------------------")
        print()
        print()

    def board_init_rand(self):
        """
        初始化棋盘，放置所有块
        :return:
        """
        temp_board = [[0] * self.board_size for _ in range(self.board_size)]  # 用于储存临时棋盘
        # 处理棋盘的第一行，保证有 4个块
        first_row_empty = randrange(0, 5)
        for col in range(self.board_size):
            if col == first_row_empty:
                temp_board[0][col] = 0
            else:
                temp_board[0][col] = 1
        # 处理棋盘的后四行
        block_count = 0
        gen_pr = [1, 0.4, 0.2, 0.2, 0.2]
        for row in range(1, self.board_size):
            for col in range(self.board_size):
                if block_count == 4:
                    break
                if random() < gen_pr[row] and [row, col] != [self.board_center, self.board_center]:
                    temp_board[row][col] = 1
                    block_count += 1
        temp_board[self.board_center][self.board_center] = 5
        self.board = temp_board
        self.board_generate_award('init')
        self.setted_board = copy.deepcopy(self.board)
        # self.show_board(self.setted_board)

    def game_level(self):
        if self.step == 0 or not self.valid_step:
            return
        if self.step % 50 == 0:
            self.board_generate_award('all')
        elif self.step % 30 == 0:
            self.board_generate_hard_block()

    def game_step(self, direction):
        self.player_move(direction)
        if not self.valid_step:
            return
        if self.step & 1 == 1:
            self.board_generate_easy_block()
        self.board_check()

    def game_status(self):
        check_row = False
        for row in range(self.board_size):
            if self.board[row][self.player_position[1]] == 2 and row < self.player_position[0]:
                check_row = False
                continue
            if self.board[row][self.player_position[1]] == 2 and row > self.player_position[0]:
                break
            if self.board[row][self.player_position[1]] in {0, 3, 4}:
                check_row = True
        check_col = False
        for col in range(self.board_size):
            if self.board[self.player_position[0]][col] == 2 and col < self.player_position[1]:
                check_col = False
                continue
            if self.board[self.player_position[0]][col] == 2 and col > self.player_position[1]:
                break
            if self.board[self.player_position[0]][col] in {0, 3, 4}:
                check_col = True
        if check_row or check_col:
            return 'continuable'
        else:
            return 'over'

    def game_reward(self):
        if self.step == self.last_status[1]:
            self.last_status = [self.score, self.step]
            return -10.0
        else:
            reward = self.score - self.last_status[0]
            self.last_status = [self.score, self.step]
            return reward + 0.01

    def player_move(self, direction):
        """
        根据玩家键入的移动方向，将游戏推进
        :param direction:
        :return:
        """
        move_step = 0  # 可移动步数
        block_count = 0  # 经过的可动块数
        move_history = []  # 保存新的移动记录
        match direction:
            case "w":
                destination = [-1, -1]  # 第一位是目的墙的位置，第二位是增长方式
            case "a":
                destination = [-1, -1]
            case "s":
                destination = [self.board_size, 1]
            case "d":
                destination = [self.board_size, 1]
        # 对水平或竖直的方向分别进行处理
        if direction == "w" or direction == "s":
            for row in range(self.player_position[0] + destination[1], destination[0], destination[1]):  # 对经过的路径进行判断
                match self.board[row][self.player_position[1]]:
                    case 0:
                        move_step += 1
                    case 1:
                        block_count += 1
                    case 2:
                        destination[0] = row
                        break
                    case 3:
                        self.score += 1
                        move_step += 1
                    case 4:
                        self.score += 1
                        move_step += 1
                        self.board_clear(row, 'row')
                        self.board_clear(self.player_position[1], 'col')
                        self.board[row][self.player_position[1]] = 0
                        if block_count > 0:
                            destination[0] = row
                            move_step += block_count
                            self.score += block_count
                            break
            if move_step > 0:
                self.step += 1
                for i in range(move_step):
                    self.board[self.player_position[0] + i * destination[1]][self.player_position[1]] = 0
                    move_history.append([self.player_position[0] + i * destination[1], self.player_position[1]])
                self.player_move_history = [move_history, self.player_move_history[0], self.player_move_history[1]]
                self.board[self.player_position[0] + move_step * destination[1]][self.player_position[1]] = 5
                self.player_position = [self.player_position[0] + move_step * destination[1], self.player_position[1]]
                for row in range(self.player_position[0] + destination[1], destination[0], destination[1]):
                    self.board[row][self.player_position[1]] = 1
        if direction == "a" or direction == "d":
            for col in range(self.player_position[1] + destination[1], destination[0], destination[1]):  # 对经过的路径进行判断
                match self.board[self.player_position[0]][col]:
                    case 0:
                        move_step += 1
                    case 1:
                        block_count += 1
                    case 2:
                        destination[0] = col
                        break
                    case 3:
                        self.score += 1
                        move_step += 1
                    case 4:
                        self.score += 1
                        self.board_clear(self.player_position[0], 'row')
                        self.board_clear(col, 'col')
                        self.board[self.player_position[0]][col] = 0
                        if block_count > 0:
                            destination[0] = col
                            move_step += block_count
                            self.score += block_count
                            break
                        else:
                            move_step += 1

            if move_step > 0:
                self.step += 1
                for i in range(move_step):
                    self.board[self.player_position[0]][self.player_position[1] + i * destination[1]] = 0
                    move_history.append([self.player_position[0], self.player_position[1] + i * destination[1]])
                self.player_move_history = [move_history, self.player_move_history[0], self.player_move_history[1]]
                self.board[self.player_position[0]][self.player_position[1] + move_step * destination[1]] = 5
                self.player_position = [self.player_position[0], self.player_position[1] + move_step * destination[1]]
                for col in range(self.player_position[1] + destination[1], destination[0], destination[1]):
                    self.board[self.player_position[0]][col] = 1

        self.valid_step = move_step > 0
        return 0

    def board_check(self):
        """
        判断是否有连在一起的情况，并调用 board_clear进行消除
        :return:
        """
        for row in range(self.board_size):
            check_row = True
            for col in range(self.board_size):
                if self.board[row][col] not in {1, 2}:
                    check_row = False
                    break
            if check_row:
                self.board_clear(row, 'row')
        for col in range(self.board_size):
            check_col = True
            for row in range(self.board_size):
                if self.board[row][col] not in {1, 2}:
                    check_col = False
                    break
            if check_col:
                self.board_clear(col, 'col')

    def board_clear(self, index, direction):
        """
        清除某一行或某一列，并生成响应的加分点
        :param index:
        :param direction:
        :return:
        """
        if direction == 'row':
            for col in range(self.board_size):
                match self.board[index][col]:
                    case 1:
                        self.board[index][col] = 3
                    case 2:
                        self.board[index][col] = 4
        else:
            for row in range(self.board_size):
                match self.board[row][index]:
                    case 1:
                        self.board[row][index] = 3
                    case 2:
                        self.board[row][index] = 4

    def board_generate_easy_block(self, block_type=1):
        if len(self.player_move_history[2]) > 0:
            n = random()
            iteration = 0
            if n < 0.5:
                while iteration < 20:
                    generate_block = choice(self.player_move_history[0])
                    if self.board[generate_block[0]][generate_block[1]] == 0:
                        self.board[generate_block[0]][generate_block[1]] = block_type
                        return
                    iteration += 1
            elif n < 0.7:
                while iteration < 20:
                    generate_block = choice(self.player_move_history[1])
                    if self.board[generate_block[0]][generate_block[1]] == 0:
                        self.board[generate_block[0]][generate_block[1]] = block_type
                        return
                    iteration += 1
            elif n < 0.9:
                while iteration < 20:
                    generate_block = choice(self.player_move_history[2])
                    if self.board[generate_block[0]][generate_block[1]] == 0:
                        self.board[generate_block[0]][generate_block[1]] = block_type
                        return
                    iteration += 1
        while True:
            generate_block = [randrange(0, self.board_size), randrange(0, self.board_size)]
            if self.board[generate_block[0]][generate_block[1]] in {0, 3, 4}:
                if self.board[generate_block[0]][generate_block[1]] == 3:
                    self.score += 1
                if self.board[generate_block[0]][generate_block[1]] == 4:
                    self.board_clear(generate_block[0], 'row')
                    self.board_clear(generate_block[1], 'col')
                    self.score += 1
                self.board[generate_block[0]][generate_block[1]] = block_type
                return

    def board_generate_award(self, award_type):
        match award_type:
            case 'all':
                for row in range(self.board_size):
                    for col in range(self.board_size):
                        if self.board[row][col] == 0:
                            self.board[row][col] = 3
            case 'init':
                for row in range(self.board_size):
                    for col in range(self.board_size):
                        if self.board[row][col] == 0 and random() < 0.6:
                            self.board[row][col] = 3

    def board_generate_hard_block(self):
        row = [0] * 12 + [1] * 7 + [2] * 1 + [3] * 7 + [4] * 12
        while True:
            place = [choice(row), randrange(0, 5)]
            shuffle(place)
            if self.board[place[0]][place[1]] in {0, 1, 3}:
                self.board[place[0]][place[1]] = 2
                return
