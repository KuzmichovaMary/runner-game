import pygame
from basic_functions import load_image, load_sprite_sheet
from constants import *


class HeroInCircle:
    def __init__(self, x, y, image_path, columns, rows, animated=True):
        self.str = ""
        self.frames = load_sprite_sheet(image_path, columns, rows)
        self.image = self.frames[0]
        self.rect = self.image.get_rect().move(x, y)
        self.iters = 0
        self.counter = 0
        self.n_frames = len(self.frames)
        self.x, self.y = x, y
        self.w, self.h = self.rect.w, self.rect.h
        self.closed_eyes = False
        self.delta = 10

    def update(self):
        self.iters += 1
        if self.iters % 500 == 0:
            self.image = self.frames[-1]
            self.closed_eyes = True
        elif self.closed_eyes and self.iters % 10 == 0:
            self.closed_eyes = False
            self.image = self.frames[self.counter]
        elif self.iters % self.delta == 0:
            self.counter += 1
            self.counter %= (self.n_frames - 1)
            self.image = self.frames[self.counter]

    def draw(self, screen):
        pygame.draw.circle(screen, (255, 230, 20, 100), (self.x + 50, self.y + 50), DIAMETER_OF_MAINMENU_CIRCLE)
        screen.blit(self.image, self.rect)

    def update_on_mouse_click(self):
        if pygame.Rect(self.x + 5, self.y + 5, DIAMETER_OF_MAINMENU_CIRCLE - 5,
                       DIAMETER_OF_MAINMENU_CIRCLE - 5).collidepoint(*pygame.mouse.get_pos()):
            return self.str
        return None


class DinoHeroInCircle(HeroInCircle):
    def __init__(self, x, y):
        super().__init__(x, y, load_image("dino_start_screen.png"), 4, 1)
        self.str = "dino"


class DeerHeroInCircle(HeroInCircle):
    def __init__(self, x, y):
        super().__init__(x, y, load_image("deer_stand_n.png"), 3, 1)
        self.str = "deer"


class MainMenu:
    def __init__(self):
        self.deer = DeerHeroInCircle(200, 100)
        self.dino = DinoHeroInCircle(400, 100)

    def display_text(self, text, x, y, screen, font_size=30):
        font = pygame.font.Font(None, 30)
        text = font.render(text, True, (100, 255, 100))
        screen.blit(text, (x, y))

    def draw(self, screen):
        screen.fill((255, 255, 255, 255))
        self.deer.draw(screen)
        self.dino.draw(screen)
        self.display_text("Play dino", 100, 10, screen)

    def update_on_mouse_click(self):
        deer = self.deer.update_on_mouse_click()
        dino = self.dino.update_on_mouse_click()
        if deer:
            return deer
        elif dino:
            return dino
        return None

    def update(self):
        self.dino.update()
        self.deer.update()

