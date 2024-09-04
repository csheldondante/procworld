import math
import random
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
from scipy.spatial import Voronoi, voronoi_plot_2d

# This is a library to recursivel partition a space into subregions and partition those subregions while maintaining a planar graph structure at each level

#


unit_box = np.array([
    [0, 0],
    [0, 1],
    [1, 0],
    [1, 1]
])

def is_point_in_convex_hull(point, bounds):
    for bound in bounds:
        midpoint, normal = bound
        if np.dot(point - midpoint, normal) < 0:
            return False
    return True

def get_neighbors_and_bounds(voronoi):
    neighbors = {}
    bounding_planes = {}
    for index1, index2 in voronoi.ridge_points:
        if index1 not in neighbors:
            neighbors[index1] = set()
        if index2 not in neighbors:
            neighbors[index2] = set()
        neighbors[index1].add(index2)
        neighbors[index2].add(index1)
        p1 = voronoi.points[index1]
        p2 = voronoi.points[index2]
        midpoint = (p1 + p2) / 2
        if index1 not in bounding_planes:
            bounding_planes[index1] = []
        if index2 not in bounding_planes:
            bounding_planes[index2] = []
        bounding_planes[index1].append([midpoint, p2-p1])#consider normalizing the vector
        bounding_planes[index2].append([midpoint, p1-p2])#consider normalizing the vector
        return neighbors, bounding_planes

#lets just limit this to voronoi diagrams, with the index and the maps produced by the methods above we should be able to easily check containment
#we can scale the random points to the range of the bb then check containment and generate new points if needed
#ideally we just generate some moderately large number of points greater than num points and then filter them and repeat if needed in batches
#our loop can terminate as soon as we have num points
def generate_points_within_convex_hull(index: int, voronoi: Voronoi, num_points: int=24, dim: int=2):
    neighbors, bounding_planes = get_neighbors_and_bounds(voronoi)
    return generate_points_within_convex_hull(index, voronoi, neighbors, bounding_planes, num_points, dim)

def generate_points_within_convex_hull(index: int, voronoi: Voronoi, neighbors: dict, bounding_planes: dict, num_points: int=24, dim: int=2):
    points_within_bounds = []
    while len(points_within_bounds) < num_points:
        points = np.random.rand(num_points, dim)
        for point in points:#definitely more efficient to vectorize this and use numpy but this is fine for now
            if is_point_in_convex_hull(point, bounding_planes[index]):
                points_within_bounds.append(point)
            if len(points_within_bounds) == num_points:
                break
    return np.array(points_within_bounds), neighbors, bounding_planes
'''
class LocationNode():
    voronoi: Voronoi
    neighbors: dict
    bounding_planes: dict
    def __init__(self, seed: int, index: int, pos: tuple, parent=None, voronoi: Voronoi=None, neighbors: dict=None, bounding_planes: dict=None):
        self.seed = seed
        self.index = index
        self.pos = pos
        self.parent = parent
        self.voronoi = voronoi
        self.neighbors = neighbors
        self.bounding_planes = bounding_planes

class LocationManager():
    def __init__(self, seed: int=0, dim: int=2, root_type: str="Universe", type_2_subregions: dict=None, type_2_dim: dict=None, type_2_num_points: dict=None):
        np.random.seed(seed)
        random.random(seed)
        num_points = random.randint(5, 24)
        points = np.random.rand(num_points, dim)
        vor = Voronoi(points)
        neighbors, bounds = get_neighbors_and_bounds(vor)
        self.root = LocationNode(0, (0, 0), voronoi=vor, neighbors=neighbors, bounding_planes=bounds)


    #filter points not in the normalized bounding_shape






    



def generate_planar_graph(min_num_points: int=3, max_num_points: int=24, debug: bool=False):
    points = generate_random_points(min_num_points=min_num_points, max_num_points=max_num_points)
    return generate_planar_graph(points, debug)

def generate_planar_graph(points, debug: bool=False):
    # Generate random points
    points = np.vstack([points, unit_box])

    # Compute Voronoi diagram
    vor = Voronoi(points)
    
    # Create a planar graph from the Voronoi vertices
    neighbor_region_indices = {}

    for ridge in vor.ridge_points:
        first, second = ridge
        if first not in neighbor_region_indices:
            neighbor_region_indices[first] = set()
        if second not in neighbor_region_indices:
            neighbor_region_indices[second] = set()
        neighbor_region_indices[first].add(second)
        neighbor_region_indices[second].add(first)
    
    map_regions = []
    for i, point_index in enumerate(vor.point_region):
        region_index = vor.point_region[i]
        region = vor.regions[region_index]
        if not -1 in region and len(region) > 0:
            centroid = np.mean(vor.vertices[region], axis=0)
            map_regions.append(MapNode(i, tuple(centroid)))
        else:
            map_regions.append(None)

    if not debug:
        return map_regions, None, None
    # Initialize the graph
    G = nx.Graph()

    # Add edges between the centroids of neighboring regions
    for i, map_region in enumerate(map_regions):
        if map_region is None:
            continue
        for neighbor_index in neighbors.get(i, []):
            neighbor = map_regions[neighbor_index]
            if neighbor is not None:
                G.add_edge(map_region.pos, neighbor.pos)                
    return map_regions, G, vor

def visualize_voronoi_graph(G, vor):
    pos = {tuple(point): point for point in G.nodes}
    
    # Draw the Voronoi cells
    voronoi_plot_2d(vor, show_points=False, show_vertices=False, line_colors='orange', line_width=.2)
    
    # Draw the graph on top of the Voronoi diagram
    nx.draw(G, pos, with_labels=False, node_size=50, node_color='blue', edge_color='black')
    plt.show()

# Generate and visualize the Voronoi-based planar graph
map_regions, G, vor = generate_planar_graph(debug=True)
visualize_voronoi_graph(G, vor)

'''