# :coding: utf-8

import setuptools

setuptools.setup(
    name="portier",
    version="0.1.2",
    description=(
        "A tool to check a host address "
        "for open ports using multiple threads."
    ),
    long_description=open("README.rst").read(),
    keywords="host, localhost, web, port, scanner, thread",
    url="https://cb109@bitbucket.org/cb109/portier.git",
    author="Christoph Buelter",
    author_email="c.buelter@arcor.de",
    packages=setuptools.find_packages(),
    install_requires=[],
    entry_points={
        "console_scripts": [
            "portier=portier:main",
        ],
    }
)

