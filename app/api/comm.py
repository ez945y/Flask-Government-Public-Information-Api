# -- coding: utf-8 -- 
import json
import requests

class Auth():

    def __init__(self, app_id, app_key):
        self.app_id = app_id
        self.app_key = app_key

    def get_auth_header(self):
        content_type = 'application/x-www-form-urlencoded'
        grant_type = 'client_credentials'

        return{
            'content-type' : content_type,
            'grant_type' : grant_type,
            'client_id' : self.app_id,
            'client_secret' : self.app_key
        }

class data():

    def __init__(self, app_id, app_key, auth_response):
        self.app_id = app_id
        self.app_key = app_key
        self.auth_response = auth_response

    def get_data_header(self):
        auth_JSON = json.loads(self.auth_response.text)
        access_token = auth_JSON.get('access_token')

        return{
            'authorization': 'Bearer '+access_token
        }

def getData(data_url):
    app_id = 't109ab0716-28845016-d0dc-44ed'
    app_key = '5a3751a8-3cc8-45ce-9468-f8f91f993efd'
    auth_url="https://tdx.transportdata.tw/auth/realms/TDXConnect/protocol/openid-connect/token"
    a = Auth(app_id, app_key)
    auth_response = requests.post(auth_url, a.get_auth_header())
    d = data(app_id, app_key, auth_response)
    return requests.get(data_url, headers=d.get_data_header()) 

def to_json(key_list, vlaue_list):
    view = []
    for item in value_list:
        view.append(dict(zip(key_list, item)))
    return view