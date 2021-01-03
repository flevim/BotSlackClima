"""
requirements:
    - geopy
    - tinydb
    - tabulate
"""

import requests
import json
from geopy.geocoders import Nominatim 
import sys 
import time
from datetime import datetime 
import argparse
from tinydb import TinyDB, Query 
import os 
import tabulate



#############################
#   Inicializaciones varias #
#############################
geolocator = Nominatim(user_agent="geolocation_places")
api_key = "8b1713b635fa5884b391b173b33386c1"
parser = argparse.ArgumentParser()

#Crear tablas de BD
db = TinyDB('openw_db.json')
Location = db.table('Location')
Profile = db.table('Profile')

# Locación a consultar
city = input("Ingrese ciudad: ")

try:
    loc = geolocator.geocode(city)
    lat, long = loc.latitude, loc.longitude
    print("Ciudad: %s ----> Latitude: %s | Longitude: %s" % (city, lat, long))
    
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

print("\nLAT\n")
print(lat)
print("\nLON\n")
print(lon)
print("\nTIMEZONE\n")
print(timezone)


###############################
#  PARSEANDO DATA IMPORTANTE  #
###############################

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


print("\n\n-----------------------------------------")
print("Pronostico semanal")
print("------------------------------------------\n\n")


for day in daily: 
    parse_data_daily(day)

#for hour in hourly:
#    parse_data_hourly(hour)
    

   
