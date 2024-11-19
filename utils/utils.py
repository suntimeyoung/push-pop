import matplotlib.pyplot as plt
import numpy as np


def plot_figure(data_list, title, xlabel, ylabel, filename, max_points=2000):
    # 如果数据点超过max_points，则进行采样
    if len(data_list) > max_points:
        indices = np.linspace(0, len(data_list) - 1, max_points).astype(int)
        sampled_data = [data_list[i] for i in indices]
        sampled_indices = [i for i in indices]
    else:
        sampled_data = data_list
        sampled_indices = range(len(data_list))

    plt.figure(figsize=(12, 6))
    plt.plot(sampled_indices, sampled_data)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(True)
    plt.savefig(filename)
    plt.close()


def plot_min_max_figure(min_list, max_list, title, xlabel, ylabel, filename, max_points=2000):
    # 如果数据点超过max_points，则进行采样
    if len(min_list) > max_points:
        indices = np.linspace(0, len(min_list) - 1, max_points).astype(int)
        sampled_min_list = [min_list[i] for i in indices]
        sampled_max_list = [max_list[i] for i in indices]
        sampled_indices = [i for i in indices]
    else:
        sampled_min_list = min_list
        sampled_max_list = max_list
        sampled_indices = range(len(min_list))
    
    plt.figure(figsize=(12, 6))
    plt.plot(sampled_indices, sampled_min_list, label="Min Values", color="blue")
    plt.plot(sampled_indices, sampled_max_list, label="Max Values", color="red")
    plt.fill_between(sampled_indices, sampled_min_list, sampled_max_list, color="gray", alpha=0.3)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(True)
    plt.legend()
    plt.savefig(filename)
    plt.close()


def draw_episode(episode_check, save_path):
    plot_figure(episode_check[0], "Episode Rewards Over Time", "Episode", "Total Reward", save_path + 'rewards.png')
    plot_figure(episode_check[1], "Episode Valid Step Over Time", "Valid Step", "Total Reward", save_path + 'valid_step.png')
    plot_figure(episode_check[2], "Episode Total Step Over Time", "Episode", "Total Reward", save_path + 'total_step.png')
    percentage_valid_steps = [valid / total * 100 for valid, total in zip(episode_check[1], episode_check[2])]
    plot_figure(percentage_valid_steps, "Episode Valid Step Ratio Over Time", "Episode", "Valid Step Ratio", save_path + 'valid_step_ratio.png')
