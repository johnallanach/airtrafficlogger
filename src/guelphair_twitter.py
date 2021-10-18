"""a simple program to tweet about aircrafts flying over Guelph ON"""
import time
from datetime import datetime
import csv

from opensky_api import OpenSkyApi
import tweepy

from config import CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET


#Authorize Twitter API
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

api = tweepy.API(auth)

#Get flight data from OpenSkyAPI
OpenSky_api = OpenSkyApi()
states = OpenSky_api.get_states(bbox=(43.473851, 43.596306, -80.326023, -80.152473))


def twitterlog():
    #Open Guelph Air logs for reading/extracting last 5 lines
    tl = open("GuelphAir_twitterlog.txt", "r")
    tl_lines = tl.read()
    tl_lines = tl_lines.splitlines()
    tl_lines = tl_lines[-10:]
    callsign_ls = []
    for i in tl_lines:
        callsign_start = i.find(":") + 2
        tl_callsign = i[callsign_start:]
        tl_callsign = tl_callsign.split(" ")
        tl_callsign = tl_callsign[0]
        callsign_ls.append(tl_callsign)
    tl.close()

    return callsign_ls


def main():

    callsign_ls = twitterlog()

    for flight in states.states:
        if flight.geo_altitude != None and flight.geo_altitude < 6100:
            callsign = str(flight.callsign)
            callsign = callsign.split(" ")
            callsign = callsign[0]
                    
            now = datetime.now()
            date = now.strftime("%m/%d/%Y")
            time = now.strftime("%H:%M:%S")
                
            origin_country = str(flight.origin_country)
            geo_altitude = int(flight.geo_altitude)
            sky_lat = flight.latitude
            sky_long = flight.longitude
                
            with open('GuelphAir_log.csv', mode='a') as csvfile:
                log_writer = csv.writer(csvfile, delimiter=',', quotechar='"', 
                    quoting=csv.QUOTE_MINIMAL)
                log_writer.writerow([date, time, geo_altitude, flight.vertical_rate, 
                    callsign, origin_country, sky_lat, sky_long])
            
            if callsign in callsign_ls:
                print (flight.squawk)
            else:
                #tweet = "Currently in Guelph airspace: %r (%r) %r m" % (callsign, origin_country, geo_altitude)
                tweet = "Currently in #Guelph airspace: " + callsign + " (from " + origin_country + ") " + str(geo_altitude) +"m"
                # (insert code to write call sign to 10 latest flights list)
                api.update_status(tweet)


if __name__ == '__main__':
    main()
