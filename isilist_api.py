import base64
import hashlib
import platform
import uuid
import os

import requests

class IsilistRequests(object):

    URL_BASE = 'https://api.isilist.com.br'
    GET_USER_URL = '/v1/users/is_store'
    REGISTER_USER_URL = '/v1/register_app'
    SYNC_FULL_URL = '/v1/sync/full'

    CLIENT_ID = os.getenv('CLIENT_ID')
    CLIENT_SECRET = os.getenv('CLIENT_SECRET')

    @classmethod
    def _auth(cls, user, password):
        return base64.encodestring('%s:%s' % (user, password)).replace('\n', '')

    @classmethod
    def get(cls, url, params=None, headers=None, user_password=None):
        kwargs = {}
        if user_password:
            kwargs['auth'] = user_password
        if headers:
            kwargs['headers'] = headers
        if params:
            kwargs['params'] = params
        return requests.get(url, **kwargs)

    @classmethod
    def post(cls, url, data=None, params=None, headers=None, user_password=None):
        kwargs = {}
        if user_password:
            kwargs['auth'] = user_password
        if headers:
            kwargs['headers'] = headers
        if params:
            kwargs['params'] = params
        if data:
            kwargs['json'] = data
        return requests.post(url, **kwargs)

    @classmethod
    def get_user_id(cls, user, password):
        url = cls.URL_BASE + cls.GET_USER_URL
        params = {'email': user}
        req = cls.get(url, params=params, user_password=(user, password))
        req.raise_for_status()
        return req.json()['user_id']

    @classmethod
    def get_register_id(cls, device_model, device_id, system_info, user, password):
        url = cls.URL_BASE + cls.REGISTER_USER_URL
        data = {
            "client_id": cls.CLIENT_ID,
            "client_secret": cls.CLIENT_SECRET,
            "device_model": device_model,
            "device_uuid": device_id,
            "system_info": system_info
        }
        req = cls.post(url, data=data, user_password=(user, password))
        req.raise_for_status()
        return req.json()['register_id']

    @classmethod
    def sync(cls, register_id, user, password):
        url = cls.URL_BASE + cls.SYNC_FULL_URL
        resources = 'contacts,products,lists,list_items,list_actions,list_payments'
        params = {
            'show_deleted': False,
            'resources': resources,
            'register_id': register_id
        }
        req = cls.get(url, params=params, user_password=(user, password))
        req.raise_for_status()
        return req.json()


class IsilistAPI(object):

    DEVICE_UUID = str(uuid.UUID(hashlib.md5(str(uuid.getnode()) +
                                            platform.node() +
                                            platform.system()).hexdigest()))
    SYSTEM_INFO = platform.platform()
    DEVICE_MODEL = '%s-%s (%s)' % (platform.python_implementation(),
                                   platform.python_version(),
                                   platform.system())

    user_id = None
    user = None
    password = None
    register_id = None
    sync_data = None

    def init(self, user, password):
        self.user = user
        self.password = password
        print "USER_ID: " + str(self._get_user_id())
        self.register_id = self._register_app()
        print "REGISTER_ID: " + str(self.register_id)

    def _get_user_id(self):
        return IsilistRequests.get_user_id(self.user, self.password)

    def _register_app(self):
        return IsilistRequests.get_register_id(IsilistAPI.DEVICE_MODEL, IsilistAPI.DEVICE_UUID,
                                               IsilistAPI.SYSTEM_INFO, self.user, self.password)

    def get_sync(self):
        return IsilistRequests.sync(self.register_id, self.user, self.password)
