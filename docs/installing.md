# Installing FLORAS
### Requirements
FLORAS requires `Python>=3.10` and a C++17-compliant compiler (for example `g++>=7.0` or `clang++>=5.0`).
You can check the versions by running `python --version` and `gcc --version`.

### From Source
If you want to modify FLORAS or contribute, you can install it directly from source (see [here](contributing.md)).

### Troubleshooting
Here are common errors we encountered and what we learned to fix the problem.

If you are on a Mac and your C++ compiler version is correct, but the build still fails, try adding the following command to your path:
```
export SDKROOT=$(xcrun --show-sdk-path)
```

FLORAS requires `spot`, which should be automatically installed. If its installation fails, please download [spot](https://spot.lre.epita.fr/install.html) from its source, follow the instructions, and repeat the FLORAS installation.
