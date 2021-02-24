from random import randint, choice

import pygame
from pygame.locals import *
from basic_functions import load_image, load_sprite_sheet
from constants import *
from time import time


class DistanceMeter:
    def __init__(self):
        self.distance = 0
        self.play_achievement_sound = False
        self.numbers = {num: image for num, image in enumerate(load_sprite_sheet(load_image("numbers.png"), 10, 1))}
        self.num_rect = self.numbers[0].get_rect()
        self.num_h = self.num_rect.h
        self.num_w = self.num_rect.w
        self.hi_image = load_image("hi.png")
        self.hi_rect = self.hi_image.get_rect()
        self.hi_w = self.hi_rect.w
        self.hi_h = self.hi_rect.h
        self.max_result = 0
        self.flashing = False
        self.flashing_timer = 0

    def draw_num(self, num, screen, top, right):
        num = self.real_distance(num)
        zeros = (5 - len(str(num))) * "0"
        to_draw = zeros + str(num)
        for i in range(5):
            screen.blit(self.numbers[int(to_draw[i])],
                        self.num_rect.move(WIDTH - right - (HIGH_SCORE_TOP - DISTANCE_METER_SPACE) - (5 - i) * self.num_w, top))

    def draw(self, screen):
        hi_x = WIDTH - 3 * DISTANCE_METER_SPACE - 10 * self.num_w - self.hi_w - (HIGH_SCORE_TOP - DISTANCE_METER_SPACE)
        hi_y = HIGH_SCORE_TOP
        screen.blit(self.hi_image, self.hi_rect.move(hi_x,  hi_y))
        first_num_right = 2 * DISTANCE_METER_SPACE + 5 * self.num_w
        self.draw_num(self.max_result, screen, HIGH_SCORE_TOP, first_num_right)
        if self.flashing:
            if self.flashing_timer < 10 or 25 > self.flashing_timer > 15 or self.flashing_timer > 30:
                self.draw_num(self.distance, screen, HIGH_SCORE_TOP, DISTANCE_METER_SPACE)
        else:
            self.draw_num(self.distance, screen, HIGH_SCORE_TOP, DISTANCE_METER_SPACE)

    def real_distance(self, distance):
        return round(distance * COEFFICIENT)

    def update(self, delta_time, speed):
        self.distance += round(delta_time * speed * DELTA_TIME_CONST)
        real_distance = self.real_distance(self.distance)
        if not self.flashing and real_distance % ACHIEVEMENT_DISTANCE == 0 and real_distance:
            self.play_achievement_sound = True
            self.flashing = True
        if self.flashing_timer > 42:
            # self.play_achievement_sound = False
            self.flashing_timer = 0
            self.flashing = False
        self.flashing_timer += 1

    def restart(self):
        self.distance = 0
        self.play_achievement_sound = False
        self.flashing = False
        self.flashing_timer = 0
