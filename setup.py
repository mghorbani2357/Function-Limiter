"""
setup.py for FunctionLimiter
"""

__author__ = "Mohsen Ghorbani"
__email__ = "m.ghorbani2357@gmail.com"
__copyright__ = "Copyright 2021, Mohsen Ghorbani"

from setuptools import setup, find_packages
import os
import versioneer

this_dir = os.path.abspath(os.path.dirname(__file__))

REQUIREMENTS = filter(None, open('requirements.txt').read().splitlines())

setup(
    name='Function Limiter',
    author=__author__,
    author_email=__email__,
    license="MIT",
    zip_safe=False,
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    install_requires=list(REQUIREMENTS),
    classifiers=[k for k in open('').read().split('\n') if k],
    description='Rate limiting for callable functions',
)
