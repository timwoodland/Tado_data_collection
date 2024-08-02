
import requests
import numpy as np
import pandas as pd
from decouple import config
from datetime import datetime, timezone
from influxdb_client import InfluxDBClient
import schedule
import time

# get env variables. Use local .env file if it exists

TADO_USERNAME = config("TADO_USERNAME")
TADO_PASSWORD = config("TADO_PASSWORD")
TADO_CLIENT_SECRET = config("TADO_CLIENT_SECRET")
INFLUX_URL = config("INFLUX_URL")
INFLUX_DB = config("INFLUX_DB")
INFLUX_ORG = config("INFLUX_ORG", default="")


def collect_tado_data(username, password, client_secret):
        
    # Set the time for Now

    now = datetime.now(timezone.utc)

    # ### Get bearer token

    payload = {'client_id':'tado-web-app',
                'grant_type':'password',
                'scope':'home.user',
                'username':username,
                'password':password,
                'client_secret':client_secret}

    token_r = requests.post('https://auth.tado.com/oauth/token', params=payload)
    token = token_r.json()["access_token"]

    # Set Header for future Requests

    header = {'Authorization' : "Bearer " + token}

    # ### Get Home ID

    home_id_r = requests.get("https://my.tado.com/api/v1/me", headers = header)
    home_id = home_id_r.json()['homeId']

    # Get name of home

    home_url = "https://my.tado.com/api/v2/homes/"+str(home_id)
    home_r = requests.get(home_url , headers = header)

    home = home_r.json()["name"]

    # Get zone data

    zones_list_url = home_url+"/zones"

    zone_list_r = requests.get(zones_list_url , headers = header)

    zone_list_json = zone_list_r.json()


    zone_list = []
    zone_dict = {}
    counter = 1


    for zone_data in zone_list_json:
        zone_id = zone_data["id"]
        zone_name = zone_data["name"]

        zone_list.append(zone_id)
        
        zone_dict[zone_id] = {"time":str(now), "zone":zone_name}

        counter = counter + 1

    # Get data from each zone and put into a dataframe

    for zone in zone_list:
        zone_url = zones_list_url+"/"+str(zone)+"/state"
        zone_r = requests.get(zone_url, headers = header)
        zone_json = zone_r.json()

        status = zone_json["setting"]["power"]
        mode = zone_json["tadoMode"]
        geo_override = zone_json["geolocationOverride"]
        type = zone_json["setting"]["type"]
        status = zone_json["setting"]["power"]
        power_level = zone_json["activityDataPoints"]["heatingPower"]["percentage"]
        zone_temp = zone_json["sensorDataPoints"]["insideTemperature"]["celsius"]
        zone_humidity = zone_json["sensorDataPoints"]["humidity"]["percentage"]

    #this checks that the status of the zone is "on". If the zone is not on then a "set_temp" value will not be available so we use no.nan
        if status == "ON":
            set_temp = zone_json["setting"]["temperature"]["celsius"]
        else:
            set_temp = np.nan

        zone_data_dict = {"mode":mode, "geo_override":geo_override, "type":type, "status":status, "set_temp":set_temp, "power_level":power_level, "zone_temp":zone_temp, "zone_humidity":zone_humidity }

        zone_dict[zone].update(zone_data_dict)
        

    zone_df = pd.DataFrame.from_dict(zone_dict, orient="index")

    zone_df = zone_df.reset_index()
    zone_df= zone_df.rename(columns={"index":"zone_id"})

    zone_df = zone_df.set_index("time")

    # ### Get Weather data and put into a dataframe

    weather_url = "https://my.tado.com/api/v2/homes/"+str(home_id)+"/weather"

    weather_r = requests.get(weather_url , headers = header)

    weather_json = weather_r.json()

    weather_data = [weather_json["outsideTemperature"]["celsius"], weather_json["weatherState"]["value"], "tado"]

    weather_columns = ["temperature_C", "state", "source"]

    weather_df = pd.DataFrame(data=[weather_data], index=[now], columns=weather_columns)

    return weather_df, zone_df


def write_to_influx(db_url, db, db_org, weather_df, zone_df):
    
    # Write Zone and Weather dataframes to Influx db
    with InfluxDBClient(url=db_url) as ifdb_client:
        with ifdb_client.write_api() as ifdb_write_client:

            ifdb_write_client.write(db, org=db_org, record=weather_df, data_frame_measurement_name="tado_weather_data", data_frame_tag_columns=["source"])

            ifdb_write_client.write(db, org=db_org, record=zone_df, data_frame_measurement_name="tado_zone_data", data_frame_tag_columns=["zone_id", "zone", "mode", "geo_override", "type", "status"])



def main():
    weather, zone = collect_tado_data(TADO_USERNAME, TADO_PASSWORD, TADO_CLIENT_SECRET)

    write_to_influx(INFLUX_URL, INFLUX_DB, INFLUX_ORG, weather, zone)

schedule.every(2).minutes.do(main)

while True:
    schedule.run_pending()
    time.sleep(1)
