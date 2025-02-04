from abc import ABC, abstractmethod

import folium
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

    def _create_map(self, search_input=None):
        # Skapa en karta baserat på den filtrerade datan
        geographical_map = folium.Map(
            location=[self.next_trip["lat"].mean(), self.next_trip["lon"].mean()],
            zoom_start=5,
        )

        # Om ett sökord har angetts, filtrera data
        if search_input:
            filtered_data = self.next_trip[self.next_trip['name'].str.contains(search_input, case=False, na=False)]
        else:
            filtered_data = self.next_trip

        # Lägg till markörer för varje station på kartan
        for _, row in filtered_data.iterrows():
            folium.Marker(
                location=[row["lat"], row["lon"]],
                popup=f"{row['name']}<br>{row['time']}<br>{row['date']}",
            ).add_to(geographical_map)

        return geographical_map

    def display_map(self):
        st.markdown("## Karta över stationerna i din resa")

        st.markdown(
            "Klicka på varje station för mer information. Detta är en exempelresa mellan Malmö och Umeå"
        )
        st.components.v1.html(self._create_map()._repr_html_(), height=500)

        st.markdown("Klicka på varje station för mer information. Detta är en exempelresa mellan Malmö och Umeå")
        
        # Lägg till textfält för att söka efter stationer
        search_input= st.text_input("Sök efter station:", "")
        
        # Skapa kartan baserat på sökningen
        map_html = self._create_map(search_input)._repr_html_()

        # Visa kartan i Streamlit
        st.components.v1.html(map_html, height=500)
