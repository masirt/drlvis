"""Data preprocessor file containing the data preprocessor class which is
used for processing data in the backend before sending it to the Vue frontend."""
import base64

import numpy as np
import tensorboard.plugins.image.metadata as meta_image
import tensorboard.plugins.scalar.metadata as meta_scalar
from tensorboard import context
from tensorboard.backend.event_processing import data_provider
from tensorboard.backend.event_processing import \
    plugin_event_multiplexer as event_multiplexer
from tensorboard.data import provider as base_provider
import re
import timeit


class DataPreprocessor:
    """The DataPreprocessor class is there for preprocessing the data coming
        from log files before sending back processed data to the frontend."""

    def __init__(self, log_dir):
        self.log_dir = log_dir
        self.inf = 1000000000
        self. ctx = context.RequestContext()
        self.provider = self._create_provider()

    def get_timestep_log_tags(self):
        """return a list of scalar logtags on a timestep level for e.g. rewards, q-values,...
        Returns:
            timestep_log_tags:
                A dict of the form {"timestep_log_tags": list(string)}, where the list of strings are
                the scalar log tags for logged timestep values like rewards...
        """
        timestep_log_tags = {}
        try:
            log_tags_list = list(self.provider.list_scalars(
                experiment_id="unused", ctx=self.ctx, plugin_name=meta_scalar.PLUGIN_NAME)['.'].keys())
            timestep_log_tags_filtered = set()
            for logged_scalar in log_tags_list:
                valid_pattern = re.compile(".*-e\d+")
                if valid_pattern.match(logged_scalar) and "reward" not in logged_scalar:
                    timestep_log_tags_filtered.add(logged_scalar.split("-")[0])
            timestep_log_tags["timestepLogTags"] = list(
                timestep_log_tags_filtered)
        except KeyError:
            print("Tags for logged scalars on a timestep level do not exist")
        return timestep_log_tags

    def get_log_tags(self):
        """return a list of tags that were used during logging of scalar values like episode returns
        Returns:
            log_tags: dict
                A dict of the form {"logTags": list(string)} where the strings inside of the list
                are the log tags.
        """
        log_tags = {}
        try:
            log_tags_list = list(self.provider.list_scalars(
                experiment_id="unused", ctx=self.ctx, plugin_name=meta_scalar.PLUGIN_NAME)['.'].keys())
            log_tags_list_filtered = []
            for logged_scalar in log_tags_list:
                non_valid_pattern = re.compile(".*-e\d+")
                if non_valid_pattern.match(logged_scalar) or logged_scalar in ["action-divergences", "episode-rewards"]:
                    continue
                log_tags_list_filtered.append(logged_scalar)
            log_tags["logTags"] = log_tags_list_filtered
        except KeyError:
            print("Tags for logged scalars do not exist")
        return log_tags

    def get_scalar_values_by_tag(self, tag):
        """A method to get scalar values by one single tag.
        Params:
            tag: string
            A simple string containing the tag of which the values (step, value) shall be returned
        Returns:
            scalar_listing:
                The values {step: [val, polyfittrend]) filtered by the tag.
        """
        scalars = self._get_scalars_by_tag(tag)
        if scalars == {}:
            print("Scalar value queried by"+str(tag)+" does not exist.")
            return {}

        scalar_listing = {}
        for scalar in scalars:
            scalar_listing[scalar.step] = scalar.value
        scalar_dict_vals = np.array(list(scalar_listing.values()))

        polynomial_fit = np.polyfit(
            np.arange(len(scalar_dict_vals)), scalar_dict_vals, 5)
        poly_handler = np.poly1d(polynomial_fit)

        for index, scalar in enumerate(scalars):
            scalar_listing[scalar.step] = [
                scalar.value, poly_handler(index)]

        return scalar_listing

    def get_all_scalar_values(self):
        """A method for returning all scalar values from the log file.
        Returns:
            all_values: all scalar values logged in the log file without any filter tags.
        """
        all_values = {}
        try:
            all_tags = list(self.provider.list_scalars(
                self.ctx, plugin_name=meta_scalar.PLUGIN_NAME, experiment_id="unused",
                run_tag_filter=None)['.'].keys())
            all_values = {tag: [] for tag in all_tags}
            for tag in all_tags:
                all_values[tag] = self.get_scalar_values_by_tag(tag)
        except KeyError:
            print("The requestet scalar value list does not exist.")
        return all_values

    def get_multiple_scalar_values_by_tag(self, tags):
        """A method for returning scalar values for multiple tags from the logged tf.summary file
        Params:
            tags: list
            A list of tags containing simple strings whose values shall be
            retrieved from the logged file.
        Returns:
            tag_vals:
            The extracted values (step, value) from the log file per tag.

        """
        tag_vals = {tag: [] for tag in tags}
        for tag in tags:
            tag_vals[tag] = self.get_scalar_values_by_tag(tag)
        return tag_vals

    def get_frames_for_episode(self, episode_num):
        """A method to get the recorded frames for a video snippet of the agent's behaviour.
        Params:
            episode_num: int
            The episode number of the frames per timestep that shall be returned.
        Returns:
            frames: The frames per episode as binary data
        """
        frames = {'frames': []}
        try:
            images = self.provider.read_blob_sequences(
                self.ctx, plugin_name=meta_image.PLUGIN_NAME, experiment_id="unused",
                downsample=self.inf)['.']

            for vals in images['episode{}'.format(episode_num)]:
                for index, tuple_vals in enumerate(vals.values):
                    if index == 2:
                        frame_raw = self.provider.read_blob(
                            self.ctx, blob_key=tuple_vals.blob_key)
                        frame_raw = base64.b64encode(frame_raw).decode('ascii')
                        frames['frames'].append(frame_raw)

        except KeyError:
            print("The requested frames do not exist.")
        return frames

    def get_probs_for_episode(self, episode_num):
        """A method for returning the probabilities per timestep predicted
            by softmax layer in the network.
        Params:
            episode_num: int
            The episode number to get the probabilities from.
        Returns:
            probs: the probabilities predicted by the agent per timestep

        """
        probs = {}
        try:
            episode_probs = self.provider.read_tensors(self.ctx, experiment_id="unused",
                                                       downsample=self.inf,
                                                       plugin_name="action_probs")[
                '.']['e{}'.format(episode_num)]
            for f_index, frame_probs_wrapped in enumerate(episode_probs):
                frame_probs_unwrapped = frame_probs_wrapped.numpy

                probs[f_index] = [{"name": "action{}".format(
                    i), "value": float(val)} for i, val in enumerate(list(frame_probs_unwrapped))]
        except KeyError:
            print(
                "The requested action probabilities (confidence)\
                do not exist for the given episode.")
        return probs

    def get_first_confidence_experiment_episode(self):
        conf_episode = -1
        try:
            experiment_ids = self.provider.list_tensors(
                experiment_id='unused', ctx=self.ctx,
                plugin_name='experiment_random_states')['.'].keys()

            experiment_ids_numerical = [int(experiment_id.split(
                '-')[-1]) for experiment_id in experiment_ids]
            conf_episode = experiment_ids_numerical[0]

        except KeyError:
            print("First conifdence episode does not exist")
        return conf_episode

    def get_experiment_random_states_tensors(self, episode_num):
        """A method to return data for the random state experiment. (Experiment to test agent's
            confidence in selecting the right actions in given random states.)
        Params:
            episode_num: int
                The episode number for which the data is being requested
        Returns:
            exp_data: dict
                A dictionary containing the relevant data for the given experiment. It consists
                of min and max bounds in means of all episodes in which the experiment was held
                , a step, which is the number of episodes between experiment episodes, a min and
                max State indicating the value of maximum and minimum state values (environment
                bounds), and the values which are a high dimensional array containing the following
                columns: [reduced_dim1, reduced_dim2, predicted_actions, entropy_on_predictions,
                actual_state_val1, ..., actual_state_valn]

        """
        exp_data = {}
        try:
            experiment_ids = self.provider.list_tensors(
                experiment_id='unused', ctx=self.ctx,
                plugin_name='experiment_random_states')['.'].keys()

            experiment_ids_numerical = [int(experiment_id.split(
                '-')[-1]) for experiment_id in experiment_ids]
            exp_data['minEpisode'] = experiment_ids_numerical[0]
            exp_data['maxEpisode'] = experiment_ids_numerical[-1]

            if len(experiment_ids_numerical) >= 2:
                exp_data['step'] = experiment_ids_numerical[1] - \
                    experiment_ids_numerical[0]
            else:
                exp_data['step'] = 0
            bound_data = self.provider.read_tensors(experiment_id='unused',
                                                    plugin_name='experiment_random_states_bounds',
                                                    ctx=self.ctx, downsample=self.inf)['.']['experiment-episode-{}-bounds'.format(episode_num)][0].numpy

            # state_names = self.provider.read_tensors(experiment_id='unused',
            #                                          plugin_name='experiment_random_states_state_meanings',
            #                                          ctx=self.ctx, downsample=self.inf)['.']['experiment-episode-{}-state-meaning'.format(episode_num)][0].numpy
           # print(state_names)
            exp_data['minState'] = bound_data[0, :].tolist()
            exp_data['maxState'] = bound_data[1, :].tolist()

            data_values = self.provider.read_tensors(experiment_id='unused',
                                                     plugin_name='experiment_random_states',
                                                     ctx=self.ctx, downsample=self.inf)[
                '.']['experiment-episode-{}'.format(episode_num)][0].numpy
            x_vals = data_values[:, 0].tolist()

            y_vals = data_values[:, 1].tolist()

            action_preds = data_values[:, 2].tolist()

            entropy_preds = data_values[:, 3]
           # print(entropy_preds)

            exp_vals = []
            entropy_preds = (np.ones_like(entropy_preds) - ((entropy_preds - entropy_preds.min()) /  # calculate 1-entropy to get confidence of being correct prediction
                                                            (entropy_preds.max() - entropy_preds.min()))).tolist()
            # entropy_preds = np.ones_like(entropy_preds).tolist()
            rest = data_values[:, 4:]
            state_info = []
            for i in range(4, 4+rest.shape[1]):
                state_info.append(data_values[:, i].tolist())

            for exp_entry in zip(x_vals, y_vals, action_preds, entropy_preds, *state_info):
                exp_vals.append(list(exp_entry))
            exp_data['values'] = exp_vals
            print("done with experiment data")

        except KeyError:
            print(
                'The requested experiment data for the random state action selection experiment does not exist.')
        return exp_data

    def get_confidence_frames(self, episode_num, index):
        confidence_frames = {'confidenceFrames': []}
        try:
            starttime = timeit.default_timer()
            images = self.provider.read_blob_sequences(
                self.ctx, plugin_name=meta_image.PLUGIN_NAME, experiment_id="unused",
                downsample=self.inf)['.']
            print("Time for loading conf image:",
                  (timeit.default_timer() - starttime), "s")
            starttime = timeit.default_timer()
            for index, tuple_vals in enumerate(images['random-state-ep-{}'.format(episode_num)][index].values):
                if index == 2:
                    frame_raw = self.provider.read_blob(
                        self.ctx, blob_key=tuple_vals.blob_key)
                    frame_raw = base64.b64encode(frame_raw).decode('ascii')
                    confidence_frames['confidenceFrames'].append(frame_raw)
            print("Time for routine:", (timeit.default_timer() - starttime), "s")
        except KeyError:
            print("The requested frames do not exist.")
        return confidence_frames

    def get_action_distributions(self):
        """A method to return the action distributions for all episodes.

        Returns:
            action_distributions: dict
                A dictionary containing actions and their corresponding count in an episode
                action_distribution[episode]=[{name: action_name, value: action_count},...]"""
        action_distributions = {}
        try:
            action_distrib_tensors = self.provider.read_tensors(
                experiment_id="unused", ctx=self.ctx, plugin_name='action_distributions', downsample=self.inf)['.']['action_distributions']
            for act_dist_tensor in action_distrib_tensors:
                action_counts = np.array(act_dist_tensor.numpy)
                action_distributions[act_dist_tensor.step] = [{"name": "action{}".format(
                    count[0]), "value": float(count[1])} for count in action_counts]
        except KeyError:
            print('Key error Action Distributions exception')

        return action_distributions

    def get_custom_distributions(self, distribution_name):
        """A method to return custom distributions for all episodes. e.g. for rewards

        Returns:
            action_distributions: dict
                A dictionary containing actions and their corresponding count in an episode
                action_distribution[episode]=[{name: action_name, value: action_count},...]"""
        custom_distributions = {}
        try:
            distrib_tensors = self.provider.read_tensors(
                experiment_id="unused", ctx=self.ctx, plugin_name=distribution_name, downsample=self.inf)['.'][distribution_name]
            for dist_tensor in distrib_tensors:

                counts = np.array(dist_tensor.numpy)
                custom_distributions[dist_tensor.step] = [{"name": "{}".format(
                    count[0]), "value": count[1]} for count in counts]
        except KeyError:
            print('Key error Action Distributions exception')
        return custom_distributions

    def get_distribution_tags(self):
        """ A method to return the tags related to being distributions.
        These are all tags except the default plugins and specified invalid ones.

        Returns:
            logTags: dict
                A dict containing a list of valid log tags for distributions
        """
        plugin_names = list(self.provider.list_plugins(
            experiment_id="unused", ctx=self.ctx))
        distrib_tags = []
        DEFAULT_PLUGINS = [
            'scalars',
            'images']
        INVALID_PLUGINS = ['action_probs',

                           'experiment_random_states_state_meanings',
                           'weights',
                           'experiment_random_states_bounds',
                           'action_meanings',
                           'experiment_random_states', 'action_distributions']

        for plugin_name in plugin_names:
            if plugin_name not in DEFAULT_PLUGINS and plugin_name not in INVALID_PLUGINS:
                distrib_tags.append(plugin_name)

        return {"logTags": distrib_tags}

    def get_weights_for_episode(self, episode_num):
        """"A method to return the logged weight matrix for each timestep in an episode.
        Params:
            episode_num: int
                The episode one wants to return the weight matrices for.
        Returns:
            weights_episode: dict
                A dict containing the weight matrices for 0..n timesteps for episode episode_num.
                Even though most algorithms don't update their weights every timestep in an episode,
                this was done for a more general applicability.
        """
        weights_episode = {}
        try:
            tensordata = self.provider.read_tensors(experiment_id="unused", ctx=self.ctx, plugin_name='weights', downsample=self.inf)[
                '.']['weights-episode-{}'.format(episode_num)]
            for h_index, tensordatum in enumerate(tensordata):
                weights = tensordatum.numpy
                weight_data = []
                for i, weight_pair in enumerate(weights):
                    for j, weight in enumerate(weight_pair):

                        index = str(i)+"," + str(j)
                        weight_data.append({index: float(weight)})
                weights_episode[h_index] = weight_data

        except KeyError:
            print('Key error Weights Exception')
        return weights_episode

    def get_action_meanings(self):
        """A method to return corresponding meanings for given actions
        Returns:
            action_meanings: dict
                A dict of the form {action_meanings: [action_0_meaning, ...., action_n_meaning]}
        """
        action_meanings = {}
        try:
            tensordata = self.provider.read_tensors(experiment_id="unused", ctx=self.ctx,
                                                    plugin_name='action_meanings', downsample=self.inf)[
                '.']['action_meanings_']
            action_meanings['action_meanings'] = tensordata[0].numpy.tolist()
            action_meanings['action_meanings'] = [
                elem.decode('utf-8') for elem in action_meanings['action_meanings']]

        except KeyError:
            print("The requested data for meanings of given actions does not exist")

        return action_meanings

    def _create_multiplexer(self):
        """A method to create a multiplexer for the data provider

        Retuns:
            multiplexer: EventMultiplexer
                The event multiplexer for loading data from a tf.summary written file
        """
        sizes = {
            "distributions": self.inf,
            "images": self.inf,
            "audio": self.inf,
            "scalars": self.inf,
            "histograms": self.inf,
            "tensors": self.inf,
        }
        multiplexer = event_multiplexer.EventMultiplexer(
            size_guidance=sizes)
        multiplexer.AddRunsFromDirectory(self.log_dir)
        multiplexer.Reload()
        return multiplexer

    def _create_provider(self):
        """A method to create a dataprovider

        Returns:
        data_provider: MultiplexerDataProvider
            The data provider which is being used for data loading inquiries (from file).
        """
        multiplexer = self._create_multiplexer()
        return data_provider.MultiplexerDataProvider(multiplexer, self.log_dir)

    def _get_scalars_by_tag(self, tag):
        """A method to return unprocessed scalar values by tags.
        Params:
            tag: string
            The tag which shall be used as filter for getting raw values from the log file.
        Returns:
            scalars:
                unprocessed scalar values, should not be used as is
        """
        scalars = []
        try:
            scalars = self.provider.read_scalars(self.ctx, plugin_name=meta_scalar.PLUGIN_NAME,
                                                 downsample=self.inf, experiment_id="unused",
                                                 run_tag_filter=base_provider.
                                                 RunTagFilter(tags=[tag]))

            scalars = scalars['.'][tag]

        except KeyError:
            print("Scalar queried with the tag "+str(tag) + " does not exist.")
        return {} if scalars == [] else scalars
