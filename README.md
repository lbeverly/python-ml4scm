# ML4SCM

## Installation

### Mac:

- Clone this repo:
  ```bash
	git clone git@github.com:lbeverly/python-ml4scm.git
  ```

- If you do not already have docker installed, Install Docker Desktop:
  https://www.docker.com/products/docker-desktop/
- Launch Docker Desktop
- If you do not already have xcode tools installed, run 
  ```bash
  xcode-select --install
  ```

- Change directory to where this repository is cloned.
- run: `make run` in your terminal
- After a bit of text, you should see something like:

  ```bash
	 To access the notebook, open this file in a browser:
	     file:///root/.local/share/jupyter/runtime/nbserver-11-open.html
	 Or copy and paste one of these URLs:
	     http://b4ae36fbff51:8888/?token=22c18087ca6feac817c08e35c3cf3a2605e24a036b73f4bf
	  or http://127.0.0.1:8888/?token=22c18087ca6feac817c08e35c3cf3a2605e24a036b73f4bf
  ```

- Click on one of the links to open jupyter in your browser
- You can launch the sample notebooks found under SampleProblems/ 

### Windows:

- Install Bash on Ubuntu for Windows:
	https://docs.microsoft.com/en-us/windows/wsl/install
- Clone this repo:
  ```bash
	git clone git@github.com:lbeverly/python-ml4scm.git
  ```

- If you do not already have docker installed, Install Docker Desktop:
  https://www.docker.com/products/docker-desktop/
- Launch Docker Desktop
- If you do not already have build-essentials installed:
  ```bash
  apt-get update && apt-get install build-essentials
  ```

- Change directory to where this repository is cloned.
- run: `make run` in your terminal
- After a bit of text, you should see something like:

  ```bash
	 To access the notebook, open this file in a browser:
	     file:///root/.local/share/jupyter/runtime/nbserver-11-open.html
	 Or copy and paste one of these URLs:
	     http://b4ae36fbff51:8888/?token=22c18087ca6feac817c08e35c3cf3a2605e24a036b73f4bf
	  or http://127.0.0.1:8888/?token=22c18087ca6feac817c08e35c3cf3a2605e24a036b73f4bf
  ```

- Click on one of the links to open jupyter in your browser
- You can launch the sample notebooks found under SampleProblems/ 

##### Notes:
This project has been set up using PyScaffold 4.1.4. For details and usage
information on PyScaffold see https://pyscaffold.org/.
