  Flask-Multi-Session [![build status](https://travis-ci.org/nbob/flask-multi-session.svg?branch=master)](https://travis-ci.org/nbob/flask-multi-session) [![build status](https://img.shields.io/pypi/l/Flask-Multi-Session.svg)](https://pypi.python.org/pypi/Flask-Multi-Session)
==============

__Flask-Multi-Session__ provides __Mongo__ session storage for __Flask__ apps. This module allows you to manage user sessions from different devices, thus you can logout user from all devices. __Flask-Multi-Session__ supports python>=3.5.

Installation
--------------
Install __Flask-Multi-Session__ from __pip__.

`pip3 install flask-multi-session`

Usage
--------------
~~~~~~~~~~~~~~
from flask import Flask, session, redirect, url_for
import random

app = Flask(__name__)

@app.route('/')
def index():
  user_id = session.get('user_id')
  if user_id is not None:
    return """
      Hello. This is index page. Your login is %s.<\br>
      <a href="/logout">Logout</a> <a href="/logout_all_devices">Logout from all devices</a>
    """ % user_id
  else:
    return 'Hello. This is index page. Please <a href="/login">login</a>.'

@app.route('/login')
def login():
  session.login(random.randint(1, 10000))
  return redirect(url_for('index'))

@app.route('/logout')
def logout():
  session.logout()
  return redirect(url_for('index'))

@app.route('/logout_all_devices')
def logout_all_devices():
  session.logout_all_devices()
  return redirect(url_for('index'))

from flask_multisession import MongoSessionInterface
app.session_interface = MongoSessionInterface()


if __name__ == '__main__':
  app.run()
~~~~~~~~~~~~~~

**Important!** Use "user_id" as a key for unique user id and add one to session after successful login.

**Important!** Added new method __clear_user_sessions__ to [Session class](http://flask.pocoo.org/docs/0.10/api/#sessions).

Example: `session.clear_user_sessions()` delete all sessions for current user, but you can specify user_id: `session.clear_user_sessions(user_id=23)` delete all sessions for user with id=23.

Set Mongo
--------------
If you have a remote __Mongo__ you may specify one in __MongoSessionInterface__ constructor.

~~~~~~~~~~~~~~

mongo_config = dict(
  host='192.168.0.1',
  port=27017
)

from flask.ext.multisession import MongoSessionInterface
app.session_interface = MongoSessionInterface(**mongo_config)
~~~~~~~~~~~~~~
