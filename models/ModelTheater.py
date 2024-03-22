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
                    'columnsNumber':section.columns_number,
                    'rowsNumber' : section.rows_number,
                    'isGeneral' : section.general,
                    'availableSeats':section.available_seats
                })
            
            payload = {'theaterName':theater.name,
                    'idLocation':theater.id_location,
                    'sections': serilized_sections
                    }
            response = requests.post(config('URL_BASE_BD')+'/webadminapi/v1/Theater',json=payload)
            return response  
        except Exception as ex:
            raise Exception(ex)