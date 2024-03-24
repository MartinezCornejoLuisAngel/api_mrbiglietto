import pika
from decouple import config

class Publisher():
    
    @classmethod
    def pub_task(self,message):
        connection_parameters = pika.ConnectionParameters(host=config('IP_VM'),port=5672)
        connection = pika.BlockingConnection(connection_parameters)
        channel = connection.channel()
        channel.queue_declare(queue='api_requests')
    
        channel.basic_publish(exchange='', routing_key='api_requests', body=message)
        print(f"Sent request: {message}")
        connection.close()