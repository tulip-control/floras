# Contributing to FLORAS

If you want to modify FLORAS or contribute, you can also install it directly from source. We are using pdm to manage the dependencies.
```
pip install pdm
git clone https://github.com/tulip-control/floras.git
```
Navigate to the repo and run to install the FLORAS and all required dependencies:
```
pdm install
```
Next, install spot by running
```
pdm run python get_spot.py
```
To enter the virtual environment created by pdm:
```
$(pdm venv activate)
```

If you need to add dependencies you can do that by running:
```
pdm add your_dependency_here
```
