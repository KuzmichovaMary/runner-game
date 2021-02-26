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

# _r_0

OBSTACLES_IMAGES = {"CACTUS_BIG_LARGE": load_image("obstacles/cactus_biggest.png"),
                    "CACTUS_BIG_MEDIUM": load_image("obstacles/cactus_two.png"),
                    "CACTUS_BIG_SMALL": load_image("obstacles/cactus_big_one.png"),
                    "CACTUS_SMALL": load_sprite_sheet(load_image("obstacles/cactus_small.png"), 6, 1),
                    "PTERODACTYL": load_sprite_sheet(load_image("obstacles/bird.png"), 2, 1),
                    "TREE_BIG": load_image("obstacles/pine_tree_r_0.png"),
                    "TREE_BIG_2": load_image("obstacles/pine_tree_2_r_0.png"),
                    "TREE_BIG_3": load_image("obstacles/bushes_r_0.png"),
                    "TREE_SMALL": load_image("obstacles/tree_s_r_0.png"),
                    "TREE_SMALL_2": load_image("obstacles/tree_s_1_r_0.png"),
                    "TREE_SMALL_3": load_image("obstacles/tree_s_2_r_0.png")}

CLOUD_PATH = "background/cloud.png"


TREE_PERMUTATIONS_2 = list(permutations(["TREE_SMALL_3", "TREE_SMALL_2", "TREE_SMALL"], 2))
TREE_PERMUTATIONS_3 = list(permutations(["TREE_SMALL_3", "TREE_SMALL_2", "TREE_SMALL"], 3))
CACTUS_PERMUTATIONS_2 = list(permutations(range(6), 2))
CACTUS_PERMUTATIONS_3 = list(permutations(range(6), 3))


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
    multiple_speed = 999
    min_gap = 150
    min_speed = 8.5

    def __init__(self, x, y):
        super().__init__(OBSTACLES_IMAGES["PTERODACTYL"],
                         x, y, animated=True)


class CactusSmall(Obstacle):
    multiple_speed = 7
    min_gap = 99
    min_speed = 0

    def __init__(self, x, y, image=choice(OBSTACLES_IMAGES["CACTUS_SMALL"])):
        super().__init__(image, x, y)


class CactusBig(Obstacle):
    multiple_speed = 1000
    min_gap = 150
    min_speed = 8

    def __init__(self, x, y):
        super().__init__(OBSTACLES_IMAGES[choice(["CACTUS_BIG_MEDIUM", "CACTUS_BIG_LARGE", "CACTUS_BIG_SMALL"])], x, y)


class Tree(Obstacle):
    multiple_speed = 1000
    min_gap = 150
    min_speed = 8

    def __init__(self, x, y):
        super().__init__(OBSTACLES_IMAGES[choice(["TREE_BIG", "TREE_BIG_2", "TREE_BIG_3"])], x, y)


class TreeSmall(Obstacle):
    multiple_speed = 6
    min_gap = 99
    min_speed = 0

    def __init__(self, x, y, image=OBSTACLES_IMAGES[choice(["TREE_SMALL_2", "TREE_SMALL_3", "TREE_SMALL"])]):
        super().__init__(image, x, y)


class MultipleObstacle:
    multiple_speed = 6
    min_gap = 150
    min_speed = 6

    def __init__(self, n, x, bottom, obstacles, space, ys_range=0, animated=False):
        w = 0
        h = 0
        for obstacle in obstacles:
            w = max(w, obstacle.rect.w)
            h = max(h, obstacle.rect.h)
        h += ys_range
        self.surface = pygame.Surface((w * n + space * (n - 1), h), pygame.SRCALPHA)
        self.rect = pygame.Rect(x, bottom - h, w * n + space * (n - 1), h)
        self.obstacles = obstacles
        self.obstacle_rect = pygame.Rect(0, 0, w, h)
        for i in range(n):
            x = w * i + space * i
            y = randint(0, ys_range)
            self.obstacles[i].y = y
            self.surface.blit(obstacles[i].image, self.obstacle_rect.move(x, y))
        self.mask = pygame.mask.from_surface(self.surface)
        self.out = False
        self.space = space
        self.n = n
        self.w = w
        self.h = h
        self.animated = animated
        self.iters = 0
        self.counter = 0

    def draw(self, screen):
        screen.blit(self.surface, self.rect)

    def update(self, delta_time, speed):
        if self.animated:
            if self.iters % 10 == 0:
                self.counter += 1
                self.counter %= 2
                self.iters %= 10
                self.surface.fill((255, 255, 255, 0))
                for i in range(self.n):
                    x = self.w * i + self.space * i
                    y = self.obstacles[i].y
                    if i % randint(1, 3) == 0:
                        self.surface.blit(self.obstacles[i].frames[self.counter], self.obstacle_rect.move(x, y))
                    else:
                        self.surface.blit(self.obstacles[i].frames[abs(self.counter - 1)], self.obstacle_rect.move(x, y))
            self.iters += 1
        self.rect.left -= round(DELTA_TIME_CONST * delta_time * speed)
        if self.rect.right <= 0:
            self.out = True


class MultipleCactusSmall2(MultipleObstacle):
    multiple_speed = 10000
    min_gap = 120
    min_speed = 6

    def __init__(self, x, bottom):
        obstacles = [CactusSmall(0, 0, OBSTACLES_IMAGES["CACTUS_SMALL"][i]) for i in choice(CACTUS_PERMUTATIONS_2)]
        super().__init__(2, x, bottom, obstacles, 5)


class MultipleCactusSmall3(MultipleObstacle):
    multiple_speed = 10000
    min_gap = 120
    min_speed = 6

    def __init__(self, x, bottom):
        obstacles = [CactusSmall(0, 0, OBSTACLES_IMAGES["CACTUS_SMALL"][i]) for i in choice(CACTUS_PERMUTATIONS_3)]
        super().__init__(3, x, bottom, obstacles, 3)


class MultipleTreeSmall2(MultipleObstacle):
    multiple_speed = 10000
    min_gap = 120
    min_speed = 6

    def __init__(self, x, bottom):
        obstacles = [TreeSmall(0, 0, OBSTACLES_IMAGES[i]) for i in choice(TREE_PERMUTATIONS_2)]
        super().__init__(2, x, bottom, obstacles, -3)


class MultipleTreeSmall3(MultipleObstacle):
    multiple_speed = 10000
    min_gap = 120
    min_speed = 6

    def __init__(self, x, bottom):
        obstacles = [TreeSmall(0, 0, OBSTACLES_IMAGES[i]) for i in choice(TREE_PERMUTATIONS_3)]
        super().__init__(3, x, bottom, obstacles, -5)


class MultipleBirds(MultipleObstacle):
    multiple_speed = 500
    min_gap = 120
    min_speed = 5

    def __init__(self, x, bottom):
        n = randint(1, 7)
        obstacles = [Pterodactyl(0, 0) for i in range(n)]
        super().__init__(n, x, bottom, obstacles, 1, 50, animated=True)


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


OBSTACLES_NUM = {0: CactusSmall,
                 1: CactusBig,
                 2: Pterodactyl,
                 3: MultipleCactusSmall2,
                 4: MultipleCactusSmall3,
                 5: MultipleBirds,
                 6: TreeSmall,
                 7: Tree,
                 8: MultipleTreeSmall2,
                 9: MultipleTreeSmall3}


class Horizon:
    def __init__(self, indexes):
        self.obstacles = []
        self.clouds = []
        self.horizon_line_1 = HorizonLine("background/horizon.png", 0, HEIGHT - GROUND_HEIGHT)
        # self.add_cloud()
        self.indexes = indexes
        self.running_time = 0
        self.distance = 0
        self.delta = 0
        self.delta_2 = 1

    def update(self, delta_time, speed):
        self.running_time += delta_time
        self.distance += speed * delta_time * DELTA_TIME_CONST
        self.horizon_line_1.update(delta_time, speed)
        if self.obstacles:
            for obstacle in self.obstacles:
                obstacle.update(delta_time, speed)
                if obstacle.out:
                    self.obstacles.remove(obstacle)
        for cloud in self.clouds:
            cloud.update(delta_time, speed)
            if cloud.out:
                self.clouds.remove(cloud)
        if self.obstacles:
            gap = WIDTH - self.obstacles[-1].rect.right
            if gap > MIN_GAP:
                self.add_obstacle(speed)
        else:
            if self.distance > 2000:
                self.add_obstacle(speed)

    def add_cloud(self):
        cloud = Cloud(CLOUD_PATH, WIDTH, randint(20, 180))
        self.clouds.append(cloud)

    def add_obstacle(self, speed):
        obstacle_index = randint(*self.indexes)
        if speed < OBSTACLES_NUM[obstacle_index].min_speed:
            self.add_obstacle(speed)
        else:
            add = 0
            if self.obstacles:
                add = self.get_gap(speed)
            if obstacle_index == 2:
                obstacle = OBSTACLES_NUM[obstacle_index](WIDTH + add, HEIGHT - choice([50, 30, 110]))
            elif obstacle_index == 5:
                obstacle = OBSTACLES_NUM[obstacle_index](WIDTH + add, HEIGHT - 110)
            else:
                obstacle = OBSTACLES_NUM[obstacle_index](WIDTH + add, HEIGHT - CACTUS_BOTTOM_HEIGHT - self.delta)
            self.obstacles.append(obstacle)

    def get_gap(self, speed):
        min_gap = round(speed)
        max_gap = round(speed * MAX_GAP_COEFFICIENT)
        return randint(min_gap, max_gap)

    def draw(self, screen):
        for cloud in self.clouds:
            cloud.draw(screen)
        for obstacle in self.obstacles:
            obstacle.draw(screen)

    def restart(self):
        self.obstacles = []
        self.clouds = []
        self.horizon_line_1 = HorizonLine("background/horizon.png", 0, HEIGHT - GROUND_HEIGHT)
        self.running_time = 0
        self.distance = 0


class DinoHorizon(Horizon):
    def __init__(self):
        super().__init__((0, 5))
        self.add_cloud()

    def update(self, delta_time, speed):
        super().update(delta_time, speed)
        # print(self.visible_clouds)
        if len(self.clouds) < MIN_CLOUDS and WIDTH - self.clouds[-1].rect.right > randint(50, 300):
            self.add_cloud()

    def draw(self, screen):
        self.horizon_line_1.draw(screen)
        super().draw(screen)

    def restart(self):
        super().restart()
        self.add_cloud()


class DeerHorizon(Horizon):
    def __init__(self):
        super().__init__((6, 9))
        self.horizon_line_0 = HorizonLine("background/ground_1.png", 0, HEIGHT - GROUND_HEIGHT)
        self.delta = 10
        self.horizon_line_1 = ParallaxHorizonLine("background/001.png", 0, HEIGHT - GROUND_HEIGHT, 0.2)
        self.horizon_line_1.first_rect.bottom = HEIGHT
        self.horizon_line_1.second_rect.bottom = HEIGHT
        self.horizon_line_2 = ParallaxHorizonLine("background/002.png", 0, HEIGHT, 0.06)
        self.horizon_line_2.first_rect.bottom = HEIGHT
        self.horizon_line_2.second_rect.bottom = HEIGHT
        self.horizon_line_3 = ParallaxHorizonLine("background/clouds_1.png", 0, HEIGHT, 0.06)
        self.horizon_line_3.first_rect.bottom = HEIGHT
        self.horizon_line_3.second_rect.bottom = HEIGHT
        self.horizon_line_4 = ParallaxHorizonLine("background/sky_1.png", 0, HEIGHT, 0.006)
        self.horizon_line_4.first_rect.bottom = HEIGHT
        self.horizon_line_4.second_rect.bottom = HEIGHT

    def draw(self, screen):
        self.horizon_line_4.draw(screen)
        # self.horizon_line_3.draw(screen)
        self.horizon_line_2.draw(screen)
        self.horizon_line_1.draw(screen)
        self.horizon_line_0.draw(screen)
        super().draw(screen)

    def update(self, delta_time, speed):
        self.horizon_line_4.update(delta_time, speed)
        self.horizon_line_3.update(delta_time, speed)
        self.horizon_line_2.update(delta_time, speed)
        self.horizon_line_1.update(delta_time, speed)
        self.horizon_line_0.update(delta_time, speed)
        super().update(delta_time, speed)

    def restart(self):
        super().restart()
        self.horizon_line_0 = HorizonLine("background/ground_1.png", 0, HEIGHT - GROUND_HEIGHT)
        self.horizon_line_0.first_rect.bottom = HEIGHT
        self.horizon_line_0.second_rect.bottom = HEIGHT
        self.horizon_line_1 = ParallaxHorizonLine("background/001.png", 0, HEIGHT - GROUND_HEIGHT, 0.23)
        self.horizon_line_1.first_rect.bottom = HEIGHT
        self.horizon_line_1.second_rect.bottom = HEIGHT
        self.horizon_line_2 = ParallaxHorizonLine("background/002.png", 0, HEIGHT, 0.07)
        self.horizon_line_2.first_rect.bottom = HEIGHT
        self.horizon_line_2.second_rect.bottom = HEIGHT
        self.horizon_line_3 = ParallaxHorizonLine("background/clouds_1.png", 0, HEIGHT, 0.055)
        self.horizon_line_3.first_rect.bottom = HEIGHT
        self.horizon_line_3.second_rect.bottom = HEIGHT
        self.horizon_line_4 = ParallaxHorizonLine("background/sky_1.png", 0, HEIGHT, 0.006)
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
