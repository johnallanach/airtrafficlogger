import time
from datetime import datetime
import csv
import requests
import json


def get_flight_lines():
    resp = requests.get('https://opensky-network.org/api/states/all')
    data = resp.json()
    states = data['states']
    flight_lines = '\n'.join([json.dumps(s) for s in states])
    with open('flight_data.txt', 'w') as outfile:
        outfile.write(flight_lines)
    print("Added " + str(len(resp.json()['states'])) + " positions")
    return flight_lines


def log():
    resp = requests.get('https://opensky-network.org/api/states/all')
    data = resp.json()
    states = data['states']
    flight_lines = '\n'.join([json.dumps(s) for s in states])
    #with open('flight_data.txt', 'w') as outfile:
        #outfile.write(flight_lines)
    print("Added " + str(len(resp.json()['states'])) + " positions.")

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

        if geo_altitude != None and geo_altitude < 6100 and longitude != None and latitude != None:
        #if latitude, longitude, geo_altitude != None and geo_altitude < 6100:
            print ("Defining Guelph air space...")
            try: 
                if latitude > 43.473851 and latitude < 43.596306 and longitude > -80.326023 and longitude < -80.152473:
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
                    
                    print ("Writing to GuelphAir_log...")
                    with open('GuelphAir_log.csv', mode='a') as csvfile:
                        log_writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                        log_writer.writerow([date, time, geo_altitude, vertical_rate, callsign, origin_country, latitude, longitude])
            except: 
                print ("Failed to log: %s" %flight)

    if flight_count > 0: 
        print ("Currently there are %d aircrafts in Guelph airspace." % (flight_count)) 
    else:
        print ("No aircrafts currently in Guelph airspace.")  

#get_flight_lines()

if __name__ == '__main__':
    log()

