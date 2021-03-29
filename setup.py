from setuptools import setup

with open('README.md') as f:
    long_description = f.read()

setup(
    name='phi-accrual-failure-detector',
    packages=['phi-accrual-failure-detector'],
    version='0.3.3',
    license='MIT',
    description='A port of the Akka\'s (φ) Accrual failure detector implementation',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='samuele.resca',
    author_email='samuele.resca@gmail.com',
    url='https://github.com/samueleresca/phi-accrual-failure-detector',
    download_url='https://github.com/samuele.resca/phi-accrual-failure-detector/archive/v_01.tar.gz',
    keywords=['distributed-systems', 'fault-tolerance', 'fault-tolerant', 'fault-detection'],
    install_requires=[
        'atomos'
    ],
    classifiers=[],
)
