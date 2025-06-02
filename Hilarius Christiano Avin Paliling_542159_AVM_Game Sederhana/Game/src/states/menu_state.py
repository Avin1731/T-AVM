from .game_state import GameState
import pygame
from settings import TITLE

class MenuState(GameState):
    def __init__(self, game):
        super().__init__(game)
        
        self.title_font = None
        self.option_font = None
        self.selected_option = 0
        self.options = [
            {"text": "Start Game (Enter)", "key": pygame.K_RETURN, "action": "play", "color": (100, 255, 100)},
            {"text": "Tutorial (T)", "key": pygame.K_t, "action": "tutorial", "color": (100, 200, 255)},
            {"text": "Credits (C)", "key": pygame.K_c, "action": "credits", "color": (255, 150, 100)},
            {"text": "Quit (Esc)", "key": pygame.K_ESCAPE, "action": "quit", "color": (255, 100, 100)}
        ]
        self.load_assets()
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
        # Navigasi menu
            if event.key == pygame.K_DOWN:
                self.selected_option = (self.selected_option + 1) % len(self.options)
            elif event.key == pygame.K_UP:
                self.selected_option = (self.selected_option - 1) % len(self.options)
            elif event.key == pygame.K_RETURN:
                # Eksekusi aksi untuk opsi yang dipilih
                selected_action = self.options[self.selected_option]["action"]
                self.game.change_state(selected_action)
            else:
                # Cek shortcut keyboard untuk setiap opsi
                for option in self.options:
                    if event.key == option["key"]:
                        self.game.change_state(option["action"])
                        break

    def load_assets(self):
        # Load fonts
        self.title_font = pygame.font.Font(None, 72)
        self.option_font = pygame.font.Font(None, 42)
        
        # Create background surface - access screen dimensions through the game reference
        self.background = pygame.Surface((self.game.screen_width, self.game.screen_height))
        # Fill with gradient
        for y in range(self.game.screen_height):
            color = (30, 30 + y//10, 60 + y//20)
            pygame.draw.line(self.background, color, (0, y), (self.game.screen_width, y))

    def load_assets(self):
        # Background gradient yang lebih smooth
        self.background = pygame.Surface((self.game.screen_width, self.game.screen_height))
        for y in range(self.game.screen_height):
            # Gradien biru gelap ke ungu
            color = (10, 15, 40 + int(y * 0.1))
            pygame.draw.line(self.background, color, (0, y), (self.game.screen_width, y))
        
        # Font yang lebih modern
        self.title_font = pygame.font.Font(None, 80)
        self.option_font = pygame.font.Font(None, 48)
    
    def update(self):
        pass

    def draw(self, surface):
        # Draw background
        surface.blit(self.background, (0, 0))
        
        # Panel tengah dengan efek glassmorphism
        panel_rect = pygame.Rect(
            self.game.screen_width//2 - 250,
            50,
            500,
            self.game.screen_height - 100
        )
        
        # Efek glass (transparan dengan blur)
        glass_surface = pygame.Surface((500, self.game.screen_height - 100), pygame.SRCALPHA)
        pygame.draw.rect(glass_surface, (30, 30, 60, 150), glass_surface.get_rect(), border_radius=25)
        surface.blit(glass_surface, (self.game.screen_width//2 - 250, 50))
        
        # Judul game dengan efek neon
        title = self.title_font.render("SURVIVAL HARDCORE", True, (50, 255, 50))
        title_shadow = self.title_font.render("SURVIVAL HARDCORE", True, (0, 100, 0))
        
        # Efek glow
        surface.blit(title_shadow, (self.game.screen_width//2 - title.get_width()//2 + 3, 80 + 3))
        surface.blit(title, (self.game.screen_width//2 - title.get_width()//2, 80))
        
        # Subtitle
        subtitle = self.option_font.render("MATRIX EDITION", True, (200, 200, 255))
        surface.blit(subtitle, (self.game.screen_width//2 - subtitle.get_width()//2, 160))
        
        # Menu options dengan efek hover modern
        for i, option in enumerate(self.options):
            y_pos = 250 + i * 80
            rect = pygame.Rect(self.game.screen_width//2 - 180, y_pos - 10, 360, 60)
            
            if i == self.selected_option:
                # Efek tombol aktif
                pygame.draw.rect(surface, (80, 80, 120, 150), rect, border_radius=15)
                pygame.draw.rect(surface, (100, 255, 100), rect, 2, border_radius=15)
                text_color = (220, 255, 220)
            else:
                # Efek tombol normal
                pygame.draw.rect(surface, (50, 50, 80, 100), rect, border_radius=15)
                text_color = option["color"]
            
            text = self.option_font.render(option["text"], True, text_color)
            surface.blit(text, (self.game.screen_width//2 - text.get_width()//2, y_pos))