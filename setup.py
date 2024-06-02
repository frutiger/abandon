from setuptools import setup

setup(name='abandon',
      version='0.4',
      description='Prune a list of snapshots from particular moments',
      url='https://github.com/frutiger/abandon',
      author='Masud Rahman',
      license='MIT',
      packages=['abandon'],
      entry_points={
          'console_scripts': ['abandon=abandon.__main__:main'],
      })

