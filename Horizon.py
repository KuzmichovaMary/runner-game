from random import randint, choice

import pygame
from pygame.locals import *
from basic_functions import load_image, load_sprite_sheet
from constants import *
from time import time
from itertools import permutations

GAME_OVER = False
FPS = 60
width, height = 800, 400

OBSTACLES_IMAGES = {"CACTUS_BIG_LARGE": load_image("cactus_biggest.png"),
                    "CACTUS_BIG_MEDIUM": load_image("cactus_two.png"),
                    "CACTUS_BIG_SMALL": load_image("cactus_big_one.png"),
                    "CACTUS_SMALL": load_sprite_sheet(load_image("cactus_small.png"), 6, 1),
                    "PTERODACTYL": load_sprite_sheet(load_image("bird.png"), 2, 1),
                    "TREE_BIG": load_image("pine_tree_r_0.png"),
                    "TREE_BIG_2": load_image("pine_tree_2_r_0.png"),
                    "TREE_BIG_3": load_image("bushes_r_0.png"),
                    "TREE_SMALL": load_image("tree_s_r_0.png"),
                    "TREE_SMALL_2": load_image("tree_s_1_r_0.png"),
                    "TREE_SMALL_3": load_image("tree_s_2_r_0.png")}

CLOUD_PATH = "cloud.png"


class Cloud:
    def __init__(self, image_path, x, y):
        self.image = load_image(image_path)
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(x, y)
        self.v = BG_CLOUD_SPEED
        self.out = False

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def update(self, delta_time, speed):
        # print("here")
        self.rect.left -= round(self.v * delta_time * DELTA_TIME_CONST)
        if self.rect.left + self.rect.width < 0:
            self.out = True


class Obstacle:
    def __init__(self, image_or_frames, x, bottom, animated=False):
        if animated:
            self.frames = image_or_frames
            self.image = self.frames[0]
            self.rect = self.frames[0].get_rect()
        else:
            self.image = image_or_frames
            self.rect = self.image.get_rect()
        self.rect = self.rect.move(x, 0)
        self.rect.bottom = bottom
        self.mask = pygame.mask.from_surface(self.image)
        self.out = False
        self.animated = animated
        self.counter = 0
        self.iters = 0
        self.multiple_speed = 0
        self.min_gap = 0
        self.min_speed = 0

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def update(self, delta_time, speed):
        if self.animated:
            if self.iters % 10 == 0:
                self.image = self.frames[self.counter % 2]
                top, left = self.rect.top, self.rect.left
                self.rect = self.image.get_rect()
                self.rect.top, self.rect.left = top, left
                self.counter += 1
        d = round(delta_time * DELTA_TIME_CONST * speed)
        self.rect.left -= d
        if self.rect.left + self.rect.width < 0:
            self.out = True
        self.iters += 1


class Pterodactyl(Obstacle):
    def __init__(self, x, y):
        super().__init__(OBSTACLES_IMAGES["PTERODACTYL"],
                         x, y, animated=True)
        self.multiple_speed = 999
        self.min_gap = 8.5
        self.min_speed = 150


class CactusSmall(Obstacle):
    def __init__(self, image, x, y):
        super().__init__(image, x, y)
        self.multiple_speed = 7
        self.min_gap = 120
        self.min_speed = 0


class CactusBig(Obstacle):
    multiple_speed = 1000
    min_gap = 150
    min_speed = 8

    def __init__(self, image, x, y):
        super().__init__(image, x, y)
        self.multiple_speed = 1000
        self.min_gap = 150
        self.min_speed = 8


class Tree(Obstacle):
    def __init__(self, image, x, y):
        super().__init__(image, x, y)
        self.multiple_speed = 1000
        self.min_gap = 150
        self.min_speed = 8


class TreeSmall(Obstacle):
    def __init__(self, image, x, y):
        super().__init__(image, x, y)
        self.multiple_speed = 6
        self.min_gap = 120
        self.min_speed = 0


class MultipleObstacle:
    def __init__(self, n, x, bottom, obstacles, space):
        w = 0
        h = 0
        for obstacle in obstacles:
            w = max(w, obstacle.rect.w)
            h = max(h, obstacle.rect.h)
        self.surface = pygame.Surface((w * n + space * (n - 1), h), pygame.SRCALPHA)
        self.rect = pygame.Rect(x, bottom - h, w * n + space * (n - 1), h)
        self.obstacles = obstacles
        self.obstacle_rect = pygame.Rect(0, 0, w, h)
        for i in range(n):
            x = w * i + space * i
            self.surface.blit(obstacles[i].image, obstacles[i].rect.move(x, 0))
        self.mask = pygame.mask.from_surface(self.surface)
        self.multiple_speed = 6
        self.min_gap = 150
        self.min_speed = 6
        self.out = False
        self.space = space
        self.n = n
        self.w = w
        self.h = h

    def draw(self, screen):
        for i in range(self.n):
            x = self.w * i + self.space * i
            self.surface.blit(obstacles[i].image, self.obstacle_rect.move(x, 0))
        screen.blit(self.surface, self.rect)

    def update(self, delta_time, speed):
        self.rect.left -= round(DELTA_TIME_CONST * delta_time * speed)
        if self.rect.right <= 0:
            self.out = True


class HorizonLine:
    def __init__(self, image_path, x, y):
        self.first_image = load_image(image_path)
        self.second_image = load_image(image_path)
        self.first_rect = self.first_image.get_rect()
        self.second_rect = self.second_image.get_rect()
        self.w = self.first_rect.w
        self.first_rect.left = x
        self.first_rect.top = y
        self.second_rect.left = x + self.w
        self.second_rect.top = y

    def draw(self, screen):
        screen.blit(self.first_image, self.first_rect)
        screen.blit(self.second_image, self.second_rect)

    def update(self, delta_time, speed):
        if self.first_rect.left + self.w < 0:
            self.first_rect.left = self.second_rect.left + self.w
        if self.second_rect.left + self.w < 0:
            self.second_rect.left = self.first_rect.left + self.w
        d = round(delta_time * DELTA_TIME_CONST * speed)
        self.first_rect.left -= d
        self.second_rect.left -= d
        # # print(self.first_rect.right, self.second_rect.left)


class ParallaxHorizonLine:
    def __init__(self, image_path, x, y, const):
        self.first_image = load_image(image_path)
        self.second_image = load_image(image_path)
        self.first_rect = self.first_image.get_rect()
        self.second_rect = self.second_image.get_rect()
        self.w = self.first_rect.w
        # print(self.w)
        self.first_rect.left = x
        self.first_rect.top = y
        self.second_rect.left = x + self.w
        self.second_rect.top = y
        self.c = const

    def draw(self, screen):
        screen.blit(self.first_image, self.first_rect)
        screen.blit(self.second_image, self.second_rect)

    def update(self, delta_time, speed):
        if self.first_rect.left + self.w < 0:
            self.first_rect.left = self.second_rect.left + self.w
        if self.second_rect.left + self.w < 0:
            self.second_rect.left = self.first_rect.left + self.w
        d = round(delta_time * DELTA_TIME_CONST * speed * self.c)
        self.first_rect.left -= d
        self.second_rect.left -= d
        # # print(self.first_rect.right, self.second_rect.left)


OBSTACLES_NUM = {}

for i in range(6):
    OBSTACLES_NUM[i] = CactusSmall(OBSTACLES_IMAGES["CACTUS_SMALL"][i],
                                   0, HEIGHT - CACTUS_BOTTOM_HEIGHT)

OBSTACLES_NUM[6] = CactusBig(OBSTACLES_IMAGES["CACTUS_BIG_MEDIUM"],
                             0, HEIGHT - CACTUS_BOTTOM_HEIGHT)
OBSTACLES_NUM[7] = CactusBig(OBSTACLES_IMAGES["CACTUS_BIG_SMALL"],
                             0, HEIGHT - CACTUS_BOTTOM_HEIGHT)
OBSTACLES_NUM[8] = CactusBig(OBSTACLES_IMAGES["CACTUS_BIG_LARGE"],
                             0, HEIGHT - CACTUS_BOTTOM_HEIGHT)
OBSTACLES_NUM[9] = Pterodactyl(0, HEIGHT - GROUND_HEIGHT - 150)
OBSTACLES_NUM[10] = Pterodactyl(0, HEIGHT - GROUND_HEIGHT - 50)
OBSTACLES_NUM[11] = Pterodactyl(0, HEIGHT - GROUND_HEIGHT - 5)

for i, permutation in enumerate(permutations((0, 1, 2, 3, 4, 5), 3)):
    d = {}
    for j in range(6):
        d[j] = CactusSmall(OBSTACLES_IMAGES["CACTUS_SMALL"][j], 0, HEIGHT - CACTUS_BOTTOM_HEIGHT)
    obstacles = [d[k] for k in permutation]
    OBSTACLES_NUM[i + 12] = MultipleObstacle(3, 0, HEIGHT - CACTUS_BOTTOM_HEIGHT, obstacles, 3)

for i, permutation in enumerate(permutations((0, 1, 2, 3, 4, 5), 2)):
    d = {}
    for j in range(6):
        d[j] = CactusSmall(OBSTACLES_IMAGES["CACTUS_SMALL"][j], 0, HEIGHT - CACTUS_BOTTOM_HEIGHT)
    obstacles = [d[k] for k in permutation]
    OBSTACLES_NUM[i + 12 + 6 * 5 * 4] = MultipleObstacle(2, 0, HEIGHT - CACTUS_BOTTOM_HEIGHT, obstacles, 3)

OBSTACLES_NUM[12 + 120 + 30] = TreeSmall(OBSTACLES_IMAGES["TREE_SMALL"],
                                    0, HEIGHT - CACTUS_BOTTOM_HEIGHT - DELTA)
OBSTACLES_NUM[13 + 120 + 30] = TreeSmall(OBSTACLES_IMAGES["TREE_SMALL_2"],
                                    0, HEIGHT - CACTUS_BOTTOM_HEIGHT - DELTA)
OBSTACLES_NUM[14 + 120 + 30] = TreeSmall(OBSTACLES_IMAGES["TREE_SMALL_3"],
                                    0, HEIGHT - CACTUS_BOTTOM_HEIGHT - DELTA)
OBSTACLES_NUM[15 + 120 + 30] = Tree(OBSTACLES_IMAGES["TREE_BIG"],
                               0, HEIGHT - CACTUS_BOTTOM_HEIGHT - DELTA)
OBSTACLES_NUM[16 + 120 + 30] = Tree(OBSTACLES_IMAGES["TREE_BIG_2"],
                               0, HEIGHT - CACTUS_BOTTOM_HEIGHT - DELTA)
OBSTACLES_NUM[17 + 120 + 30] = Tree(OBSTACLES_IMAGES["TREE_BIG_3"],
                               0, HEIGHT - CACTUS_BOTTOM_HEIGHT - DELTA)

for i, permutation in enumerate(permutations((0, 1, 2))):
    d = {0: TreeSmall(OBSTACLES_IMAGES["TREE_SMALL"], 0, HEIGHT - CACTUS_BOTTOM_HEIGHT - DELTA),
         1: TreeSmall(OBSTACLES_IMAGES["TREE_SMALL_2"], 0, HEIGHT - CACTUS_BOTTOM_HEIGHT - DELTA),
         2: TreeSmall(OBSTACLES_IMAGES["TREE_SMALL_3"], 0, HEIGHT - CACTUS_BOTTOM_HEIGHT - DELTA)}
    OBSTACLES_NUM[i + 18 + 120 + 30] = MultipleObstacle(3, 0, HEIGHT - CACTUS_BOTTOM_HEIGHT - DELTA,
                                                   [d[permutation[0]], d[permutation[1]], d[permutation[2]]], -10)

for i, permutation in enumerate(permutations((0, 1, 2), 2)):
    d = {0: TreeSmall(OBSTACLES_IMAGES["TREE_SMALL"], 0, HEIGHT - CACTUS_BOTTOM_HEIGHT - DELTA),
         1: TreeSmall(OBSTACLES_IMAGES["TREE_SMALL_2"], 0, HEIGHT - CACTUS_BOTTOM_HEIGHT - DELTA),
         2: TreeSmall(OBSTACLES_IMAGES["TREE_SMALL_3"], 0, HEIGHT - CACTUS_BOTTOM_HEIGHT - DELTA)}
    OBSTACLES_NUM[i + 18 + 120 + 6 + 30] = MultipleObstacle(2, 0, HEIGHT - CACTUS_BOTTOM_HEIGHT - DELTA,
                                                   [d[permutation[0]], d[permutation[1]]], -5)


class Horizon:
    def __init__(self, indexes):
        self.obstacles_indexes = {i: 0 for i in range(*indexes)}
        self.clouds = []
        self.horizon_line_1 = HorizonLine("horizon.png", 0, HEIGHT - GROUND_HEIGHT)
        # self.add_cloud()
        self.indexes = indexes
        self.running_time = 0
        self.distance = 0
        self.delta = 0
        self.delta_2 = 1
        self.last_added_obstacle_index = 0
        self.visible_obstacles_indexes = []
        self.invisible_obstacles_indexes = []

    def update(self, delta_time, speed):
        self.running_time += delta_time
        self.distance += speed * delta_time * DELTA_TIME_CONST
        self.horizon_line_1.update(delta_time, speed)
        self.visible_obstacles_indexes = list(filter(lambda x: self.obstacles_indexes[x] == 1,
                                                     self.obstacles_indexes.keys()))
        self.invisible_obstacles_indexes = list(set(self.obstacles_indexes.keys()) - set(self.visible_obstacles_indexes))
        if self.visible_obstacles_indexes:
            for obstacle_index in self.visible_obstacles_indexes:
                OBSTACLES_NUM[obstacle_index].update(delta_time, speed)
                if OBSTACLES_NUM[obstacle_index].out:
                    self.obstacles_indexes[obstacle_index] = 0
        for cloud in self.clouds:
            cloud.update(delta_time, speed)
            if cloud.out:
                self.clouds.remove(cloud)
        if self.obstacles_indexes:
            gap = WIDTH - OBSTACLES_NUM[self.last_added_obstacle_index].rect.right
            if gap > MIN_GAP:
                self.add_obstacle(gap, speed)
        else:
            if self.distance > 2000:
                self.add_obstacle(MIN_GAP + 2, speed)

    def add_cloud(self):
        cloud = Cloud(CLOUD_PATH, WIDTH, randint(20, 180))
        self.clouds.append(cloud)

    def add_obstacle(self, gap, speed):
        obstacle = choice(self.invisible_obstacles_indexes)
        if speed < OBSTACLES_NUM[obstacle].min_speed or gap < OBSTACLES_NUM[obstacle].min_gap:
            self.add_obstacle(gap, speed)
        else:
            add = 0
            if self.visible_obstacles_indexes:
                add = self.get_gap(speed)
            OBSTACLES_NUM[obstacle].rect.left = WIDTH + add
            self.obstacles_indexes[obstacle] = 1
            self.last_added_obstacle_index = obstacle

    def get_gap(self, speed):
        min_gap = round(OBSTACLES_NUM[self.last_added_obstacle_index].rect.w * speed)
        max_gap = round(min_gap * MAX_GAP_COEFFICIENT)
        return randint(min_gap, max_gap)

    def draw(self, screen):
        for cloud in self.clouds:
            cloud.draw(screen)
        self.horizon_line_1.draw(screen)
        for obstacle in self.visible_obstacles_indexes:
            OBSTACLES_NUM[obstacle].draw(screen)

    def restart(self):
        self.obstacles_indexes = {i: 0 for i in range(*self.indexes)}
        self.clouds = []
        self.horizon_line_1 = HorizonLine("horizon.png", 0, HEIGHT - GROUND_HEIGHT)
        self.running_time = 0
        self.distance = 0


class DinoHorizon(Horizon):
    def __init__(self):
        super().__init__((0, 162))
        self.add_cloud()

    def update(self, delta_time, speed):
        super().update(delta_time, speed)
        # print(self.visible_clouds)
        if len(self.clouds) < MIN_CLOUDS and WIDTH - self.clouds[-1].rect.right > randint(50, 300):
            self.add_cloud()

    def restart(self):
        super().restart()
        self.add_cloud()


class DeerHorizon(Horizon):
    def __init__(self):
        super().__init__((162, 5 + 18 + 120 + 6 + 30))
        self.delta = 10
        self.horizon_line_1 = HorizonLine("forest/001.png", 0, HEIGHT - GROUND_HEIGHT)
        self.horizon_line_1.first_rect.bottom = HEIGHT
        self.horizon_line_1.second_rect.bottom = HEIGHT
        self.horizon_line_2 = ParallaxHorizonLine("forest/002.png", 0, HEIGHT, 0.2)
        self.horizon_line_2.first_rect.bottom = HEIGHT
        self.horizon_line_2.second_rect.bottom = HEIGHT
        self.horizon_line_3 = ParallaxHorizonLine("forest/clouds.png", 0, HEIGHT, 0.06)
        self.horizon_line_3.first_rect.bottom = HEIGHT
        self.horizon_line_3.second_rect.bottom = HEIGHT
        self.horizon_line_4 = ParallaxHorizonLine("forest/sky.png", 0, HEIGHT, 0.06)
        self.horizon_line_4.first_rect.bottom = HEIGHT
        self.horizon_line_4.second_rect.bottom = HEIGHT
        self.indexes = [3, 4]
        self.delta_2 = 1.5

    def draw(self, screen):
        self.horizon_line_4.draw(screen)
        self.horizon_line_3.draw(screen)
        self.horizon_line_2.draw(screen)
        super().draw(screen)

    def update(self, delta_time, speed):
        self.horizon_line_2.update(delta_time, speed)
        self.horizon_line_3.update(delta_time, speed)
        super().update(delta_time, speed)

    def restart(self):
        super().restart()
        self.horizon_line_1 = HorizonLine("forest/001.png", 0, HEIGHT - GROUND_HEIGHT)
        self.horizon_line_1.first_rect.bottom = HEIGHT
        self.horizon_line_1.second_rect.bottom = HEIGHT
        self.horizon_line_2 = ParallaxHorizonLine("forest/002.png", 0, HEIGHT, 0.2)
        self.horizon_line_2.first_rect.bottom = HEIGHT
        self.horizon_line_2.second_rect.bottom = HEIGHT
        self.horizon_line_3 = ParallaxHorizonLine("forest/clouds.png", 0, HEIGHT, 0.06)
        self.horizon_line_3.first_rect.bottom = HEIGHT
        self.horizon_line_3.second_rect.bottom = HEIGHT
        self.horizon_line_4 = ParallaxHorizonLine("forest/sky.png", 0, HEIGHT, 0.06)
        self.horizon_line_4.first_rect.bottom = HEIGHT
        self.horizon_line_4.second_rect.bottom = HEIGHT


class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y, *groups):
        super().__init__(*groups)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]
