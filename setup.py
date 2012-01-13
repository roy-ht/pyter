from setuptools import setup
import sys

install_requires = ['distribute']
if sys.hexversion < 0x2070000:
    install_requires += ['argparse']
setup(name='pyter',
      version='0.1',
      description='Simple ffuzzy matching library using Translation Error Rate algorithm',
      author='Hiroyuki Tanaka',
      author_email='aflc0x@gmail.com',
      url='https://github.com/aflc/pyter',
      packages=['pyter'],
      install_requires=install_requires,
      )
