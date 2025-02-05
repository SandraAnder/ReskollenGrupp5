import os
from datetime import datetime

import pandas as pd
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()


class ResRobot:
    API_KEY = st.secrets.get("API_KEY", os.getenv("API_KEY"))

    def trips(self, origin_id, destination_id):
        """origing_id and destination_id can be found from Stop lookup API"""
        url = (
            f"https://api.resrobot.se/v2.1/trip?format=json"
            f"&originId={origin_id}"
            f"&destId={destination_id}"
            f"&passlist=true"
            f"&showPassingPoints=true"
            f"&accessId={self.API_KEY}"
        )

        try:
            response = requests.get(url)
            response.raise_for_status()

            return response.json()
        except requests.exceptions.RequestException as err:
            print(f"Network or HTTP error: {err}")

    def access_id_from_location(self, location):
        url = (
            f"https://api.resrobot.se/v2.1/location.name?input={location}"
            f"&format=json"
            f"&accessId={self.API_KEY}"
        )
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
        url_stopName = (
            f"https://api.resrobot.se/v2.1/location.name?input={location}"
            f"&format=json"
            f"&accessId={self.API_KEY}"
        )

        result_name = requests.get(url_stopName)
        return result_name.json().get("stopLocationOrCoordLocation")

    def get_departures(self, location_ids, max_results=8):
        url_departures = (
            f"https://api.resrobot.se/v2.1/departureBoard?id={location_ids}"
            f"&format=json"
            f"&maxJourneys={max_results}"
            f"&accessId={self.API_KEY}"
        )

        response = requests.get(url_departures)
        data = response.json()
        departures = data.get("Departure", [])

        return departures[:max_results]

    def get_arrivals(self, location_ids, max_results=8):
        url_arrivals = (
            f"https://api.resrobot.se/v2.1/arrivalBoard?id={location_ids}"
            f"&format=json"
            f"&maxJourneys={max_results}"
            f"&accessId={self.API_KEY}"
        )
        response = requests.get(url_arrivals)

        data_arrivals = response.json()
        arrivals = data_arrivals.get("Arrival", [])
        return arrivals[:max_results]

    # Filter stops on arrival and departure ^

    # Filter one hour ahead v
    def get_departures_around_one_hour_ahead(self, stop_id):
        now = datetime.now()  # Hämtar tiden nu
        date = now.strftime("%Y-%m-%d")
        time = now.strftime("%H:%M")

        url = (
            f"https://api.resrobot.se/v2.1/departureBoard?id={stop_id}"
            f"&date={date}"
            f"&time={time}"
            f"&format=json"
            f"&accessId={self.API_KEY}"
        )

        response = requests.get(url)
        if response.status_code != 200:
            print(f"Error: {response.status_code}")
            return pd.DataFrame()

        data = response.json()
        departures = data.get("Departure", [])

        if not departures:
            print(f"No departures found for stop_id {stop_id}.")
            # Returnerar en tom DataFrame istället för en lista.
            return pd.DataFrame()

        departures_df = pd.DataFrame(departures)

        return departures_df

    def get_station_ids(self, location1, location2):
        def fetch_station_id(location):
            url = f"https://api.resrobot.se/v2.1/location.name?input={location}&format=json&accessId={self.API_KEY}"
            response = requests.get(url)

            if response.status_code != 200:
                print(
                    f"Error: API request failed for {location} with status code {response.status_code}"
                )
                return None

            data = response.json().get("stopLocationOrCoordLocation")

            if isinstance(data, list) and len(data) > 0:
                return data[0].get("StopLocation", {}).get("extId")

            print(f"Error: No station found for {location}")
            return None

        station_id1 = fetch_station_id(location1)
        station_id2 = fetch_station_id(location2)

        return station_id1, station_id2

    # Filter one hour ahead ^


if __name__ == "__main__":
    resrobot = ResRobot()
