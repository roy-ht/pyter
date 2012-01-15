from setuptools import setup
import sys

install_requires = ['distribute']
if sys.hexversion < 0x2070000:
    install_requires += ['argparse']
setup(name='pyter',
      version='0.1.1',
      description='Simple ffuzzy matching library using Translation Error Rate algorithm',
      author='Hiroyuki Tanaka',
      author_email='aflc0x@gmail.com',
      url='https://github.com/aflc/pyter',
      platforms = "any",
      packages=['pyter'],
      install_requires=install_requires,
      classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Information Technology',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Text Processing',
        ],
      )
