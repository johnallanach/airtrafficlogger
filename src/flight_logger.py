import time
from datetime import datetime
import csv
import requests
import json


def get_location_data():
    #https://nominatim.org/release-docs/develop/api/Search/
    geo_resp = requests.get('https://nominatim.openstreetmap.org/search?q=guelph&format=json&addressdetails=1&limit=1&polygon_svg=1')
    geo_data = geo_resp.json()
    if len(geo_data) == 1:
        geo_data = geo_data[0]
        boundingbox = geo_data['boundingbox']
        lat = geo_data['lat']
        lon = geo_data['lon']
        display_name = geo_data['display_name']
        print ("Do you mean %r ?" % (display_name)) 

    #'boundingbox': ['43.4738217', '43.594353', '-80.3269091', '-80.1535013']
    #'lat': '43.5460516', 'lon': '-80.2493276'
    #'display_name': 'Guelph, Southwestern Ontario, Ontario, Canada'

    return
    

def get_flight_states():
    resp = requests.get('https://opensky-network.org/api/states/all')
    data = resp.json()
    flight_states = data['states']

    flights = len(flight_states)
    print ("Current number of flight states: %d " % (flights)) 

    return


def log():
    resp = requests.get('https://opensky-network.org/api/states/all')
    data = resp.json()
    states = data['states']
    
    lower_lat = 43.4738217
    upper_lat = 43.596306
    lower_long = -80.326023
    upper_long = -80.152473

    flight_count = 0
    for flight in states:

        #icao24 = flight[0]
        callsign = flight[1]
        origin_country = flight[2]
        #time_position = flight[3]
        #last_contact = flight[4]
        longitude = flight[5]
        latitude = flight[6]
        geo_altitude = flight[7]
        #on_ground = flight[8]
        #velocity = flight[9]
        #heading = flight[10]
        vertical_rate = flight[11]
        #sensors = flight[12]
        #baro_altitude = flight[13]
        #squawk = flight[14]
        #spi = flight[15]
        #position_source = flight[16]

        #print ("Defining air space...")

        if geo_altitude != None and geo_altitude < 6100 and longitude != None and latitude != None:
        #if geo_altitude != None and longitude != None and latitude != None:
        #if latitude, longitude, geo_altitude != None and geo_altitude < 6100:
            
            try: 
                if latitude > lower_lat and latitude < upper_lat and longitude > lower_long and longitude < upper_long:
                    flight_count += 1
                    
                    callsign = str(callsign)
                    callsign = callsign.split(" ")
                    callsign = callsign[0]
                    origin_country = str(origin_country)
                    geo_altitude = int(geo_altitude)
                            
                    now = datetime.now()
                    date = now.strftime("%m/%d/%Y")
                    time = now.strftime("%H:%M:%S")
                        
                    message = "%r, %r, %r, %r, %r, %r, %r, %r \n" % (date, time, geo_altitude, vertical_rate, callsign, origin_country, latitude, longitude)
                    print (message)
                    
                    print ("Writing to air_log...")
                    with open('air_log.csv', mode='a') as csvfile:
                        log_writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                        log_writer.writerow([date, time, geo_altitude, vertical_rate, callsign, origin_country, latitude, longitude])
            except: 
                print ("Failed to log: %s" %flight)

    if flight_count > 0: 
        print ("Currently there are %d aircrafts in the defined airspace." % (flight_count)) 
    else:
        print ("No aircrafts currently in the defined airspace.")  


if __name__ == '__main__':
    #get_location_data()
    #flight_states = get_flight_states()
    log()


#https://openflights.org/data.html