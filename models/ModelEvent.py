from decouple import config 
import requests

class ModelEvent():
    
    @classmethod
    def register_event(self,event):
        try:
            serilized_sections = []
            for section in event.pricepersection:
                serilized_sections.append({
                    'idSection':int(section.id_section),
                    'availableSeats':int(section.available_seats),
                    'price' : float(section.price)
                })
            payload = {'idArtist':event.id_artist,
                    'idTheater':event.id_theater,
                    'datetime':event.datetime,
                    'pricePerSection': serilized_sections,
                    }
            response = requests.post(config('URL_BASE_BD')+'/webadminapi/v1/Event',json=payload)
            return response 
        except Exception as ex:
            raise Exception(ex)
        
    @classmethod
    def register_event_bc(self,id_event):
        try:
            
            payload = {'id_event':id_event,
                    'name_events':id_event,
                    }
            response = requests.post(config('URL_BASE_BC')+'/create_event',json=payload)
            return response 
        except Exception as ex:
            raise Exception(ex)