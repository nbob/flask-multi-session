"""
Flask-Multi-Session
==============

Flask-Multi-Session provides to store sessions in Mongo for Flask apps

"""

import os

from distutils.core import setup

module_path = os.path.join(os.path.dirname(__file__), 'flask_multisession.py')
version_line = [line for line in open(module_path)
                if line.startswith('__version_info__')][0]

__version__ = '.'.join(eval(version_line.split('__version_info__ = ')[-1]))


def get_requirements():
    with open('requirements.txt') as f:
        rv = f.read().splitlines()
    return rv


setup(
    name='Flask-Multi-Session',
    version=__version__,
    url='https://github.com/nbob/flask-multi-session',
    license='MIT',
    author='Nikita Bobrov',
    author_email='evil.bobior@gmail.com',
    description='Mongo multidevice sessions for Flask apps',
    py_modules=['flask_multisession'],
    zip_safe=False,
    package_data={'': ['.travis.yml', 'LICENSE']},
    include_package_data=True,
    platforms='any',
    requires=['pymongo', 'flask'],
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
