from dotenv import load_dotenv
import os
import requests
from pprint import pprint
import re
import pandas as pd

load_dotenv()


class ResRobot:

    API_KEY = os.getenv("API_KEY")

    def trips(self, origin_id=740000001, destination_id=740098001):
        """origing_id and destination_id can be found from Stop lookup API"""
        url = f"https://api.resrobot.se/v2.1/trip?format=json&originId={origin_id}&destId={destination_id}&passlist=true&showPassingPoints=true&accessId={self.API_KEY}"

        try:
            response = requests.get(url)
            response.raise_for_status()

            return response.json()
        except requests.exceptions.RequestException as err:
            print(f"Network or HTTP error: {err}")

    def access_id_from_location(self, location):
        url = f"https://api.resrobot.se/v2.1/location.name?input={location}&format=json&accessId={self.API_KEY}"
        response = requests.get(url)
        result = response.json()

        print(f"{'Name':<50} extId")

        for stop in result.get("stopLocationOrCoordLocation"):
            stop_data = next(iter(stop.values()))

            # returns None if extId doesn't exist
            if stop_data.get("extId"):
                print(f"{stop_data['name']:<50} {stop_data['extId']}")

    # Filter stops on arrival and departure v

    # Function to extract the stopname
    def get_stop_name(self, location):
        url_stopName = f"https://api.resrobot.se/v2.1/location.name?input={location}&format=json&accessId={self.API_KEY}"

        result_name = requests.get(url_stopName)
        return result_name.json().get("stopLocationOrCoordLocation")

    def get_departures(self, location_ids, max_results=8):
        url_departures = f"https://api.resrobot.se/v2.1/departureBoard?id={location_ids}&format=json&maxJourneys={max_results}&accessId={self.API_KEY}"

        response = requests.get(url_departures)
        data = response.json()
        departures = data.get("Departure", [])

        return departures[:max_results]

    def get_timetable_dep(self, station):
        if station:
            station_name = station[0]["StopLocation"]["name"]
            station_id_raw = station[0]["StopLocation"]["id"]

            match = re.search(r"L=(\d+)", station_id_raw)
            if match:
                station_id = match.group(1)
            else:
                print("Kunde inte extrahera stationens ID.")
                station_id = None
            print(f"Stationens namn: {station_name}")
            print(f"Stations id: {station_id}")

            departures = self.get_departures(station_id, max_results=8)

            if departures:
                dep_data = []
                for departure in departures:
                    transport = departure.get('ProductAtStop', {}).get(
                        'displayNumber', 'Okänt fordon')
                    dep_data.append(
                        {"Tid": departure['time'], "Destination": departure['direction'], "Linje": transport})
                return pd.DataFrame(dep_data)
            else:
                print("Inga avgångar")
                return pd.DataFrame()
        else:
            print("Stationen hittades inte")
            return pd.DataFrame()

    def get_arrivials(self, location_ids, max_results=8):
        url_arrivals = f"https://api.resrobot.se/v2.1/arrivalBoard?id={location_ids}&format=json&maxJourneys={max_results}&accessId={self.API_KEY}"
        response = requests.get(url_arrivals)

        data_arrivals = response.json()
        arrivals = data_arrivals.get("Arrival", [])
        return arrivals[:max_results]

    def get_timetable_arr(self, station):
        if station:
            station_name = station[0]["StopLocation"]["name"]
            station_id_raw = station[0]["StopLocation"]["id"]

            match = re.search(r"L=(\d+)", station_id_raw)
            if match:
                station_id = match.group(1)
            else:
                print("Kunde inte extrahera stationens ID.")
                station_id = None
            print(f"Stationens namn: {station_name}")
            print(f"Stations id: {station_id}")

            arrivals = self.get_arrivials(station_id, max_results=8)

            if arrivals:
                arr_data = []
                for arrival in arrivals:
                    transport = arrival.get('ProductAtStop', {}).get(
                        'displayNumber', 'Okänt fordon')
                    arr_data.append({
                        "Tid": arrival['time'], "Origin": arrival['origin'], "Linje": transport})
                return pd.DataFrame(arr_data)
            else:
                print("Inga avgångar")
                return pd.DataFrame()
        else:
            print("Stationen hittades inte")
            return pd.DataFrame()

    # Filter stops on arrival and departure ^


if __name__ == "__main__":
    resrobot = ResRobot()
    response = resrobot.trips(740000001, 740098001)
    print(response)
