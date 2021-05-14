"""setup.py for function_limiter"""

__author__ = "Mohsen Ghorbani"
__email__ = "m.ghorbani2357@gmail.com"
__copyright__ = "Copyright 2021, Mohsen Ghorbani"

from setuptools import setup, find_packages
import os
import versioneer

this_dir = os.path.abspath(os.path.dirname(__file__))

REQUIREMENTS = filter(None, open('requirements/main.txt').read().splitlines())

setup(
    name='Function-Limiter',
    author=__author__,
    author_email=__email__,
    url="https://github.com/mghorbani2357/Function-Limiter",
    license="MIT",
    zip_safe=False,
    packages=find_packages(exclude=["tests*"]),
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    classifiers=[k for k in open('CLASSIFIERS').read().split('\n') if k],
    install_requires=list(REQUIREMENTS),
    long_description=open('README.rst').read() + open('HISTORY.rst').read(),
    long_description_content_type='text/x-rst',
    description='Rate limiting for callable functions',
)
