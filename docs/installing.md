# Installing Floras
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

### From Source
To install floras directly from source, please clone the repository:
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

### Troubleshooting
Here are common errors we encountered and what we learned to fix the problem.

If you are on a Mac and your C++ compiler version is correct, but the build still fails, try adding the following command to your path:
```
export SDKROOT=$(xcrun --show-sdk-path)
```

If installing pygraphviz fails, you can try to install it using the following command:
```
pip install --no-cache-dir \
   --config-settings="--global-option=build_ext" \
   --config-settings="--global-option=-I$(brew --prefix graphviz)/include/" \
   --config-settings="--global-option=-L$(brew --prefix graphviz)/lib/" \
   pygraphviz
```

Floras requires `spot`, which should be automatically installed. If its installation fails, please download [spot](https://spot.lre.epita.fr/install.html) from its source, follow the instructions, and repeat the floras installation.
