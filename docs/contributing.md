# Contributing to FLORAS

If you want to modify FLORAS or contribute, you can also install it directly from source. We are using pdm to manage the dependencies.
```
pip install pdm
git clone url
```
Navigate to the repo and run to install the FLORAS and all required dependencies:
```
pdm install
```
Next, enter the virtual environment created by pdm:
```
$(pdm venv activate)
```
New dependencies can be added by running:
```
pdm add your_dependency_here
```
