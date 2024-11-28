from setuptools import setup, find_packages

setup(
    name="treeline",
    version="0.1.0",
    packages=find_packages(),
    description="A simple ASCII tree structure generator",
    author="oha",
    author_email="none",
    url="https://github.com/duriantaco/treeline",
    entry_points={
        'console_scripts': [
            'treeline=treeline.core:main',
        ],
    },
)