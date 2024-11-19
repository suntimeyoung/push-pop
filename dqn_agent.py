import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import random

from Network.module import *
from utils.utils import plot_figure, plot_min_max_figure


class ReplayBuffer:
    def __init__(self, capacity):
        self.capacity = capacity
        self.memory = []
        self.position = 0

    def push(self, transition):
        if len(self.memory) < self.capacity:
            self.memory.append(None)
        self.memory[self.position] = transition
        self.position = (self.position + 1) % self.capacity

    def sample(self, batch_size):
        return random.sample(self.memory, batch_size)


class DQNAgent:
    def __init__(self, board_size, input_channels, action_size, gamma=0.95, epsilon=1.0, epsilon_decay=0.9999, epsilon_min=0.05):
        self.board_size = board_size
        self.action_size = action_size
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        self.device = torch.device('cuda:3')

        self.q_network = QNetwork_5CNN(board_size, input_channels, action_size).to(self.device)
        self.target_network = QNetwork_5CNN(board_size, input_channels, action_size).to(self.device)
        self.target_network.load_state_dict(self.q_network.state_dict())
        self.target_network.eval()

        self.optimizer = optim.Adam(self.q_network.parameters(), lr=0.001)
        self.criterion = nn.MSELoss()

        self.memory = ReplayBuffer(capacity=50000)

        self.q_values_range_history_epsilon = {'min':[], 'max': []}
        self.loss_history_epsilon = []
        self.q_values_range_history = {"min": [], "max": []}
        self.loss_history = []

    def select_action(self, state):
        if random.random() < self.epsilon:
            return random.randint(0, self.action_size - 1)
        else:
            state_tensor = torch.FloatTensor(np.array(state)).to(self.device)
            with torch.no_grad():
                q_values = self.q_network(state_tensor)
            return torch.argmax(q_values).item()
    
    def select_action_test(self, state):
        state_tensor = torch.FloatTensor(np.array(state)).to(self.device)
        with torch.no_grad():
            q_values = self.q_network(state_tensor)
        return torch.argmax(q_values).item()

    def remember(self, state, action, reward, next_state, done):
        transition = (state, action, reward, next_state, done)
        self.memory.push(transition)

    def replay(self, batch_size):
        if len(self.memory.memory) < batch_size * 10:
            return

        transitions = self.memory.sample(batch_size)
        batch = list(zip(*transitions))
        state_batch = torch.FloatTensor(np.array(batch[0])).to(self.device)
        action_batch = torch.LongTensor(batch[1]).to(self.device)
        reward_batch = torch.FloatTensor(batch[2]).to(self.device)
        next_state_batch = torch.FloatTensor(np.array(batch[3])).to(self.device)
        done_batch = torch.BoolTensor(batch[4]).to(self.device)

        max_reward = reward_batch.abs().max()
        reward_batch = reward_batch / (max_reward + 1e-8)

        current_q_values = self.q_network(state_batch).gather(1, action_batch.unsqueeze(1))
        next_q_values = torch.zeros(batch_size).to(self.device)
        with torch.no_grad():
            next_q_values[~done_batch] = self.target_network(next_state_batch[~done_batch]).max(1)[0]
        target_q_values = reward_batch + self.gamma * next_q_values

        self.optimizer.zero_grad()
        loss = self.criterion(current_q_values, target_q_values.unsqueeze(1))
        loss.backward()
        self.optimizer.step()

        self.q_values_range_history_epsilon["min"].append(current_q_values.min().item())
        self.q_values_range_history_epsilon["max"].append(current_q_values.max().item())
        self.loss_history_epsilon.append(loss.item())

    def update_target_network(self):
        self.target_network.load_state_dict(self.q_network.state_dict())
        length = len(self.q_values_range_history_epsilon["min"])
        if length <= 0:
            return
        self.q_values_range_history["min"].append(sum(self.q_values_range_history_epsilon["min"]) / length)
        self.q_values_range_history["max"].append(sum(self.q_values_range_history_epsilon["max"]) / length)
        self.loss_history.append(sum(self.loss_history_epsilon) / length)
        self.q_values_range_history_epsilon = {"min": [], "max": []}
        self.loss_history_epsilon = []

    def decay_epsilon(self):
        self.epsilon = max(self.epsilon * self.epsilon_decay, self.epsilon_min)

    def multi_channel_init(self, board_size, channel_num):
        self.board_size = board_size
        self.channel_num = channel_num

    def multi_channel_divide(self, board, step):
        board = np.array(board)
        # 初始化6个通道的输入数据
        input_channels = []

        # 遍历每个离散变量，创建一个通道
        for variable_index in range(self.channel_num):
            # 创建一个通道，其中对应离散变量的位置为1，其余位置为0
            channel = np.zeros((self.board_size, self.board_size))
            channel[board == variable_index] = 1
            input_channels.append(channel)

        binary_str = bin(step)[2:]  # 使用 [2:] 去掉二进制字符串前缀 '0b'
        binary_array = list(
            map(int, binary_str.zfill(25)[:25])
        )  # 填充到 25 位，然后转换为整数列表
        binary_matrix = np.array(binary_array).reshape((5, 5))
        input_channels.append(binary_matrix)
        # 将通道叠加在一起形成多通道输入数据
        multi_channel_input = np.stack(input_channels, axis=0)

        return multi_channel_input

    def plot_q_loss(self):
        plot_figure(self.loss_history, 'loss history', 'epoch', 'loss', './results/episode/loss.png')
        plot_min_max_figure(self.q_values_range_history['min'], self.q_values_range_history['max'], 'q_values', 'epoch', 'q_value', './results/episode/q_values.png')

    def save_model(self, episode):
        torch.save(self.target_network, f"./results/models/target_network_episode_{episode}.pth")
        
    def load_model(self, episode, epsilon):
        self.epsilon = epsilon
        self.target_network = torch.load(f"./results/models/target_network_episode_{episode}.pth")
        self.q_network = torch.load(f"./results/models/target_network_episode_{episode}.pth")
        