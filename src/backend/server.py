"""Server that handles all the requests for DRLVis frontend."""
import argparse
import timeit
from flask import Flask, request
from flask_cors import CORS
import os

from data_preprocessor import DataPreprocessor

APP = Flask(__name__)
CORS(APP)
OK_STATUS = 200
JSON_TYPE = {'ContentType': 'application/json'}
TEXT_TYPE = {'ContentType': 'text/plain'}

#########
# Serving
#########


@APP.route('/episode-rewards')
def get_episode_rewards():
    """Get Action Divergence data from log files
    Returns:
        chart_data: dict
            A dict containing episode rewards 
    """

    chart_data = data_preprocessor.get_scalar_values_by_tag('episode-rewards')
    return chart_data, 200, JSON_TYPE


@APP.route('/action-divergences')
def get_action_divergences():
    """Get Action Divergence data from log files
    Returns:
        chart_data: dict
            A dict containing action_divergences    
    """

    chart_data = data_preprocessor.get_scalar_values_by_tag(
        'action-divergences')
    return chart_data, 200, JSON_TYPE


@APP.route('/get-frames')
def get_frames():
    """Get frames for an episode
    Params:
        episode: int
            The episode for which the frames shall be returned
    Returns:
        frames: dict
            The frames for an episode per timestep
    """
    episode = int(request.args.get('user'))
    frames = data_preprocessor.get_frames_for_episode(episode)
    return frames, 200, JSON_TYPE


@APP.route('/get-probs')
def get_probs():
    """Get probabilities of action selection for given action
    at given timestep
    Params:
        episode: int
            The episode for which the probabilities shall be returned
    Returns:
        probs: dict
            The probabilities of selecting an action per action
            for the given episode per timestep
    """
    episode = int(request.args.get('user'))
    probs = data_preprocessor.get_probs_for_episode(episode)

    return probs, 200, JSON_TYPE


@APP.route('/get-rewards')
def get_rewards():
    """Get rewards for all timesteps in an episode
    Params:
        episode: int
            The episode for which the rewards shall be returned
        Returns:
            rewards: dict
                The rewards for each timestep in the requested episode
    """
    episode = int(request.args.get('user'))
    rewards = data_preprocessor.get_scalar_values_by_tag(
        "reward-e"+str(episode))
    return rewards, 200, JSON_TYPE


@APP.route('/get-experiment-random-states-data')
def get_experiment_random_states_data():
    """Get the data for random states experiment

    Params:
        episode: int
            The episode for which the data of an
            experiment instance shall be returned
    Returns:
        exp_data: dict
            The experiment data. For further explanation
            see the docs in data_preprocessor
    """
    episode = int(request.args.get('user'))
    exp_data = data_preprocessor.get_experiment_random_states_tensors(episode)

    return exp_data, 200, JSON_TYPE


@APP.route("/get-confidence-frame")
def get_confidence_frame():
    user = request.args.get('user').split(",")
    episode_num = int(user[0])
    index = int(user[1])
    frames = data_preprocessor.get_confidence_frames(episode_num, index)
    return frames, 200, JSON_TYPE


@APP.route("/get-confidence-exp-first-episode")
def get_confident_exp_first_episode():
    episode = data_preprocessor.get_first_confidence_experiment_episode()
    return {"episode": episode}, 200, JSON_TYPE


@APP.route('/get-action-distributions')
def get_action_distributions():
    """Get the distribution of actions. (Count of number of times in which
    an individual action was selected)
    Returns:
        action_distributions: dict
            The actions distribution per episode
    """

    action_distributions = data_preprocessor.get_action_distributions()

    return action_distributions, 200, JSON_TYPE


@APP.route('/get-weights-for-episode')
def get_weights_for_episode():
    """Get weight matrix for an episode
    Params:
        episode: int
            The episode for which the weight matrices per timestep
            shall be returned
    Returns:
        weights_for_episode: dict
            The weight matrices per timestep of a requested episode
    """
    episode = int(request.args.get('user'))
    weights_for_episode = data_preprocessor.get_weights_for_episode(episode)

    return weights_for_episode, 200, JSON_TYPE


@APP.route('/get-action-meanings')
def get_action_meanings():
    """Get the meanings of given actions
    Returns:
        action_meanings: dict
            A dict containing a list of names/meanings
            for all actions
    """
    action_meanings = data_preprocessor.get_action_meanings()

    return action_meanings, 200, JSON_TYPE


@APP.route('/get-log-tags')
def get_log_tags():
    """Return all tags which were created in the logging process for
    scalar values
    Returns:
        log_tags: dict of the form {"logTags": list(string)}
            A dict of a list of tags used during logging to log scalar values
            most commonly in episode value format
    """
    log_tags = data_preprocessor.get_log_tags()

    return log_tags, 200, JSON_TYPE


@APP.route("/get-tag-scalars")
def get_tag_scalars():
    """Return the values logged under a certain log tag.
    Params:
        tag: string
            The tag for which the data shall be returned.

    Returns:
        scalars_tag: dict
            A dict containing the values for a certain logged tag.
            Form {step:[val,polyfittrend]}
    """
    tag = str(request.args.get('user'))
    scalars_tag = data_preprocessor.get_scalar_values_by_tag(tag)

    return scalars_tag, 200, JSON_TYPE


@APP.route("/get-timestep-log-tags")
def get_timestep_log_tags():
    """Return a list of all log tags from timestep level logged scalars e.g. rewards, q-values,...APP
    Returns:
        timestep_log_tags:
            A dict containing the queried log tags on a timestep level. see Datapreprocessor for further info.
    """
    timestep_log_tags = data_preprocessor.get_timestep_log_tags()
    return timestep_log_tags, 200, JSON_TYPE


@APP.route("/get-custom-distribution")
def get_custom_distribution():
    """Get the distribution of a custom value. (Count of number of times in which
    an individual value was selected/received/encountered)
    Returns:
        custom_distributions: dict
            The custom distribution per episode for a specific value"""
    tag = str(request.args.get("user"))
    custom_distributions = data_preprocessor.get_custom_distributions(tag)
    return custom_distributions, 200, JSON_TYPE


@APP.route("/get-distribution-log-tags")
def get_distribution_log_tags():
    """Get the log tags which are related to logged distribution values

    Returns:
        distrib_log_tags: dict
            A dict containing a list of all log tags related to logged distributions (of e.g. actions
            ,rewards)    
    """
    distrib_log_tags = data_preprocessor.get_distribution_tags()
    return distrib_log_tags, 200, JSON_TYPE


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--logdir", type=str, default="backend/logs")
    args = parser.parse_args()

    #os.system("cd dist; python3 -m http.server 8000 &")

    starttime = timeit.default_timer()
    data_preprocessor = DataPreprocessor(args.logdir)
    print("Time for start:", (timeit.default_timer() - starttime), "s")
    APP.run(debug=True)
