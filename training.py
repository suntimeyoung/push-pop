import matplotlib.pyplot as plt

from game.game import Game
from dqn_agent import DQNAgent
from utils.utils import *

action_num = ["a", "w", "s", "d"]
game = Game()
game.board_init_rand()

input_channels = 7
action_size = 4  # 上、下、左、右四个动作
agent = DQNAgent(game.board_size, input_channels, action_size)
agent.multi_channel_init(game.board_size, len(game.notion))
episode_check = [[], [], []]

# 模拟训练过程
rand = False
for episode in range(6000):
    game.game_reset(rand=rand)
    state = agent.multi_channel_divide(game.board, game.step)  # 初始状态
    # game.show_board(game.board)
    total_reward = 0
    done = False  # 模拟环境返回是否终止
    count = 0

    # while not done:
    for step in range(10):
        action = agent.select_action(state)
        game.game_step(action_num[int(action)])
        game.game_level()
        next_state = agent.multi_channel_divide(game.board, game.step)  # 环境返回下一个状态
        reward = game.game_reward()  # 环境返回奖励
        # print(f'Step {step}: reward = {reward}')
        if game.game_status() == "over":
            done = True

        count += 1
        agent.remember(state, action, reward, next_state, done)
        agent.replay(batch_size=256)

        state = next_state
        total_reward += reward

        if done:
            break
    if episode % 5 == 0:
        agent.update_target_network()
        agent.decay_epsilon()

    episode_check[0].append(total_reward)
    episode_check[1].append(game.step)
    episode_check[2].append(count)

    if episode % 50 == 5:
        print(f"Episode {episode + 1}: epsilon = {agent.epsilon}")
        draw_episode(episode_check, "./results/")
        agent.plot_q_loss()
