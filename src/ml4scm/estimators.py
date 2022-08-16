import numpy as np
from typing import Callable, List, cast


def log_likelihood(concs: np.ndarray, conc_measured: np.ndarray) -> np.ndarray:  # type: ignore
    # TODO: research builtin log-likelihood estimation in scikit
    # applies the log likelihood equation to 1 set of generated concentrations
    # concs: 1 set of concentrations from phreeqc run
    concs = concs * 1e6
    p = np.exp(-1 * np.sum(np.power(np.array(concs) - conc_measured, 2)) / np.power(np.std(concs), 2))
    return cast(np.ndarray, p)


def ll_func(exp_U: List[float]) -> Callable[[np.ndarray], np.ndarray]:
    return lambda concs: log_likelihood(concs, exp_U)  # type: ignore
