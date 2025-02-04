from abc import ABC, abstractmethod
from datetime import timedelta

import folium
import pandas as pd
import streamlit as st

from backend.trips import TripPlanner


class Maps(ABC):
    """
    Abstract base class for map-related operations.

    Methods:
    --------
    display_map():
        Abstract method to display a map. Must be implemented by subclasses.
    """

    @abstractmethod
    def display_map(self):
        """
        Abstract method to display a map.

        Subclasses must provide an implementation for this method.
        """
        raise NotImplementedError


class TripMap(Maps):
    def __init__(self, origin_id, destination_id):
        trip_planner = TripPlanner(origin_id, destination_id)
        self.next_trip = trip_planner.next_available_trip()

    def _create_map(self):
        geographical_map = folium.Map(
            location=[self.next_trip["lat"].mean(), self.next_trip["lon"].mean()],
            zoom_start=5,
        )

        for _, row in self.next_trip.iterrows():
            folium.Marker(
                location=[row["lat"], row["lon"]],
                popup=f"{row['name']}<br>{row['time']}<br>{row['date']}",
            ).add_to(geographical_map)

        return geographical_map

    def _calculate_total_trip_time(self):
        self.next_trip["datetime"] = pd.to_datetime(
            self.next_trip["date"] + " " + self.next_trip["time"]
        )
        self.next_trip["time_diff"] = self.next_trip["datetime"].diff()

        total_trip_time = self.next_trip["time_diff"].sum()

        if pd.isna(total_trip_time):
            total_trip_time = timedelta(seconds=0)

        return total_trip_time

    def display_map(self):
        st.markdown("## Karta över stationerna i din resa")
        st.markdown(
            "Klicka på varje station för mer information. Detta är en exempelresa mellan Malmö och Umeå"
        )
        st.components.v1.html(self._create_map()._repr_html_(), height=500)

        total_trip_time = self._calculate_total_trip_time()
        st.markdown(f"**Total restid: {str(total_trip_time)}**")
