#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open("README.md") as readme_file:
    readme = readme_file.read()

requirements = []

setup_requirements = []

test_requirements = []

setup(
    author="Omar Sharaki",
    author_email="omarsharaki@gmail.com",
    python_requires=">=3.5",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    description="A Software Library for Processing and Evaluating Travel Region Models",
    install_requires=requirements,
    long_description=readme,
    include_package_data=True,
    keywords="travel_regions",
    name="travel_regions",
    packages=find_packages(include=["travel_regions", "travel_regions.*"]),
    setup_requires=setup_requirements,
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/osharaki/travel_regions",
    version="0.3",
    zip_safe=False,
)
