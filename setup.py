"""
Flask-Redis-Session
==============

Flask-Redis-Session provides to store sessions in Redis for Flask apps

"""

import sys, os

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


module_path = os.path.join(os.path.dirname(__file__), 'flask_redis_session.py')
version_line = [line for line in open(module_path)
                if line.startswith('__version_info__')][0]

__version__ = '.'.join(eval(version_line.split('__version_info__ = ')[-1]))



def get_requirements():
  with open('requirements.txt') as f:
    rv = f.read().splitlines()
  return rv


setup(
  name='Flask-Redis-Session',
  version=__version__,
  url='https://github.com/atkin1450/flask-redis-session',
  license='MIT',
  author='Nikita Bobrov',
  author_email='atkin1450@gmail.com',
  description='Redis sessions for Flask apps',
  py_modules=['flask_redis_session'],
  zip_safe=False,
  package_data={'': ['.travis.yml', 'LICENSE', 'requirements.txt']},
  include_package_data=True,
  platforms='any',
  install_requires=get_requirements(),
  classifiers=[
    'Development Status :: 5 - Production/Stable',
    'Environment :: Web Environment',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    'Topic :: Software Development :: Libraries :: Python Modules'
  ]
)
