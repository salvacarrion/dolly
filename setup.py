from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(name='dolly',
      version='0.0.1',
      description='Dolly is a simple program to find your doubles',
      url='https://github.com/salvacarrion/dolly',
      author='Salva Carrión',
      license='MIT',
      install_requires=requirements,
      zip_safe=False,
      entry_points={
          'console_scripts': [
              'dolly = dolly:main'
          ]
      },
      )