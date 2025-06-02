import numpy as np

def circle_collision(pos1, radius1, pos2, radius2):
    """Deteksi tabrakan antara dua lingkaran"""
    distance = np.linalg.norm(pos1 - pos2)
    return distance < (radius1 + radius2)

def polygon_circle_collision(poly_points, circle_pos, circle_radius):
    """Deteksi tabrakan antara polygon dan lingkaran"""
    closest_point = None
    min_distance = float('inf')
    
    for i in range(len(poly_points)):
        start = poly_points[i]
        end = poly_points[(i + 1) % len(poly_points)]
        
        # Proyeksi titik ke garis
        line_vec = end - start
        point_vec = circle_pos - start
        line_length = np.linalg.norm(line_vec)
        line_unit_vec = line_vec / line_length
        projection = np.dot(point_vec, line_unit_vec)
        projection = np.clip(projection, 0, line_length)
        nearest = start + projection * line_unit_vec
        
        distance = np.linalg.norm(nearest - circle_pos)
        if distance < min_distance:
            min_distance = distance
            closest_point = nearest
    
    return min_distance < circle_radius