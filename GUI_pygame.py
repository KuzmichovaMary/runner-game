import pygame
from basic_functions import load_image
from constants import HIGH_SCORE_TOP


class Button:
    def __init__(self, x, y, job_on_click, active=True, color=(255, 200, 10, 0), icon_path_1="", icon_path_2=""):
        self.default_image = load_image(icon_path_1)
        self.clicked_image = load_image(icon_path_2)
        self.image = self.default_image
        self.rect = pygame.Rect(0, 0, self.image.get_rect().w, self.image.get_rect().h).move(x, y)
        self.color = color
        self.icon_path_1 = icon_path_1
        self.icon_path_2 = icon_path_2
        self.clicked = False
        self.job = job_on_click
        self.active = active

    def update(self):
        if self.active:
            mouse_on_widget = self.rect.collidepoint(pygame.mouse.get_pos())
            if mouse_on_widget and not self.clicked:
                self.clicked = True
                self.change_icon()
                self.job()
            elif mouse_on_widget and self.clicked:
                self.clicked = False
                self.change_icon()
                self.job()

    def display(self, screen):
        screen.blit(self.image, self.rect)

    def change_icon(self):
        pass


class Menu:
    def __init__(self, x, y, elements, element_width=40, element_height=40, border=3, color=(98, 98, 98, 100)):
        self.element_width = element_width
        self.n_elements = len(elements)
        self.surface = pygame.Surface((3 * border + element_width + self.element_width,
                                       element_height * self.n_elements + border * (1 + self.n_elements)),
                                      pygame.SRCALPHA)
        self.rect = self.surface.get_rect().move(x - border, y - border)
        self.element_rect = pygame.Rect(0, 0, element_width, element_height)
        self.elements = elements
        self.border = border
        self.element_height = element_height
        self.visible = False
        self.color = color
        self.open_close_btn = Button(x, y, job_on_click=self.change_menu_visibility,
                                     icon_path_1="menu.png", icon_path_2="x.png")

    def display(self, screen):
        self.open_close_btn.rect = self.element_rect.move(self.rect.x + self.border,
                                                          self.rect.y + self.border)
        if self.visible:
            self.surface.fill(self.color)
            self.surface.blit(self.open_close_btn.image, self.element_rect.move(self.border, self.border))
            for i, element in enumerate(self.elements):
                y = self.element_height * i + self.border * (i + 1)
                x = self.border + self.element_width + self.border
                self.surface.blit(element.image, self.element_rect.move(x, y))
                element.rect = self.element_rect.move(self.rect.x + x,
                                                      self.rect.y + y)
            screen.blit(self.surface, self.rect)
        else:
            screen.blit(self.open_close_btn.image, self.element_rect.move(self.rect.x + self.border,
                                                                          self.rect.y + self.border))

    def update(self):
        for element in self.elements:
            element.update()
        self.open_close_btn.update()

    def change_menu_visibility(self):
        if self.visible:
            self.visible = False
            self.open_close_btn.image = self.open_close_btn.default_image
            for element in self.elements:
                element.active = False
        else:
            self.visible = True
            self.open_close_btn.image = self.open_close_btn.clicked_image
            for element in self.elements:
                element.active = True
