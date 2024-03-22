from .entities.Artist import Artist
from decouple import config

import requests
 
class ModelArtist():

    @classmethod
    def register_artist(self,artist):
        try:
            payload = {'name':artist.artistName,
                    'description':artist.artistDescription,
                    'genre': artist.artistGenre,
                    'urlPhoto':artist.artistUrl,
                    'tourName':artist.artistTourName}
            response = requests.post(config('URL_BASE_BD')+'/webadminapi/v1/Artist',json=payload)
            return response  
        except Exception as ex:
            raise Exception(ex)
