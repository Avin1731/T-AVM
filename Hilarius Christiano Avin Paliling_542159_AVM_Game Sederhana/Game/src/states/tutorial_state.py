from .game_state import GameState
import pygame

class TutorialState(GameState):
    def __init__(self, game):
        super().__init__(game)
        # Load fonts
        self.title_font = pygame.font.SysFont('Arial', 48, bold=True)
        self.text_font = pygame.font.SysFont('Arial', 32)
        self.control_font = pygame.font.SysFont('Arial', 28)
        
        # Tutorial content
        self.tutorial_pages = [
            [
                "CONTROLS",
                "WASD - Movement",
                "LShift - Run",
                "RClick - Shoot",
                "Q/E - Rotate",
                "H/V - Flip"
            ],
            [
                "ZOOM CONTROLS",
                "+ - Zoom In",
                "- - Zoom Out",
                "",
                "Other Controls",
                "ESC - Pause",
                "M - Menu"
            ]
        ]
        self.current_page = 0

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:  # Right arrow for next page
                if self.current_page < len(self.tutorial_pages) - 1:
                    self.current_page += 1
            elif event.key == pygame.K_LEFT:  # Left arrow for previous page
                if self.current_page > 0:
                    self.current_page -= 1
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                self.game.change_state('menu')
            elif event.key == pygame.K_ESCAPE:
                self.game.change_state('menu')

    def update(self):
        pass

    def draw(self, surface):
        surface.fill((30, 30, 70))
        
        # Draw title
        title = self.title_font.render("TUTORIAL", True, (255, 215, 0))
        surface.blit(title, (surface.get_width()//2 - title.get_width()//2, 80))
        
        # Draw current page content
        y_position = 180
        line_spacing = 40
        
        # Draw page indicator
        page_text = self.text_font.render(
            f"Page {self.current_page + 1}/{len(self.tutorial_pages)}", 
            True, (150, 150, 150))
        surface.blit(page_text, (surface.get_width()//2 - page_text.get_width()//2, 120))
        
        # Draw tutorial items
        for i, line in enumerate(self.tutorial_pages[self.current_page]):
            if i == 0:  # Section title
                text = self.text_font.render(line, True, (255, 255, 255))
            else:
                text = self.control_font.render(line, True, (200, 200, 255))
            surface.blit(text, (surface.get_width()//2 - text.get_width()//2, y_position))
            y_position += line_spacing
        
        # Draw navigation instructions
        nav_text = self.control_font.render(
            "Use LEFT/RIGHT arrows to navigate", 
            True, (150, 255, 150))
        surface.blit(nav_text, (surface.get_width()//2 - nav_text.get_width()//2, 
                     surface.get_height() - 80))
        
        # Draw exit instructions
        exit_text = self.control_font.render(
            "ENTER/SPACE to return to menu | ESC to exit", 
            True, (200, 150, 150))
        surface.blit(exit_text, (surface.get_width()//2 - exit_text.get_width()//2, 
                     surface.get_height() - 40))