import os

from setuptools import setup, find_packages

requires = []

setup(
    name='kbsb',
    version='0.1.0',
    description='Royal Belgian Chess Federatin',
    long_description='',
    classifiers=[
        "Programming Language :: Python",
        "Framework :: Django-cms",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
    ],
    author='Ruben Decrop',
    author_email='ruben@decrop.net',
    url='https://www.frbe-kbsb.be',
    keywords='Chess, Belgium',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
)
