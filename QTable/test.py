import dill
import gymnasium as gym
import numpy as np
import matplotlib.pyplot as plt


def load_qtable(filename):
    with open(filename, 'rb') as f:
        qtable = dill.load(f)
    return qtable


mode = 'range'
act_buckets = 11
obs_buckets = 11

if mode == range:
    obs_buckets = 1

filename = f'qtable_{mode}.dill'
qtable = load_qtable(filename)
env = gym.make("BipedalWalker-v3", render_mode = 'human')


def test_qtable(env, qtable, episodes=100, render=True):
    rewards = []  
    for episode in range(1, episodes + 1):
        total_reward = 0
        state = env.reset()[0]
        state = discretizeState(state)

        while True:
            action = np.argmax(qtable[state])
            continuous_action = undiscretizeAction(action)
            next_state, reward, done, _, _ = env.step(continuous_action)

            if render:
                env.render()

            next_state = discretizeState(next_state)
            total_reward += reward
            state = next_state

            if done:
                break

        rewards.append(total_reward)
        print(f"Test Episode {episode}/{episodes}, Total Reward: {total_reward}")

    env.close()
    return rewards


def discretizeState(state):
    """
    Discretize the continuous observation state into discrete buckets based on the mode.

    Parameters:
    state (np.array): Continuous observation state.

    Returns:
    tuple: Discretized state.
    """
    if mode == 'uniform':
        discrete_state = np.round((state - env.observation_space.low) / (env.observation_space.high - env.observation_space.low) * (obs_buckets - 1)).astype(int)
    elif mode == 'range':
        discrete_state = []
        for i, val in enumerate(state):
            # compute the number of buckets for each dimension
            bucket_size = (env.observation_space.high[i] - env.observation_space.low[i]) * obs_buckets
            # make sure that there is at least one bucket for each dimension
            bucket_size = max(1, int(bucket_size))
            # discretize the dimension
            discrete_val = round((val - env.observation_space.low[i]) / (env.observation_space.high[i] - env.observation_space.low[i]) * (bucket_size - 1))
            discrete_state.append(discrete_val)
    else:
        raise ValueError(f"Invalid mode '{mode}'. Supported modes are 'uniform' and 'range'.")

    return tuple(discrete_state)

def discretizeAction(action):
    """
    Discretize the continuous action into discrete buckets.

    Parameters:
    action (np.array): Continuous action.

    Returns:
    tuple: Discretized action.
    """
    discrete_action = np.round((action - env.action_space.low) / (env.action_space.high - env.action_space.low) * (act_buckets - 1)).astype(int)
    return tuple(discrete_action)

def undiscretizeAction(action):
    """
    Convert a discrete action back into a continuous action.

    Parameters:
    action (tuple): Discretized action.

    Returns:
    tuple: Continuous action.
    """
    action = (np.array(action) / (act_buckets - 1)) * (env.action_space.high - env.action_space.low) + env.action_space.low
    return tuple(action)


test_rewards = test_qtable(env, qtable, episodes=100, render=False)

plt.figure(figsize=(12, 6))
plt.plot(test_rewards, label='Total Reward')
plt.xlabel('Episode')
plt.ylabel('Total Reward')
plt.title(f'Rewards of {mode} mode (Testing with Loaded Q-table)')
plt.legend()
plt.savefig(f'Rewards {mode}.png')
