[![build status](https://travis-ci.org/atkin1450/flask-redis-session.svg?branch=master)](https://travis-ci.org/atkin1450/flask-redis-session)


Flask-Redis-Session
==============

__Flask-Redis-Session__ provides __Redis__ session storage for __Flask__ apps. This module allows you to manage user sessions from different devices, thus you can logout user from all devices. __Flask-Redis-Session__ supports python>=3.4.

Installation
--------------
Install __Flask-Redis-Session__ from __pip__.

`pip3 install flask-redis-session`

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
  session['user_id'] = random.randint(1, 10000)
  return redirect(url_for('index'))

@app.route('/logout')
def logout():
  del session = random.randint(1, 10000)
  return redirect(url_for('index'))

@app.route('/logout_all_devices')
def logout_all_devices():
  session.clear_user_sessions()
  return redirect(url_for('index'))

from flask_redis_session import RedisSessionInterface
app.session_interface = RedisSessionInterface()


if __name__ == '__main__':
  app.run()
~~~~~~~~~~~~~~

**Important!** Use "user_id" as a key for unique user id and add one to session after successful login.

**Important!** Added new method __clear_user_sessions__ to [Session class](http://flask.pocoo.org/docs/0.10/api/#sessions).

Example: `session.clear_user_sessions()` delete all sessions for current user, but you can specify user_id: `session.clear_user_sessions(user_id=23)` delete all sessions for user with id=23.

Set Redis
--------------
If you have a remote __Redis__ you may specify one in __RedisSessionInterface__ constructor. Also a `prefix` argument is available to set prefix for saving user sessions in __Redis__.

~~~~~~~~~~~~~~

import redis

redis_storage = redis.Redis(
  host='192.168.0.1',
  port=6379,
  db=2,
  password="password",
  charset='utf-8'
)

from flask_redis_session import RedisSessionInterface
app.session_interface = RedisSessionInterface(redis=redis_storage, prefix='session:')
~~~~~~~~~~~~~~
