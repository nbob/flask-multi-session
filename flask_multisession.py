import pymongo
from pymongo import MongoClient

__version_info__ = ('0', '2', '1')
__version__ = '.'.join(__version_info__)
__author__ = 'Nikita Bobrov'
__license__ = 'MIT/X11'
__copyright__ = '(c) 2017 by Nikita Bobrov'

from datetime import datetime
from uuid import uuid4
from werkzeug.datastructures import CallbackDict
from flask.sessions import SessionInterface, SessionMixin


class MongoSessionManager:
    collection_name = 'sessions'

    def __init__(self, db='flask_multisession', permanent=True, *args, **kwargs):
        self._permanent = permanent
        self._client = MongoClient(*args, **kwargs)
        self._db = self._client[db]
        self._collection = self._db[self.collection_name]
        self._check_indexes()

    def _check_indexes(self):
        sid_index = False
        uid_index = False
        ttl_index = False
        for _, index in enumerate(self._collection.list_indexes()):
            if index['key'].get('session_id') is not None:
                sid_index = True
            if index['key'].get('user_id') is not None:
                uid_index = True
            if index['key'].get('expired') is not None:
                ttl_index = True

        if not sid_index:
            self._collection.create_index([('session_id', pymongo.HASHED)])

        if not uid_index:
            self._collection.create_index([('user_id', pymongo.HASHED)], sparse=True)

        if not ttl_index:
            self._collection.create_index('expired', expireAfterSeconds=0)

    def get_session(self, sid):
        uid = None
        data = {}
        if sid:
            session = self._collection.find_one({'session_id': sid})
            if session is not None:
                uid = session.get('user_id', uid)
                data = session.get('data', {})
        else:
            sid = str(uuid4())
        session = MongoSession(
            data=data,
            session_id=sid,
            user_id=uid,
            permanent=self._permanent,
            manager=self
        )
        return session

    def update_session(self, session, expired):
        sid = session.session_id
        data = {
            'session_id': sid,
            'expired': expired,
            'last_update': datetime.now(),
            'data': dict(session)
        }
        if session.is_authenticated():
            data['user_id'] = session.user_id
        self._collection.replace_one({'session_id': sid}, data, upsert=True)

    def logout_all_devices(self, session):
        if session.user_id is not None:
            self._collection.update_many(
                {'user_id': session.user_id},
                {'$unset': {'user_id': ''}}
            )


class MongoSession(CallbackDict, SessionMixin):
    def __init__(self, data={}, session_id=None, user_id=None, permanent=None, manager=None):
        self.manager = manager
        self.session_id = session_id
        self.user_id = user_id
        self.modified = False
        self.permanent = permanent

        def on_update():
            self.modified = True

        CallbackDict.__init__(self, data, on_update)

    def login(self, uid):
        self.user_id = uid
        self.modified = True

    def logout(self):
        self.user_id = None
        self.modified = True

    def is_authenticated(self):
        return self.user_id is not None

    def logout_all_devices(self):
        self.manager.logout_all_devices(self)
        self.logout()


class MongoSessionInterface(SessionInterface):
    collection_name = 'sessions'

    def __init__(self, *args, **kwargs):
        self._manager = MongoSessionManager(*args, **kwargs)

    def open_session(self, app, request):
        sid = request.cookies.get(app.session_cookie_name)
        return self._manager.get_session(sid)

    def save_session(self, app, session: MongoSession, response):
        domain = self.get_cookie_domain(app)
        sid = session.session_id
        expired = self.get_expiration_time(app, session)
        response.set_cookie(app.session_cookie_name, sid, expires=expired, httponly=True, domain=domain)

        if session.modified or expired:
            self._manager.update_session(session, expired)
