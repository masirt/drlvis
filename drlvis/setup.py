#!/usr/bin/env python


from setuptools import setup


def get_required_packages():
    with open("requirements.txt") as f:
        return f.read().splitlines()


REQUIRED_PACKAGES = get_required_packages()

setup(name="drlvis",
      version='0.0',
      # list folders, not files
      packages=['drlvis'],
      scripts=['drlvis/server.py'],
      package_data={'drlvis': ['drlvis/dist']},
      include_package_data=True,
      entry_points={
          'console_scripts': [
              'drlvis = server:main'
          ]
      },
      install_requires=REQUIRED_PACKAGES,
      python_requires=">=3.0.*"
      )
