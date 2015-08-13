import json
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.web.client import getPage

import bdgg.config as config

_allusers = {}
_change_handlers = set()

def _wrap_user_cb(func):
    def handle_response(data):
        user_json = json.loads(data)
        user = User.from_json(user_json)
        return func(user)
    return handle_response

@inlineCallbacks
def _get_user(token, callback):
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    postdata = 'authtoken=%s' % token
    data = yield getPage('https://www.destiny.gg/api/auth', method='POST', postdata=postdata, headers=headers)
    ret = _wrap_user_cb(callback)(data)
    returnValue(ret)

def _notify_change():
    for cb in _change_handlers:
        try:
            cb()
        except:
            pass

# Returns True if allusers changed, otherwise False
def add(user):
    current = _allusers.get(user.username, None)
    if user != current:
        _allusers[user.username] = user
        if config.debug: print "add user: %s" % user
        _notify_change()
        return True
    return False

# Returns True if allusers changed, otherwise False
def delete(user):
    current = _allusers.pop(user.username, None)
    if current != None:
        if config.debug: print "del user: %s" % user
        _notify_change()
        return True
    return False

@inlineCallbacks
def update(token):
    ret = yield _get_user(token, add)
    returnValue(ret)

@inlineCallbacks
def remove(token):
    ret = yield _get_user(token, delete)
    returnValue(ret)

def get_all_dict():
    return {k: _allusers[k].__dict__ for k in _allusers.keys()}

def add_change_handler(callback):
    _change_handlers.add(callback)

def remove_change_handler(callback):
    _change_handlers.discard(callback)

class User:
    def __init__(self, username, country):
        self.username = username
        self.country = country

    @classmethod
    def from_json(cls, user_json):
        return cls(user_json['username'], user_json['country'])

    def __str__(self):
        return "User(%s, %s}" % (self.username, self.country)

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and
            self.__dict__ == other.__dict__)

    def __ne__(self, other):
        return not self == other
