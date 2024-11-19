from datetime import datetime

from game.game import Game
from dqn_agent import DQNAgent
from utils.utils import *

action_num = ["a", "w", "s", "d"]
game = Game()
game.board_init_rand()
state_size = game.board_size  # 棋盘大小

input_channels = 7
action_size = 4  # 上、下、左、右四个动作
agent = DQNAgent(game.board_size, input_channels, action_size)
agent.multi_channel_init(game.board_size, len(game.notion))
# load trained model
episode_check = [[], [], []]

test_reward = []
test_total_step = []
test_valid_step_ratio = []

# Test Settings
model_episode = 140000
test_rounds = 10

agent.load_model_test(model_episode, 0.01)
rand = True
date_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
print(f"[{date_str}]: start of testing...")

for episode in range(test_rounds):
    date_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    print(f"[{date_str}]: testing episode {episode}")
    # Test true value
    game.game_reset(rand=rand)
    total_reward = 0
    done = False  # 模拟环境返回是否终止
    count = 0

    while not done:
        state = agent.multi_channel_divide(game.board, game.step)  # 初始状态
        action = agent.select_action_test(state)
        game.game_step(action_num[int(action)])
        game.game_level()
        reward = game.game_reward()
        if game.game_status() == "over":
            done = True
        count += 1
        total_reward += reward
        if done or total_reward <= -100:
            break
    
    # print(f"total reward is {total_reward}")
    # print(f"total count is {count}")
    # print(f"valid step ratio is {int(game.step / count * 100)}%")
    test_reward.append(total_reward)
    test_total_step.append(count)
    test_valid_step_ratio.append(game.step / count * 100)

date_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
print(f"[{date_str}]: end of testing...")

print(f"\n\ntested for {test_rounds} times")
print("=" * 30)
print(f"total reward is {sum(test_reward)/test_rounds}")
print(f"total count is {sum(test_total_step)/test_rounds}")
print(f"valid step ratio is {sum(test_valid_step_ratio)/test_rounds}%")

print("=" * 30)
