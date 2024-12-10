# this file seeks to stop the route assignment process
# create a new file called stop_route_assign.py

# read stops from the stops.txt file
import pandas as pd
aa_stops = pd.read_csv('./data/google_transit/stops.txt')

# read stop_times from the stop_times.txt file
aa_stop_times = pd.read_csv('./data/google_transit/stop_times.txt')

# read trips from the trips.txt file
aa_trips = pd.read_csv('./data/google_transit/trips.txt')

# a dictionary to store each route and the stops it serves
route_stops = {}

# for every trip_id in the trips.txt file
for trip in aa_trips['trip_id']:
    # get all the stop times for that trip
    trip_stops = aa_stop_times[aa_stop_times['trip_id'] == trip]
    route_id = int(aa_trips[aa_trips['trip_id'] == trip]['route_id'].values[0])  # Convert to str
    # for every stop in the trip_stops
    for stop in trip_stops['stop_id'].values:
        stop = int(stop)  # Convert stop to int
        # if the route_id is not in the route_stops dictionary
        if route_id not in route_stops:
            # create a new key with the route_id and an empty list as the value
            route_stops[route_id] = []
        # if the stop is not in the list of stops for that route
        if stop not in route_stops[route_id]:
            # add the stop to the list of stops for that route
            route_stops[route_id].append(stop)

# export the route_stops dictionary to a json file
import json
with open('./outputs/route_stops.json', 'w') as f:
    json.dump(route_stops, f)

# next we will need to also include the M-Bus stops in the route_stops dictionary
# the bus stops are the json files in ./data/MBus
# every json file in the MBus folder is a route
# for every json file in the MBus folder

# create a shapefile with all the stops in the MBus data
import os
import geopandas as gpd
from shapely.geometry import Point
# create an empty GeoDataFrame
stops = gpd.GeoDataFrame()
# for every file in the MBus folder
for file in os.listdir('./data/MBus'):
    # open the file
    with open(f'./data/MBus/{file}', 'r') as f:
        # read the json file
        data = json.load(f)
        # the file name is the route_id
        route_id = file.split('.')[0]
        # the points are stored in bustime-response->ptr->pt
        # for every point:
        # data structure: seq, lat, lon, typ (S for stop, W for other), pdist, (if stop) stpid, stpnm
        for point in data['bustime-response']['ptr'][0]['pt']:
            # if the point is a stop
            if point['typ'] == 'S':
                # create a new GeoDataFrame with the stop
                stop = gpd.GeoDataFrame({
                    'stop_id': [point['stpid']],
                    'stop_name': [point['stpnm']],
                    'stop_lat': [point['lat']],
                    'stop_lon': [point['lon']],
                    'route_id': [route_id],
                    'geometry': [Point(point['lon'], point['lat'])]
                    })
                # append the stop to the stops GeoDataFrame
                stops = gpd.GeoDataFrame(pd.concat([stops, stop], ignore_index=True))

# save the stops GeoDataFrame to a shapefile
stops.to_file('./outputs/MBus_stops.shp')

# also create a line shapefile with the routes
from shapely.geometry import LineString
# create an empty GeoDataFrame
routes = gpd.GeoDataFrame()
# for every file in the MBus folder
for file in os.listdir('./data/MBus'):
    # open the file
    with open(f'./data/MBus/{file}', 'r') as f:
        # read the json file
        data = json.load(f)
        # the file name is the route_id
        route_id = file.split('.')[0]
        # the points are stored in bustime-response->ptr->pt
        # for every point:
        # data structure: seq, lat, lon, typ (S for stop, W for other), pdist, (if stop) stpid, stpnm
        # create a list of points for the route
        points = []
        for point in data['bustime-response']['ptr'][0]['pt']:
            # add the point to the list of points
            points.append(Point(point['lon'], point['lat']))
        # create a new GeoDataFrame with the route
        route = gpd.GeoDataFrame({
            'route_id': [route_id],
            'geometry': [LineString(points)]
            })
        # append the route to the routes GeoDataFrame
        routes = gpd.GeoDataFrame(pd.concat([routes, route], ignore_index=True))

# save the routes GeoDataFrame to a shapefile
routes.to_file('./outputs/MBus_routes.shp')


# update the route_stops dictionary with the M-Bus stops
# read the route_stops dictionary from the json file
with open('./outputs/route_stops.json', 'r') as f:
    route_stops = json.load(f)
for file in os.listdir('./data/MBus'):
    # open the file
    with open(f'./data/MBus/{file}', 'r') as f:
        # read the json file
        data = json.load(f)
        # the file name is the route_id
        route_id = file.split('.')[0]
        # the points are stored in bustime-response->ptr->pt
        # for every point:
        # data structure: seq, lat, lon, typ (S for stop, W for other), pdist, (if stop) stpid, stpnm
        for point in data['bustime-response']['ptr'][0]['pt']:
            # if the route_id is not in the route_stops dictionary
            if route_id not in route_stops:
                # create a new key with the route_id and an empty list as the value
                route_stops[route_id] = []
            # if the stop is not in the list of stops for that route
            # and if the point is a stop
            if  point['typ'] == 'S' and point['stpid'] not in route_stops[route_id]:
                # add the stop to the list of stops for that route
                route_stops[route_id].append(point['stpid'])

# export the updated route_stops dictionary to a json file
with open('./outputs/route_stops.json', 'w') as f:
    json.dump(route_stops, f)