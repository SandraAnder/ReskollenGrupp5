from setuptools import find_packages, setup

print(find_packages(exclude=["test*", "explorations"]))

setup(
    name="travel_planner",
    version="0.0.1",
    description="""This ackage is userd for travel planning in public transport.
    It has backend, frontend and utils.""",
    author="Sandra Andersson",
    author_email="dvasdvjnaaadvjn@gmail.com",
    install_packages=[
        "streamlit",
        "pandas",
        "requests",
        "folium",
        "pprint",
        "python-dotenv",
    ],
    packages=find_packages(exclude=["test*", "explorations"]),
    entry_points={"console_scripts": ["dashboard = utils.run_dashboard:run_dashboard"]},
)
