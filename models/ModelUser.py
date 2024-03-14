from .entities.User import User
from decouple import config

import requests
 

class ModelUser():

    @classmethod
    def login(self,user):
        try:
            payload = {'user':user.username,'password':user.password}
            response = requests.post(config('URL_BASE_BD')+'/adminapi/v1/AdminUser/login',json=payload)
            return response  
        except Exception as ex:
            raise Exception(ex)

    
    @classmethod
    def get_by_username(self,user):
        try:
            return User(1,"Administrador Cornejo",None)
        except Exception as ex:
            raise Exception(ex)