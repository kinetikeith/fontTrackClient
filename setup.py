from setuptools import setup

def getDependencies():
    with open('requirements.txt') as f:
        return [l.strip() for l in f.readlines()]

setup(
    name = "fonttrackclient",
    version = '0.0.1',
    author = "Keith Hartman",
    author_email = "khman32@protonmail.com",
    description = "Prototype font tracking client",
    install_requires=getDependencies(),
    scripts=['main.py']
    )

