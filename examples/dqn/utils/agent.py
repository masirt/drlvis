'''https://keras.io/examples/rl/deep_q_network_breakout/'''
import time
import tensorflow.keras as keras
import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt

from utils.replay_buffer import ReplayBuffer
from utils.models import Models
import logger


class Agent():
    """A class representation of an agent using a DQN to solve different atari learning tasks."""

    def __init__(self, env, model, model_target, epsilon):
        self.env = env
        self.num_actions = self.env.action_space.n
        self.model = model
        self.model_target = model_target
        self.epsilon = epsilon
        logger.create_logger("logs")
        self.frame_count = 0

    def train(self,
              max_memory_length,
              batch_size,
              gamma,
              learning_rate,
              max_episode_steps,
              max_episodes,
              max_frames,
              epsilon_random_frames,
              epsilon_greedy_frames,
              update_after_actions,
              update_target_network,
              save_model_steps,
              save_model_path,
              ddqn
              ):
        """Method for learning a dqn or double dqn

        Parameters
        ----------
        max_memory_length: int
            Max memory size for replay buffer

        batch_size: int
            batch size for sampling experience replay data before performing a gradient update

        gamma: float
            discount factor gamma for controlling the importance of future rewards

        learning_rate: float
            learning_rate of optimizer

        max_episode_steps: int
            maximum number of steps per episode

        max_episodes: int
            maximum number of episode per training


        epsilon_random_frames: float
            Number of first n random frames before acting greedily

        epsilon_greedy_frames: float
            Number of greedy frames after random frames

        update_after_actions: int
            Number for controlling after how many actions an update
            should occure ( like in original dqn paper )

        update_target_network: int
            Number of passed frames after which one has to update the target network

        save_model_steps: int
            Number of steps between saving a model

        save_model_path: String
            Path for saving a model

        ddqn: bool
            boolean for whether to train with or without double dqn for reducing overestimation
        """

        optimizer, running_reward, episode_reward_history,\
            memory, loss_function = initialize_training(
                learning_rate, max_memory_length)

        accum_timesteps = 0
        logger.log_action_meanings(["NOOP", "FIRE", "RIGHT", "LEFT"])

        for episode_count in range(0, max_episodes):

            losses = []
            state = np.array(self.env.reset())
            episode_reward = 0
            actions_episode = []
            rewards = []
            curr_probs = []
            #import time
            # time.sleep(1)
            # self.env.render()
            if memory.buffer_count >= 1000 and episode_count % 5 == 0:
                states, _, _, _, _ = memory.sample(800)
                print("STATE SHAPES", states.shape)
                predicted_dists = np.array(self.model.predict(states))

                logger.log_experiment_random_states(random_state_samples=states, predicted_dists=predicted_dists,
                                                    obs_min=[-1, -1], obs_max=[-1, -1], episode_count=episode_count, state_meanings=[], image_data=True,  apply_softmax=True)

            for t in range(0, max_episode_steps):
                self.frame_count += 1
                # print(state.shape)
                # print(np.max(state*255))
                # plt.imsave("test{}.png".format(t),arr=state*255)
                random = True
                if self.frame_count < epsilon_random_frames or self.epsilon > np.random.rand(1)[0]:
                    action = np.random.choice(self.num_actions)
                else:
                    action = self.select_action_greedily(state)
                    random = False
                actions_episode.append(action)

                # FOR LOGGING
                state_tensor = tf.convert_to_tensor(state)
                state_tensor = tf.expand_dims(state_tensor, 0)
                action_probs = self.model.predict(state_tensor)
                # print("ACTION PROBS:", action_probs,
                #      "ACTION PROBS AFTER:", action_probs[0])
                logger.log_action_probs(
                    action_probs[0], episode_count, t, apply_softmax=True)
                curr_probs.append(logger.softmax(action_probs[0]))
                # print("SOFTMAXED PROBS", logger.softmax(action_probs[0]))

                weights = self.model.weights[-2].numpy()
                #print("Weights:", weights[-2].numpy().shape)
                logger.log_weights(weight_tensor=weights,
                                   step=t, episode_count=episode_count)
                #####

                self.decay_epsilon(epsilon_greedy_frames)
                state_next, reward, done, _ = self.env.step(action)
                rewards.append(reward)

                episode_reward += reward
                # tf.summary.scalar("random", data=random, step=self.frame_count)
                # tf.summary.scalar("reward", data=reward, step=self.frame_count)
                # tf.summary.scalar("action", data=action, step=self.frame_count)

                # tf.summary.image(name="episode{}".format(
                #    episode_count), data=tf.expand_dims(state, 0), step=t)
                logger.log_frame(
                    frame=state, episode_count=episode_count, step=t)
                logger.log_custom_timestep_scalar(
                    reward, t, episode_count, 'reward')
                logger.log_custom_timestep_scalar(
                    action, t, episode_count, 'action')
                logger.log_custom_timestep_scalar(
                    random, t, episode_count, 'random')
                memory.add(action, state, state_next, done, reward)

                state = np.array(state_next)

                if self.frame_count % update_after_actions == 0 and memory.__len__() > batch_size:
                    loss = self.train_step(
                        memory, batch_size, ddqn, gamma, loss_function, optimizer, episode_count, t)
                    losses.append(loss)

                if self.frame_count % update_target_network == 0:
                    self.model_target.set_weights(self.model.get_weights())

                if self.frame_count % save_model_steps == 0:
                    Models.save_model(self.model, save_model_path)

                if done:
                    logger.log_episode_return(
                        episode_return=episode_reward, episode_count=episode_count)
                    logger.log_action_distribution(
                        np.array(actions_episode), episode_count)
                    logger.log_custom_distribution(
                        np.array(rewards), 'reward_distribution', episode_count)
                    if episode_count >= 1:
                        logger.log_action_divergence(
                            curr_probs, probs_old, episode_count)
                    probs_old = curr_probs
                    curr_probs = []
                    if len(losses) != 0:
                        loss_avg = np.mean(losses)
                        logger.log_custom_episode_scalar(
                            loss_avg, episode_count, 'loss')
                        losses = []
                        accum_timesteps += t
                        print("EPISODE", episode_count, "DONE WITH RETURN:",
                              episode_reward, "AND #STEPS:", t, "OVERALL STEPS:", accum_timesteps)
                    break

            # tf.summary.scalar("episode_reward",
            #                  data=episode_reward, step=episode_count)
            episode_reward_history.append(episode_reward)
            if len(episode_reward_history) > 100:
                del episode_reward_history[:1]
            running_reward = np.mean(episode_reward_history)

            if running_reward > 40:  # Condition to consider the task solved
                print("Solved at episode {}!".format(episode_count))
                break
            if self.frame_count >= max_frames:
                print("Max frames completed")
                break

    def train_step(self, memory, batch_size, ddqn, gamma, loss_function, optimizer, episode_count, t):
        """Method for train step and updating weights of model

        Parameters
        ----------
        memory: ReplayBuffer
            the ReplayBuffer used for sampling

        batch_size: int
            Sampling Batch Size
        ddqn: bool
            variable for deciding whether tu use ddqn or vanilla dqn
        gamma: float
            discount factor
        loss_function: keras.losses.Huber
            loss function for updating gradients
        optimizer: keras.optimizers.Adam
            optimizer
        """
        state_sample, state_next_sample, rewards_sample, action_sample, \
            done_sample = memory.sample(batch_size)

        if ddqn:
            qs_next_model = self.model(state_next_sample)

            argmax_qs_next = tf.argmax(qs_next_model, axis=-1)
            next_action_mask = tf.one_hot(argmax_qs_next,
                                          self.num_actions, on_value=1., off_value=0.)

            qs_next_target = self.model_target(state_next_sample)

            # tf.summary.scalar("Q Value estimates", data=np.mean(
            #    qs_next_target), step=self.frame_count)

            logger.log_custom_timestep_scalar(
                np.mean(qs_next), t, episode_count, 'q_vals_avg')

            masked_qs_next = tf.reduce_sum(tf.multiply(next_action_mask,
                                                       qs_next_target), axis=-1)

            target = rewards_sample + \
                (1. - done_sample) * gamma * masked_qs_next

        else:

            qs_next = self.model_target.predict(
                state_next_sample)

            # tf.summary.scalar("Q Value estimates", data=np.mean(
            #    qs_next), step=self.frame_count)
            logger.log_custom_timestep_scalar(
                np.mean(qs_next), t, episode_count, 'q_vals_avg')

            max_qs_next = tf.reduce_max(qs_next, axis=-1)

            target = rewards_sample + (1.-done_sample) * gamma * \
                max_qs_next

        with tf.GradientTape() as tape:
            qs_curr = self.model(state_sample)
            masks = tf.one_hot(
                action_sample, self.num_actions, on_value=1., off_value=0.)
            masked_qs = tf.multiply(qs_curr, masks)

            masked_qs = tf.reduce_sum(masked_qs, axis=-1)
            loss = loss_function(target, masked_qs)

        grads = tape.gradient(
            loss, self.model.trainable_variables)
        optimizer.apply_gradients(
            zip(grads, self.model.trainable_variables))
        return loss

    def test(self, max_episodes, max_episode_steps, render):
        """Method for testing a dqn model

        Parameters
        ----------
        max_episode_steps: int
            maximum number of steps per episode

        max_episodes: int
            maximum number of episode per training
        render: bool
            indicator whether to render or not
        """
        episode_rewards = []
        for episode_count in range(0, max_episodes):
            state = np.array(self.env.reset())
            episode_reward = 0

            for t in range(0, max_episode_steps):
                # frame_img = self.env.render(mode="rgb_array")
                # plt.imsave("frames/frame{}.png".format(t), frame_img)
                if render:
                    self.env.render()
                    time.sleep(0.05)

                self.frame_count += 1

                random = True
                if np.random.rand(1)[0] < 0.05:
                    action = np.random.choice(self.num_actions)
                else:
                    action = self.select_action_greedily(state)
                    random = False

                tf.summary.scalar("random", data=random, step=self.frame_count)

                state_next, reward, done, _ = self.env.step(action)
                state_next = np.array(state_next)

                episode_reward += reward
                tf.summary.scalar("reward", data=reward, step=self.frame_count)
                tf.summary.scalar("action", data=action, step=self.frame_count)
                tf.summary.image(name="episode{}".format(
                    episode_count), data=tf.expand_dims(state, 0), step=t)

                state = state_next

                if done:
                    time.sleep(3)
                    break

            tf.summary.scalar("episode_reward",
                              data=episode_reward, step=episode_count)
            episode_rewards.append(episode_reward)
        print("END OF TESTING AFTER {} EPISODES WITH AVG PERFORMANCE OF {} PER EPISODE ".format(
            episode_count, np.mean(episode_rewards)))

    def select_action_greedily(self, state):
        """Return an action greedily based on current dqn predictions

        Parameters
        ----------
        state: np.array
            The current state

        Returns
        -------
        action: int
            one of the possible actions but selected greedily based on current dqn preds
        """
        state_tensor = tf.convert_to_tensor(state)
        state_tensor = tf.expand_dims(state_tensor, 0)
        action_probs = self.model(state_tensor, training=False)

        action = tf.argmax(action_probs[0].numpy())

        return action

    def decay_epsilon(self, epsilon_greedy_frames):
        """Decays epsilon based on number of greedy frames"""
        epsilon_interval = 1.0 - 0.1  # epsilon_max - epsilon_min
        self.epsilon -= epsilon_interval/epsilon_greedy_frames
        self.epsilon = max(self.epsilon, 0.1)  # epsilon_min is 0.1


def initialize_training(learning_rate, max_memory_length):
    """Initialize training variables

    Parameters
    ----------
    learning_rate: float
        The learning rate for the optimizer
    max_memory_length: int
        The maximal size of the replay buffer

    Returns
    -------
    optimizer: keras.otptimizers.Adam
        an initialised optimizer
    running_reward: int
        the initial running reward
    memory: ReplayBuffer
        the initial replay buffer memory
    episode_reward_history: list
        the initial history of episode rewards for solving the task
    loss_function: keras.losses.Huber
        the initialised loss function
    """

    optimizer = keras.optimizers.Adam(
        learning_rate=learning_rate, clipnorm=1.0)

    running_reward = 0

    memory = ReplayBuffer(max_memory_length)
    episode_reward_history = []

    loss_function = keras.losses.Huber()

    return optimizer, running_reward, episode_reward_history, memory, loss_function
