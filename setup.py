#!/usr/bin/env python
"""Setup script for pkpass"""
import os
import shutil
from setuptools import setup
import versioneer

def rcfile_check():
    """Copy example rc file if one does not exist"""
    home = os.path.expanduser("~")
    here = os.path.abspath(os.path.dirname(__file__))
    rc_location = os.path.join(home, ".pkpassrc")
    example_location = os.path.join(here, 'example_pkpassrc')
    if os.path.exists(rc_location):
        if os.path.isdir(rc_location):
            print("WARN: default rc file location is a directory")
        else:
            print(".pkpassrc already defined, skipping")
            return
    else:
        print("Copying example rc file to %s" % rc_location)
        shutil.copyfile(example_location, rc_location)

setup(
    version=versioneer.get_version(),
    install_requires=[
        'PyYAML>=4.2b1',
        'colored>=1.4.0',
        'cryptography>=2.3',
        'exrex>=0.10.5',
        'pem>=20.1.0',
        'pyperclip>=1.6.0',
        'pyseltongue>=0.3.1',
        'setuptools>=41.2.0',
    ],
    extras_require={
        'testing': ["mock", "tox"]
    },
    cmdclass=versioneer.get_cmdclass(),
    )

try:
    rcfile_check()
except FileNotFoundError as err:
    print("WARN: could not copy example rc file")
