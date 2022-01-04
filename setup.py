import os

from setuptools import find_packages, setup

VERSION = "0.0.3"
DESCRIPTION = "Space-Track Pull through TLE cache"
LONG_DESCRIPTION = "This is a utility to cache and index TLE files from space-track.org"

REQUIRED = [
    "requests",
    "rush",
    "spacetrack",
]

DEV_REQUIRES = [
    "black",  # Linting
    "pre-commit", # Hooks
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
