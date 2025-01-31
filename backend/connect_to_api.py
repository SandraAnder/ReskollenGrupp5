import os
from datetime import datetime, timedelta

import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()


class ResRobot:
    API_KEY = os.getenv("API_KEY")

    def trips(self, origin_id=740000001, destination_id=740098001):
        """origing_id and destination_id can be found from Stop lookup API"""
        url = f"""https://api.resrobot.se/v2.1/trip?format=json&originId={origin_id}
        &destId={destination_id}&passlist=true&
        showPassingPoints=true&accessId={self.API_KEY}"""

        try:
            response = requests.get(url)
            response.raise_for_status()

            return response.json()
        except requests.exceptions.RequestException as err:
            print(f"Network or HTTP error: {err}")

    def access_id_from_location(self, location):
        url = f"""https://api.resrobot.se/v2.1/location.name?input={location}
        &format=json&accessId={self.API_KEY}"""
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
        url_stopName = f"""https://api.resrobot.se/v2.1/location.name?input={location}
        &format=json&accessId={self.API_KEY}"""

        result_name = requests.get(url_stopName)
        return result_name.json().get("stopLocationOrCoordLocation")

    def get_departures(self, location_ids, max_results=8):
        url_departures = f"""https://api.resrobot.se/v2.1/departureBoard?
        id={location_ids}&format=json&maxJourneys={max_results}&
        accessId={self.API_KEY}"""

        response = requests.get(url_departures)
        data = response.json()
        departures = data.get("Departure", [])

        return departures[:max_results]

    def get_arrivals(self, location_ids, max_results=8):
        url_arrivals = f"""https://api.resrobot.se/v2.1/arrivalBoard?id={location_ids}
        &format=json&maxJourneys={max_results}&accessId={self.API_KEY}"""
        response = requests.get(url_arrivals)

        data_arrivals = response.json()
        arrivals = data_arrivals.get("Arrival", [])
        return arrivals[:max_results]

    # Filter stops on arrival and departure ^

    # Filter one hour ahead v
    def get_departures_around_one_hour_ahead(self, stop_id):
        url = f"""https://api.resrobot.se/v2.1/departureBoard?id={stop_id}
        &format=json&accessId={self.API_KEY}"""

        response = requests.get(url)
        if response.status_code != 200:
            print(f"Error: {response.status_code}")
            return None

        departures = pd.DataFrame(response.json().get("Departure", []))
        departures["datetime"] = pd.to_datetime(
            departures["date"] + " " + departures["time"], errors="coerce"
        )
        departures = departures.dropna(subset=["datetime"])

        if departures.empty:
            print("No valid datetime data.")
            return None

        one_hour_ahead = datetime.now() + timedelta(hours=1)
        time_range = [
            one_hour_ahead - timedelta(minutes=15),
            one_hour_ahead + timedelta(minutes=15),
        ]
        departures_filtered = departures[
            (departures["datetime"] >= time_range[0])
            & (departures["datetime"] <= time_range[1])
        ]

        if departures_filtered.empty:
            print(f"No departures within ±15 minutes for stop_id {stop_id}.")
            return None

        departures_filtered["stop_id"] = stop_id
        return departures_filtered[["name", "stop", "direction", "datetime", "stop_id"]]

    # Filter one hour ahead ^


if __name__ == "__main__":
    resrobot = ResRobot()
