#!/usr/bin/env python3

from setuptools import setup

setup(
    name="btp2-monitor",
    version="0.1.0",
    py_modules=['btp2-monitor'],
    install_requires=[
        'iconsdk',
        'click',
        'web3',
        'requests',
        'textual',
    ],
    entry_points={
        'console_scripts': [
            'btp2-monitor=btp2-monitor.main:main',
        ]
    }
)
