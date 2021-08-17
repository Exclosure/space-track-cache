from setuptools import setup, find_packages

VERSION = '0.0.2' 
DESCRIPTION = 'Space-Track Pull through TLE cache'
LONG_DESCRIPTION = 'This is a utility to cache and index TLE files from space-track.org'

# Setting up
setup(
        name="stcache", 
        version=VERSION,
        author="TheExclosure",
        author_email="<matt@exclosure.io>",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=["stcache"],
        install_requires=[
            "spacetrack==0.16.0",
            "requests==2.23.0"
        ],
        
        keywords=['satellite', 'TLE', 'orbit', 'astronomy'],
        classifiers= [
            "Development Status :: 4 - Beta",
            "Programming Language :: Python :: 3",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows",
            "Operating System :: POSIX :: Linux",
            "Intended Audience :: Science/Research",
            "Topic :: Scientific/Engineering :: Astronomy"
        ]
)