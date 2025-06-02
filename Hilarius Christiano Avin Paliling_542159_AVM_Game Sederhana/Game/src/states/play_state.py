from .game_state import GameState
import pygame

class PlayState(GameState):
    def enter(self):
        self.game.reset_game()

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_EQUALS or event.key == pygame.K_PLUS:  # Tombol +
                self.game.scale_factor = min(self.game.scale_factor + 0.1, self.game.max_scale)
                self.game.apply_scale_to_entities()
            elif event.key == pygame.K_MINUS:  # Tombol -
                self.game.scale_factor = max(self.game.scale_factor - 0.1, self.game.min_scale)
                self.game.apply_scale_to_entities()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.game.change_state('pause')
        if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
            self.game.change_state('menu')

    def update(self):
        # Cek jika player mati, langsung pindah ke gameover
        if self.game.player.hp <= 0:
            self.game.change_state('gameover')
            return
        self.game.update_gameplay()

    def draw(self, surface):
        self.game.draw_gameplay(surface)