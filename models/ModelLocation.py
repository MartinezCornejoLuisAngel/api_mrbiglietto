from .entities.Location import Location
from decouple import config

import requests
 
class ModelLocation():

    @classmethod
    def register_location(self,location):
        try:
            payload = {'idLocation':location.id,
                    'country':location.country,
                    'state': location.state,
                    'city': location.city,
                    'colony':location.colony,
                    'postalCode':location.postal_code,
                    'direction':location.address}
            response = requests.post(config('URL_BASE_BD')+'/webadminapi/v1/Location',json=payload)
            return response  
        except Exception as ex:
            raise Exception(ex)

    @classmethod
    def get_locations(self):
        try:
            response = requests.get(config('URL_BASE_BD')+'/webadminapi/v1/Location')
            return response  
        except Exception as ex:
            raise Exception(ex)

