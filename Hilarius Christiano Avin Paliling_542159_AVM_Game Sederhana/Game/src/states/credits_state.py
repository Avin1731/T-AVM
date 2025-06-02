from .game_state import GameState
import pygame
import os
import random
import math

class CreditsState(GameState):
    def __init__(self, game):
        super().__init__(game)
        # Initialize fonts
        self.title_font = pygame.font.SysFont('Arial', 48, bold=True)
        self.text_font = pygame.font.SysFont('Arial', 28)
        self.small_font = pygame.font.SysFont('Arial', 20)
        
        # Credit information
        self.credit_lines = [
            "Made by Hilarius Christiano Avin Paliling",
            "TRPL 24-T.AVM",
            "Survival Hardcore Matrix Edition"
        ]
        
        # Load background with original resolution
        self.original_bg = self.load_background("Game/assets/bg/credit.png")
        self.background = self.original_bg.copy()
        self.bg_rect = self.background.get_rect(center=(self.game.screen.get_width()//2, 
                                                  self.game.screen.get_height()//2))
        
        # Animation setup
        self.animation_type = random.choice(["zoom", "pan", "fade", "pixelate", "wave"])
        self.animation_params = {
            "zoom": {"scale": 1.0, "target_scale": 1.2, "speed": 0.001},
            "pan": {"offset_x": 0, "offset_y": 0, "direction": [random.random(), random.random()]},
            "fade": {"alpha": 0, "target_alpha": 255, "fade_in": True},
            "pixelate": {"pixel_size": 1, "max_pixel": 10, "increasing": True},
            "wave": {"time": 0, "amplitude": random.randint(5, 20), 
                    "frequency": random.uniform(0.01, 0.05)}
        }
        
        # Semi-transparent overlay
        self.overlay = pygame.Surface((game.screen.get_width(), game.screen.get_height()), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 180))

    def load_background(self, path):
        """Load background image with original resolution"""
        try:
            return pygame.image.load(path).convert_alpha()
        except:
            print(f"Background image not found at {path}")
            bg = pygame.Surface((self.game.screen.get_width(), self.game.screen.get_height()), pygame.SRCALPHA)
            bg.fill((20, 20, 40, 255))
            return bg

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
            self.game.change_state('menu')

    def update(self):
        """Update current animation"""
        params = self.animation_params[self.animation_type]
        
        if self.animation_type == "zoom":
            params["scale"] += params["speed"]
            if params["scale"] > params["target_scale"]:
                params["scale"] = 1.0  # Reset zoom
            
            # Apply scaling
            new_width = int(self.original_bg.get_width() * params["scale"])
            new_height = int(self.original_bg.get_height() * params["scale"])
            self.background = pygame.transform.scale(self.original_bg, (new_width, new_height))
            self.bg_rect = self.background.get_rect(center=(self.game.screen.get_width()//2, 
                                                      self.game.screen.get_height()//2))
            
        elif self.animation_type == "pan":
            params["offset_x"] += params["direction"][0] * 2
            params["offset_y"] += params["direction"][1] * 2
            
            # Reverse direction at edges
            if abs(params["offset_x"]) > 100:
                params["direction"][0] *= -1
            if abs(params["offset_y"]) > 100:
                params["direction"][1] *= -1
                
        elif self.animation_type == "fade":
            if params["fade_in"]:
                params["alpha"] += 3
                if params["alpha"] >= params["target_alpha"]:
                    params["fade_in"] = False
            else:
                params["alpha"] -= 3
                if params["alpha"] <= 0:
                    params["fade_in"] = True
            
            self.background = self.original_bg.copy()
            self.background.fill((255, 255, 255, params["alpha"]), special_flags=pygame.BLEND_RGBA_MULT)
            
        elif self.animation_type == "pixelate":
            if params["increasing"]:
                params["pixel_size"] += 0.1
                if params["pixel_size"] >= params["max_pixel"]:
                    params["increasing"] = False
            else:
                params["pixel_size"] -= 0.1
                if params["pixel_size"] <= 1:
                    params["increasing"] = True
            
            # Apply pixelation effect
            if params["pixel_size"] > 1:
                small = pygame.transform.scale(self.original_bg, 
                    (int(self.original_bg.get_width() / params["pixel_size"]), 
                     int(self.original_bg.get_height() / params["pixel_size"])))
                self.background = pygame.transform.scale(small, 
                    (self.original_bg.get_width(), self.original_bg.get_height()))
            else:
                self.background = self.original_bg.copy()
                
        elif self.animation_type == "wave":
            params["time"] += 0.1
            # Wave effect will be applied during draw()

    def draw(self, surface):
        # Draw background with current animation
        if self.animation_type == "pan":
            offset_rect = self.bg_rect.move(
                self.animation_params["pan"]["offset_x"],
                self.animation_params["pan"]["offset_y"])
            surface.blit(self.background, offset_rect)
            
        elif self.animation_type == "wave":
            # Apply wave distortion
            wave_params = self.animation_params["wave"]
            temp_surface = pygame.Surface((self.background.get_width(), 
                                         self.background.get_height()), pygame.SRCALPHA)
            
            for y in range(0, self.background.get_height(), 2):  # Step by 2 for performance
                offset = math.sin(y * wave_params["frequency"] + wave_params["time"]) * wave_params["amplitude"]
                temp_surface.blit(self.background, (offset, y), 
                                (0, y, self.background.get_width(), 2))
            
            surface.blit(temp_surface, self.bg_rect)
            
        else:
            surface.blit(self.background, self.bg_rect)
        
        # Draw overlay
        surface.blit(self.overlay, (0, 0))
        
        # Draw title with shadow effect
        title = self.title_font.render("CREDITS", True, (50, 50, 50))
        surface.blit(title, (surface.get_width()//2 - title.get_width()//2 + 3, 103))
        title = self.title_font.render("CREDITS", True, (255, 215, 0))
        surface.blit(title, (surface.get_width()//2 - title.get_width()//2, 100))
        
        # Draw credit lines
        y_position = 180
        line_spacing = 45
        
        for line in self.credit_lines:
            shadow = self.text_font.render(line, True, (20, 20, 20))
            surface.blit(shadow, (surface.get_width()//2 - shadow.get_width()//2 + 2, y_position + 2))
            
            text = self.text_font.render(line, True, (200, 255, 200))
            surface.blit(text, (surface.get_width()//2 - text.get_width()//2, y_position))
            y_position += line_spacing
        
        # Decorative line
        pygame.draw.line(surface, (150, 150, 150), 
                        (surface.get_width()//2 - 100, y_position + 20),
                        (surface.get_width()//2 + 100, y_position + 20), 2)
        
        # Instruction text
        instruction = self.small_font.render("Press any key or click to return to menu", 
                                           True, (200, 200, 255))
        surface.blit(instruction, (surface.get_width()//2 - instruction.get_width()//2, 
                                 y_position + 50))