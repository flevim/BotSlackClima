#!/usr/bin/env python
import pika
import time
import os
import requests
import json
from geopy.geocoders import Nominatim 
import sys 
import time
from datetime import datetime 
import os 
import tabulate


#############################
#   Inicializaciones varias #
#############################
time.sleep(30)
geolocator = Nominatim(user_agent="geolocation_places")
api_key = "8b1713b635fa5884b391b173b33386c1"


#######################
# Conexión a RabbitMQ #
#######################

HOST = os.environ['RABBITMQ_HOST']

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host=HOST))
channel = connection.channel()

channel.exchange_declare(exchange='bot', exchange_type='topic', durable=True)

#Se crea un cola temporaria exclusiva para este consumidor (búzon de correos)
result = channel.queue_declare(queue="openweather", exclusive=True, durable=True)
queue_name = result.method.queue

#La cola se asigna a un 'exchange'
channel.queue_bind(exchange='bot', queue=queue_name, routing_key="weather")


print(' [*] Esperando por mensajes. Para salir CTRL+C')

#########################
#  Parseado de datos API #
#########################

def parse_data_hourly(data):
    dt = datetime.fromtimestamp(int(data['dt'])).strftime('%d-%m-%Y %H:%M:%S')
    temp = "%s °C" % (data['temp'])
    feels_like = '%s °C' % (data['feels_like'])
    humidity = '{} %'.format(data['humidity'])
    weather = data['weather'][0]['description']
    pressure = "%s Pa" % (data['pressure'])
    visibility = '%s Km' % (int(data['visibility']) / 1e3)

    headers = ['Item','Valor']
    table = [["Fecha",dt],["Temperatura",temp],["Se siente como", feels_like], ["Humedad", humidity], ["Descripción",weather], ["Presión", pressure], ["Visibilidad", visibility]]
    print(tabulate.tabulate(table, headers, tablefmt="github"))
    print('\n=================================================\n')

def parse_data_daily(data):
    dt = datetime.fromtimestamp(int(data['dt'])).strftime('%d-%m-%Y %H:%M:%S')
    temp_min, temp_max = '%s °C' % (data['temp']['min']), '%s °C' % (data['temp']['max'])
    temp_day = '%s °C' % (data['temp']['morn'])
    temp_eve = '%s °C' % (data['temp']['eve']) 
    temp_night = '%s °C' % (data['temp']['night'])
    humidity = '{} %'.format(data['humidity'])
    weather = data['weather'][0]['description']
    pressure = "%s Pa" % (data['pressure'])
    wind_speed = '%s m/s' % (data['wind_speed'])

    
    headers = ['Item','Valor']
    table = [["Fecha",dt],["Temp mínima",temp_min],["Temp máxima", temp_max], ["Temp mañana", temp_day], 
    ["Temp tarde",temp_eve], ["Temp noche", temp_night], ["Humedad", humidity], ["Descripción", weather], ["Presión", pressure], ["Velocidad viendo", wind_speed]]
    
    print(tabulate.tabulate(table, headers, tablefmt="github"))
    print('\n=================================================\n')


def title(string):
    print("\n\n-----------------------------------------")
    print("Pronostico %s" % (string))
    print("------------------------------------------\n\n")
            

def callback(ch, method, properties, body):
    # Formato de consulta 
    # [clima] <periodicidad> <ciudad>
    # <periodicidad> : Tiempo 24 horas | Tiempo 7 días a la semana | Tiempo actual 
    body = body.decode('utf-8').split(" ")
    
    if body[0] == "[clima]":
        if len(body) < 3:
            print("Formato de consulta: [clima] <periodicidad> <ciudad>")
            print("Ejemplo: [clima] -s Valdivia,chile")
            sys.exit(0)

        if body[1] not in ('-s', '-d', '-a'):
            print("Argumento del periodo de consulta incorrecto")
            sys.exit(0) 

        try:
            loc = geolocator.geocode(body[2:])
            lat, long = loc.latitude, loc.longitude
            print("Ciudad: %s ----> Latitude: %s | Longitude: %s" % (body[2:], lat, long))
    
        except AttributeError:
            print("No ha sido posible encontrar este lugar.")
            sys.exit(0)

        url = "https://api.openweathermap.org/data/2.5/onecall?lat=%s&lon=%s&exclude=minutely&units=metric&lang=es&appid=%s" % (lat, long, api_key)

        response = requests.get(url)
        data = json.loads(response.text)
        
        if 'cod' in data.keys():
            print(data['cod'])
            sys.exit(0)

        lat = data["lat"]
        lon = data["lon"]
        timezone = data["timezone"]
        hourly = data["hourly"]
        daily = data["daily"]

        if body[1] == '-s':
            title("semanal")
            for day in daily: 
                parse_data_daily(day)

        elif body[1] == '-d':
            title("diario")
            for hour in hourly: 
                parse_data_hourly(hour)
                        
     
        channel.basic_publish(exchange='bot', routing_key="weather", body='hola')


channel.basic_consume(
    queue=queue_name, on_message_callback=callback, auto_ack=True)

channel.start_consuming()

sys.exit(0)

