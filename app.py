from flask import Flask, render_template, request, jsonify
import traceback
import osmnx as ox
import networkx as nx
from graph import prepare_graph
from routing import heuristic, greedy
from postprocess import get_route_coordinates, get_stats_of_route, get_elevation_of_route

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

def read_preferences(elevation, surface, nature, lighting, poi):
    pref = [0,0,0,0,0,0,0,0]
    if elevation == "hilly":
        pref[0] = 1
    if elevation == "flat":
        pref[1] = 1
    if surface == "road":
        pref[2] = 1
    if surface == "trail":
        pref[3] = 1
    if nature == "yes":
        pref[4] = 1
    if lighting == "yes":
        pref[5] = 1
    if poi == "tourism":
        pref[6] = 1
    if poi == "viewpoint":
        pref[7] = 1

    return pref

@app.route('/route', methods=['POST'])
def generate_route():
    data = request.json
    lat, long = data.get("coords")
    distance = data.get("distance")
    elevation = data.get("elevation")
    surface = data.get("surface")
    nature = data.get("nature")
    lighting = data.get("lighting")
    poi = data.get("poi")
    print(f"Received start coords: {lat, long}, distance: {distance}, elevation: {elevation}")

    pref = read_preferences(elevation, surface, nature, lighting, poi)
    allpref = [1,1,1,1,1,1,1,1]

    try:
        G = prepare_graph(lat, long, distance, pref, allpref)
        start_vertex = ox.nearest_nodes(G, long, lat)
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": "No paths near start point, try changing startpoint"}), 500
    
    try:
        route = heuristic(G, start_vertex, distance, [])

        if len(route) == 1:
            route = greedy(G, start_vertex, distance)

        route_coords = get_route_coordinates(G, route)

        route_stats = get_stats_of_route(distance, ox.routing.route_to_gdf(G, route, weight="length"))
        length = route_stats.get("length", 0)
        elevation = route_stats.get("elevation", 0)
        elevation_of_route = get_elevation_of_route(G, route)

        return jsonify({"route": route_coords,
                        "length": length,
                        "elevation": elevation,
                        "elevationOfRoute": elevation_of_route})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)