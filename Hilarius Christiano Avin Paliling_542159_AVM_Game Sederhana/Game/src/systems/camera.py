import numpy as np

class Camera:
    def __init__(self, width, height):
        self.offset = np.array([0, 0], dtype=float)
        self.width = width
        self.height = height
        self.zoom = 1.0
        self.target = None
        
    def set_target(self, target):
        self.target = target
        
    def update(self):
        if self.target is not None:
            # Hitung offset agar target di tengah layar
            target_offset = np.array([self.width//2, self.height//2]) - self.target.pos
            self.offset = target_offset
            
    def apply(self, position):
        """Apply camera offset ke posisi entity"""
        return position + self.offset