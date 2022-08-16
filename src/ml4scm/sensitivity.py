from SALib.analyze import morris as sam
from SALib.analyze import sobol as sas

import numpy as np

from .simulation import SimulationRunner


# runs run_sims and formats analyte results into matrix of iteration# and observation
# save matrix results into file
# write function to load file later
def ensemble_sim(phreeqc, problem, params, analyte=['U'], savefile=''):
    # analyte: single analyte to measure; name of colummn from phreeqc .sel output file
    # savefile: saves results array to a .npy file. needs to contain '.npy' in name
    #    also saves params array as 'savefile_p.npy'
    # return: #simulations by #observations matrix

    sim = SimulationRunner(phreeqc)
    sims = sim.run_problem(problem=problem, values=params, analytes=analyte)

    # [0][1] index of run_sims will be the list of analyte values
    output = sims[0][1]
    for sim in sims[1:]:
        output = np.vstack((output, sim[1]))

    if savefile:
        if ".npy" in savefile:
            np.save(savefile, output)
            sfp = savefile.split(".npy")[0] + "_p.npy"
            np.save(sfp, params)
        else:
            print("error: savefile name \"{}\" does not contain '.npy': Results not saved." \
                  .format(savefile))

    return output


def load_sim(savefile):
    if ".npy" not in savefile:
        print("error: file name \"{}\" does not contain '.npy'".format(savefile))
        return
    return np.load(savefile)


# generates a list of morris result dictionaries per parameter
def morris_analysis(problem, X, Y):
    # Perform Morris analysis on first parameter
    morris_result = [sam.analyze(problem.to_salib(), X, Y.T[0], conf_level=0.95, num_levels=4,
                                 print_to_console=False)]

    # Storing the sensitivity indices as a list of dictionaries
    # each dictionary represents the results for one observation
    for i_obs in range(1, np.shape(Y)[1]):
        Si = sam.analyze(problem.to_salib(), X, Y.T[i_obs], conf_level=0.95, num_levels=4,
                         print_to_console=False)
        morris_result.append(Si)

    #     # Making a matrix of observations by parameters
    #     mu_all = morris_result[0].get("mu")
    #     for obs in morris_result[1:]:
    #         mu_all = np.vstack((mu_all, obs.get("mu")))

    return morris_result


def dictionaries_to_matrix(dlist, key):
    # helper function to convert SALib dictionary results back into matrices
    mtrx = dlist[0].get(key)
    for d in dlist[1:]:
        mtrx = np.vstack((mtrx, d.get(key)))
    return mtrx


def morris_summary(morris_res):
    # returns SALib dictionary results in matrix form by (parameter, simulation#)
    return dictionaries_to_matrix(morris_res, "mu").T, dictionaries_to_matrix(morris_res, "mu_star").T, \
           dictionaries_to_matrix(morris_res, "sigma").T, dictionaries_to_matrix(morris_res, "mu_star_conf").T


def sobol_analysis(problem, X, Y):
    # Perform sobol analysis on parameter 1
    sobol_result = [sas.analyze(problem.to_salib(), Y.T[0], conf_level=0.95, print_to_console=False)]

    # Storing the sensitivity indices as a list of dictionaries
    # each dictionary represents the results for one observation
    # returning this list instead gets a lot more information, but it might not
    # be necessary for now
    for i_obs in range(1, np.shape(Y)[1]):
        Si = sas.analyze(problem.to_salib(), Y.T[i_obs], conf_level=0.95, print_to_console=False)
        sobol_result.append(Si)

    return sobol_result