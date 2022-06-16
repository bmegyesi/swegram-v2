"""Swegram setup"""
from setuptools import setup, find_packages
from pathlib import Path
from src.swegram.version import VERSION

BASE_PATH = Path.cwd()

REQUIREMENTS_PATH = Path.joinpath(BASE_PATH, 'requirements.txt')
if REQUIREMENTS_PATH:
    with open(REQUIREMENTS_PATH, mode='r') as dependency_file:
        dependencies = [d.strip() for d in dependency_file.readlines() if d.strip()]
else:
    dependencies = []


setup(
    name='swegram',
    version=VERSION,
    author='Uppsala University',
    description='',
    long_description='',
    packages=find_packages(exclude=['test*']),
    include_package_data=True,
    install_requires=dependencies,
    python_requires='>=3.6',
    classifiers=['Programming Language :: Python :: 3'],
    entry_points={
        'console_scripts': [
            'swegram=src.swegram.swegram:main'
        ]
    }
)




