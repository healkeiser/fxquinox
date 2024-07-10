"""PyPI setup script."""

# Built-in
from setuptools import setup, find_packages
from pathlib import Path

# Metadata
__author__ = "Valentin Beaumont"
__email__ = "valentin.onze@gmail.com"


###### CODE ####################################################################


# Add `README.md` as project long description
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="fxquinox",
    version="0.0.1",
    long_description=long_description,
    long_description_content_type="text/markdown",
    description="USD centric pipeline for feature animation and VFX projects.",
    url="https://github.com/healkeiser/fxquinox",
    author="Valentin Beaumont",
    author_email="valentin.onze@gmail.com",
    license="MIT",
    keywords="VFX USD Qt Houdini Maya Nuke PySide2 DCC UI",
    packages=find_packages(),
    install_requires=[
        "fxgui",
        "colorama",
    ],
    include_package_data=True,
)

# To install as a local editable package:
# python -m pip install -e .
