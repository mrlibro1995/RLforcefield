from setuptools import find_packages, setup

setup(
    name='rlff',
    packages=find_packages(include=['rlff']),
    version='0.1.0',
    description='Reinforcemt Learning Force Field Library',
    author='Me',
    license='MIT',
    install_requires=[],
    setup_requires=['pytest-runner'],
    tests_require=['pytest==4.4.1'],
    test_suite='tests', 
)