import numpy as np
from typing import Callable, List, cast, Tuple
from .simulation import SimulationRunner, Problem
from .grid_search import gs_resample
from .estimators import log_likelihood


def _get_norm_weights(concentrations, conc_measured):
    weights = [log_likelihood(concentrations[0], conc_measured)]
    for run in concentrations[1:]:
        weights.append(log_likelihood(run, conc_measured))

    norm_weights = np.array(weights) / np.sum(weights)
    return norm_weights


def _bayes_1params(lower, upper, pool_size=100):
    # helper function for returning 1 set of params
    params = []
    for i in range(len(lower)):
        sample = np.linspace(lower[i], upper[i], num=pool_size)
        params.append(np.random.choice(sample, p=None))
    return params


def _bayes_init_params(num_sets, lower, upper, pool_size=100):
    # generates 1 set of parameters to be used in run_bayes()
    # num_sets: number of parameter sets to generate
    # lower, upper: list of parameter bounds
    # pool_size: number of linspace samples to sample from when picking each parameter
    # return: num_sets sets of params as a matrix

    plist = _bayes_1params(lower, upper, pool_size)
    while num_sets > 1:
        plist = np.vstack((plist, _bayes_1params(lower, upper, pool_size)))
        num_sets -= 1
    return plist


def _bayes_eval(sim: SimulationRunner, problem: Problem, params: np.ndarray, exp_U: List[float]) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    # evaluates parameters and returns concentrations, new weights, and parameters given

    # run phreeqc for matrix of U concentrations
    run = sim.run_problem(problem=problem, values=params, analytes=['U'])
    concs = np.array(run)[:, 1::2].reshape((np.shape(params)[0], 6))

    # get matrix of new weights
    new_weights = _get_norm_weights(concs, exp_U)

    return concs, new_weights, params


def bayes_resample(
        sim: SimulationRunner,
        problem: Problem,
        exp_U: List[float],
        num_trials: int,
        num_sets: int,
        pool_size: int=100):
    # samples num_trials times and stacks results
    # remaining input parameters are inputs for bayes_init_params()
    # return: matrix for concs, params, new_weights
    lower = [x.lower for x in problem.bounds]
    upper = [x.upper for x in problem.bounds]
    cc, nw, pp = _bayes_eval(sim, problem, _bayes_init_params(num_sets, lower, upper, pool_size), exp_U)
    cc = np.array([cc])
    nw = np.array([nw])
    pp = np.array([pp])
    while num_trials > 1:
        # resample parameters with new weights and stack into master list
        re_pp = [pp[-1][np.random.choice(np.arange(len(pp[-1])), p=nw[-1])] for i in range(len(pp[-1]))]
        #         print(pp, re_pp)
        pp = np.vstack((pp, [re_pp]))

        # evaluate and stack other values
        re_cc, re_nw, _ = _bayes_eval(sim, problem, pp[-1], exp_U)
        cc = np.vstack((cc, [re_cc]))
        nw = np.vstack((nw, [re_nw]))
        num_trials -= 1
    return {'cc': cc, 'nw': nw, 'pp': pp}


def bayes_param_count(pp_mtrx):
    # returns list of summed counts of each original parameter

    params_count = np.ones(len(pp_mtrx[0]))
    # summing while accounting for the shape of input
    if len(np.shape(pp_mtrx)) > 2:
        for i in range(1, len(pp_mtrx)):
            for p in pp_mtrx[i]:
                params_count[pp_mtrx[0].tolist().index(list(p))] += 1
    else:
        for i in range(1, len(pp_mtrx)):
            for p in pp_mtrx[i]:
                params_count[pp_mtrx[0].tolist().index(p)] += 1
    return params_count


def bayes_param_count_by_original(pp_mtrx, original_params):
    # can be implemented additively
    # returns list of summed counts of each original parameter

    params_count = np.zeros(len(original_params))
    # summing while accounting for the shape of input
    if len(np.shape(pp_mtrx)) > 2:
        for i in range(len(pp_mtrx)):
            for p in pp_mtrx[i]:
                params_count[original_params.tolist().index(list(p))] += 1
    else:
        for i in range(len(pp_mtrx)):
            for p in pp_mtrx[i]:
                params_count[original_params.tolist().index(p)] += 1
    return params_count


def best_params_by_num_samples(resamp_gs, step_size, xx, yy):
    steps = range(step_size, len(resamp_gs[0])+1, step_size)
    prev_s = 0
    gspc = np.zeros(len(resamp_gs[0]))
    samples_dict = dict()
    for s in steps:
        gspc = gspc + bayes_param_count_by_original(resamp_gs[prev_s:s], resamp_gs[0])
        yy_maxvals = np.amax(gspc.reshape(50,50), 0)
        xx_max_idx = np.argmax(yy_maxvals)
        xx_maxvals = np.amax(gspc.reshape(50,50), 1)
        yy_max_idx = np.argmax(xx_maxvals)
        prev_s = s
        samples_dict[s] = (xx[0,:][xx_max_idx], yy[:,0][yy_max_idx])
    return samples_dict


def consecutive_resample(max_samples, step_size, gsll, xx, yy):
    steps = range(step_size, max_samples + 1, step_size)
    samples_dict = dict()

    for s in steps:
        gspc = bayes_param_count(gs_resample(s, gsll))
        yy_maxvals = np.amax(gspc.reshape(50,50), 0)
        xx_max_idx = np.argmax(yy_maxvals)
        xx_maxvals = np.amax(gspc.reshape(50,50), 1)
        yy_max_idx = np.argmax(xx_maxvals)
        samples_dict[s] = (xx[0,:][xx_max_idx], yy[:,0][yy_max_idx])
    return samples_dict
