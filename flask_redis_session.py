__version_info__ = ('0', '1', '0')
__version__ = '.'.join(__version_info__)
__author__ = 'Nikita Bobrov'
__license__ = 'MIT/X11'
__copyright__ = '(c) 2015 by Nikita Bobrov'


import json
from datetime import timedelta, datetime
from uuid import uuid4
from redis import Redis
from werkzeug.datastructures import CallbackDict
from flask.sessions import SessionInterface, SessionMixin
from werkzeug.local import Local
import dateutil.parser


local = Local()


def sync_user_sessions(redis, prefix, user_id):

  user_key = _get_user_prefix(user_id)
  sessions = redis.hgetall(user_key)

  del_sids = []

  for sid, value in sessions.items():
    sid = sid.decode()
    value = json.loads(value.decode())
    expires = value['expires']
    expires = dateutil.parser.parse(expires)

    if expires < datetime.now():
      del_sids.append(sid)
    else:
      session = redis.get("".join([prefix, sid]))
      if session:
        session = json.loads(session.decode())
        if user_id != session['user_id']:
          del_sids.append(sid)


  if len(del_sids) > 0:
    redis.hdel(user_key, *del_sids)



def _get_user_prefix(user_id):
  return "user_sessions:%s" % user_id


class RedisSession(CallbackDict, SessionMixin):

  def __init__(self, initial=None, sid=None, new=False, redis=None, prefix=None):
    def on_update(self):
      self.modified = True
    CallbackDict.__init__(self, initial, on_update)
    self.sid = sid
    self.new = new
    self.modified = False

    self.redis = redis
    self.prefix = prefix or ''

  def clear_user_sessions(self, user_id=None):

    if self.redis is None:
      return

    user_id = user_id or self.get('user_id')

    if user_id is None:
      return

    sync_user_sessions(self.redis, self.prefix, user_id)

    user_key = _get_user_prefix(user_id)
    sessions = self.redis.hgetall(user_key)
    keys = ["".join([self.prefix, sid.decode()]) for sid, _ in sessions.items()]

    keys.append(user_key)
    self.redis.delete(*keys)

    local.force_null = True
    local.user_id = None


class RedisSessionInterface(SessionInterface):
  serializer = json
  session_class = RedisSession

  def __init__(self, redis=None, prefix='session:'):
    if redis is None:
      redis = Redis()
    self.redis = redis
    self.prefix = prefix

  def generate_sid(self):
    return str(uuid4())

  def get_redis_expiration_time(self, app, session):
    if session.permanent:
      return app.permanent_session_lifetime
    return timedelta(days=1)

  def open_session(self, app, request):

    local.user_id = None
    local.force_null = False
    sid = request.cookies.get(app.session_cookie_name)

    if not sid:
      sid = self.generate_sid()
      return self.session_class(sid=sid, new=True, redis=self.redis, prefix=self.prefix)
    val = self.redis.get(self.prefix + sid)

    if val is not None:
      val = val.decode()
      data = self.serializer.loads(val)
      local.user_id = data.get('user_id')
      return self.session_class(data, sid=sid, redis=self.redis, prefix=self.prefix)

    return self.session_class(sid=sid, new=True, redis=self.redis, prefix=self.prefix)

  def save_session(self, app, session, response):

    if local.force_null:
      session = self.session_class(sid=session.sid, new=True, redis=self.redis, prefix=self.prefix)

    domain = self.get_cookie_domain(app)

    if not session:
      self.redis.delete(self.prefix + session.sid)
      if session.modified:
        response.delete_cookie(app.session_cookie_name,
                               domain=domain)
      return

    redis_exp = self.get_redis_expiration_time(app, session)
    cookie_exp = self.get_expiration_time(app, session)

    val = self.serializer.dumps(dict(session))
    self.redis.setex(self.prefix + session.sid, val,
                     int(redis_exp.total_seconds()))

    user_id = session.get("user_id")
    if user_id is not None:
      
      if local.user_id is None:
        sync_user_sessions(self.redis, self.prefix, user_id)

      exp_date = datetime.now() + redis_exp
      data = {'expires': exp_date.isoformat()}
      data = self.serializer.dumps(data)
      self.redis.hset(_get_user_prefix(user_id), session.sid, data)

    

    response.set_cookie(app.session_cookie_name, session.sid,
                        expires=cookie_exp, httponly=True,
                        domain=domain)
