from setuptools import setup, find_packages

setup(name='process_launcher',
      version='0.0.1',
      description='Tool to launch predefined groups of commands in a terminal',
    packages=['process_launcher'],
    package_dir={'process_launcher': 'src/'},
      entry_points={
          'console_scripts': [
              'process_launcher = process_launcher.app_window:main'
          ],
      },
      # data_files=[('.', ['img/*'])],
      package_data={'process_launcher': ['img/fontawesome/*.svg', 'img/fontawesome/regular/*.svg', 'img/fontawesome/solid/*.svg']},
      author='Borja Fourquet'
      )
