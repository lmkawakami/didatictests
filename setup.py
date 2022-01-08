#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['Click>=7.0', ]

test_requirements = [ ]

setup(
    author="Lincoln Makoto Kawakami",
    author_email='lmkawakami@hotmail.com',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="build simple tests to validate functions with configurable args, kwargs and user inputs",
    entry_points={
        'console_scripts': [
            'didatictests=didatictests.cli:main',
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='didatictests',
    name='didatictests',
    packages=find_packages(include=['didatictests', 'didatictests.*']),
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/lmkawakami/didatictests',
    version='0.0.1',
    zip_safe=False,
)
