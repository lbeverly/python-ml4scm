import os.path
import shutil
import subprocess
import numpy as np
import re
from dataclasses import dataclass
from typing import Optional, Tuple, List, cast, IO

@dataclass
class PHREEQCOutput:
    """
    The output of the external phreeqc binary.

    stdout, stderr: string-output of the command execution
    output: numpy n-dimensional array of simulation number vs
            analyte concentration from the .sel file
    """
    stdout: str
    stderr: str
    output: np.ndarray


class PHREEQC:
    """
    phreeqc invocation wrapper class
    """
    def __init__(self, path: Optional[str] = None) -> None:
        """
        path: absolute path to phreeqc binary.
              PATH will be searched if not provided.
        """
        self._path = path
        if self._path is None:
            self._path = shutil.which(cmd='phreeqc')
        if self._path is None:
            raise RuntimeError('Cannot find phreeqc, please specify absolute path to phreeqc')
        return

    @staticmethod
    def write_db_from_template(template_filename: str, pars: List[str], values: List[str],
                               outfile: Optional[str] = None) -> None:
        """
        Write a database from a template, parameters will be
        literally replaced with values.

        template_filename: thermodynamic database name
        pars:              array of parameter names
        values:            array of parameter values
        outfile:           optional name of output file;
                           defaults to name of template_filename
                           without the .tpl extension
        """
        with open(template_filename + '.tpl', 'r') as fd:
            fd.readline()  # Discard first line of file
            c = fd.read()  # read remainder of file

        # Replace the target string
        for i in range(len(pars)):
            c = c.replace(pars[i], str(values[i]))

        if outfile is None:
            outfile = template_filename

        # Write the file out again
        with open(outfile + '.txt', 'w') as fd:
            fd.write(c)
        return

    # helper function to get col indices of "sim", "state", and "U" for use in readOutput
    # so it can be more robust with different phreeqc output formats
    @staticmethod
    def _get_col_indices(file: IO, elems: List[str]) -> list:
        # file: file object to read
        # return: list of 2 indices and an analytes list for use in readOutput
        c = file.readline()
        headers = re.split(r"[\s,\"]+", c)

        # try to find the indices if they exist
        # otherwise print error message
        try:
            sim = headers.index("sim")
        except ValueError:
            print("error: sim not found")
            print(headers)
            raise
        try:
            state = headers.index("state")
        except ValueError:
            print("error: state not found")
            print(headers)
            raise
        analytes = []
        for elem in elems:
            try:
                idx = headers.index(elem)
                analytes.append(idx)
            except ValueError:
                print("error: key \"{}\" not found".format(elem))
                print(headers)
                raise

        # print(headers)
        return [sim, state, analytes]

    @staticmethod
    def _filter_react_states(input_obs: List[str], idx: int) -> List[List[str]]:
        return [x for x in [re.split(r"[\s,\"]+", line) for line in input_obs] if x[idx] == "react"]

    @classmethod
    def read_output(cls, filename: str, analytes: Optional[List[str]] = None) -> np.ndarray:
        """
        This reads a .sel file produced by phreeqc and parses the output into
        an n-dimensional array.

        filename: output .sel file name that we intend to read
        analytes: list of analytes names to find; Defaults to U concentration
        return:   numpy array of simulation number vs analyte concentration
        """
        if analytes is None:
            analytes = ['U']

        with open(filename, 'r') as f:
            try:
                # assign indices
                i_sm, i_st, i_elems = cls._get_col_indices(f, analytes)
            except ValueError:
                raise ValueError("failed to parse columns of {}".format(filename))

            # finish reading the file if getColIndicies didn't error
            input_obs = f.readlines()

        # filter out states for 'react' state (assuming all states are i_soln or react)
        obs = PHREEQC._filter_react_states(input_obs, i_st)

        # set up output matrix

        # column of simulation numbers
        opt = np.array([int(row[i_sm]) for row in obs])

        for i_elem in i_elems:
            values = np.array([float(row[i_elem]) for row in obs])
            opt = np.vstack((opt, values))

        return opt

    def run_phreeqc(self, in_file: str, out_file: str,
                    db_file: str, screen_output: Optional[str] = None) -> Tuple[str, str]:
        """
        Low-level method to invoke phreeqc.
        Takes the same arguments as the phreeqc binary itself.
        in_file and db_file must exist if specified;
        out_file will be overwritten.

        in_file:       input file for phreeqc
        out_file:      output file for phreeqc
        db_file:       database file
        screen_output: screen output file
        return:        a tuple of stdout, stderr
        """

        if not os.path.exists(in_file):
            raise ValueError(f'in_file: {in_file} not found')
        if not os.path.exists(db_file):
            raise ValueError(f'db_file: {db_file} not found')

        args = [cast(str, self._path), in_file, out_file, db_file]
        if screen_output is not None:
            args.append(screen_output)

        pid = subprocess.run(
                args=args,
                shell=False,
                check=True,
                stdin=None,
                capture_output=True,
                text=True
        )

        return pid.stdout, pid.stderr

    @staticmethod
    def find_selected_output_filename(in_filename: str) -> str:
        with open(in_filename, 'r') as fd:
            for line in fd.readlines():
                m = re.match(r'\s*-file\s+(.*?)\s*$', line)
                if m:
                    return m.group(1)
        return 'selected.out'

    def run(self, db_filename: str, in_filename: str, analytes: Optional[List[str]]=None) -> PHREEQCOutput:
        """
        Run phreeqc with input and database files.
        Output will be output.out and output.sel.
        Reads output into numpy array and returns a PHREEQCOutput.

        db_filename: name of database to pass to phreeqc
        in_filename: name of input file to pass to phreeqc
        return:      PHREEQCOutput
        """
        stdout, stderr = self.run_phreeqc(
            in_file=in_filename,
            out_file='output.out',
            db_file=f'{db_filename}.txt'
        )
        output = self.read_output(self.find_selected_output_filename(in_filename), analytes)

        return PHREEQCOutput(stderr=stderr, stdout=stdout, output=output)