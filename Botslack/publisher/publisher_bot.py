#!/usr/bin/env python
import pika
import sys
import time
import os

time.sleep(35)
message1 = '[clima] -s Valdivia'

HOST = os.environ['RABBITMQ_HOST']

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host=HOST))
channel = connection.channel()

#Creamos el exchange 'nestor' de tipo 'fanout'
channel.exchange_declare(exchange='bot', exchange_type='topic', durable=True)

#Publicamos los mensajes a través del exchange 'nestor' 
channel.basic_publish(exchange='bot', routing_key='weather', body=message1)

print(" [x] Sent %r" % message1)
connection.close()
