import numpy as np
import pygame
from pygame.sprite import Sprite
import sys
from pathlib import Path
import math

# Fix import path
sys.path.append(str(Path(__file__).parent.parent.parent))
from settings import *

class Player(Sprite):
    def __init__(self, pos, game,):
        super().__init__()
        # Position and physics
        self.pos = np.array(pos, dtype='float64')
        self.vel = np.zeros(2)
        self.acc = np.zeros(2)
        self.speed = 5.0
        self.run_speed = 8.0
        self.facing = np.array([0, 1])  # Default facing down
        self.game = game
        
        # Rotation and flipping properties
        self.rotation_angle = 0  # in degrees
        self.flip_horizontal = False
        self.flip_vertical = False
        self.rotation_speed = 5  # degrees per key press
        self.last_h_pressed = False
        self.last_v_pressed = False

        # Animation properties
        self.sprite_width = 128
        self.sprite_height = 128
        self.animations = {
            'idleR': self.load_sprites('Game/assets/sprites/MC/IdleR.png'),
            'idleL': self.load_sprites('Game/assets/sprites/MC/IdleL.png'),
            'attackR': self.load_sprites('Game/assets/sprites/MC/ShotR.png'),
            'attackL': self.load_sprites('Game/assets/sprites/MC/ShotL.png'),
            'walkR': self.load_sprites('Game/assets/sprites/MC/WalkR.png'),
            'walkL': self.load_sprites('Game/assets/sprites/MC/WalkL.png'),
            'runR': self.load_sprites('Game/assets/sprites/MC/RunR.png'),
            'runL': self.load_sprites('Game/assets/sprites/MC/RunL.png'),
        }
        self.state = 'idleR'
        self.direction = (0, 1)  # Default facing down
        self.frame_index = 0
        self.animation_speed = 0.1
        self.attack_animation_speed = 0.2  # Lebih lambat untuk animasi attack

        # Initialize sprite image and rect
        dir_index = self.get_direction_index(self.direction)
        self.image = self.animations[self.state][dir_index][0]
        self.rect = self.image.get_rect(center=pos)

        # Combat and stats
        self.hp = 300
        self.max_hp = 300
        self.stamina = 300
        self.projectiles = []
        self.projectile_speed = 30
        self.projectile_radius = 5
        self.projectile_color = (255, 255, 0)
        self.attack_cooldown_max = 10
        self.attack_cooldown = 0
        self.can_attack = True
        self.damage = 25
        self.is_running = False
        self.is_attacking = False
        self.attack_anim_length = {
            'attackR': len(self.animations['attackR'][0]),
            'attackL': len(self.animations['attackL'][0])
        }
        self.original_sprite_width = 128
        self.original_sprite_height = 128
        self.original_speed = 5.0
        self.original_run_speed = 8.0
        self.original_projectile_radius = 5
        self.current_scale = 1.0
        
    def apply_scale(self, scale_factor):
        """Terapkan scaling ke player"""
        self.current_scale = scale_factor
        # Scale ukuran sprite
        self.sprite_width = int(self.original_sprite_width * scale_factor)
        self.sprite_height = int(self.original_sprite_height * scale_factor)
        
        # Scale kecepatan
        self.speed = self.original_speed * (1/scale_factor)  # Semakin besar, semakin lambat
        self.run_speed = self.original_run_speed * (1/scale_factor)
        
        # Scale projectile
        self.projectile_radius = int(self.original_projectile_radius * scale_factor)
        
        # Scale ulang semua animasi
        for anim_name, anim_frames in self.animations.items():
            for dir_idx in range(4):
                for frame_idx in range(len(anim_frames[dir_idx])):
                    original_frame = anim_frames[dir_idx][frame_idx]
                    scaled_size = (self.sprite_width, self.sprite_height)
                    self.animations[anim_name][dir_idx][frame_idx] = pygame.transform.smoothscale(original_frame, scaled_size)
        
        # Update image dan rect saat ini
        dir_index = self.get_direction_index(self.direction)
        self.image = self.animations[self.state][dir_index][int(self.frame_index)]
        self.rect = self.image.get_rect(center=self.pos)
        
    def load_sprites(self, path):
        """Load single-row sprite sheet and split into animation frames"""
        frame_counts = {
            'IdleR.png': 11, 'IdleL.png': 11,
            'ShotR.png': 4,  # <-- Ubah ke 4
            'ShotL.png': 4,  # <-- Ubah ke 4
            'WalkR.png': 10,  'WalkL.png': 10,
            'RunR.png': 10,  'RunL.png': 10
        }
        filename = Path(path).name
        num_frames = frame_counts.get(filename, 1)
        try:
            sheet = pygame.image.load(path).convert_alpha()
            sheet_width = sheet.get_width()
            max_frames = sheet_width // self.sprite_width
            if num_frames > max_frames:
                print(f"Warning: {filename} only has {max_frames} frames, but {num_frames} requested.")
                num_frames = max_frames
            frames = []
            for i in range(num_frames):
                x = i * self.sprite_width
                frame = sheet.subsurface(pygame.Rect(x, 0, self.sprite_width, self.sprite_height))
                frames.append(frame)
            return [frames] * 4
        except Exception as e:
            print(f"Failed to load spritesheet: {path} ({e})")
            blank_frame = pygame.Surface((self.sprite_width, self.sprite_height), pygame.SRCALPHA)
            return [[blank_frame] * num_frames] * 4

    def get_direction_index(self, direction):
        """Convert direction vector to animation row index"""
        x, y = direction
        if y > 0: return 0  # down
        if x < 0: return 1  # left
        if x > 0: return 2  # right
        if y < 0: return 3  # up
        return 0  # default to down

    def update(self, keys=None):
        """Update player position, animation, and state"""
        # Handle rotation
        if keys is not None:
            if keys[pygame.K_q]:
                self.rotation_angle = (self.rotation_angle - self.rotation_speed) % 360
            if keys[pygame.K_e]:
                self.rotation_angle = (self.rotation_angle + self.rotation_speed) % 360
                
            # Handle flipping
            if keys[pygame.K_h] and not self.last_h_pressed:
                self.flip_horizontal = not self.flip_horizontal
            if keys[pygame.K_v] and not self.last_v_pressed:
                self.flip_vertical = not self.flip_vertical
                
            self.last_h_pressed = keys[pygame.K_h]
            self.last_v_pressed = keys[pygame.K_v]
            
        # Movement dan state tetap diproses meski menyerang
        if keys is not None:
            self.acc = np.zeros(2)
            self.is_running = keys[pygame.K_LSHIFT] and self.stamina > 0
            moving = False
            if keys[pygame.K_w]:
                self.acc[1] -= 1
                moving = True
            if keys[pygame.K_s]:
                self.acc[1] += 1
                moving = True
            if keys[pygame.K_a]:
                self.acc[0] -= 1
                moving = True
            if keys[pygame.K_d]:
                self.acc[0] += 1
                moving = True
            if moving:
                if np.any(self.acc):
                    norm = np.linalg.norm(self.acc)
                    self.acc = self.acc / norm
                    self.direction = tuple(self.acc)
                    self.facing = np.array(self.direction)
                    current_speed = self.run_speed if self.is_running else self.speed
                    self.acc *= current_speed
                    if self.is_running:
                        self.stamina = max(0, self.stamina - 0.5)
                if self.acc[0] < 0:
                    suffix = 'L'
                else:
                    suffix = 'R'
                if self.is_attacking:
                    self.state = 'attack' + suffix
                else:
                    self.state = ('run' if self.is_running else 'walk') + suffix
            else:
                if self.facing[0] < 0:
                    suffix = 'L'
                else:
                    suffix = 'R'
                if self.is_attacking:
                    self.state = 'attack' + suffix
                else:
                    self.state = 'idle' + suffix
                self.stamina = min(100, self.stamina + 0.5)
        else:
            if self.facing[0] < 0:
                suffix = 'L'
            else:
                suffix = 'R'
            if self.is_attacking:
                self.state = 'attack' + suffix
            else:
                self.state = 'idle' + suffix
            self.stamina = min(100, self.stamina + 0.5)

        self.vel = self.acc

        # Batasi Y agar tidak keluar area (misal, 120 sampai HEIGHT-80)
        self.pos[1] = np.clip(self.pos[1], 50, self.game.bg_height - 50)

        new_x = self.pos[0] + self.vel[0]
        new_y = self.pos[1] + self.vel[1]

        # Cek walkable pada posisi baru (tanpa modulo X)
        if self.game.is_walkable(new_x, new_y):
            # Setelah valid, baru lakukan modulo agar X looping
            self.pos[0] = new_x % self.game.bg_width
            self.pos[1] = new_y

        self.rect.center = self.pos

        # Animasi: gunakan kecepatan berbeda untuk attack
        if self.is_attacking:
            self.frame_index += self.attack_animation_speed
            if self.frame_index >= self.attack_anim_length[self.state]:
                self.is_attacking = False
                self.frame_index = 0
        else:
            self.frame_index += self.animation_speed
            if self.frame_index >= len(self.animations[self.state][0]):
                self.frame_index = 0

        dir_index = self.get_direction_index(self.direction)
        self.image = self.animations[self.state][dir_index][int(self.frame_index)]

        # Handle attack cooldown
        if not self.can_attack:
            self.attack_cooldown -= 1
            if self.attack_cooldown <= 0:
                self.can_attack = True

    def attack(self):
        """Create a new projectile and set attack animation"""
        if self.can_attack and np.any(self.facing) and not self.is_attacking:
            # Posisi peluru benar-benar di tengah sprite player
            projectile_pos = self.pos.copy()
            self.projectiles.append({
                'pos': projectile_pos,
                'direction': self.facing.copy(),
                'speed': self.projectile_speed,
                'radius': self.projectile_radius,
                'lifetime': 60
            })
            self.can_attack = False
            self.attack_cooldown = self.attack_cooldown_max
            if self.facing[0] < 0:
                self.state = 'attackL'
            else:
                self.state = 'attackR'
            self.frame_index = 0
            self.is_attacking = True
            return True
        return False

    def update_projectiles(self):
        """Update all active projectiles"""
        for proj in self.projectiles[:]:
            proj['pos'] += proj['direction'] * proj['speed']
            proj['lifetime'] -= 1
            if proj['lifetime'] <= 0:
                self.projectiles.remove(proj)

    def draw_projectiles(self, surface, offset):
        """Draw all active projectiles"""
        for proj in self.projectiles:
            pygame.draw.circle(
                surface,
                self.projectile_color,
                (proj['pos'] + offset).astype(int),
                proj['radius']
            )

    def take_damage(self, amount):
        """Apply damage to player"""
        self.hp -= amount
        if self.hp <= 0:
            self.hp = 0
            return True  # Player died
        return False

    def draw_health_bar(self, surface, offset):
        """Draw health bar above player"""
        bar_width = 50
        bar_height = 5
        fill = (self.hp / self.max_hp) * bar_width
        outline_rect = pygame.Rect(
            self.pos[0] + offset[0] - bar_width//2,
            self.pos[1] + offset[1] - self.sprite_height//2 - 10,
            bar_width, bar_height
        )
        fill_rect = pygame.Rect(
            self.pos[0] + offset[0] - bar_width//2,
            self.pos[1] + offset[1] - self.sprite_height//2 - 10,
            fill, bar_height
        )
        pygame.draw.rect(surface, (255, 0, 0), fill_rect)
        pygame.draw.rect(surface, (255, 255, 255), outline_rect, 1)

        # Draw stamina bar (selalu tampil)
        stamina_width = 30
        stamina_fill = (self.stamina / 100) * stamina_width
        stamina_rect = pygame.Rect(
            self.pos[0] + offset[0] - stamina_width//2,
            self.pos[1] + offset[1] - self.sprite_height//2 - 20,
            stamina_fill, 3
        )
        pygame.draw.rect(surface, (0, 200, 255), stamina_rect)

    def draw(self, surface, offset=np.zeros(2)):
        """Draw player with rotation and flipping"""
        # Get current animation frame
        dir_index = self.get_direction_index(self.direction)
        original_image = self.animations[self.state][dir_index][int(self.frame_index)]
        
        # Apply transformations
        transformed_image = original_image
        if self.flip_horizontal or self.flip_vertical:
            transformed_image = pygame.transform.flip(
                transformed_image, 
                self.flip_horizontal, 
                self.flip_vertical
            )
        if self.rotation_angle != 0:
            transformed_image = pygame.transform.rotate(transformed_image, self.rotation_angle)
        
        # Calculate draw position
        draw_pos = (self.pos + offset - [self.sprite_width//2, self.sprite_height//2]).astype(int)
        surface.blit(transformed_image, draw_pos)
        self.draw_health_bar(surface, offset)