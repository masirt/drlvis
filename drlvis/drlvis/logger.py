"""Logger implementation for appropriate logging. This is important for visualisation with
drlvis"""

import tensorflow as tf
import numpy as np
import umap.umap_ as umap
from tensorboard.compat.proto import summary_pb2
from sklearn.preprocessing import StandardScaler
from scipy.stats import entropy
from scipy.special import softmax


def create_logger(logdir):
    """create a logger and select the logging directory
    Important: The directory should only contain one tf.summary file,
    so if one restarts the training procedures, all other log files
    in the directory should be deleted.

    Params:
        logdir: string
            path to the logging directory, which shall contain the logging
            file
    """
    logger = tf.summary.create_file_writer(logdir)
    logger.set_as_default()


def log_episode_return(episode_return, episode_count):
    """log the return/score/accumulated reward per episode
    Params:
        episode_return: int
            A scalar value --> the return/score/accumulated reward
        episode_count: int
            This should regularly be the episode in which the return is logged
    """
    tf.summary.scalar(name="episode-rewards", data=episode_return,
                      step=episode_count, description=None)


def log_frame(frame, episode_count,  step):
    """log the frame per timestep for a given episode
    Params:
        frame: numpy.ndarray
            a numpy.ndarray with shape (x,y, 3),
            representing RGB values for an x-by-y pixel image
        episode_count: int
            The episode in which this frame shall be logged
        step: int
            The timestep in which the frame is being logged

    """
    tf.summary.image(name="episode{}".format(episode_count), data=tf.expand_dims(frame, 0), step=step,
                     max_outputs=3, description=None)  # for max_outputs see https://www.tensorflow.org/api_docs/python/tf/summary/image


def log_action_divergence(action_probs, action_probs_old, episode_count, apply_softmax=False):
    """log the divergence of actions per episode

    Params:
        action_probs: numpy.ndarray
            A one dimensional array (can be a list too)
            containing all predicted action
            probabilties per timestep from the
            current episode
        action_probs_old: numpy.ndarray
            A one dimensional array (can be a list too)
            containing all predicted action probabilities per
            timestep from the previous episode
        episode_count: int
            The current episode count/number
        apply_softmax: bool
            A flag on whether to apply a softmax function on the action_probs.
            This should not be the case as the action_probs should allready be
            probability but can be done if one logs a model output without softmax
            activation in the end.
    """
    action_probs_old = np.array(
        action_probs_old)  # just in case a list or other iterable is passed
    preds = np.array(action_probs)  # instead of np.array

    if apply_softmax:
        action_probs_old = softmax(action_probs_old, axis=1)
        action_probs = softmax(action_probs, axis=1)

    prior = np.mean(action_probs_old, axis=0)
    prior += 1e-4
    prior = prior/np.sum(prior)

    kl_div = np.sum(preds * np.log2(preds/prior))
    tf.summary.scalar(name='action-divergences', data=kl_div,
                      step=episode_count, description=None)


def log_action_probs(predictions, episode_count, step,  apply_softmax=False):
    """log the predicted probabilities for each action per timestep
    in an episode

    Params:
        predictions: numpy.ndarray
            the tensor containing predictions for the current timestep
        episode_count: int
            The current episode
        step: int
            The current timestep in the episode
        apply_softmax: bool
            A flag on whether to apply softmax on the predicted_dists
            or not. Not necessary if last layer
            of ones model allready contains softmax activation
    """
    metadata = summary_pb2.SummaryMetadata()
    metadata.plugin_data.plugin_name = 'action_probs'
    metadata.data_class = summary_pb2.DATA_CLASS_TENSOR
    predictions = np.array(predictions)

    if apply_softmax:
        predictions = softmax(predictions)

    tf.summary.write(tag='e{}'.format(episode_count),
                     tensor=predictions,
                     step=step,
                     metadata=metadata)


def log_experiment_random_states(random_state_samples, predicted_dists,
                                 obs_min, obs_max, episode_count, image_data=False, apply_softmax=False):
    """log data for a random states experiment.

    Params:
        random_state_samples: numpy.ndarray
            A high dimensional numpy array with size (x, num_states) where num_states is the number
            of different states in the used environment
        predicted_dists: numpy.ndarray
            The corresponding predictions for the random state samples
        obs_min: numpy.ndarray
            An iterable containing the minimal values possible in an environment
        obs_max: numpy.ndarray
            An iterable containing the max values possible in an environment
        episode_count: int
            The current episode count/number
        apply_softmax: bool
            A flag on whether to apply softmax on the predicted_dists
            or not. Not necessary if last layer
            of ones model allready contains softmax activation

    """

    reducer = umap.UMAP(random_state=42)
    if apply_softmax:
        predicted_dists = softmax(predicted_dists, axis=1)

    preds_entropy = entropy(predicted_dists, axis=1).reshape((-1, 1))
    predicted_actions = predicted_dists.argmax(
        axis=1).reshape((-1, 1))
    if image_data:
        for index, image in enumerate(random_state_samples):
            tf.summary.image(name="random-state-ep-{}".format(episode_count), data=tf.expand_dims(image, 0), step=index,
                             max_outputs=3, description=None)
        nsamples, nx, ny, nz = random_state_samples.shape
        random_state_samples = random_state_samples.reshape(
            (nsamples, nx*ny*nz))

    random_state_samples = StandardScaler().fit_transform(random_state_samples)
    reduced_samples = reducer.fit_transform(random_state_samples)

    if image_data:
        random_state_samples = np.zeros(reduced_samples.shape)

    logging_data = np.concatenate(
        [reduced_samples, predicted_actions, preds_entropy, random_state_samples], axis=1)

    bound_data = np.array([obs_min, obs_max])

    metadata = summary_pb2.SummaryMetadata()
    metadata.plugin_data.plugin_name = 'experiment_random_states_bounds'
    metadata.data_class = summary_pb2.DATA_CLASS_TENSOR
    tf.summary.write(tag='experiment-episode-{}-bounds'.format(episode_count),
                     step=0,
                     tensor=bound_data,
                     metadata=metadata)

    metadata = summary_pb2.SummaryMetadata()
    metadata.plugin_data.plugin_name = 'experiment_random_states'
    metadata.data_class = summary_pb2.DATA_CLASS_TENSOR
    tf.summary.write(tag='experiment-episode-{}'.format(episode_count),
                     step=0,
                     tensor=logging_data,
                     metadata=metadata
                     )


def log_action_distribution(actions, episode_count):
    """log the distribution of actions per episode
    Params:
        actions: numpy.ndarray
            the selected actions (by agent) for the current episode
            one dimensional array. (can be a list too)
        episode_num: int
            the current episode count/number

    """
    log_custom_distribution(actions, 'action_distributions', episode_count)


def log_weights(weight_tensor, step, episode_count):
    """log the weight tensor of the last layer of a model.
    Params:
        weight_tensor: numpy.ndarray
            The weight tensor of the last layer of ones neural network.
            Will most commonly be of the form
            (# actions) x (# units of layer before last layer)
            or in general (# units in last layer) x (# units in layer before last layer)
        step: int
            The current timestep for which the weight tensor shall be logged
        episode_count: int
            The current episode count/number in which the timestep is/ wheight
            tensor shall be logged
    """
    metadata = summary_pb2.SummaryMetadata()
    metadata.plugin_data.plugin_name = 'weights'
    metadata.data_class = summary_pb2.DATA_CLASS_TENSOR
    tf.summary.write(tag='weights-episode-{}'.format(episode_count),
                     step=step,
                     tensor=weight_tensor,
                     metadata=metadata
                     )


def log_action_meanings(action_meanings):
    """log the meanings behind given actions
    Params:
        action_meanings: numpy.ndarray
            A one dimensional array (can be a list too)
            containing the meaning per action for
            higher verbosity
    """
    action_meanings = np.array(action_meanings)
    metadata = summary_pb2.SummaryMetadata()
    metadata.plugin_data.plugin_name = 'action_meanings'
    metadata.data_class = summary_pb2.DATA_CLASS_TENSOR
    tf.summary.write(tag='action_meanings_', step=0,
                     tensor=action_meanings, metadata=metadata)


def log_custom_episode_scalar(custom_scalar, episode_count, log_tag):
    """log a custom scalar for each episode (e.g. the average loss)

    Params:
        custom_scalar: float
            The custom scalar one wants to log
        episode_count: int
            The current episode in which the scalar is logged
        log_tag: string
            The tag one wants to use for logging the scalar (e.g. loss)
    """
    tf.summary.scalar(name=log_tag, data=custom_scalar,
                      step=episode_count, description=None)


def log_custom_timestep_scalar(custom_scalar, timestep, episode_count, log_tag):
    """log a custom scalar for each timestep in an episode (e.g. the reward, action, ...)

    Params:
        custom_scalar: float
            The custom scalar one wants to log
        timestep: int
            The current timestep in an episode $episode_count
        episode_count: int
            The current episode in which the scalar is logged
        log_tag: string
            The tag one wants to use for logging the scalar (e.g. reward)
    """
    tf.summary.scalar(name=log_tag+"-e{}".format(episode_count),
                      data=custom_scalar, step=timestep)


def log_custom_distribution(distribution_data, custom_tag, episode_count):
    """log the distribution of a custom value (e.g. selected actions, earned rewards)
    Params:
        distribution_data: numpy.ndarray
            An array or a list of counts for the specified value per episode. Could for
            example be like: Rewards: [0, 5, 3, 5, 7] in an episode with 5 timesteps, where the
            agent receives 0 reward in the first timestep, 5 in the second, ...
        episode_num: int
            the current episode count/number

    """
    distribution_data = np.array(distribution_data)
    # returns unique values and corresponding value counts
    values, value_counts = np.unique(distribution_data, return_counts=True)

    metadata = summary_pb2.SummaryMetadata()
    tensor_dict = {}
    for val, val_c in zip(values, value_counts):
        tensor_dict[val] = val_c
    metadata.plugin_data.plugin_name = str(custom_tag)
    metadata.data_class = summary_pb2.DATA_CLASS_TENSOR
    tf.summary.write(tag=str(custom_tag), step=episode_count, metadata=metadata,
                     tensor=np.array(list(tensor_dict.items())))
