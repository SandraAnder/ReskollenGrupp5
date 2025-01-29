import streamlit as st

from backend.connect_to_api import ResRobot
from backend.trips import StopPlanner
from frontend.plot_maps import TripMap
from utils.constants import StationIds

trip_map = TripMap(
    origin_id=StationIds.MALMO.value, destination_id=StationIds.UMEA.value
)
resrobot = ResRobot()

tripPlanner = StopPlanner("")


def main():
    st.markdown("# Reseplanerare")
    st.markdown(
        "Den här dashboarden syftar till att både utforska data för olika platser, men ska även fungera som en reseplanerare där du får välja och planera din resa."
    )

    trip_map.display_map()

    # Val av station
    station_name = st.text_input("Ange stationsnamn:", "Göteborg C")

    if station_name:
        print(f"Anropar get_stop_name med {station_name}")
        station = resrobot.get_stop_name(station_name)

        if station:
            # Visa departures
            st.subheader(f"Avgångar från {station_name}")
            departures_df = tripPlanner.get_timetable_dep(station)
            if not departures_df.empty:
                st.dataframe(departures_df)
            else:
                st.write("Inga avgångar hittades.")

            # Visa arrivals
            st.subheader(f"Ankomster till {station_name}")
            arrivals_df = tripPlanner.get_timetable_arr(station)
            if not arrivals_df.empty:
                st.dataframe(arrivals_df)
            else:
                st.write("Inga ankomster hittades.")
        else:
            st.write(f"Kunde inte hitta stationen: {station_name}")


if __name__ == "__main__":
    main()
