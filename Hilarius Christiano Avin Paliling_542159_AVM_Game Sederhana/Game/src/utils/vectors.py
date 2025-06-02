import numpy as np

def normalize_vector(vector):
    norm = np.linalg.norm(vector)
    if norm == 0: 
        return vector
    return vector / norm

def get_rotation_matrix(angle):
    return np.array([
        [np.cos(angle), -np.sin(angle)],
        [np.sin(angle), np.cos(angle)]
    ])

def apply_transform(point, position, rotation, scale):
    """Terapkan transformasi ke titik"""
    # Buat matriks rotasi
    rot_matrix = get_rotation_matrix(rotation)
    
    # Rotasi titik
    rotated = np.dot(rot_matrix, point)
    
    # Scale titik
    scaled = np.multiply(rotated, scale)
    
    # Translasi
    return position + scaled