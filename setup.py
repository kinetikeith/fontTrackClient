from setuptools import setup, find_packages

import sys

def getDependencies():
    with open('requirements.txt') as f:
        return [l.strip() for l in f.readlines()]


py2exe = None

if(sys.platform.startswith('win32')):
    import py2exe

setup(
    name = "fonttrackclient",
    version = '0.0.1',
    author = "Keith Hartman",
    author_email = "khman32@protonmail.com",
    description = "Prototype font tracking client",
    install_requires=getDependencies(),
    packages=find_packages("."), 
    scripts=['main.py'],
    console=['main.py']
    )

