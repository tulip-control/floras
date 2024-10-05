# Floras: Flow-Based Reactive Test Synthesis for Autonomous Systems

<p align="center">
  <img src="https://raw.githubusercontent.com/jgraeb/floras/refs/heads/main/docs/logo.png" width="250" />
</p>

Floras documentation can be found [here](https://floras.readthedocs.io).

### Requirements
Floras requires `Python>=3.10` and a C++17-compliant compiler (for example `g++>=7.0` or `clang++>=5.0`).
You can check the versions by running `python --version` and `gcc --version`.
#### MacOS
If you are using a Mac, please pre-install [graphviz](https://graphviz.org) and [pygraphviz](https://pygraphviz.github.io).
Using [conda](https://conda.org/):
```
conda install --channel conda-forge pygraphviz
```
Or otherwise please install it via brew and pip:
```
brew install graphviz
pip install pygraphviz
```
## Installing Floras

To install floras, please clone the repository:
```
git clone https://github.com/tulip-control/floras.git
```
We are using [pdm](https://pdm-project.org/en/latest/) to manage the dependencies.
```
pip install pdm
```
Navigate to the repo to install floras and all required dependencies:
```
cd floras
pdm install
```
Next, install [spot](https://spot.lre.epita.fr/) by running:
```
pdm run python get_spot.py
```
If you are using [conda](https://conda.org/), instead of the above command, you can install spot directly from [conda-forge](https://conda-forge.org/) (this is faster). This does not work on MacOS, please use the above command to build spot in that case.
```
conda install -c conda-forge spot
```
If the spot installation does not work, please install it according to the instructions on the [spot website](https://spot.lre.epita.fr/install.html).

To enter the virtual environment created by pdm:
```
$(pdm venv activate)
```
For installation instructions and troubleshooting, please visit [this page](https://floras.readthedocs.io/en/latest/contributing/).


The floras repository contains implementations of the algorithms developed in the following paper:

[Josefine B. Graebener*, Apurva S. Badithela*, Denizalp Goktas, Wyatt Ubellacker, Eric V. Mazumdar, Aaron D. Ames, and Richard M. Murray. "Flow-Based Synthesis of Reactive Tests for Discrete Decision-Making Systems with Temporal Logic Specifications." ArXiv abs/2404.09888 (2024).](https://arxiv.org/abs/2404.09888)
