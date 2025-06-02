from .game_state import GameState
import pygame

class GameOverState(GameState):
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            self.game.change_state('play')
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.game.change_state('menu')

    def update(self):
        pass

    def draw(self, surface):
        self.game.draw_gameover(surface)