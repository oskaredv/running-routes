import osmnx as ox
import networkx as nx
from networkx.exception import NetworkXNoPath
from collections import defaultdict
import random
import math

# Combines 3 routes into 1 for the heuristic
def combine_routes(route1, route2, route3):
    route1.pop()
    route2.pop()
    return route1 + route2 + route3 

# Remove out-and-back at via-vertices.
def remove_out_and_back(route, via_vertex):
    index = route.index(via_vertex)
    i = 0

    while(index-i > 0 and index+i < len(route)):
        if route[index-(1+i)] == route[index+(1+i)]:
            i += 1
        else:
            break

    route[index-i:index+i] = []
    return route
    
# Returns isochrone nodes of radius +- 10% around the center node
def get_isochrone_nodes(graph, center_node, radius):
    outer_subgraph = nx.ego_graph(graph, center_node, radius=radius*1.1, distance="length")
    inner_subgraph = nx.ego_graph(graph, center_node, radius=radius*0.9, distance="length")

    return outer_subgraph.nodes - inner_subgraph.nodes

# Find set of random pairs of via-vertices
def find_random_pairs_of_via_vertices(G, start_vertex, route_length):
    isochrone = get_isochrone_nodes(G, start_vertex, route_length/3)

    valid_pairs_of_via_vertices = list()
    
    random.seed(42)
    random_via_vertices = random.sample(list(isochrone), min(10, len(list(isochrone))))
  
    for vv1 in random_via_vertices:
        isochrone2 = get_isochrone_nodes(G, vv1, route_length/3)
        for vv2 in isochrone2:
            if vv2 in isochrone and vv2 != start_vertex:
                valid_pairs_of_via_vertices.append((vv1, vv2))
                break

    return valid_pairs_of_via_vertices

# Generates a route for the heuristic algorithm based on start node and a pair of via-vertices
def generate_heuristic_route(G, start, viavertex1, viavertex2, pref):
    try:
        route1 = nx.shortest_path(G, source=start, target=viavertex1, weight="weight_heuristic")
        route2 = nx.shortest_path(G, source=viavertex1, target=viavertex2, weight="weight_heuristic")
        route3 = nx.shortest_path(G, source=viavertex2, target=start, weight="weight_heuristic")
    except NetworkXNoPath:
        return [start]
    
    # Remove out-and back
    route = combine_routes(route1, route2, route3)
    route = remove_out_and_back(route, viavertex1)
    route = remove_out_and_back(route, viavertex2)
    
    return route

def get_length_of_route(route_gdf):
    return route_gdf["length"].sum()

def heuristic(G, start_vertex, route_length, pref):
    possible_via_vertices = find_random_pairs_of_via_vertices(G, start_vertex, route_length)
    best_route = [start_vertex]
    best_route_dev = math.inf
    
    for i, pair_of_via_vertices in enumerate(possible_via_vertices):
        route = generate_heuristic_route(G, start_vertex, pair_of_via_vertices[0], pair_of_via_vertices[1], pref)
        #weight = weight_of_route(ox.routing.route_to_gdf(G, route, weight="weight_heuristic"))
        if len(route) <= 1:
            length = 0
        else:
            length = get_length_of_route(ox.routing.route_to_gdf(G, route, weight="length"))
        dev = abs(length - route_length)
        if dev < best_route_dev:
            best_route = route
            best_route_dev = dev
    return best_route
    
def greedy(G, start, k):
    # Calculate shortest path from every vertex to s using Dijkstra on reverse of graph
    SPD = nx.single_source_dijkstra_path_length(G.reverse(copy=True), source=start, weight="length")

    walk = [start]
    L = 0
    u = start
    Rep = defaultdict(int)  # repetition count of edges (u,v)

    for _ in range(2*G.number_of_edges()):
        candidates = []
        L_current = L + SPD[u]

        for n in G.neighbors(u):
            # Make sure it does not go back to start for as long as possible
            if start == n:
                continue
            
            if n not in SPD:
                continue
            L_possible = L + G[u][n][0].get("length") + SPD[n]
            if abs(k - L_possible) <= abs(k - L_current):
                candidates.append(n)

        if not candidates:
            break

        min_rep_nodes = [c for c in candidates if Rep[(u, c)] == min(Rep[(u, c)] for c in candidates)]

        c = max(min_rep_nodes, key=lambda c: G[u][c][0].get("length"))
        Rep[(u, c)] += 1
        Rep[(c, u)] += 1
        walk.append(c)
        L += G[u][c][0].get("length")
        u = c
    
    if u != start:
        # append closest walk 
        shortest_path = nx.shortest_path(G, u, start, weight='length')
        shortest_path.pop(0)
        walk.extend(shortest_path)

    return walk