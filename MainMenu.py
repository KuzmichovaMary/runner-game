import sys

import pygame
from basic_functions import load_image, load_sprite_sheet
from constants import *
from GUI_pygame import Button


FONT_START = "data/fonts/"
FONT_PATHS = ["DotGothic16/DotGothic16-Regular.ttf", "AbrilFatface-Regular.ttf", "ArchitectsDaughter-Regular.ttf",
              "Cinzel-VariableFont_wght.ttf", "SigmarOne-Regular.ttf", "Peepo.ttf", "andina.ttf"]
FONT_FILEPATH = FONT_START + FONT_PATHS[6]


class CharacterInCircle:
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
        pygame.draw.circle(screen, (255, 230, 20, 100), (self.x + 45, self.y + 45), DIAMETER_OF_MAINMENU_CIRCLE)
        screen.blit(self.image, self.rect)

    def update_on_mouse_click(self):
        if pygame.Rect(self.x + 5, self.y + 5, DIAMETER_OF_MAINMENU_CIRCLE - 5,
                       DIAMETER_OF_MAINMENU_CIRCLE - 5).collidepoint(*pygame.mouse.get_pos()):
            return self.str
        return None


class DinoCharacterInCircle(CharacterInCircle):
    def __init__(self, x, y):
        super().__init__(x, y, load_image("dino_start_screen.png"), 4, 1)
        self.str = "dino"


class DeerCharacterInCircle(CharacterInCircle):
    def __init__(self, x, y):
        super().__init__(x, y, load_image("deer_stand_n.png"), 3, 1)
        self.str = "deer"


class MainMenu:
    def __init__(self):
        self.active = True
        self.deer = DeerCharacterInCircle(245, 150)
        self.dino = DinoCharacterInCircle(465, 150)
        self.info_button = Button(350, 340, job_on_click=self.change_info_visibility, icon_path_1="info.png",
                                  icon_path_2="info.png")
        self.exit_button = Button(410, 340, job_on_click=sys.exit, icon_path_1="log-out.png", icon_path_2="log-out.png")
        self.display_information = False
        self.display_surface = pygame.Surface((500, 200), pygame.SRCALPHA)
        self.display_rect = pygame.Rect(150, 100, 200, 500)
        self.info = ["Choose character to start playing.",
                     "Dino is classical Chrome variant.",
                     "Deer is mine. It's a bit harder.",
                     "Avoid obstacles.",
                     "(c) MaryKuzmicheva, Chromium Authors"]
        self.open_close_btn = Button(600, 110, job_on_click=self.change_info_visibility,
                                     icon_path_1="x.png", icon_path_2="x.png")

    def change_info_visibility(self):
        self.display_information = abs(self.display_information - 1)
        self.active = abs(self.active - 1)

    def display_info(self, screen):
        self.display_surface.fill((90, 90, 90, 0))
        if self.display_information:
            pygame.draw.rect(self.display_surface, (90, 90, 90, 200), (0, 0, 500, 200), border_radius=10)
            for i, line in enumerate(self.info):
                self.display_text(line, 10 + 5 * i + 20 * i, self.display_surface, 20, pos="align-left", width=400)
            screen.blit(self.display_surface, self.display_rect)
            self.open_close_btn.display(screen)

    def display_text(self, text, y, screen, font_size=50, pos="middle", x=10, width=WIDTH):
        font = pygame.font.Font(FONT_FILEPATH, font_size)
        text = font.render(text, True, (0, 0, 0, 100))
        text_width = text.get_rect().w
        if pos == "middle":
            screen.blit(text, (width / 2 - text_width / 2, y))
        else:
            screen.blit(text, (x, y))

    def draw(self, screen):
        screen.fill((255, 255, 255, 255))
        self.deer.draw(screen)
        self.dino.draw(screen)
        self.display_text("Runner", 20, screen, 40)
        self.display_text("Choose character to start a game.", 60, screen, 30)
        self.info_button.display(screen)
        self.exit_button.display(screen)
        self.display_info(screen)

    def update_on_mouse_click(self):
        self.info_button.update()
        self.exit_button.update()
        self.open_close_btn.update()
        if self.active:
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

