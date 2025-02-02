import re
from datetime import datetime, timedelta

import pandas as pd

from backend.connect_to_api import ResRobot

resrobot = ResRobot()


class TripPlanner:
    """
    A class to interact with Resrobot API to plan
    trips and retrieve details of available journeys.

    Check explorations to find id for your location

    Attributes:
    ----------
    trips : list
        A list of trips retrieved from the Resrobot API
        for the specified origin and destination.
    number_trips : int
        The total number of trips available
        for the specified origin and destination.

    Methods:
    -------
    next_available_trip() -> pd.DataFrame:
        Returns a DataFrame containing details of
        the next available trip, including stop names,
        coordinates, departure and arrival times, and dates.
    next_available_trips_today() -> list[pd.DataFrame]
        Returns a list of DataFrame objects, where each
        DataFrame contains similar content as next_available_trip()
    """

    def __init__(self, origin_id, destination_id) -> None:
        self.resrobot = ResRobot()

        response = resrobot.trips(origin_id, destination_id)
        if response and "Trip" in response:
            self.trips = response["Trip"]
            self.number_trips = len(self.trips)
        else:
            print("Inga resor hittades.")
            self.trips = []
            self.number_trips = 0

    def next_available_trip(self) -> pd.DataFrame:
        if not self.trips:
            print("Inga tillgängliga resor.")
            return pd.DataFrame()

        next_trip = self.trips[0]

        leglist = next_trip.get("LegList", {}).get("Leg", [])
        if not leglist:
            print("Inga steg i resan.")
            return pd.DataFrame()

        df_legs = pd.DataFrame(leglist)

        if "Stops" not in df_legs or df_legs["Stops"].isnull().all():
            print("Inga hållplatser hittades.")
            return pd.DataFrame()

        df_stops = pd.json_normalize(df_legs["Stops"].dropna(), "Stop", errors="ignore")

        df_stops["time"] = df_stops["arrTime"].fillna(df_stops["depTime"])
        df_stops["date"] = df_stops["arrDate"].fillna(df_stops["depDate"])

        return df_stops[
            [
                "name",
                "extId",
                "lon",
                "lat",
                "depTime",
                "depDate",
                "arrTime",
                "arrDate",
                "time",
                "date",
            ]
        ]

    def next_available_trips_today(self) -> list[pd.DataFrame]:
        """Fetches all available trips today between the origin_id and destination_id
        It returns a list of DataFrame objects, where each item corresponds to a trip
        """
        return []

    # One hour ahead filter v

    def get_departures_around_one_hour_ahead(self, stop_id) -> pd.DataFrame:
        """
        Fetches departures around one hour ahead for a specific stop_id.
        Returns a DataFrame containing the filtered
        departures within ±15 minutes of one hour ahead.
        """
        return self.resrobot.get_departures_around_one_hour_ahead(stop_id)

    # One hour ahead filter ^


class StopPlanner:
    def __init__(self, station) -> None:
        self.station = station

        # Filter stops on arrival and departure v

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

            departures = resrobot.get_departures(station_id, max_results=8)

            if departures:
                dep_data = []
                for departure in departures:
                    transport = departure.get("ProductAtStop", {}).get(
                        "displayNumber", "Okänt fordon"
                    )
                    transport_type = "Unknown"

                    products = departure.get("Product", [])
                    if isinstance(products, list):
                        for product in products:
                            transport_type = product.get("catOutL", "Unknown")

                            dep_time = datetime.strptime(
                                departure["time"], "%H:%M:%S"
                            ).time()
                            current_time = datetime.now().time()
                            time_until_departure = datetime.combine(
                                datetime.today(), dep_time
                            ) - datetime.combine(datetime.today(), current_time)

                            if time_until_departure < timedelta(0):
                                time_until_departure += timedelta(days=1)

                    dep_data.append(
                        {
                            "Tid": departure["time"],
                            "Destination": departure["direction"],
                            "Linje": transport,
                            "Typ av transport": transport_type,
                            "Tid kvar": str(time_until_departure).split(".")[0],
                        }
                    )
                return pd.DataFrame(dep_data)
            else:
                print("Inga avgångar")
                return pd.DataFrame()
        else:
            print("Stationen hittades inte")
            return pd.DataFrame()

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

            arrivals = resrobot.get_arrivals(station_id, max_results=8)

            if arrivals:
                arr_data = []
                for arrival in arrivals:
                    transport = arrival.get("ProductAtStop", {}).get(
                        "displayNumber", "Okänt fordon"
                    )
                    transport_type = "Unknown"

                    products = arrival.get("Product", [])
                    if isinstance(products, list):
                        for product in products:
                            transport_type = product.get("catOutL", "Unknown")

                            arr_time = datetime.strptime(
                                arrival["time"], "%H:%M:%S"
                            ).time()
                            current_time = datetime.now().time()
                            time_until_arrival = datetime.combine(
                                datetime.today(), arr_time
                            ) - datetime.combine(datetime.today(), current_time)

                            if time_until_arrival < timedelta(0):
                                time_until_arrival += timedelta(days=1)

                    arr_data.append(
                        {
                            "Tid": arrival["time"],
                            "Origin": arrival["origin"],
                            "Linje": transport,
                            "Typ av transport": transport_type,
                            "Tid kvar": str(time_until_arrival).split(".")[0],
                        }
                    )
                return pd.DataFrame(arr_data)
            else:
                print("Inga avgångar")
                return pd.DataFrame()
        else:
            print("Stationen hittades inte")
            return pd.DataFrame()

    # Filter stops on arrival and departure ^


if __name__ == "__main__":
    TripPlanner(740000190, 740000001)
    StopPlanner()
