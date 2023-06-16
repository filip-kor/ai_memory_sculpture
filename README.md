# AI Memory Sculpture
This repository is a part of COMP4029 Individual Programming Project at the University of Nottingham. This README file is a supplement to my master's dissertation document where all project's components are explained in detail. The document is accessible in this repository as `dissertation.pdf` [here](dissertation.pdf).

## Overview
This project contains a Flask web application described in the dissertation. It can be hosted locally after installing the dependencies.

## Project structure

The back-end is contained in *.py* files in the source directory.

The front-end is contained in *static/* and *templates/* directories.

```
ai_memory_sculpture
└───audio_processed
└───outputs
│       └───examples
└───recordings
│       └───examples
└───static
│       └───images
│       │   scripts.js
│       │   style.css
└───templates
│       └───Memory Sculpture Generator 
│       │   website.html
│   app.py
│   config.py
│   SculptureGenerator.py
│   EmotionExtractor.py
│   WaveProcessor.py
│   README.md
│   requirements.txt
```

## Dependencies Installation

### CadQuery

The dependencies installation was tested on Computer Science Windows Remote Desktop using the following steps.

1. Install Conda with Miniforge 3
```
curl -L -o miniforge.exe https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Windows-x86_64.exe
```
```
start /wait "" miniforge.exe /InstallationType=JustMe /RegisterPython=0 /NoRegistry=1 /NoScripts=1 /S /D=%USERPROFILE%\Miniforge3
```

2. Activate the base conda evrionment
```
cmd /K ""%USERPROFILE%/Miniforge3/Scripts/activate.bat" "%USERPROFILE%/Miniforge3""
```

3. Install the latest CadQuery version
```
conda install -c cadquery -c conda-forge cadquery=master
```

To do this on Linux, follow the instructions in [CadQuery Documentation](https://cadquery.readthedocs.io/en/latest/installation.html). To run it on an ARM-based Mac, you will have to create a Conda environment which emulates x86 architectures.

### Other dependencies

To install all the other dependencies please navigate to the source directory of the project and run the following command inside the conda environment:
```
pip install -r requirements.txt
```

Should there be any issues with the requirements document, there is a complete list of all the packages used to run the project on the Computer Science Windows Virtual Desktop in `requirements-full.txt`, and my personal Mac in `requirements-mac.txt`.

### IBM APIs

The project uses two IBM APIs:
- [Natural Language Understanding](https://cloud.ibm.com/apidocs/natural-language-understanding)
- [Speech to Text](https://cloud.ibm.com/apidocs/speech-to-text)

To use the application, you will need to create an account and fill in the API keys and URLs in `config.py`.

## Running the code

Run the following code to launch the Flask application. The website will be hosted locally on your device under the address printed in the command line.
```
python app.py
```
