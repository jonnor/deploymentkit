#!/usr/bin/env python

from distutils.core import setup

setup(name='DeploymentKit',
    version='0.0.1',
    description='Easy deployment of software using platform-native packages',
    author='Jon Nordby',
    author_email='jononor@gmail.com',
    url='http://www.jonnor.com', # TEMP
    packages=['deploymentkit'],
    scripts=['bin/dk-generate'],
    )
