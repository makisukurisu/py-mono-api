from setuptools import setup, find_packages
from io import open
import re

def read(filename):
    with open(filename, encoding='utf-8') as file:
        return file.read()

with open('pymono/version.py', 'r', encoding='utf-8') as f:  # Credits: LonamiWebs
    version = re.search(r"^__version__\s*=\s*'(.*)'.*$",
                        f.read(), flags=re.MULTILINE).group(1)

setup(name='PyMonoLib',
      version=version,
      description='Monobank Python wrapper',
      long_description=read('readme.md'),
      long_description_content_type="text/markdown",
      author='makisukurisu',
      author_email='667strets@gmail.com',
      url='https://github.com/makisukurisu/py-mono-api',
      packages = find_packages('pymono', exclude = ['misc', 'examples']),
      license='GPL2',
      keywords='telegram api tools',
      install_requires=['requests'],
      extras_require={
          'json': 'ujson'
      },
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Programming Language :: Python :: 3',
          'Environment :: Console',
          'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
      ],
      )