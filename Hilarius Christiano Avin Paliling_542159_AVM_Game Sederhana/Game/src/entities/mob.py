import numpy as np
import pygame
from settings import *
from src.utils.vectors import *
from pygame.sprite import Sprite
import math

class Mob(Sprite):
    def __init__(self, x, y, target, game):
        self.pos = np.array([x, y], dtype='float64')
        self.target = target
        self.game = game
        self.radius = 5
        
        self.original_speed = 1.0 + np.random.rand()  # Kecepatan dasar acak
        self.speed = self.original_speed
        self.original_hp = 50
        self.hp = self.original_hp  # Gunakan original_hp sebagai dasar
        self.original_damage = 25
        self.damage = self.original_damage
        
        # Rotation and flipping properties
        self.rotation_angle = 0
        self.flip_horizontal = False
        self.flip_vertical = False

        # Animasi
        self.state = "walk"  # "walk" atau "attack"
        self.facing = "R"    # "R" atau "L"
        self.frame = 0
        self.frame_timer = 0
        self.frame_speed = 0.15

        # Sprite setup
        self.sprites = {
            "walkR": self.load_frames("Game/assets/sprites/Mob/WalkR.png"),
            "walkL": self.load_frames("Game/assets/sprites/Mob/WalkL.png"),
            "attackR": self.load_frames("Game/assets/sprites/Mob/AttackR.png"),
            "attackL": self.load_frames("Game/assets/sprites/Mob/AttackL.png"),
        }
        self.current_frames = self.sprites["walkR"]
        
        # Scaling
        self.original_speed = 1.0
        self.original_radius = 10
        self.original_frame_w = 128
        self.original_frame_h = 128
        self.current_scale = 1.0
        
    def apply_scale(self, scale_factor, difficulty=1.0):
        """Terapkan scaling ke mob dengan parameter difficulty"""
        self.current_scale = 1.0  # Selalu gunakan scale 1.0
        
        # Scale ukuran sprite tetap normal
        frame_w = self.original_frame_w
        frame_h = self.original_frame_h
        
        # Properti mob disesuaikan dengan difficulty
        self.radius = self.original_radius
        self.hp = self.original_hp * difficulty  # HP meningkat dengan difficulty
        self.speed = self.original_speed * (1 + (difficulty - 1) * 0.2)  # Sedikit lebih cepat
        self.damage = self.original_damage * difficulty  # Damage meningkat
        
        # Scale ulang semua animasi ke ukuran normal
        for key in self.sprites.keys():
            scaled_frames = []
            for frame in self.sprites[key]:
                scaled_frame = pygame.transform.smoothscale(frame, (frame_w, frame_h))
                scaled_frames.append(scaled_frame)
            self.sprites[key] = scaled_frames
        
    def load_frames(self, path):
        sheet = pygame.image.load(path).convert_alpha()
        frames = []
        sheet_width, sheet_height = sheet.get_size()
        frame_w, frame_h = 128, 128
        num_frames = sheet_width // frame_w
        for i in range(num_frames):
            frame = sheet.subsurface((i * frame_w, 0, frame_w, frame_h))
            frames.append(frame)
        return frames

    def update(self):
        # Sync transformations with player
        self.rotation_angle = self.target.rotation_angle
        self.flip_horizontal = self.target.flip_horizontal
        self.flip_vertical = self.target.flip_vertical
        
        # Movement logic (independent of player's facing)
        bg_width = self.game.bg_width
        dx = self.target.pos[0] - self.pos[0]
        if abs(dx) > bg_width / 2:
            dx = dx - bg_width if dx > 0 else dx + bg_width
        
        dy = self.target.pos[1] - self.pos[1]
        direction = np.array([dx, dy])
        
        if np.linalg.norm(direction) > 0:
            direction = direction / np.linalg.norm(direction)
        
        # Apply movement (accounting for flips)
        move_dir = direction.copy()
        if self.flip_horizontal:
            move_dir[0] *= -1
        if self.flip_vertical:
            move_dir[1] *= -1
            
        new_pos = self.pos + move_dir * self.speed
        
        # Boundary checks
        new_pos[0] = new_pos[0] % bg_width
        new_pos[1] = np.clip(new_pos[1], 0, self.game.bg_height)
        
        if self.game.is_walkable(new_pos[0], new_pos[1]):
            self.pos = new_pos

        # Animation state
        dist_to_player = np.linalg.norm(self.target.pos - self.pos)
        self.state = "attack" if dist_to_player < 50 else "walk"
        self.facing = "R" if direction[0] >= 0 else "L"  # Keep original facing for animation
        
        # Animation update
        self.current_frames = self.sprites[f"{self.state}{self.facing}"]
        self.frame_timer += self.frame_speed
        if self.frame_timer >= 1:
            self.frame = (self.frame + 1) % len(self.current_frames)
            self.frame_timer = 0

    def draw(self, surface, offset):
        if not self.current_frames or self.frame >= len(self.current_frames):
            return
            
        frame_img = self.current_frames[self.frame]
        
        # Apply transformations in same order as player
        transformed_img = pygame.transform.flip(
            frame_img, 
            self.flip_horizontal, 
            self.flip_vertical
        )
        if self.rotation_angle != 0:
            transformed_img = pygame.transform.rotate(transformed_img, self.rotation_angle)
        
        # Calculate draw position
        draw_pos = self.pos + offset
        rect = transformed_img.get_rect(center=draw_pos.astype(int))
        surface.blit(transformed_img, rect)

        # Draw health bar (accounting for scale)
        bar_width = 50 * self.current_scale
        health_width = (self.hp / 50) * bar_width
        health_pos = (draw_pos[0] - bar_width/2, draw_pos[1] - 40 * self.current_scale)
        pygame.draw.rect(surface, (255,0,0), (*health_pos, health_width, 5 * self.current_scale))

        # Draw wrapped versions (if needed)
        if self.game.bg_width < SCREEN_WIDTH:
            # Left wrap
            left_pos = draw_pos.copy()
            left_pos[0] -= self.game.bg_width
            rect = transformed_img.get_rect(center=left_pos.astype(int))
            surface.blit(transformed_img, rect)
            pygame.draw.rect(surface, (255,0,0), (left_pos[0]-bar_width/2, left_pos[1]-40*self.current_scale, health_width, 5*self.current_scale))
            
            # Right wrap
            right_pos = draw_pos.copy()
            right_pos[0] += self.game.bg_width
            rect = transformed_img.get_rect(center=right_pos.astype(int))
            surface.blit(transformed_img, rect)
            pygame.draw.rect(surface, (255,0,0), (right_pos[0]-bar_width/2, right_pos[1]-40*self.current_scale, health_width, 5*self.current_scale))

    def take_damage(self, amount):
        self.hp -= amount
        return self.hp <= 0