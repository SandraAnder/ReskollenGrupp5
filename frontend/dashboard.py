import streamlit as st
import pandas as pd

from backend.connect_to_api import ResRobot
from backend.trips import StopPlanner
from frontend.plot_maps import TripMap
from utils.constants import StationIds
from backend.connect_to_api import ResRobot
from backend.trips import TripPlanner
from backend.trips import StopPlanner
from pathlib import Path


st.set_page_config(
    page_title="Reskollen",  # Titel på browserfliken
    page_icon="🦜",  # Icon på browserfliken
    layout="wide",  # Ger en fullskärms upplevelse
    initial_sidebar_state="expanded",  # Sidebaren startar i utfällt läge
)

trip_map = TripMap(
    origin_id=StationIds.MALMO.value, destination_id=StationIds.UMEA.value
)
resrobot = ResRobot()

tripPlanner = StopPlanner("")


def render_table_without_index(df):
    # Konverterar DataFrame till HTML utan indexkolumnen
    table_html = df.to_html(index=False, header=True, classes='styled-table')
    st.markdown(table_html, unsafe_allow_html=True)


def main():
    st.markdown("""
    <div class="header-container">
        <h1>Reseplanerare</h1>
        <p>Den här dashboarden syftar till att både utforska data för olika platser, men ska även fungera som en reseplanerare där du får välja och planera din resa.</p>
    </div>
    """, unsafe_allow_html=True)
    # st.markdown("# Reseplanerare")
    # st.markdown(
    #     "Den här dashboarden syftar till att både utforska data för olika platser, men ska även fungera som en reseplanerare där du får välja och planera din resa."
    # )

    # trip_map.display_map()

    # Visar tabell med val av station
    station_name = st.text_input("Ange stationsnamn:", "Göteborg C")

    if station_name:
        print(f"Anropar get_stop_name med {station_name}")
        station = resrobot.get_stop_name(station_name)

        if station:
            # Visar departures
            st.subheader(f"Avgångar från {station_name}")
            departures_df = tripPlanner.get_timetable_dep(station)
            if not departures_df.empty:
                departures_df = departures_df.reset_index(
                    drop=True)  # Tar bort index i DataFramen
                render_table_without_index(departures_df)
            else:
                st.write("Inga avgångar hittades.")

            # Visar arrivals
            st.subheader(f"Ankomster till {station_name}")
            arrivals_df = tripPlanner.get_timetable_arr(station)
            if not arrivals_df.empty:
                arrivals_df = arrivals_df.reset_index(drop=True)
                render_table_without_index(arrivals_df)
            else:
                st.write("Inga ankomster hittades.")
        else:
            st.write(f"Kunde inte hitta stationen: {station_name}")

    read_css()


def read_css():
    css_path = Path(__file__).parent / '../style.css'

    with open(css_path) as css:
        st.markdown(
            f'<style>{css.read()}</style>', unsafe_allow_html=True
        )


if __name__ == "__main__":
    main()
