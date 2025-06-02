import pygame
import numpy as np
import sys
from pathlib import Path
import math
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, TITLE, FPS

pygame.init()

# Ambil ukuran layar, lalu kurangi agar tidak menutupi taskbar
info = pygame.display.Info()
SCREEN_WIDTH = int(info.current_w * 0.8)
SCREEN_HEIGHT = int(info.current_h * 0.8)

TITLE = "Game Window Mode"
FPS = 60
WHITE = (255, 255, 255)

# Fix import path
sys.path.append(str(Path(__file__).parent))
from settings import *
from src.entities.player import Player
from src.entities.mob import Mob
from src.systems.camera import Camera
from src.states.menu_state import MenuState
from src.states.play_state import PlayState
from src.states.pause_state import PauseState
from src.states.gameover_state import GameOverState
from src.states.credits_state import CreditsState
from src.states.tutorial_state import TutorialState

class Game:
    def __init__(self):
        pygame.init()
        # Store screen dimensions from settings as instance attributes
        self.settings = {
            'game_title': TITLE,  # From your settings import
            'screen_width': SCREEN_WIDTH,
            'screen_height': SCREEN_HEIGHT
            # Add other settings as needed
        }
        
        self.screen_width = SCREEN_WIDTH
        self.screen_height = SCREEN_HEIGHT
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption(self.settings['game_title'])
        
        self.clock = pygame.time.Clock()
        self.running = True
        self.scale_factor = 1.0  # Faktor skala default
        self.min_scale = 0.5    # Skala minimum
        self.max_scale = 2.0     # Skala maksimum

        # State system
        self.states = {
        'menu': MenuState(self),
        'play': PlayState(self),
        'pause': PauseState(self),
        'gameover': GameOverState(self),
        'credits': CreditsState(self),
        'tutorial': TutorialState(self)
        }
        self.current_state = self.states['menu']
        self.current_state.enter()

        # Data gameplay (reset di PlayState.enter)
        self.reset_game()

        # Font untuk UI
        self.font = pygame.font.SysFont('Arial', 24)
        self.game_over_font = pygame.font.Font(None, 72)
        self.instruction_font = pygame.font.Font(None, 36)

        # Load background asli (3840x2160)
        self.bg = pygame.image.load("Game/assets/bg/bg.png").convert()
        # Skala background ke ukuran window
        self.bg_scaled = pygame.transform.smoothscale(self.bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.bg_width = self.bg_scaled.get_width()
        self.bg_height = self.bg_scaled.get_height()
        self.bg_mask = pygame.image.load("Game/assets/bg/bg_mask.png").convert()
        self.bg_mask = pygame.transform.smoothscale(self.bg_mask, (self.bg_width, self.bg_height))
        
        self.last_spawn_time = pygame.time.get_ticks()
        self.spawn_cooldown = MOB_SPAWN_COOLDOWN
        self.difficulty = 1.0
        self.wave = 0
        self.wave_timer = 0
        self.wave_duration = 30000  # 30 detik per wave
        
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_EQUALS or event.key == pygame.K_PLUS:
                self.scale_factor = min(self.scale_factor + 0.1, self.max_scale)
                self.apply_scale_to_entities()
            elif event.key == pygame.K_MINUS:
                self.scale_factor = max(self.scale_factor - 0.1, self.min_scale)
                self.apply_scale_to_entities()
            # Add these to ensure immediate response
            elif event.key == pygame.K_q:
                self.player.rotation_angle = (self.player.rotation_angle - self.player.rotation_speed) % 360
            elif event.key == pygame.K_e:
                self.player.rotation_angle = (self.player.rotation_angle + self.player.rotation_speed) % 360
            elif event.key == pygame.K_h:
                self.player.flip_horizontal = not self.player.flip_horizontal
            elif event.key == pygame.K_v:
                self.player.flip_vertical = not self.player.flip_vertical
    
    def apply_scale_to_entities(self):
        """Terapkan skala ke semua entitas"""
        self.player.apply_scale(self.scale_factor)
        for mob in self.mobs:
            mob.apply_scale(self.scale_factor)
            
    def change_state(self, state_name):
        self.current_state.exit()
        self.current_state = self.states[state_name]
        self.current_state.enter()

    def reset_game(self):
        self.game_over = False
        self.player = Player(np.array([SCREEN_WIDTH//2, SCREEN_HEIGHT//2]), self)
        self.mobs = [Mob(100, 100, self.player, self)]
        self.camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.camera.set_target(self.player)
        self.spawn_timer = 0
        self.spawn_interval = 120
        self.difficulty = 1.0
        self.score = 0
        self.high_score = 0
        self.score_increment = 0.1
        self.kill_score = 100
        self.load_high_score()
        
        self.game_over = False
        self.scale_factor = 1.0  # Reset scale factor
        self.player = Player(np.array([SCREEN_WIDTH//2, SCREEN_HEIGHT//2]), self)
        

    def load_high_score(self):
        try:
            with open('highscore.txt', 'r') as f:
                self.high_score = float(f.read())
        except (FileNotFoundError, ValueError):
            self.high_score = 0

    def save_high_score(self):
        if self.score > self.high_score:
            with open('highscore.txt', 'w') as f:
                f.write(str(int(self.score)))
    
    def apply_scale_to_entities(self):
        """Terapkan skala ke semua entitas"""
        self.player.apply_scale(self.scale_factor)
        for mob in self.mobs:
            mob.apply_scale(1.0, self.difficulty)  # Gunakan scale 1.0 dan kirim difficulty

    def run(self):
        while self.running:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                self.current_state.handle_event(event)
            self.current_state.update()
            self.current_state.draw(self.screen)
            pygame.display.flip()
        self.save_high_score()
        pygame.quit()
        sys.exit()
            
    def update_gameplay(self):
        if self.game_over:
            return self.handle_game_over()

        current_time = pygame.time.get_ticks()
        
        # Sistem wave
        if current_time - self.wave_timer > self.wave_duration:
            self.start_new_wave()
            self.wave_timer = current_time
            
        # Sistem spawn mob
        if (current_time - self.last_spawn_time > self.spawn_cooldown and 
            len(self.mobs) < MAX_MOBS * self.difficulty):
            self.spawn_mob()
            self.last_spawn_time = current_time
            # Sesuaikan cooldown untuk spawn berikutnya
            self.spawn_cooldown = max(500, MOB_SPAWN_COOLDOWN - (self.wave * 100))

        # Dapatkan input keyboard
        keys = pygame.key.get_pressed()

        # Update player dengan input
        self.player.update(keys)

        # Update kamera
        self.camera.update()

        # Handle serangan
        if pygame.mouse.get_pressed()[0]:
            self.player.attack()

        # Update projectile
        self.player.update_projectiles()

        # Cek tabrakan projectile dengan mob
        projectiles_to_remove = []
        mobs_to_remove = []

        for proj_idx, proj in enumerate(self.player.projectiles):
            for mob_idx, mob in enumerate(self.mobs):
                if self.check_collision(proj['pos'], proj['radius'], mob.pos, mob.radius):
                    if mob.take_damage(self.player.damage):
                        mobs_to_remove.append(mob_idx)
                    projectiles_to_remove.append(proj_idx)
                    break

        # Hapus projectile dan mob yang kena
        for idx in sorted(projectiles_to_remove, reverse=True):
            if idx < len(self.player.projectiles):
                self.player.projectiles.pop(idx)

        for idx in sorted(mobs_to_remove, reverse=True):
            if idx < len(self.mobs):
                self.mobs.pop(idx)
                self.score += self.kill_score * self.difficulty

        # Update mob dan cek tabrakan dengan player
        for mob in self.mobs:
            mob.update()
            if self.check_collision(self.player.pos, 15, mob.pos, mob.radius):
                if self.player.take_damage(10):
                    self.game_over = True
                    self.save_high_score()

        # Sistem spawn mob
        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_interval / self.difficulty and len(self.mobs) < 20:
            self.spawn_mob()
            self.spawn_timer = 0
            self.difficulty += 0.05
            self.score += 10

        return False

    def get_random_walkable_pos(self):
        while True:
            x = np.random.uniform(0, self.bg_width)
            y = np.random.uniform(0, self.bg_height)
            if self.is_walkable(x, y):
                return x, y
    
    def start_new_wave(self):
        self.wave += 1
        self.difficulty = 1.0 + (self.wave * 0.2)
        print(f"Wave {self.wave} started! Difficulty: {self.difficulty:.1f}x")
        
        # Atur ulang spawn cooldown untuk wave baru
        self.spawn_cooldown = max(1000, MOB_SPAWN_COOLDOWN - (self.wave * 50))  # Minimal 1 detik
        
    def spawn_mob(self):
        # Tentukan posisi spawn di sekitar player (tidak terlalu dekat)
        spawn_distance = np.random.uniform(200, 400)
        angle = np.random.uniform(0, 2 * math.pi)
        
        # Hitung posisi spawn relatif terhadap player
        spawn_x = self.player.pos[0] + spawn_distance * math.cos(angle)
        spawn_y = self.player.pos[1] + spawn_distance * math.sin(angle)
        
        # Pastikan posisi dalam batas layar dan walkable
        spawn_x = max(0, min(spawn_x, self.bg_width - 1))
        spawn_y = max(0, min(spawn_y, self.bg_height - 1))
        
        if self.is_walkable(spawn_x, spawn_y):
            new_mob = Mob(spawn_x, spawn_y, self.player, self)
            # Terapkan difficulty saat scaling
            new_mob.apply_scale(1.0, self.difficulty)  # Kirim difficulty sebagai parameter
            self.mobs.append(new_mob)
            
            # Tingkatkan kesulitan sedikit setiap spawn
            self.difficulty += MOB_SPAWN_INCREASE_RATE
            self.score += 10 * self.difficulty

    def check_collision(self, pos1, radius1, pos2, radius2):
        distance = np.linalg.norm(pos1 - pos2)
        return distance < (radius1 + radius2)

    def handle_game_over(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            self.__init__()
            return True
        return False

    def draw_gameplay(self, surface):
        # Kamera mengikuti player secara horizontal (atau bisa fixed)
        offset = np.array([0, 0])  # Tidak perlu offset_x

        # Gambar background hanya sekali
        surface.blit(self.bg_scaled, (0, 0))

        # Gambar projectile, player, mobs
        self.player.draw_projectiles(surface, offset)
        self.player.draw(surface, offset)
        for mob in self.mobs:
            mob.draw(surface, offset)

        # Panel score (tetap)
        score_surface = pygame.Surface((200, 200), pygame.SRCALPHA)
        pygame.draw.rect(score_surface, (0, 0, 0, 128), (0, 0, 200, 80), border_radius=5)
        score_text = self.font.render(f"SCORE: {int(self.score)}", True, (255, 255, 0))
        high_score_text = self.font.render(f"HIGH: {int(self.high_score)}", True, (255, 215, 0))
        diff_text = self.font.render(f"DIFFICULTY: {self.difficulty:.1f}x", True, WHITE)
        score_surface.blit(score_text, (10, 10))
        score_surface.blit(high_score_text, (10, 35))
        score_surface.blit(diff_text, (10, 60))
        surface.blit(score_surface, (10, 10))

    def draw_gameover(self, surface):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        game_over_text = self.game_over_font.render("GAME OVER", True, (255, 50, 50))
        text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
        surface.blit(game_over_text, text_rect)

        score_text = self.instruction_font.render(f"Final Score: {int(self.score)}", True, (255, 255, 255))
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 20))
        surface.blit(score_text, score_rect)

        if self.score >= self.high_score:
            hs_text = self.instruction_font.render("NEW HIGH SCORE!", True, (255, 215, 0))
            hs_rect = hs_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 60))
            surface.blit(hs_text, hs_rect)

        retry_text = self.instruction_font.render("Press R to Retry", True, (200, 200, 255))
        retry_rect = retry_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 100))
        surface.blit(retry_text, retry_rect)

    def is_walkable(self, x, y):
        xi = int(x)
        yi = int(y)
        if 0 <= xi < self.bg_width and 0 <= yi < self.bg_height:
            color = self.bg_mask.get_at((xi, yi))
            # Field merah: R tinggi, G & B rendah (misal R > 200, G < 80, B < 80)
            if color.r > 200 and color.g < 80 and color.b < 80:
                return True
        return False

if __name__ == "__main__":
    game = Game()
    game.run()
    pygame.quit()
    sys.exit()