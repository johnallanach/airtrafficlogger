import csv
from datetime import datetime
import json
import time

#import pandas as pd
import requests


def get_location_data():
    #https://nominatim.org/release-docs/develop/api/Search/
    loc_input = str(input("Please enter location to track: "))
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
        #lat = geo_data['lat']
        #lon = geo_data['lon']
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

    #'https://opensky-network.org/api/states/all?lamin=30.038&lomin=\
    #   -125.974&lamax=52.214&lomax=-68.748'
    url = ('https://opensky-network.org/api/states/all?'+'lamin='+\
            str(lower_lat)+'&lomin='+str(lower_long)+'&lamax='+str(upper_lat)+
            '&lomax='+str(upper_long))
    resp = requests.get(url)
    data = resp.json()
    states = data['states']

    return states


def log_flights(states, date, time):
    with open('air_log.csv', mode='a', newline='') as csvfile:
        log_writer = csv.writer(csvfile, delimiter=',', quotechar='"',
                        quoting=csv.QUOTE_MINIMAL)
        for flight in states:
            try:
                #COLLECT STATE FIELDS
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
                true_track = flight[10]
                vertical_rate = flight[11]
                #sensors = flight[12]
                #baro_altitude = flight[13]
                #squawk = flight[14]
                #spi = flight[15]
                #position_source = flight[16]

                #RE-FORMAT
                callsign = str(callsign).split(" ")[0]
                origin_country = str(origin_country)
                geo_altitude = int(geo_altitude)

                #DEFINE FIELDS OF INTEREST
                fields_to_log = [date, 
                    time, 
                    callsign, 
                    origin_country, 
                    latitude, 
                    longitude, 
                    geo_altitude, 
                    true_track, 
                    vertical_rate
                    ]

                #WRITE TO AIR_LOG
                if (geo_altitude != None and geo_altitude < 6100
                        and longitude != None and latitude != None):
                    update_message = "Writing to air_log... %r" % (callsign)
                    print (update_message)
                    log_writer.writerow(fields_to_log)
            except: 
                print ("Failed to log: %s" %flight)


'''
def pandize():
    #CONVERT TO PANDAS DATAFRAME
    cols = ['date','time','callsign','origin_country',
                'latitude','longitude','geo_altitude',
                'true_track','vertical_rate']

    flight_df=pd.DataFrame(states) 
    flight_df.columns=col_name
    flight_df=flight_df.fillna('No Data')


def write_pandas_df_to_csv(flight_df):
    flight_df = flight_df
'''

if __name__ == '__main__':
    #DEFINE LOCATION TO TRACK
    boundingbox = get_location_data()
    
    #WRITE HEADER TO AIR_LOG
    with open('air_log.csv', mode='a', newline='') as csvfile:
        log_writer = csv.writer(csvfile, delimiter=',', quotechar='"',
                        quoting=csv.QUOTE_MINIMAL)
        header = ['date', 
                    'time', 
                    'callsign', 
                    'origin_country', 
                    'latitude', 
                    'longitude', 
                    'geo_altitude', 
                    'true_track', 
                    'vertical_rate'
                    ]
        log_writer.writerow(header)
    
    #GET FLIGHTS AND WRITE TO AIR_LOG
    while(True):
        states = get_flight_states(boundingbox)
        if states is not None:
            now = datetime.now()
            flight_date = now.strftime("%m/%d/%Y")
            flight_time = now.strftime("%H:%M:%S")
            log_flights(states, flight_date, flight_time)
        time.sleep(15)
    #write_pandas_df_to_csv(flight_df)

