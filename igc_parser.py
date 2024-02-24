import argparse
from datetime import datetime
from pathlib import Path
from statistics import median
from typing import Dict, Union

import overpy
import pandas as pd
from geopy.distance import distance
from geopy.geocoders import Nominatim
from geopy.location import Location

import igc_lib


def find_closest_peak_to_location(location: Location,
                                  search_radius_meters: int = 2000) -> str:
    """Finds the closest mountain peak to a geopy Location within a given
    search radius

    Args:
        location (Location): location to search around
        search_radius_meters (int, optional): search radius in meters. Defaults to 2000.

    Returns:
        str: name of the closest peak or 'Unknown Location' in case of errors
    """
    try:
        api = overpy.Overpass()
        response = api.query(f"""
            node[natural=peak](around:{search_radius_meters}, {location.raw['lat']}, {location.raw['lon']});
            out;
            """)

        peak_list = []
        for node in response.nodes:
            if 'ele' in node.tags.keys() and 'name' in node.tags.keys():
                tr = {
                    ord('m'): None,
                    ord(','): '.'
                }  # mitigate some mapping errors
                ele = float(node.tags['ele'].translate(tr).replace(
                    ' Meter', ''))
                lat = float(node.lat)
                lon = float(node.lon)
                dist = distance((lat, lon),
                                (location.raw['lat'], location.raw['lon']))
                peak_list.append({
                    'elevation': ele,
                    'latitude': lat,
                    'longitude': lon,
                    'distance': dist.kilometers,
                    'name': node.tags['name']
                })
        peaks_sorted = sorted(peak_list, key=lambda k: int(k['distance']))

        return peaks_sorted[0].get(
            'name', 'Unknown Location') if peaks_sorted else 'Unknown Location'
    except:
        return 'Unknown Location'


def parse_flight_details(igc_path: Path) -> Dict[str, Union[str, int, float]]:
    """Parse an igc file and return details about the flight

    Args:
        igc_path (Path): path to the flight IGC file

    Returns:
        Dict[str, Union[str, int, float]]: a dict containing stats about the flight
    """
    flight = igc_lib.Flight.create_from_file(igc_path)
    if not flight.valid:
        print(f"Flight {igc_path.name} is invalid: {flight.notes}")
        return None
    geolocator = Nominatim(user_agent="igc_flightbook")
    location_takeoff = geolocator.reverse(
        f"{flight.takeoff_fix.lat},{flight.takeoff_fix.lon}")
    dt_takeoff = datetime.fromtimestamp(flight.takeoff_fix.timestamp)
    location_landing = geolocator.reverse(
        f"{flight.landing_fix.lat},{flight.landing_fix.lon}")

    dt_landing = datetime.fromtimestamp(flight.landing_fix.timestamp)
    landing_city = location_landing.raw['address'].get("city", '')
    landing_village = location_landing.raw['address'].get("village", '')
    location_landing_str = landing_city if landing_city else landing_village
    thermal_gain = 0
    thermal_velocities = []
    for thermal in flight.thermals:
        thermal_gain += round(thermal.alt_change())
        thermal_velocities.append(thermal.vertical_velocity())
    median_thermal_velocity = median(
        thermal_velocities) if thermal_velocities else 0

    return {
        'Day': dt_landing.day,
        'Month': dt_landing.month,
        'Year': dt_landing.year,
        'Glider': flight.glider_type,
        'Takeoff Time (UTC)': dt_takeoff.strftime('%H:%M'),
        'Takeoff Location': find_closest_peak_to_location(location_takeoff),
        'Takeoff lat,lon':
        f"{flight.takeoff_fix.lat},{flight.takeoff_fix.lon}",
        'GPS Altitude Takeoff (m)': flight.takeoff_fix.gnss_alt,
        'Landing Time (UTC)': dt_landing.strftime('%H:%M'),
        'Landing Location': location_landing_str,
        'Landing lat,lon':
        f"{flight.landing_fix.lat},{flight.landing_fix.lon}",
        'GPS Altitude Landing (m)': flight.landing_fix.gnss_alt,
        'Airtime (min)': round((dt_landing - dt_takeoff).total_seconds() / 60),
        'Number of thermals': len(flight.thermals),
        'Thermal gain (m)': thermal_gain,
        'Median thermal velocity (m/s)': median_thermal_velocity,
        'IGC File': igc_path.name
    }


def parse_flights(igc_folder: str, output_folder: str, output_filename: str):
    """Recursively iterate through tree and find IGC files, parse files and write
    stats to csv

    Args:
        igc_folder (str): folder/tree to crawl
        output_folder (str): where to save output file
        output_filename (str): name of output csv file
    """
    if not igc_folder:
        print('Please select IGC file location.')
        return
    if not output_folder:
        print(
            'Please select output folder (and optionally change the filename).'
        )
        return
    output_file = Path(output_folder) / Path(output_filename)
    flight_dicts = []
    print('Starting.')
    igc_files_list = list(Path(igc_folder).rglob('*.[iI][gG][cC]'))
    if not igc_files_list:
        print(f'No IGC files found in {igc_folder} and subfolders.')
        return
    for i, igc_path in enumerate(igc_files_list):
        print(
            f"Processing flight {i + 1}/{len(igc_files_list)} {igc_path.name}",
            flush=True)
        flight_dict = parse_flight_details(igc_path)
        if flight_dict is not None:
            flight_dicts.append(flight_dict)

        df = pd.DataFrame.from_dict(flight_dicts)
        df = df.sort_values(['Year', 'Month', 'Day'])
        df.to_csv(output_file, sep=';', index=False)
    print('Done.')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("igc_folder",
                        help="folder/tree to crawl for IGC files")
    parser.add_argument("output_folder", help="where to save output file")
    parser.add_argument("output_filename", help="name of output csv file")
    args = parser.parse_args()
    parse_flights(igc_folder=args.igc_folder,
                  output_folder=args.output_folder,
                  output_filename=args.output_filename)
