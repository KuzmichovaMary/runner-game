import sys

import pygame
from constants import *
pygame.init()
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT), pygame.NOFRAME)
from pygame.locals import *
from basic_functions import load_image, load_sprite_sheet
from time import time
from Trex import TRex, Deer
from Horizon import DeerHorizon, DinoHorizon, OBSTACLES_NUM
from DistanceMeter import DistanceMeter
from GUI_pygame import Button, Menu
from MainMenu import MainMenu

jump_sound = pygame.mixer.Sound('data/jump.wav')
crashed_sound = pygame.mixer.Sound('data/crashed.wav')
achievement_sound = pygame.mixer.Sound('data/check_point.wav')


GAME_OVER = False
FPS = 60
width, height = 800, 400


class Runner:
    def __init__(self):
        self.plaing_main_menu = True
        self.activated = False
        self.crashed = False
        self.time = time()
        self.currentSpeed = SPEED

        pygame.display.set_caption('Google Trex')
        self.screen = SCREEN
        self.screen.fill((255, 255, 255, 255))

        # DeerHorizon contains clouds, obstacles and the ground.
        # self.horizon = DeerHorizon(self.screen)
        menu_btn_1 = Button(0, 0, job_on_click=sys.exit, icon_path_1="log-out.png", icon_path_2="log-out.png",
                            active=False)
        menu_btn_2 = Button(0, 0, job_on_click=self.to_main_menu,
                            icon_path_1="home.png", icon_path_2="home.png", active=False)
        self.menu = Menu(HIGH_SCORE_TOP - 8, HIGH_SCORE_TOP - 8, [menu_btn_1, menu_btn_2])
        self.main_menu = MainMenu()
        self.runningTime = 0
        self.playing = True
        self.clock = pygame.time.Clock()
        self.game_over = False
        self.main_hero_name = ""
        self.games = {"deer": {"horizon": DeerHorizon(),
                               "hero": Deer(10, HEIGHT - DINO_RUNNING_HEIGHT - 16),
                               "distance_meter": DistanceMeter()},
                      "dino": {"horizon": DinoHorizon(),
                               "hero": TRex(10, HEIGHT - DINO_RUNNING_HEIGHT - 10),
                               "distance_meter": DistanceMeter()}}

    def to_main_menu(self):
        self.plaing_main_menu = True
        self.menu.change_menu_visibility()
        self.start_game()

    def start_game(self):
        if self.plaing_main_menu:
            running = True
            main_hero = None
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        main_hero = self.main_menu.update_on_mouse_click()
                self.main_menu.update()
                self.main_menu.draw(self.screen)
                pygame.display.flip()
                self.clock.tick(FPS)
                if main_hero:
                    self.main_hero_name = main_hero
                    self.plaing_main_menu = False
                    self.main_hero = self.games[main_hero]["hero"]
                    self.horizon = self.games[main_hero]["horizon"]
                    self.distance_meter = self.games[main_hero]["distance_meter"]
                    self.restart()
                    self.start_game()
        else:
            self.runningTime = 0
            self.plaing_main_menu = False
            self.main_hero.playingIntro = False
            running = True
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    if event.type == KEYDOWN:
                        if self.playing:
                            if (event.key == K_UP or event.key == K_SPACE) and not self.main_hero.jumping\
                                    and self.main_hero.rect.top == self.main_hero.ct:
                                self.main_hero.jumping = True
                                if pygame.mixer.get_init():
                                    pass
                                    # jump_sound.play()
                                self.main_hero.state = JUMPING
                                self.main_hero.start_jump(self.currentSpeed)
                                # print("START")
                            if event.key == K_DOWN:
                                self.main_hero.ducked = True
                                self.main_hero.state = DUCKING
                        else:
                            self.restart()
                    if event.type == KEYUP:
                        if self.playing:
                            if self.main_hero.ducked:
                                self.main_hero.ducked = False
                                self.main_hero.rect.top = self.main_hero.ct
                                self.main_hero.state = RUNNING
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        self.menu.update()
                self.update()
                # self.screen.fill((255, 255, 255, 255))
                self.clear_canvas()
                self.horizon.draw(self.screen)
                self.main_hero.draw(self.screen)
                self.distance_meter.draw(self.screen)
                self.menu.display(self.screen)
                pygame.display.flip()
                self.clock.tick(FPS)

    def clear_canvas(self):
        self.screen.fill((46, 20, 93, 255) if self.main_hero_name == "deer" else (255, 255, 255, 255))

    def update(self):
        now = time()
        deltaTime = now - self.time
        self.time = now

        if self.playing:
            self.runningTime += deltaTime

            for obstacle in self.horizon.obstacles:
                if pygame.sprite.collide_mask(self.main_hero, obstacle):
                    if self.main_hero.ducked:
                        self.main_hero.image = self.main_hero.frames[self.main_hero.states[CRASHED_D][frames][0]]
                    else:
                        self.main_hero.image = self.main_hero.frames[self.main_hero.states[CRASHED_R][frames][0]]
                    self.main_hero.crashed = True
                    # crashed_sound.play()
                    self.currentSpeed = 0
                    self.playing = False
                    self.game_over = True
                    self.distance_meter.max_result = max(self.distance_meter.max_result, self.distance_meter.distance)

            if self.currentSpeed < MAX_SPEED and not self.game_over:
                self.currentSpeed += ACCELERATION
            if not self.game_over:
                self.horizon.update(deltaTime, self.currentSpeed)
                self.main_hero.update(deltaTime)
                self.distance_meter.update(deltaTime, self.currentSpeed)
                if self.distance_meter.play_achievement_sound:
                    pass
                    # achievement_sound.play()

    def restart(self):
        self.plaing_main_menu = False
        self.activated = False
        self.crashed = False
        self.time = time()
        self.currentSpeed = SPEED
        self.screen.fill((255, 255, 255, 255))

        # DeerHorizon contains clouds, obstacles and the ground.
        # self.horizon = DeerHorizon(self.screen)
        self.horizon.restart()
        self.main_hero.restart()
        self.distance_meter.restart()
        self.runningTime = 0
        self.playing = True
        self.clock = pygame.time.Clock()
        self.game_over = False


if __name__ == '__main__':
    runner = Runner()
    runner.start_game()