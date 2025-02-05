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

        if not isinstance(leglist, list):
            print("Felaktig data för resans steg.")
            return pd.DataFrame()

        trip_data = []

        for leg in leglist:
            # Hanterar om "Product" finns och är en lista
            products = (
                leg["Product"]
                if "Product" in leg and isinstance(leg["Product"], list)
                else []
            )
            transport_line = (
                products[0]["displayNumber"]
                if products and "displayNumber" in products[0]
                else "Okänd linje"
            )

            stops = leg.get("Stops", {}).get("Stop", [])
            if not isinstance(stops, list):
                continue  # Hoppar över om stopplistan är felaktig

            for stop in stops:
                trip_data.append(
                    {
                        "name": stop.get("name", "Okänd"),
                        "extId": stop.get("extId", None),
                        "lon": stop.get("lon", None),
                        "lat": stop.get("lat", None),
                        "depTime": stop.get("depTime", None),
                        "depDate": stop.get("depDate", None),
                        "arrTime": stop.get("arrTime", None),
                        "arrDate": stop.get("arrDate", None),
                        "line": transport_line,
                    }
                )

        df_stops = pd.DataFrame(trip_data)
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
                "line",
            ]
        ]

    def count_changes(self) -> int:
        if not self.trips:
            return 0

        next_trip = self.trips[0]
        leglist = next_trip.get("LegList", {}).get("Leg", [])

        return max(0, len(leglist) - 1)


class StopPlanner:
    def __init__(self, station) -> None:
        self.station = station

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
                            current_time = (
                                datetime.now() + timedelta(minutes=-1)
                            ).time()
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
                            current_time = (
                                datetime.now() + timedelta(minutes=-1)
                            ).time()
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

    def get_departures_around_one_hour_ahead(self, stop_id) -> pd.DataFrame:
        """
        Fetches departures around one hour ahead for a specific stop_id.
        Returns a DataFrame containing the filtered
        departures within the next hour.
        """

        # Hämtar avgångar från API
        departures_df = resrobot.get_departures_around_one_hour_ahead(stop_id)

        # Om DataFramen är tom, returneras en tom DataFrame
        if departures_df.empty:
            print(f"No departures found for stop_id {stop_id}")
            return pd.DataFrame()

        # Lägger till en datetime-kolumn så vi kan filtrera avgångar baserat på tid
        departures_df["date"] = departures_df["date"].fillna(
            datetime.now().strftime("%Y-%m-%d")
        )
        departures_df["time"] = departures_df["time"].fillna("00:00")

        # Konverterar till datetime-format
        departures_df["datetime"] = pd.to_datetime(
            departures_df["date"] + " " + departures_df["time"], errors="coerce"
        )

        # Tar bort rader där datetime är NaT
        departures_df = departures_df.dropna(subset=["datetime"])

        # Om DataFrame är tom efter att den rensats, returneras en tom DataFrame
        if departures_df.empty:
            print("No valid datetime data.")
            return pd.DataFrame()

        # Filtrerar avgångar som sker mellan 'nu' och en timme framåt
        now = datetime.now()
        one_hour_ahead = now + timedelta(hours=1)

        departures_filtered = departures_df[
            (departures_df["datetime"] >= now)
            & (departures_df["datetime"] <= one_hour_ahead)
        ].copy()

        # Om inga avgångar hittas, returneras en tom DataFrame
        if departures_filtered.empty:
            print(f"No departures within the next hour for stop_id {stop_id}.")
            return pd.DataFrame()

        # Fixar till `SettingWithCopyWarning`
        departures_filtered = departures_filtered.copy()
        departures_filtered["stop_id"] = stop_id

        # Ändrar kolumnnamn för att matcha UI:t
        departures_filtered = departures_filtered.rename(
            columns={"name": "Transport", "direction": "Destination", "time": "Tid"}
        )

        return departures_filtered[["Tid", "Destination", "Transport"]]
