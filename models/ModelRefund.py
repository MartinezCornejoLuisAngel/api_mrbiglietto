from decouple import config
import requests

class ModelRefund():
    
    
    @classmethod
    def set_answer(self,refund_id,result):
        try: 
            payload = {
                'result':result
            }
            response = requests.put(config('URL_BASE_BD')+'/webadminapi/v1/Refund/'+str(refund_id),json=payload)
            return response
        except Exception as ex:
            raise Exception(ex)
    
    @classmethod
    def get_refunds(self):
        try: 
            response = requests.get(config('URL_BASE_BD')+'/webadminapi/v1/Refund')
            return response
        except Exception as ex:
            raise Exception(ex)