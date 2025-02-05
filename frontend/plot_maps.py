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
        self.number_of_changes = trip_planner.count_changes()
        self.first_stop = self.next_trip.iloc[0]
        self.last_stop = self.next_trip.iloc[-1]

    def _create_map(self):
        geographical_map = folium.Map(
            location=[self.next_trip["lat"].mean(), self.next_trip["lon"].mean()],
            zoom_start=5,
        )

        for i, row in self.next_trip.iterrows():
            marker_color = "red"
            popup_text = (
                f"<b>Station:</b> {row['name']}<br>"
                f"<b>Avgångstid:</b> {row['time']}<br>"
                f"<b>Linje:</b> {row['line']}"
            )

            if i == 0:
                popup_text += f"<br><b>Avgångstid: {row['time']}</b>"
            elif i == len(self.next_trip) - 1:
                popup_text += f"<br><b>Ankomsttid: {row['time']}</b>"

            if i in self.next_trip.index[1:-1]:
                if self.next_trip.iloc[i - 1]["name"] != row["name"]:
                    marker_color = "blue"

            folium.Marker(
                location=[row["lat"], row["lon"]],
                popup=popup_text,
                icon=folium.Icon(color=marker_color),
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
        st.components.v1.html(self._create_map()._repr_html_(), height=500)

        total_trip_time = self._calculate_total_trip_time()
        total_hours, remainder = divmod(total_trip_time.total_seconds(), 3600)
        total_minutes = remainder // 60
        departure_time = pd.to_datetime(
            self.first_stop["time"], format="%H:%M:%S"
        ).strftime("%H:%M")
        arrival_time = pd.to_datetime(
            self.last_stop["time"], format="%H:%M:%S"
        ).strftime("%H:%M")

        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])  # Gör kolumnerna lika breda

        with col1:
            st.markdown(
                f"<p class='trip-info'>⏳ Total restid: "
                f"{int(total_hours)}h {int(total_minutes)}m</p>",
                unsafe_allow_html=True,
            )

        with col2:
            st.markdown(
                f"<p class='trip-info'>🚆 Avgångstid: {departure_time}</p>",
                unsafe_allow_html=True,
            )

        with col3:
            st.markdown(
                f"<p class='trip-info'>🏁 Ankomsttid: {arrival_time}</p>",
                unsafe_allow_html=True,
            )

        with col4:
            st.markdown(
                f"<p class='trip-info'>🔄 Antal byten: {self.number_of_changes}</p>",
                unsafe_allow_html=True,
            )
