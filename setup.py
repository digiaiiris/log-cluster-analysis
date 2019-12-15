#!/usr/bin/python

# Python imports
import os
from setuptools import setup

setup(
    name="log-cluster-analysis",
    version="1.0.0",
    author="Tommi Palomaki",
    author_email="tommi.palomaki@digia.com",
    description="Log file cluster analysis",
    url="https://github.com/digiaiiris/log-cluster-analysis/",
    license="MIT",
    packages=["ic_analysis"],
    entry_points={
        "console_scripts": [
            "log_cluster_analysis = ic_analysis.log_cluster_analysis:main"
        ]
    }
)
