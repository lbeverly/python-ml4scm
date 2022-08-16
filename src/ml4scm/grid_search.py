import numpy as np
from typing import Callable, List, cast
from .simulation import SimulationRunner, Problem


def grid_search(sim: SimulationRunner, problem: Problem, params: np.ndarray) -> np.ndarray:
    run = sim.run_problem(problem=problem, values=params, analytes=['U'])
    res = np.array(run)[:, 1::2].reshape(np.shape(np.array(run))[0], np.shape(np.array(run))[2])
    return res


def grid_search_rss(sim: SimulationRunner, problem: Problem, params: np.ndarray, exp_U: List[float]) -> np.ndarray:
    run = sim.run_problem(problem=problem, values=params, analytes=['U'])
    res = np.array(run)[:, 1::2].reshape(np.shape(np.array(run))[0], np.shape(np.array(run))[2])
    cost = np.sum(np.square(exp_U - res[0]*1e6))
    for row in res[1:]:
        cost = np.vstack((cost, np.sum(np.square(exp_U - row*1e6))))
    return cast(np.ndarray, cost)


def grid_search_f(
        sim: SimulationRunner,
        problem: Problem,
        params: np.ndarray,
        func: Callable[[np.ndarray], np.ndarray]) -> np.ndarray:
    run = sim.run_problem(problem=problem, values=params, analytes=['U'])
    res = np.array(run)[:, 1::2].reshape(np.shape(np.array(run))[0], np.shape(np.array(run))[2])
    cost = func(res[0]*1e6)
    for row in res[1:]:
        cost = np.vstack((cost, func(row*1e6)))
    return cast(np.ndarray, cost)


def gs_resample(num_trials: int, gsll: np.ndarray) -> List[np.ndarray]:
    # samples num_trials times from gs_log_likelihood grid and stacks results
    # return: num_trials by 2500 matrix of each index sampled from gsll grid

    # summing the indices of the grid search
    pp = [np.arange(len(gsll))]

    while num_trials > 1:
        # resample parameters with new weights and stack into master list
        samples = gsll[[np.arange(len(gsll))][-1]]
        samples = samples / np.sum(samples)
        re_pp = [pp[-1][np.random.choice(pp[-1], p=samples.T[0])] for i in range(len(pp[-1]))]
        pp = np.vstack((pp, re_pp))  # type: ignore
        num_trials -= 1
    return pp



