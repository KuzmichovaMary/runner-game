import pygame
from pygame.locals import *
from basic_functions import load_image, load_sprite_sheet
from constants import *
from time import time


GAME_OVER = False
FPS = 60
width, height = 800, 400


class MainHero:
    def __init__(self, x, y):
        self.frames = []
        self.states = {}
        self.state = RUNNING
        self.counter = 0
        self.image = None
        # self.ms_per_second = self.states[self.state][ms_per_frame]
        self.rect = None
        self.mask = None
        self.jumping = False
        self.ducked = False
        self.crashed = False
        self.v0 = INITIAL_JUMP_VELOCITY
        self.g = 0.6
        self.y0 = y
        self.w, self.h = None, None
        self.iters = 0
        self.ct = None
        self.timer = 0
        self.jump_velocity = self.v0
        self.reached_min_height = False
        self.speedDrop = False

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def start_jump(self, speed):
        self.jump_velocity = self.v0 - (speed / 10)
        self.jumping = True
        self.reached_min_height = False
        self.speedDrop = False

    def end_jump(self):
        if self.reached_min_height and self.jump_velocity < DROP_VELOCITY:
            self.jump_velocity = DROP_VELOCITY

    def update_jump(self, delta_time):
        const = DELTA_TIME_CONST  # self.states[self.state][ms_per_frame]
        t = delta_time * const

        self.rect.top += round(self.jump_velocity * t)
        self.jump_velocity += self.g * t
        if self.rect.bottom >= self.ct + self.w:
            self.jumping = False
            self.rect.top = self.ct

    def update(self, delta_time):
        self.mask = pygame.mask.from_surface(self.image)
        if self.jumping:
            self.image = self.frames[self.states[JUMPING][frames][0]]
            self.rect.w = self.w
            self.rect.h = self.h
            self.update_jump(delta_time)
        elif self.ducked and not self.jumping:
            self.rect.top = self.ct + DINO_RUNNING_HEIGHT - DINO_DUCKED_HEIGHT
            self.image = self.frames[self.states[DUCKING][frames][self.counter % 2]]
            self.rect.width = self.image.get_rect().width
            self.rect.height = self.image.get_rect().height
        elif not self.crashed:
            self.image = self.frames[self.states[RUNNING][frames][self.counter % 2]]
            self.rect.width = self.w
            self.rect.height = self.h
        if self.iters % 5 == 0 and not self.ducked:
            self.counter += 1
        elif self.iters % 10 == 0:
            self.counter += 1
        # self.time += 1
        self.iters += 1

    def restart(self):
        self.state = RUNNING
        self.counter = 0
        self.image = self.frames[self.states[self.state][frames][self.counter % 2]]
        self.mask = pygame.mask.from_surface(self.image)
        self.jumping = False
        self.ducked = False
        self.crashed = False
        self.v0 = INITIAL_JUMP_VELOCITY
        self.g = 0.6
        self.iters = 0
        self.rect.top = self.ct
        self.timer = 0
        self.jump_velocity = self.v0
        self.reached_min_height = False
        self.speedDrop = False


class TRex(MainHero):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.frames = load_sprite_sheet(load_image("dino_rd_3.png"), 5, 1) + \
                      load_sprite_sheet(load_image("dino_d.png"), 2, 1) + [load_image("dino_dd.png")]
        self.states = {
            1: {
                0: [2, 3],
                1: 1000 / 12
            },
            2: {
                0: [4],
                1: 1000 / 60
            },
            3: {
                0: [0],
                1: 1000 / 60
            },
            4: {
                0: [5, 6],
                1: 1000 / 8
            },
            5: {
                0: [-1]
            }
        }
        self.image = self.frames[self.states[self.state][frames][self.counter % 2]]
        # self.ms_per_second = self.states[self.state][ms_per_frame]
        self.rect = self.image.get_rect().move(x, y)
        self.mask = pygame.mask.from_surface(self.image)
        self.w, self.h = self.image.get_rect().w, self.image.get_rect().h
        self.ct = self.rect.top
        self.v0 -= 1


class Deer(MainHero):
    def __init__(self, x, y):
        super().__init__(x, y)
        for i in range(5):
            self.frames.append(load_image(f"deer0{i + 1}_no_black.png"))
        self.states = {
            1: {
                0: [0, 1, 2, 3, 4],
                1: 1000 / 12
            },
            2: {
                0: [-1],
                1: 1000 / 60
            },
            3: {
                0: [2],
                1: 1000 / 60
            },
            4: {
                0: [0, 1, 2, 3, 4],
                1: 1000 / 8
            },
            5: {
                0: [-1]
            }
        }
        self.run_len = len(self.states[RUNNING][frames])
        self.duck_len = len(self.states[DUCKING][frames])
        self.image = self.frames[self.states[self.state][frames][self.counter % self.run_len]]
        self.rect = self.image.get_rect().move(x, y)
        self.mask = pygame.mask.from_surface(self.image)
        self.w, self.h = self.image.get_rect().w, self.image.get_rect().h
        self.ct = self.rect.top

    def update(self, delta_time):
        self.mask = pygame.mask.from_surface(self.image)
        if self.jumping:
            self.image = self.frames[self.states[JUMPING][frames][0]]
            self.rect.w = self.w
            self.rect.h = self.h
            self.update_jump(delta_time)
        elif self.ducked and not self.jumping and False:  # Deer can't run with head down
            self.rect.top = self.ct + DINO_RUNNING_HEIGHT - DINO_DUCKED_HEIGHT
            self.image = self.frames[self.states[DUCKING][frames][self.counter % self.duck_len]]
            self.rect.width = self.image.get_rect().width
            self.rect.height = self.image.get_rect().height
        elif not self.crashed:
            self.image = self.frames[self.states[RUNNING][frames][self.counter % self.run_len]]
            self.rect.width = self.w
            self.rect.height = self.h
        if self.iters % 5 == 0 and not self.ducked:
            self.counter += 1
        elif self.iters % 5 == 0:
            self.counter += 1
        # self.time += 1
        self.iters += 1



