def get_route_coordinates(G, route):
    coords = []

    for u, v in zip(route[:-1], route[1:]):
        data = G.get_edge_data(u, v)
        # If multiple edges exist, pick the first one
        edge_data = data[list(data.keys())[0]]  
        
        if "geometry" in edge_data:
            # Use all points in the geometry
            xs, ys = edge_data["geometry"].xy
            edge_coords = list(zip(ys, xs))  # (lat, lon)
        else:
            # Straight line between nodes
            x1, y1 = G.nodes[u]['y'], G.nodes[u]['x']
            x2, y2 = G.nodes[v]['y'], G.nodes[v]['x']
            edge_coords = [(x1, y1), (x2, y2)]
        
        # Why was it risk of duplications?
        # Avoid duplicating nodes
        if coords and edge_coords[0] == coords[-1]:
            del edge_coords[0]
        coords.extend(edge_coords)
    
    return coords

def get_elevation_of_route(G, route):
    elevation_data = []
    total_length = 0
    previous_node = None 

    # Loop all nodes. Keep track of length by remembering last node and total length up til that node.
    for node in route:
        if previous_node:
            total_length += list(G.get_edge_data(previous_node, node).values())[0]["length"]

        elevation_data.append({"length": total_length, "elevation": G.nodes[node]["elevation"]})
        previous_node = node

    return elevation_data

def get_stats_of_route(route_length, route_gdf):

    total_length = 0
    
    length_of_repetition = 0
    visited_edges = set()

    total_elevation = 0

    length_of_road = 0
    length_of_trail = 0
    length_of_nature = 0
    length_of_lighting = 0
    
    number_of_viewpoints = 0
    number_of_tourism = 0

    for edge, edge_info in route_gdf.iterrows():
        
        u, v, _ = edge
        
        # Update total length
        edge_length = edge_info.get("length")
        total_length += edge_length

        # Update elevation
        if edge_info.get("rise") and edge_info.get("rise") > 0:
            total_elevation += edge_info.get("rise")

        # Update surface
        if edge_info.get("Road") == True:
            length_of_road += edge_length
        elif edge_info.get("Trail") == True:
            length_of_trail += edge_length
            
        # Update nature
        if edge_info.get("Nature") == True:
            length_of_nature += edge_length

        # Update lighting
        if edge_info.get("lit") == "yes":
            length_of_lighting += edge_length


        # Update POI
        if (edge_info.get("Viewpoint") == True) and ((u,v) not in visited_edges) and ((v,u) not in visited_edges):
            number_of_viewpoints += 1
            
        if (edge_info.get("Tourism") == True) and ((u,v) not in visited_edges) and ((v,u) not in visited_edges):
            number_of_tourism += 1
            
        # Update repetition
        if (u,v) in visited_edges or (v,u) in visited_edges:
            length_of_repetition += edge_length
        else:
            visited_edges.add((u,v))

    
    statistics = dict()
    
    statistics["length"] = total_length

    statistics["length_deviation"] = abs(total_length - route_length)
    
    if total_length > 0:
        statistics["repetition"] = length_of_repetition / total_length
        statistics["road"] = length_of_road / total_length
        statistics["trail"] = length_of_trail / total_length
        statistics["nature"] = length_of_nature / total_length
        statistics["lighting"] = length_of_lighting / total_length
    else:
        statistics["repetition"] = 0
        statistics["road"] = 0
        statistics["trail"] = 0
        statistics["nature"] = 0
        statistics["lighting"] = 0       
        
    statistics["elevation"] = total_elevation

    statistics["viewpoint"] = number_of_viewpoints
    statistics["tourism"] = number_of_tourism

    return statistics