from .entities.Theater import Theater
from .entities.Section import Section
from decouple import config
import requests,json
 
class ModelTheater():

    @classmethod
    def register_theater(self,theater):
        try:
            serilized_sections = []
            for section in theater.sections:
                serilized_sections.append({
                    'sectionName':section.name,
                    'columnsNumber':int(section.columns_number),
                    'rowsNumber' : int(section.rows_number),
                    'isGeneral' : section.general,
                    'availableSeats':int(section.available_seats)
                })
            payload = {'theaterName':theater.name,
                    'idLocation':theater.id_location,
                    'sections': serilized_sections,
                    'urlGrid':theater.theater_url
                    }
            response = requests.post(config('URL_BASE_BD')+'/webadminapi/v1/Theater',json=payload)
            return response  
        except Exception as ex:
            raise Exception(ex)
        
    @classmethod
    def get_theaters(self):
        try:
            response = requests.get(config('URL_BASE_BD')+'/webadminapi/v1/Theater')
            return response
        except Exception as ex:
            raise Exception(ex)