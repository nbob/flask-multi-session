from flask import Flask, session, redirect, url_for
from flask_multisession import MongoSessionInterface
import random

app = Flask(__name__)
app.secret_key = 'SECRET_KEY'


@app.route('/')
def index():
    user_id = session.get('user_id')
    if user_id is not None:
        return """
            Hello. This is index page. Your login is %s.</br>
            <a href="/logout">Logout</a></br>
            <a href="/logout_all_devices">Logout from all devices</a>
          """ % user_id
    else:
        return 'Hello. This is index page. Please <a href="/login">login</a>.'


@app.route('/login')
def login():
    session['user_id'] = random.randint(1, 10000)
    return redirect(url_for('index'))


@app.route('/logout')
def logout():
    del session['user_id']
    return redirect(url_for('index'))


@app.route('/logout_all_devices')
def logout_all_devices():
    session.clear_user_sessions()
    return redirect(url_for('index'))


app.session_interface = MongoSessionInterface()

if __name__ == '__main__':
    app.run()
