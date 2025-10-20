import osmnx as ox
import geopandas as gpd
from osmnx._errors import InsufficientResponseError
import numpy as np
import networkx as nx
from collections import defaultdict
import random
import math

#Retrives the graph around the start point in a route length / 2 radius
def retrieve_graph(start_point, route_length):
    try:
        # Retrieve all types of roads/pathways within the radius of route length / 2 from the start in the form of a graph
        G = ox.graph.graph_from_point(center_point=start_point, dist=route_length/2, dist_type="network", network_type="all", simplify=True)

        # When using a simplified graph the edges that are straight lines get no geometry attribute
        # Making sure all edges include geometry attribute. Create GeoDataFrames for nodes and edges, with geometry attribute filled in for all edges
        nodes, edges = ox.graph_to_gdfs(G, fill_edge_geometry=True)
        # then re-create a graph from those GeoDataFrames
        G = ox.graph_from_gdfs(nodes, edges, graph_attrs=G.graph)

        # Make sure all edges actually have geometry data
        for u, v, data in G.edges(keys=False, data=True):
            assert "geometry" in data

        return G
    except ValueError:
        # Return empty graph
        return nx.MultiDiGraph()

# Adds corresponding elevation data to all nodes in a graph. Using this, it calculates the edge grade and rise for all edges
def add_elevation(graph):
    # Assign elevation to all nodes using data from Open Topo Data, then calculate the edge grades
    original_elevation_url = ox.settings.elevation_url_template
    ox.settings.elevation_url_template = (
        "https://api.opentopodata.org/v1/aster30m?locations={locations}"
    )
    graph = ox.elevation.add_node_elevations_google(graph, batch_size=100, pause=1)
    graph = ox.elevation.add_edge_grades(graph)
    ox.settings.elevation_url_template = original_elevation_url

    for edge in graph.edges:
        graph.edges[edge]["rise"] = graph.edges[edge]["grade"] * graph.edges[edge]["length"]

    return graph

def assign_elevation_tags(graph):
    # Get a list including all the absolute edge grades
    grades = [
        data["grade_abs"]
        for _, _, data in graph.edges(data=True)
        if "grade_abs" in data
    ]

    # Calculate the 33rd and 66th percentiles
    p33 = np.percentile(grades, 33)
    p66 = np.percentile(grades, 66)

    # Assign elevation tags
    for edge in graph.edges:
        edge_grade = graph.edges[edge]["grade_abs"]
        if edge_grade <= p33:
            graph.edges[edge]["elev_tag"] = "Flat"
        elif edge_grade <= p66:
            graph.edges[edge]["elev_tag"] = "Moderate"
        else:
            graph.edges[edge]["elev_tag"] = "Hilly"

    return graph

# Return the X and Y values of a series of features. For lines and polygons the coordinates of the centroid is returned
def get_feature_coordinates(features):
    return features.geometry.centroid.x, features.geometry.centroid.y

# Tags the closest edge to each viewpoint POI as a viewpoint edge
def assign_viewpoint_edges(G, start_point, route_length):

    tags = {"tourism": "viewpoint"}


    # Find POI features
    try:
        viewpoint_features = ox.features.features_from_point(start_point, tags, route_length/2)
    except InsufficientResponseError:
        viewpoint_features = None
    
    if viewpoint_features is not None and not viewpoint_features.empty:
        # Project graph to UTM, to be able to measure distance in meters
        G_proj = ox.project_graph(G)

        # Project the viewpoint features to the same CRS as the graph
        viewpoint_features_proj = viewpoint_features.to_crs(G_proj.graph['crs'])

        # Connect the viewpoint to their closest edge
        viewpoint_features_proj_x, viewpoint_features_proj_y = get_feature_coordinates(viewpoint_features_proj)
        viewpoint_edges = ox.distance.nearest_edges(G_proj, viewpoint_features_proj_x, viewpoint_features_proj_y)

        for edge in viewpoint_edges:
            G.edges[edge]["Viewpoint"] = True

    return G

# Tags the closest edge to each tourism POI as a tourism edge
def assign_tourism_edges(G, start_point, route_length):

    tags = {"toursim": "artwork", "memorial": "statue", "tourism": "attraction"}


    # Find POI features
    try:
        tourism_features = ox.features.features_from_point(start_point, tags, route_length/2)
    except InsufficientResponseError:
        tourism_features = None

    if tourism_features is not None and not tourism_features.empty:
        # Project graph to UTM, to be able to measure distance in meters
        G_proj = ox.project_graph(G)
        
        # Project the tourism features to the same CRS as the graph
        tourism_features_proj = tourism_features.to_crs(G_proj.graph['crs'])

        # Connect the viewpoint to their closest edge
        tourism_features_proj_x, tourism_features_proj_y = get_feature_coordinates(tourism_features_proj)
        tourism_edges = ox.distance.nearest_edges(G_proj, tourism_features_proj_x, tourism_features_proj_y)

        for edge in tourism_edges:
            G.edges[edge]["Tourism"] = True

    return G

# Tags all edges that are within 15 of park, wood or farmland as a nature edge
def assign_nature_edges(G, start_point, route_length):

    nature_feature_tags = {"leisure": "park", "natural": "wood", "landuse": "farmland"}

    # Add nature data to edges
    try:
        nat_features = ox.features.features_from_point(start_point, nature_feature_tags, route_length/2)
    except InsufficientResponseError:
        nat_features = None

    if nat_features is not None and not nat_features.empty:

        # Project graph to UTM, to be able to measure distance in meters
        G_proj = ox.project_graph(G)
    
        # Project the nature features to the same CRS as the graph
        nat_features_proj = nat_features.to_crs(G_proj.graph['crs'])

        # Create a buffer of 15m around the nature features
        buffer_distance = 15
        buffered_nature = nat_features_proj.buffer(buffer_distance)
        buffered_union = gpd.GeoSeries(buffered_nature).union_all()

        # Mark edges as near nature if they intersect the buffered union
        for u, v, k, data in G_proj.edges(keys=True, data=True):
            edge = (u, v, k)
            geom = data.get("geometry")
            if geom is not None and geom.intersects(buffered_union):
                G.edges[edge]["Nature"] = True
            else:
                G.edges[edge]["Nature"] = False

    return G

# Tag edges as either trail or road based on surface types of edge
def assign_surface_types(G):
    trail_surfaces ={"fine_gravel", "gravel", "ground", "dirt", "grass"}
    trail_highways = {"path", "track"}

    for u, v, k, data in G.edges(keys=True, data=True):
        edge_type = data.get("highway")
        surface = data.get("surface")

        # Handle cases where edge_type and/or surface are lists
        if isinstance(edge_type, list):
            type_match = any(t in trail_highways for t in edge_type)
        else:
            type_match = edge_type in trail_highways

        if isinstance(surface, list):
            surface_match = any(s in trail_surfaces for s in surface)
        else:
            surface_match = surface in trail_surfaces

        if type_match or surface_match:
            G.edges[u, v, k]["Trail"] = True
        else:
            G.edges[u, v, k]["Road"] = True

    return G

# Retrives feature data for the specified features in features_wanted (same size as in preference vector)
def retrieve_relevant_feature_data(G, pref, start_point, route_length, features_wanted):
    
    if features_wanted[0] == 1 or features_wanted[1] == 1:
        G = add_elevation(G)
        G = assign_elevation_tags(G)

    if features_wanted[2] == 1 or features_wanted[3] == 1:
        G = assign_surface_types(G)
    if features_wanted[4] == 1:
        G = assign_nature_edges(G, start_point, route_length)
    # Lighting data already present in G
    if features_wanted[6] == 1:
        G = assign_tourism_edges(G, start_point, route_length)
    if features_wanted[7] == 1:
        G = assign_viewpoint_edges(G, start_point, route_length)
    
    return G

def calculate_attribute_values_approx_alg(edge_data):
    attribute_values = 8 * [0]

    # Flat and hilly attribute value
    match edge_data.get("elev_tag"):
        case "Flat":
            attribute_values[0] = 2
            attribute_values[1] = 0.5
        case "Moderate":
            attribute_values[0] = 1
            attribute_values[1] = 1
        case "Hilly":
            attribute_values[0] = 0.5
            attribute_values[1] = 2
    
    # Road, trail, nature and lighting attribute values
    if edge_data.get("Road") == True:
        attribute_values[2] = 2
    else:
        attribute_values[3] = 2

    if edge_data.get("Nature") == True:
        attribute_values[4] = 2

    if edge_data.get("lit") == "yes":
        attribute_values[5] = 2
    
    # POI attribute values
    if edge_data.get("Tourism") == True:
        attribute_values[6] = 2
    if edge_data.get("Viewpoint") == True:
        attribute_values[7] = 2

    return attribute_values

def assign_weights_approx_alg(G, pref):
    for u, v, k, data in G.edges(keys=True, data=True):
        edge = (u, v, k)
        attribute_values = calculate_attribute_values_approx_alg(data)
        the_sum = sum(a * b for a, b in zip(pref, attribute_values))
        G.edges[edge]["weight_approx_alg"] = data["length"] * max(1, the_sum)
        
    return G

def calculate_attribute_values_heuristic(edge_data):
    attribute_values = 8 * [1]

    # Flat and hilly attribute value
    match edge_data.get("elev_tag"):
        case "Flat":
            attribute_values[0] = 0.7
            attribute_values[1] = 1.3
        case "Moderate":
            attribute_values[0] = 1
            attribute_values[1] = 1
        case "Hilly":
            attribute_values[1] = 1.3
            attribute_values[1] = 0.7
    
    # Road, trail, nature and lighting attribute values
    if edge_data.get("Road") == True:
        attribute_values[2] = 0.7
    else:
        attribute_values[3] = 0.7

    if edge_data.get("Nature") == True:
        attribute_values[4] = 0.7

    if edge_data.get("lit") == "yes":
        attribute_values[5] = 0.7

    return attribute_values

def assign_weights_heuristic(G, pref):
    for u, v, k, data in G.edges(keys=True, data=True):
        edge = (u, v, k)
        attribute_values = calculate_attribute_values_heuristic(data)
        G.edges[edge]["weight_heuristic"] = data["length"] * math.prod(a ** b for a, b in zip(attribute_values, pref))
        
    return G

# Prepares the graph for a route starting in a location with a specific route length
def prepare_graph(lat, long, route_length, pref, features_wanted):
    start_point = lat, long

    # Retrieve graph and relevant feature data
    G = retrieve_graph(start_point, route_length)
    
    if G.number_of_nodes() != 0:
        G = retrieve_relevant_feature_data(G, pref, start_point, route_length, features_wanted)

        # Assign edge weights based on preferences and feature data
        G = assign_weights_approx_alg(G, pref)
        G = assign_weights_heuristic(G, pref)
    
    return G