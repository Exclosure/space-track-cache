import os

from setuptools import find_packages, setup

DESCRIPTION = "Space-Track Pull through TLE cache"
LONG_DESCRIPTION = "This is a utility to cache and index TLE files from space-track.org"

# Note: Version set in stcache/__version__.py

REQUIRED = [
    "requests",
    "rush",
    "spacetrack",
]

DEV_REQUIRES = [
    "black",  # Linting
    "pre-commit",  # Hooks
    "pytest",  # Testing
    "pylint",  # Linting
]

_DIRECTORY = os.path.abspath(os.path.dirname(__file__))
with open(
    os.path.join(_DIRECTORY, "server", "requirements.txt")
) as server_requirements:
    SERVER_REQUIRES = server_requirements.readlines()


EXTRAS = {
    "dev": DEV_REQUIRES,
    "server": SERVER_REQUIRES,
}

<<<<<<< HEAD
=======
# Read in the version from __version__.py
def get_version_info(module: str):
    """Execute a module's __version__.py file and return the variables.

    This approach is used because the setup.py file should not
    attempt to import the modules that it is setting up.
    """
    here = os.path.abspath(os.path.dirname(__file__))
    about = {}
    with open(os.path.join(here, "stcache", "__version__.py")) as f:
        exec(f.read(), about)
    return about


VERSION = get_version_info("stcache")["__version__"]


# Setting up
setup(
    name="stcache",
    version=VERSION,
    author="TheExclosure",
    author_email="<matt@exclosure.io>",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=["stcache"],
    install_requires=REQUIRED,
    extras_require=EXTRAS,
    keywords=["satellite", "TLE", "orbit", "astronomy"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Astronomy",
    ],
)
