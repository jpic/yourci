import os, sys
from setuptools import setup, find_packages, Command


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name='yourci',
    version='0.0.0',
    description='My dead simple CI server',
    author='James Pic',
    author_email='jpic@yourlabs.org',
    url='http://github.com/jpic/yourci',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    long_description=read('README.rst'),
    license='MIT',
    keywords='continuous integration github',
    install_requires=[
        'rq',
        'githubpy',
    ],
    classifiers=[
        'Development Status :: 1 - Alpha/Planning',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
