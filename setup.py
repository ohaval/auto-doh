from setuptools import setup, find_packages

PACKAGE_NAME = "doh"
VERSION = "0.0.1"


def parse_requirements(filename: str):
    with open(filename, "r") as fh:
        return fh.readlines()


setup(name=PACKAGE_NAME,
      version=VERSION,
      description="A simple, lightweight piece of code to report doh.",
      packages=find_packages(),
      install_requires=parse_requirements("requirements.txt"))
