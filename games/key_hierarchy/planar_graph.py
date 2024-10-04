# voronoi_map_util.py

import numpy as np
from scipy.spatial import Voronoi
from shapely.geometry import Polygon, MultiPolygon, LineString
from shapely.ops import triangulate, unary_union
import random
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection

def generate_points(n, seed=None):
    """
    Generate n points within the normalized range [0, 1].
    """
    if seed is not None:
        np.random.seed(seed)
    points = np.random.rand(n, 2)
    return points

def compute_voronoi(points, wrap_x=False, wrap_y=False):
    """
    Compute the Voronoi diagram of the specified set of points.
    Optionally make the map wrap in the x, y, or both directions.
    Returns the Voronoi diagram and a mapping from extended point indices to original indices.
    """
    # Create shifted copies of the points for wrapping
    extended_points = []
    point_indices = []
    shifts = [(0, 0)]  # No shift

    if wrap_x and wrap_y:
        shifts = [(dx, dy) for dx in [-1, 0, 1] for dy in [-1, 0, 1]]
    elif wrap_x:
        shifts = [(dx, 0) for dx in [-1, 0, 1]]
    elif wrap_y:
        shifts = [(0, dy) for dy in [-1, 0, 1]]

    for shift in shifts:
        shifted_points = points + np.array(shift)
        extended_points.append(shifted_points)
        # Map extended points back to original indices
        point_indices.extend(range(len(points)))

    extended_points = np.vstack(extended_points)
    point_indices = np.array(point_indices)

    # Compute Voronoi diagram
    vor = Voronoi(extended_points)

    return vor, point_indices

def get_neighbors(vor, point_indices):
    """
    Return a dictionary mapping point IDs to their neighboring point IDs.
    """
    num_original_points = np.max(point_indices) + 1
    neighbors = {i: set() for i in range(num_original_points)}

    # Build neighbor relationships
    for (p1, p2) in vor.ridge_points:
        idx1 = point_indices[p1]
        idx2 = point_indices[p2]
        if idx1 != idx2:
            neighbors[idx1].add(idx2)
            neighbors[idx2].add(idx1)

    # Convert sets to lists
    neighbors = {i: list(neighbors[i]) for i in neighbors}

    return neighbors

def get_cell_polygon(vor, point_indices, original_point_index):
    """
    Get the polygon of a Voronoi cell corresponding to the original point index.
    """
    # Find indices of extended points mapping to the original point
    extended_point_indices = np.where(point_indices == original_point_index)[0]

    # Collect regions corresponding to these extended points
    polygons = []
    for idx in extended_point_indices:
        region_index = vor.point_region[idx]
        region = vor.regions[region_index]
        if -1 in region or len(region) == 0:
            continue  # Skip infinite or empty regions
        vertices = [vor.vertices[i] for i in region]
        polygon = Polygon(vertices)
        polygons.append(polygon)

    if not polygons:
        return None

    # Merge polygons using unary_union
    cell_polygon = unary_union(polygons)

    return cell_polygon

def get_normalization_transform(polygon):
    """
    Get functions to map points to and from a normalized coordinate system within the polygon.
    """
    minx, miny, maxx, maxy = polygon.bounds
    scale_x = maxx - minx
    scale_y = maxy - miny

    def to_normalized(x, y):
        nx = (x - minx) / scale_x if scale_x != 0 else 0.0
        ny = (y - miny) / scale_y if scale_y != 0 else 0.0
        return nx, ny

    def to_original(nx, ny):
        x = nx * scale_x + minx
        y = ny * scale_y + miny
        return x, y

    return to_normalized, to_original

def random_point_in_triangle(triangle):
    """
    Sample a random point within a triangle.
    """
    x1, y1 = triangle.exterior.coords[0]
    x2, y2 = triangle.exterior.coords[1]
    x3, y3 = triangle.exterior.coords[2]

    r1 = random.random()
    r2 = random.random()

    if r1 + r2 > 1:
        r1 = 1 - r1
        r2 = 1 - r2

    x = x1 + r1 * (x2 - x1) + r2 * (x3 - x1)
    y = y1 + r1 * (y2 - y1) + r2 * (y3 - y1)

    return x, y

def generate_points_in_cell(polygon, num_points, cell_id, depth):
    """
    Generate points within a given cell polygon, using a seed based on cell ID and depth.
    Points are generated within a normalized version of the cell.
    """
    seed = hash((cell_id, depth))
    random.seed(seed)

    # Handle MultiPolygon by converting it to a list of Polygons
    if isinstance(polygon, Polygon):
        polygons = [polygon]
    elif isinstance(polygon, MultiPolygon):
        polygons = list(polygon.geoms)
    else:
        raise ValueError("Input is neither a Polygon nor a MultiPolygon")

    points_in_cell = []
    total_area = sum(poly.area for poly in polygons)

    for poly in polygons:
        if poly.area == 0:
            continue  # Skip degenerate polygons

        # Normalize the polygon
        to_normalized, to_original = get_normalization_transform(poly)
        normalized_coords = [to_normalized(x, y) for x, y in poly.exterior.coords]
        normalized_polygon = Polygon(normalized_coords)

        # Triangulate the normalized polygon
        triangles = triangulate(normalized_polygon)
        areas = [triangle.area for triangle in triangles]
        triangle_total_area = sum(areas)
        if triangle_total_area == 0:
            continue  # Skip degenerate polygons
        area_weights = [area / triangle_total_area for area in areas]

        # Determine the number of points to generate in this polygon
        num_points_in_poly = max(1, int(num_points * (poly.area / total_area)))

        for _ in range(num_points_in_poly):
            # Select a triangle based on area weights
            triangle = random.choices(triangles, weights=area_weights, k=1)[0]
            x, y = random_point_in_triangle(triangle)
            x_orig, y_orig = to_original(x, y)
            points_in_cell.append([x_orig, y_orig])

    points_in_cell = np.array(points_in_cell)

    return points_in_cell

def generate_points_in_adjacent_cell(vor, point_indices, original_point_index, num_points, cell_id, depth):
    """
    Generate points in an adjacent cell and update the graph to connect all points at that level.
    """
    # Get the polygon of the adjacent cell
    cell_polygon = get_cell_polygon(vor, point_indices, original_point_index)
    if cell_polygon is None:
        return None

    # Generate points within the cell
    points_in_cell = generate_points_in_cell(cell_polygon, num_points, cell_id, depth)

    return points_in_cell

def plot_voronoi_and_cell_points(points, vor, point_indices, cell_polygon, points_in_cell):
    """
    Plots the top-level Voronoi diagram, the specific cell, and the generated points within it.
    """
    fig, ax = plt.subplots(figsize=(8, 8))

    # Plot the Voronoi diagram
    # Prepare lines for plotting
    lines = []
    for ridge_vertices in vor.ridge_vertices:
        if -1 in ridge_vertices:
            continue  # Skip infinite ridges
        v0, v1 = vor.vertices[ridge_vertices]
        # Clip lines to [0,1] x [0,1] bounds
        line = LineString([v0, v1]).intersection(Polygon([(0,0), (1,0), (1,1), (0,1)]))
        if line.is_empty:
            continue
        if isinstance(line, LineString):
            x, y = line.xy
            lines.append([(x[0], y[0]), (x[1], y[1])])
        elif isinstance(line, MultiPolygon):
            for geom in line.geoms:
                x, y = geom.xy
                lines.append([(x[0], y[0]), (x[1], y[1])])

    # Create a LineCollection
    lc = LineCollection(lines, colors='gray', linewidths=0.5)
    ax.add_collection(lc)

    # Plot the initial points
    ax.scatter(points[:, 0], points[:, 1], color='blue', s=10, label='Initial Points')

    # Plot the specific cell polygon
    if isinstance(cell_polygon, Polygon):
        x, y = cell_polygon.exterior.xy
        ax.plot(x, y, color='black', linewidth=2, label='Selected Cell')
        # Plot interior holes if any
        for interior in cell_polygon.interiors:
            xh, yh = interior.xy
            ax.plot(xh, yh, color='black', linewidth=2)
    elif isinstance(cell_polygon, MultiPolygon):
        for poly in cell_polygon.geoms:
            x, y = poly.exterior.xy
            ax.plot(x, y, color='black', linewidth=2, label='Selected Cell')
            # Plot interior holes if any
            for interior in poly.interiors:
                xh, yh = interior.xy
                ax.plot(xh, yh, color='black', linewidth=2)

    # Plot the generated points within the cell
    ax.scatter(points_in_cell[:, 0], points_in_cell[:, 1], color='red', s=20, label='Generated Points')

    ax.set_aspect('equal')
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_title('Voronoi Diagram and Generated Points Within a Cell')
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.legend()
    plt.show()

# Example usage:
if __name__ == "__main__":
    # Generate initial points
    n = 100
    points = generate_points(n, seed=0)

    # Compute Voronoi diagram with wrapping in x and y directions
    vor, point_indices = compute_voronoi(points, wrap_x=True, wrap_y=True)

    # Get neighbors
    neighbors = get_neighbors(vor, point_indices)

    # Generate points within a specific cell
    original_point_index = 0  # Index of the cell's point
    cell_id = original_point_index
    depth = 1
    num_points_in_cell = 100  # Increase number for better visualization

    cell_polygon = get_cell_polygon(vor, point_indices, original_point_index)
    if cell_polygon:
        points_in_cell = generate_points_in_cell(cell_polygon, num_points_in_cell, cell_id, depth)

        # Plot the Voronoi diagram, the cell, and the points within it
        plot_voronoi_and_cell_points(points, vor, point_indices, cell_polygon, points_in_cell)
    else:
        print(f"Cell {cell_id} is infinite or could not be retrieved.")