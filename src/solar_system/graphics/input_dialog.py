"""Simple input dialog for pygame applications."""

import pygame
from typing import Optional, Tuple


class InputDialog:
    """Simple text input dialog for getting user input."""

    def __init__(self, screen, title: str, prompt: str, default_value: str = ""):
        self.screen = screen
        self.title = title
        self.prompt = prompt
        self.input_text = default_value
        self.font = pygame.font.Font(None, 24)
        self.active = True
        self.result = None

        # Dialog dimensions
        self.width = 400
        self.height = 200
        self.x = (screen.get_width() - self.width) // 2
        self.y = (screen.get_height() - self.height) // 2

        # Colors
        self.bg_color = (50, 50, 50)
        self.border_color = (255, 255, 255)
        self.text_color = (255, 255, 255)
        self.input_bg_color = (30, 30, 30)
        self.input_border_color = (100, 100, 100)

    def handle_event(self, event) -> bool:
        """Handle pygame events. Returns True if dialog should continue."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                # Accept input
                self.result = self.input_text
                self.active = False
                return False
            elif event.key == pygame.K_ESCAPE:
                # Cancel input
                self.result = None
                self.active = False
                return False
            elif event.key == pygame.K_BACKSPACE:
                # Remove last character
                self.input_text = self.input_text[:-1]
            else:
                # Add character if it's printable
                if event.unicode.isprintable():
                    self.input_text += event.unicode

        return True

    def draw(self):
        """Draw the input dialog."""
        # Draw background
        dialog_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(self.screen, self.bg_color, dialog_rect)
        pygame.draw.rect(self.screen, self.border_color, dialog_rect, 2)

        # Draw title
        title_surface = self.font.render(self.title, True, self.text_color)
        title_x = self.x + (self.width - title_surface.get_width()) // 2
        self.screen.blit(title_surface, (title_x, self.y + 20))

        # Draw prompt
        prompt_surface = self.font.render(self.prompt, True, self.text_color)
        prompt_x = self.x + 20
        self.screen.blit(prompt_surface, (prompt_x, self.y + 60))

        # Draw input box
        input_rect = pygame.Rect(self.x + 20, self.y + 90, self.width - 40, 30)
        pygame.draw.rect(self.screen, self.input_bg_color, input_rect)
        pygame.draw.rect(self.screen, self.input_border_color, input_rect, 1)

        # Draw input text
        input_surface = self.font.render(self.input_text, True, self.text_color)
        self.screen.blit(input_surface, (input_rect.x + 5, input_rect.y + 5))

        # Draw cursor
        cursor_x = input_rect.x + 5 + input_surface.get_width()
        if pygame.time.get_ticks() % 1000 < 500:  # Blink cursor
            pygame.draw.line(self.screen, self.text_color,
                           (cursor_x, input_rect.y + 5),
                           (cursor_x, input_rect.y + 25), 1)

        # Draw instructions
        instructions = ["Press ENTER to confirm, ESC to cancel"]
        inst_surface = self.font.render(instructions[0], True, self.text_color)
        inst_x = self.x + (self.width - inst_surface.get_width()) // 2
        self.screen.blit(inst_surface, (inst_x, self.y + 140))


def get_text_input(screen, title: str, prompt: str, default_value: str = "") -> Optional[str]:
    """Show input dialog and return the entered text or None if cancelled."""
    dialog = InputDialog(screen, title, prompt, default_value)
    clock = pygame.time.Clock()

    while dialog.active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if not dialog.handle_event(event):
                break

        # Clear screen and redraw dialog
        screen.fill((0, 0, 0))
        dialog.draw()
        pygame.display.flip()
        clock.tick(60)

    return dialog.result
