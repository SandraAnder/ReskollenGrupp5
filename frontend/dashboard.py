from pathlib import Path

import streamlit as st

from backend.connect_to_api import ResRobot
from backend.trips import StopPlanner
from frontend.plot_maps import TripMap

#
st.set_page_config(
    page_title="Reskollen",  # Titel på browserfliken
    page_icon="🦜",  # Icon på browserfliken
    layout="wide",  # Ger en fullskärms upplevelse
    initial_sidebar_state="expanded",  # Sidebaren startar i utfällt läge
)

resrobot = ResRobot()

tripPlanner = StopPlanner("")


def render_table_without_index(df):
    # Konverterar DataFrame till HTML utan indexkolumnen
    table_html = df.to_html(index=False, header=True, classes="styled-table")
    st.markdown(table_html, unsafe_allow_html=True)


def main():
    # Custom HTML/CSS for the banner
    banner_img = (
        """
    <div class="banner">
        <img src="""
        + (
            "https://static.vecteezy.com/ti/gratis-vektor/p1/14041676-metro-"
            "underjordisk-och-tunnelbana-rader-transport-karta-vector.jpg"
        )
        + """
        alt="Banner Image">
    </div>"""
    )
    # Visar bannern med spec höjd
    st.components.v1.html(banner_img, height=350)

    st.markdown(
        """
    <div class="logo-container">
        <img src="""
        + (
            "https://static.vecteezy.com/system/resources/previews/027/529/362/"
            "non_2x/tour-bus-and-map-with-traffic-navigation-route-location-marker-"
            "scheme-flat-illustration-for-passenger-traffic-service-vector.jpg"
        )
        + """
        alt="Logotyp" class="logo">
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.sidebar.markdown(
        """
        <div class="sidebar-logo">
            <img src= """
        + (
            "https://static.vecteezy.com/system/resources/previews/027/529/"
            "362/non_2x/tour-bus-and-map-with-traffic-navigation-route-location-"
            "marker-scheme-flat-illustration-for-passenger-traffic-service-vector.jpg"
        )
        + """>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
    <div class="header-container">
        <h1>Reseplanerare</h1>
        <p>
            Denna dashboarden syftar till att utforska data för olika platser,
            <br>men ska även fungera som en reseplanerare där du får välja och
            planera din resa.
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Skapar en meny i sidofältet till vänster
    st.sidebar.title("Meny")
    st.sidebar.markdown("### Välj sida")
    page = st.sidebar.radio(label="", options=["Sök resa", "Karta"])

    if page == "Karta":
        origin_id_name = st.text_input("FRÅN", "Göteborg C")
        destination_id_name = st.text_input("TILL", "Stockholm C")

        station_id1, station_id2 = resrobot.get_station_ids(
            origin_id_name, destination_id_name
        )

        trip_map = TripMap(station_id1, station_id2)

        trip_map.display_map()

    elif page == "Sök resa":
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
                        drop=True
                    )  # Tar bort index i DataFramen
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

                # Visar avgångar en timma framåt
                st.subheader(f"Avgångar inom en timme från {station_name}")
                # Extrahera stopID från stationen
                stop_id = station[0]["StopLocation"]["id"]
                departures_one_hour_df = (
                    tripPlanner.get_departures_around_one_hour_ahead(stop_id)
                )
                if (
                    departures_one_hour_df is not None
                    and not departures_one_hour_df.empty
                ):
                    # render_table_without_index(departures_one_hour_df)
                    table_html = departures_one_hour_df.to_html(
                        index=False, header=True, classes="styled-table"
                    )
                    st.markdown(
                        f"""
                        <div class="scrollable-table">
                            {table_html}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                else:
                    st.write("Inga avgångar inom en timme hittades.")
            else:
                st.write(f"Kunde inte hitta stationen: {station_name}")

    read_css()


def read_css():
    css_path = Path(__file__).parent / "../style.css"

    with open(css_path) as css:
        st.markdown(f"<style>{css.read()}</style>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
