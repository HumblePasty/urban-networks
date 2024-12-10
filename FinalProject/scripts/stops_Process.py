# this file is to process the bus stops shapefile
import os
import geopandas as gpd
from shapely.geometry import Point
from shapely.geometry import LineString
import pandas as pd
import json

# read the current stops shapefile
AA_stops = gpd.read_file('./outputs/AA_Bus_Table.shp')

# read the census blocks shapefile
AA_blocks = gpd.read_file('./outputs/AA_Census_Blocks.shp')

# read the filtered LODES data
AA_Lodes = pd.read_csv('./outputs/aa_lodes_cleaned.csv')

# read the route_stops json files
with open('./outputs/route_stops.json', 'r') as f:
    route_stops = json.load(f)

cnt_a = 0
cnt_b = 0

# for every lodes record
for index, row in AA_Lodes.iterrows():
    # get the code for home and work place
    home = str(row['h_geocode'])
    work = str(row['w_geocode'])
    # get the total number of workers as weight
    weight = row['S000']
    cnt_a += weight
    # use the code to find the block
    home_block = AA_blocks[AA_blocks['GEOID20'] == home]
    work_block = AA_blocks[AA_blocks['GEOID20'] == work]
    # if the home and work block are not found, skip this record
    if home_block.empty or work_block.empty:
        continue
    # find the bus stop to the home and work place
    # first try to find the stop using the code
    home_stop = AA_stops[AA_stops['GEOID20'] == home]
    # if there are more than one stops with the same code, randomly choose one
    if len(home_stop) > 1:
        home_stop = home_stop.sample().iloc[0]
    # if there is only one stop with the code, get the stop
    elif len(home_stop) == 1:
        home_stop = home_stop.iloc[0]
    # if the stop is not found, find the stop with the minimum distance
    else:
        # use the centroid of the block to find the stop
        home_stop = AA_stops.loc[AA_stops.distance(home_block.unary_union).idxmin()]
    # repeat the same process for the work place
    work_stop = AA_stops[AA_stops['GEOID20'] == work]
    if len(work_stop) > 1:
        work_stop = work_stop.sample().iloc[0]
    elif len(work_stop) == 1:
        work_stop = work_stop.iloc[0]
    else:
        work_stop = AA_stops.loc[AA_stops.distance(work_block.unary_union).idxmin()]
    # see if the home and work stops are on the same route
    # loop through the route_stops dictionary
    for a_route_id, a_stops in route_stops.items():
        # if the home stop and work stop are on the same route
        if home_stop['stop_id'] in a_stops and work_stop['stop_id'] in a_stops:
            # add the weight to the total workers on bus routes
            cnt_b += weight

print(f"Total workers: {cnt_a}")
print(f"Workers on bus routes: {cnt_b}")
