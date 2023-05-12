

import pygame
import os
from pygame.locals import *
from player import Joel
from texturing import *

BLACK = (0,0,0)


class Game:

    def __init__(self) -> None:
        '''Create the main game instance that controls the flow of the game,
        such as: player and enemies construction, map contruction, update calls, and render
        to the screen.'''

        self.name: str = "Joel the Squid"
        self.amp_factor: int = 3
        self.tile_size:  int = 16
        self.width:      int = self.tile_size * self.amp_factor * 25
        self.height:     int = self.tile_size * self.amp_factor * 15
        self.resolution: tuple = (self.width, self.height)

        '''CREATE WINDOW'''
        self.screen = pygame.display.set_mode(self.resolution)
        pygame.display.set_caption(self.name)

        '''SET GAME FPS AND DT (TIME INTERVAL TO PHYSICS CALCULATION)'''
        self.fps = 60
        self.clock = pygame.time.Clock()
        self.dt = self.clock.tick(self.fps) * 0.001 * self.fps

        self.userInput = 0

    def load_map(self, spritesheet: str, level: str, spritesheet_size: tuple[int,int]) -> None:
        '''Load the map and the player. Must be called before the main loop.'''

        '''LOAD ENTITIES'''
        self.player = Joel(self.amp_factor)

        '''LOAD MAP'''
        self.level = Level(filename_sp=spritesheet,
                           filename_map=level,
                           tile_size=self.tile_size,
                           amp_factor=self.amp_factor,
                           spritesheet_size=spritesheet_size)

    def handle_events(self) -> None:
        '''Main function that handle game events such as quit button,
        user input, and etc.'''

        '''CATCH GAME EVENTS'''
        for event in pygame.event.get():

            '''QUIT GAME EVENT'''
            if event.type == QUIT:
                pygame.quit()
                exit()

            '''USER INPUT EVENTS'''
            if event.type == KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.player.left_key = True
                elif event.key == pygame.K_RIGHT:
                    self.player.right_key = True
                elif event.key == pygame.K_SPACE:
                    self.player.jump()
                elif event.key == pygame.K_z:
                    self.player.is_running = True
                elif event.key == pygame.K_r:
                    self.player.reset()

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    self.player.left_key = False
                elif event.key == pygame.K_RIGHT:
                    self.player.right_key = False
                elif event.key == pygame.K_SPACE:
                    if self.player.jumping:
                        self.player.velocity.y *= self.player.jump_control
                        self.player.jumping = False
                elif event.key == pygame.K_z:
                    self.player.is_running = False

    def update(self) -> None:
        '''Call update methods for every entitie created.'''

        self.player.update(self.dt, self.level)

    def render(self) -> None:
        '''Control and call the rendering of every instance:
        player, enemies, and map.'''

        '''START FILLING THE SCREEN WITH BLACK BACKGROUND'''
        self.screen.fill(BLACK)

        '''RENDER MAP'''
        self.level.render(self.screen)

        '''RENDER ENTITIES'''
        self.player.render(self.screen, self.level)

        '''UPDATE FULL DISPLAY SURFACE TO THE SCREEN'''
        pygame.display.flip()