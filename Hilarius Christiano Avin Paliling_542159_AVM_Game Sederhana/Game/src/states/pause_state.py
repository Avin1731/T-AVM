from .game_state import GameState
import pygame

class PauseState(GameState):
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.game.change_state('play')

    def update(self):
        pass

    def draw(self, surface):
        self.game.draw_gameplay(surface)
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))
        font = pygame.font.SysFont('Arial', 48)
        text = font.render("PAUSED", True, (255, 255, 255))
        surface.blit(text, (surface.get_width()//2 - text.get_width()//2, surface.get_height()//2 - 40))