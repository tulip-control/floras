# Contributing to FLORAS

If you want to modify FLORAS or contribute, you can install it directly from source. We are using pdm to manage the dependencies.
```
pip install pdm
git clone https://github.com/tulip-control/floras.git
```
Navigate to the repo to install floras and all required dependencies:
```
cd floras
pdm install
```
Next, install spot by running:
```
pdm run python get_spot.py
```
If you are using [conda](https://conda.org/), instead of the above command, you can install spot directly from [conda-forge](https://conda-forge.org/) (this is faster):
```
conda install -c conda-forge spot
```
If the spot installation does not work, please install it according to the instructions on the [spot website](https://spot.lre.epita.fr/install.html).

To enter the virtual environment created by pdm:
```
$(pdm venv activate)
```
Now FLORAS is ready to use. If there are problems installing FLORAS, please create an issue on GitHub.

If you need to add any new dependencies you can do that by running:
```
pdm add your_dependency_here
```
