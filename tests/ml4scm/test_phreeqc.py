import pytest
import re
from ml4scm.phreeqc import PHREEQC

def test_filter_react_states():
    input_obs	= '           1	       react	        3.56	  9.6316e-08	  2.9772e-09	  6.1726e-10	  1.7752e-17	  7.4692e-26	  4.4651e-08	  1.9047e-13	  2.3979e-04	  1.1088e-09	  4.7299e-15	  5.9546e-06 '
    assert PHREEQC._filter_react_states([input_obs,input_obs], 2) == [re.split(r"\s+", input_obs), re.split(r"\s+", input_obs)]




