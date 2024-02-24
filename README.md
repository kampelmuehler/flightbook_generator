# Flightbook generator

A tool to generate an overview table with stats of flights represented by IGC files. It is useful for generating an overview of flight records in bulk.

Each flight is represented by 
- Date
- Glider
- Takeoff Time (UTC)
- Takeoff Location
- Takeoff lat,lon
- GPS Altitude Takeoff (m)
- Landing Time (UTC)
- Landing Location
- Landing lat,lon
- GPS Altitude Landing (m)
- Airtime (min)
- Number of thermals
- Thermal gain (m)
- Median thermal velocity (m/s)

## Usage

```
python igc_parser.py [-h] igc_folder output_folder output_filename

positional arguments:
  igc_folder       folder/tree to crawl for IGC files
  output_folder    where to save output file
  output_filename  name of output csv file
```

## Create a binary

Run `pyinstaller gui_app.py --collect-data sv_ttk` in repository root.

## Acknowledgements

This repository builds on top of [igc_lib](https://github.com/marcin-osowski/igc_lib).
