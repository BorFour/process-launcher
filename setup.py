from setuptools import setup, find_packages

setup(name='process_launcher',
      version='0.0.1',
      description='Tool to launch predefined groups of commands in a terminal',
      packages=find_packages(),
      entry_points={
          'console_scripts': [
              'process_launcher = src.app_window:main'
          ],
      },
      author='Borja Fourquet'
      )
