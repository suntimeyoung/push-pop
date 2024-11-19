import torch
import torch.nn as nn
import torch.nn.functional as F

class QNetwork(nn.Module):
    def __init__(self, board_size, input_channels, action_size):
        super(QNetwork, self).__init__()
        # 计算全连接层的输入节点数量
        self.board_size = board_size
        self.input_channels = input_channels

        # 定义卷积层
        self.conv1 = nn.Conv2d(in_channels=input_channels, out_channels=64, kernel_size=2, stride=1, padding=1)
        self.conv2 = nn.Conv2d(in_channels=64, out_channels=128, kernel_size=2, stride=1, padding=1)
        self.conv3 = nn.Conv2d(in_channels=128, out_channels=256, kernel_size=2, stride=1, padding=1)

        # 定义全连接层
        self.fc1 = nn.Linear(16384, 256)
        self.fc2 = nn.Linear(256, action_size)

    def forward(self, x):
        # 将多通道输入展平
        x = x.view(-1, self.board_size, self.board_size, self.input_channels)
        x = x.permute(0, 3, 1, 2)  # 将通道移到正确的位置

        # 卷积层1
        x = torch.relu(self.conv1(x))
        # 卷积层2
        x = torch.relu(self.conv2(x))
        # 卷积层3
        x = torch.relu(self.conv3(x))
        x = x.contiguous().view(x.size(0), -1)
        # 全连接层1
        x = torch.relu(self.fc1(x))
        # 全连接层2
        x = self.fc2(x)

        return x


class QNetwork_5CNN(nn.Module):
    def __init__(self, board_size, input_channels, action_size):
        super(QNetwork_5CNN, self).__init__()
        self.board_size = board_size
        self.input_channels = input_channels

        # 定义卷积层
        self.conv1 = nn.Conv2d(
            in_channels=input_channels,
            out_channels=64,
            kernel_size=2,
            stride=1,
            padding=1,
        )
        self.conv2 = nn.Conv2d(
            in_channels=64, out_channels=128, kernel_size=2, stride=1, padding=1
        )
        self.conv3 = nn.Conv2d(
            in_channels=128, out_channels=128, kernel_size=2, stride=1, padding=1
        )
        self.conv4 = nn.Conv2d(
            in_channels=128, out_channels=128, kernel_size=2, stride=1, padding=1
        )
        self.conv5 = nn.Conv2d(
            in_channels=128, out_channels=64, kernel_size=2, stride=1, padding=1
        )

        # 根据卷积后的输出大小计算全连接层输入节点数量
        conv_output_size = self._calculate_conv_output_size(board_size)
        self.fc1 = nn.Linear(conv_output_size, 256)
        self.fc2 = nn.Linear(256, action_size)

    def _calculate_conv_output_size(self, board_size):
        """计算卷积层输出的节点数量"""
        output_size = board_size + 5
        return output_size * output_size * 64  # 最后一层输出通道数为 64

    def forward(self, x):
        # 将多通道输入展平
        x = x.view(-1, self.input_channels, self.board_size, self.board_size)

        # 多层卷积
        x = F.relu(self.conv1(x))
        x = F.relu(self.conv2(x))
        x = F.relu(self.conv3(x))
        x = F.relu(self.conv4(x))
        x = F.relu(self.conv5(x))

        # 展平并通过全连接层
        x = x.view(x.size(0), -1)  # Flatten
        x = F.relu(self.fc1(x))
        x = self.fc2(x)

        return x
