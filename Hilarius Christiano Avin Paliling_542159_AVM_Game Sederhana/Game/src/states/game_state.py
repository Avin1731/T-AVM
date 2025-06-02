class GameState:
    """Base class for game states (menu, play, pause, etc)"""
    def __init__(self, game):
        self.game = game

    def enter(self):
        pass

    def exit(self):
        pass

    def handle_event(self, event):
        pass

    def update(self):
        pass

    def draw(self, surface):
        pass