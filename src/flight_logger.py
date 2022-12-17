import csv
from datetime import datetime
import json
import time

import pandas as pd
import requests


def get_location_data(loc_input):
    #https://nominatim.org/release-docs/develop/api/Search/
    request_url = ('https://nominatim.openstreetmap.org/search?q='+loc_input+
                    '&format=json&addressdetails=1&limit=1&polygon_svg=1')
    geo_resp = requests.get(request_url)
    geo_data = geo_resp.json()
    if geo_data is  None:
        print ("No location data found for %s" %loc_input)
        exit()
    elif len(geo_data) == 1:
        geo_data = geo_data[0]
        boundingbox = geo_data['boundingbox']
        display_name = geo_data['display_name']
        print ("Beginning flight tracking for: %s" %display_name)
    elif len(geo_data) > 1:
        print ("Multiple locations found. Terminating flight tracking.")
        exit()
    else:
        print ("Encountered an error. Terminating flight tracking.")
        exit()

    #EXAMPLE DATA
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

    try:
        #'https://opensky-network.org/api/states/all?lamin=30.038&lomin=\
        #   -125.974&lamax=52.214&lomax=-68.748'
        url = ('https://opensky-network.org/api/states/all?'+'lamin='+\
                str(lower_lat)+'&lomin='+str(lower_long)+'&lamax='+str(upper_lat)+
                '&lomax='+str(upper_long))
        resp = requests.get(url)
        data = resp.json()
        flight_states = data['states']
    except:
        flight_states = None

    return flight_states


def log_flights(flight_states, date, time, df_flights):
    df_header = ['date', 
                    'time', 
                    'icao24',
                    'callsign',
                    'origin_country',
                    'time_position',
                    'last_contact',
                    'longitude',
                    'latitude',
                    'geo_altitude',
                    'on_ground',
                    'velocity',
                    'true_track',
                    'vertical_rate',
                    'sensors',
                    'baro_altitude',
                    'squawk',
                    'spi',
                    'position_source'
                    ]

    for flight in flight_states:
        try:
            #COLLECT STATE FIELDS
            icao24 = flight[0]
            callsign = flight[1]
            origin_country = flight[2]
            time_position = flight[3]
            last_contact = flight[4]
            longitude = flight[5]
            latitude = flight[6]
            geo_altitude = flight[7]
            on_ground = flight[8]
            velocity = flight[9]
            true_track = flight[10]
            vertical_rate = flight[11]
            sensors = flight[12]
            baro_altitude = flight[13]
            squawk = flight[14]
            spi = flight[15]
            position_source = flight[16]

            #RE-FORMAT
            #callsign = str(callsign).split(" ")[0]
            #origin_country = str(origin_country)

            #TypeError: int() argument must be a string, a bytes-like 
            # object or a number, not 'NoneType'
            geo_altitude = int(geo_altitude)

            # Define fields of interest
            flight_data = [date, 
                            time, 
                            icao24,
                            callsign,
                            origin_country,
                            time_position,
                            last_contact,
                            longitude,
                            latitude,
                            geo_altitude,
                            on_ground,
                            velocity,
                            true_track,
                            vertical_rate,
                            sensors,
                            baro_altitude,
                            squawk,
                            spi,
                            position_source
                            ]

            # Write to air_log
            if (geo_altitude != None and geo_altitude < 6100
                    and longitude != None and latitude != None):
                #update_message = "Logging... %r" % (callsign)
                #print (update_message)
                #log_writer.writerow(flight_data)
                df_new_flight = pd.DataFrame([flight_data], columns=df_header)
                df_flights = pd.concat([df_flights,df_new_flight], ignore_index=True)
        except: 
            #print ("Failed to log: %s" %flight)
            pass

    return df_flights
     

def main():

    location_to_track = str(input("Please enter location to track: "))

    # Define location to track
    boundingbox = get_location_data(location_to_track)

    # Create pandas database to hold flight data pre-logging
    df_flights = pd.DataFrame()

    # Get flights and write to air_log
    while(True):
        flight_states = get_flight_states(boundingbox)
        if flight_states is not None:
            now = datetime.now()
            flight_date = now.strftime("%m/%d/%Y")
            flight_time = now.strftime("%H:%M:%S")
            df_flights = log_flights(flight_states, flight_date, 
                                        flight_time, df_flights)
            
            rows = len(df_flights.axes[0])  # Count number of rows
            if rows > 500:
                print ('Writing %d flights to air_log...' %rows)
                df_flights.to_csv('air_log.csv', mode='a') 
                df_flights = df_flights[0:0]    # Delete all rows 

            time.sleep(15)


if __name__ == '__main__':

    main()
