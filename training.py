from datetime import datetime

from game.game import Game
from dqn_agent import DQNAgent
from utils.utils import *

# nohup python -u training.py > ./results/training.log 2>&1 &

action_num = ["a", "w", "s", "d"]
game = Game()
game.board_init_rand()
state_size = game.board_size  # 棋盘大小

input_channels = 7
action_size = 4  # 上、下、左、右四个动作
agent = DQNAgent(game.board_size, input_channels, action_size)
agent.multi_channel_init(game.board_size, len(game.notion))
# load trained model
agent.load_model(140000, 0.05231380110081405)
episode_check = [[], [], []]

test_reward = []
test_total_step = []
test_valid_step_ratio = []

# 模拟训练过程
rand = True
for episode in range(1000000):
    game.game_reset(rand=rand)
    state = agent.multi_channel_divide(game.board, game.step)  # 初始状态
    # game.show_board(game.board)
    total_reward = 0
    done = False  # 模拟环境返回是否终止
    count = 0

    while not done:
    # for step in range(10):
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

        state = next_state
        total_reward += reward

        if done:
            break
        
    agent.replay(batch_size=512)
    if episode % 10 == 0:
        agent.update_target_network()
        agent.decay_epsilon()

    episode_check[0].append(total_reward)
    episode_check[1].append(game.step)
    episode_check[2].append(count)

    if episode % 500 == 0 and episode > 0:
        date_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        print(f"[{date_str}]: Episode {episode + 1}: epsilon = {agent.epsilon}")
        draw_episode(episode_check, "./results/episode/")
        agent.plot_q_loss()
    
    if episode % 1000 == 0 and episode > 0:
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
        
        test_reward.append(total_reward)
        test_total_step.append(count)
        test_valid_step_ratio.append(game.step / count * 100)
        
        plot_figure(test_reward, 'test reward', 'epoch(per 500)', 'reward', './results/test/test_reward.png')
        plot_figure(test_total_step, 'test total step', 'epoch(per 500)', 'step', './results/test/total_step.png')
        plot_figure(test_valid_step_ratio, 'test valid step ratio', 'epoch(per 500)', 'step', './results/test/valid_step_ratio.png')
    
    if episode % 10000 == 0 and episode > 0:
        agent.save_model(episode)
