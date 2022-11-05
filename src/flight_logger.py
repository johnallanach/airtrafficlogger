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

    return boundingbox



def get_flight_states(boundingbox):

    #'boundingbox': ['43.4738217', '43.594353', '-80.3269091', '-80.1535013']
    lower_lat = float(boundingbox[0])
    upper_lat = float(boundingbox[1])
    lower_long = float(boundingbox[2])
    upper_long = float(boundingbox[3])

    #'https://opensky-network.org/api/states/all?lamin=30.038&lomin=-125.974&lamax=52.214&lomax=-68.748'
    url = 'https://opensky-network.org/api/states/all?'+'lamin='+str(lower_lat)+'&lomin='+str(lower_long)+'&lamax='+str(upper_lat)+'&lomax='+str(upper_long)
    resp = requests.get(url)
    data = resp.json()
    states = data['states']

    return states



def log_flights(states):

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

        if geo_altitude != None and geo_altitude < 6100 and longitude != None and latitude != None:
        #if geo_altitude != None and longitude != None and latitude != None:
        #if latitude, longitude, geo_altitude != None and geo_altitude < 6100:
            try:                
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



def track_flights():
    boundingbox = get_location_data()
    while(True):
        states = get_flight_states(boundingbox)
        if len(states) > 0: 
            log_flights(states)
        time.sleep(15)


if __name__ == '__main__':

    track_flights()
