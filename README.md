# Reddit X-ray Automated Systems 

This set of files are various Python programs for Reddit X-ray. The files consist of the following, as of December 19, 2023: 

- `cwl.py` -- this is a Python program designed to automatically keep track of CWL weighted random distribution data per month. To use this file, you must have created a virtual environment and have installed the packages present in `requirements.txt`. 
- `strikes.py` -- this is a Python program, that given manual user input, outputs a file containing strikes. To use this file, you must have created a virtual environment and have installed the packages present in `requirements.txt`.
- `analysis.py` -- this is a Python program designed to emulate manual user input by taking in raw inputs from Minion Bot & Sidekick, and formatting them for use in `strikes.py`. 
- `weights.py` -- this is a Python program designed to read the screen to automatically capture war weights, dumping them in `weights.txt`
