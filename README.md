# DRLVIS - Visualising Deep Reinforcement Learning
<img src="images/drlvis-overview.png"/>



\
Created by [Marios Sirtmatsis](https://mariossirtmatsis.com) with the support of [Alex Bäuerle](https://a13x.io/).


DRLVis is an application used for visualising deep reinforcement learning. The goal is to enable developers to get a further understanding of broadly used algorithms across the deep reinforcement learning landscape. Also DRLVis shall provide a tool for researchers and developers to help them understand errors in their implemented algorithms.



## Installation
1. Install the `drlvis pip package` by using the following command `pip install -e drlvis` from the directory above the drlvis directory
2. After that simply run `drlvis --logdir @PATH_TO_LOGDIR`
3. Open your browser on http://localhost:8000


## Implementation
### Architecture
<img src="images/architecture_drlvis.png"/>

The application is split into a backend and a fronted, where the backend does most of the data preprocessing. The frontend provides meaningful visualisations for further understanding of what the agent is doing, how rewards, weights and actions develop over time and how confident the agent is in selecting its actions.


## Workflow for using DRLVis
1. Train agent and log data
2. Run drlvis
3. Interpret meaningful visualisations in your browser 

## Logging
Logging for the use of drlvis is done by `logger.py`. The file contains a documentation on which values should be passed for logging.
Th`logger.py` contains an individual function for every loggable value/values. Some (the most important) of these functions are:



<br/>


```python
def create_logger(logdir)
```
The `create_logger()` function has to be used for initializing the logger and specifying the target destination of the logging directory. It is always important, that the *logdir* either does not exist yet or is an empty directory.

<br/>

```python
def log_episode_return(episode_return, episode_count)
```
With `log_episode_return()` one is able to log the accumulated reward per episode, with the step being the curresponding current episode count.

<br/>

```python
def log_action_divergence(action_probs, action_probs_old, episode_count, apply_softmax )
```
With `log_action_divergence()` one can calculate the divergence between actions in the current episode and actions in the last episode. Therefore the action_probabilities for each observation per timestep in an episode has to be collected. In the end of an episode this collection of action probabilites and the collection from the episode before can be passed to the `log_action_divergence()` method, which then calculates the kl divergence between action probabilities of the last episode and the current episode. Example code snippet with a model with softmax activation in the last layer:

<br/>

```python
def log_frame(frame, episode_count, step)
```
Using `log_frame()` one can log the frame which is currently being observed, or which corresponds with the current timestep. The episode count is the current episode and the step is the timestep within the episode on which the frame is being observed or corresponds with.

<br/>


```python
from drlvis import logger
import numpy as np

probs_curr = []

for episode in range(episode_range):

    for timestep in range(optional_timestep_range):
    
        if end_of_current_episode: #done in openai gym
            if episode >= 1:
                logger.log_action_divergence(probs_old, probs_curr, episode)
            probs_old = probs_curr

        probs_curr.append(model(observation[np.newaxis,:]))
```

<br/>

```python
def log_action_probs(predictions, episode_count, step, apply_softmax)
```
One can use `log_action_probs()` for logging the predictions of ones model for the currently observed timestep in an episode. If the model does not output probabilites, one can set *apply_softmax* to ```True``` for creating probabilities based on predictions.

<br/>

```python
def log_experiment_random_states(random_state_samples, predicted_dists, obs_min, obs_max, episode_num, state_meanings, apply_softmax)
```
The `log_experiment_random_states()`function takes a highdimensional array containing randomly generated states in bounds of the environments capabilities. *(obs_min, obs_max)*
It also needs the episode in which a random states experiment shall be performed. The function then reduces the dimensions to two dimensions with [UMAP](https://umap-learn.readthedocs.io/en/latest/) for visualisation purposes. The state meanings can be passed for easier environments to reflect what the different states mean. A random state experiment itself is just a method to evaluate the agents confidence in selecting certain actions for randomly generated states. Example code snippet:

```python
from drlvis import logger
import numpy as np

def random_states_experiment(model, episode_num):
   
    obs_space = env.observation_space
    obs_min = obs_space.low
    obs_max = obs_space.high


    num_samples = 10000 # can be an arbitrary number
    random_state_samples = np.random.uniform(
        low=obs_min, high=obs_max, size=(num_samples, len(obs_min)))

    predicted_dists = model(random_state_samples)
   
    logger.log_experiment_random_states(random_state_samples, predicted_dists, obs_min, obs_max, episode_num, [])

```

<br/>

```python
def log_action_distribution(actions, episode_count)
```
The `log_action_distribution()` function calculates the distribution of actions in the specified episode. Therefore one solely has to pass the *actions*, which where selected in the current episode *episode_count*

<br/>

```python
def log_weights(weight_tensor, step, episode_count)
```
With `log_weights()`one can log the weights of the last layer of ones model in a given timestep in an episode. This can be done as follows (model is keras model but not of major importance):
```python
from drlvis import logger

weights = agent.model.weights[-2].numpy()
logger.log_weights(weight_tensor=weights, step=timestep ,episode_count=episode)
```

<br/>



## Examples
Examples on how to use them in real implementations can be found in the examples folder that contains simple cartpole implementation in ```dqn_cartpole.ipynb``` and a more complex DQN implementation for playing Atari Breakout in ```dqn/```


## Bachelor Thesis
For further information on how to use DRLVis and details about the application, I refer to my bachelor thesis located at <a href=documents/bachelor_thesis_visdrl.pdf>```documents/bachelor_thesis_visdrl.pdf```</a>.

## License
[MIT](https://opensource.org/licenses/MIT)