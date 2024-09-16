# PyAudio Audio-Signal-Processing Practice

This repository is PyAudio Audio-Signal-Processing Practice Test Code.

## Python Version

This repository is used "**Python 3.11**".
I recommend setting up "**venv**" with python version = "3.11".
venv setup is below commands.

`python -m venv .venv`

## pip Requirements

pip requirements install command is below.

`pip install -r ./requirements.txt`

## Note

- This repository is used direnv.

  - Please install `direnv` and execute `direnv allow` commands at Repository Top directory.
    (If you use Windows, please execute `.\.venv\Scripts\activate` commnads)

- If you deploy on Raspberry Pi OS, you should install below apt package for pip installing scipy, matplotlib.

  - `sudo apt install cmake`
  - `sudo apt install gfortran`
  - `sudo apt install llvm`
