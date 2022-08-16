import pytest
import ml4scm
import numpy as np
from ml4scm.simulation import Problem, Bound, get_random_values

def test_sim_ctor1():
    p = Problem.from_dict({
            'input_filename': 'input.file',
            'output_filename': 'output.file',
            'db_template_filename': 'db_template.file',
            'bounds': [Bound(x,y) for x,y in [(1,2), (3,4), (5,6)]],
            'names': ['a', 'b','c'],
            'num_vars': 3
    })
    assert p.names == ['a', 'b', 'c']
    assert p.bounds == [Bound(1,2), Bound(3,4), Bound(5,6)]
    assert p.num_vars == 3

def test_sim_ctor2():
    p = Problem(
        bounds=[Bound(x, y) for x, y in [(1, 2), (3, 4), (5, 6)]],
        names=['a', 'b', 'c'],
        num_vars=3,
        db_template_filename='db_template.file',
        input_filename='input.file',
        output_filename='output.file',
    )
    assert p.names == ['a', 'b', 'c']
    assert p.bounds == [Bound(1,2), Bound(3,4), Bound(5,6)]
    assert p.num_vars == 3

def test_get_random_values():
    lower = [1,3,5]
    upper = [2,4,6]
    np.random.seed(0)
    expected = np.array([
        [1.5488135, 3.71518937, 5.60276338],
        [1.54488318, 3.4236548, 5.64589411]
    ])
    bounds = [Bound(x, y) for x, y in zip(lower, upper)]
    r = get_random_values(bounds, 2)
    assert np.allclose(expected, r)
