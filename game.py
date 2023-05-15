

import pygame
from pygame.locals import *
from player import Joel
from level import Level
from camera import Camera


class Game:

    def __init__(self, config: dict) -> None:
        '''Create the main game instance that controls the flow of the game,
        such as: player and enemies construction, map contruction, update calls, and render
        to the screen.'''

        '''INIT SETUP'''
        self.config: dict    = config
        self.name: str       = config["game"]["name"]
        self.scale: int      = config["tiles"]["scale"]
        self.tile_size:  int = config["tiles"]["tile-size"]
        self.width:      int = self.tile_size * self.scale * config["game"]["ntiles_width"]
        self.height:     int = self.tile_size * self.scale * config["game"]["ntiles_height"]

        '''CREATE MAIN SCREEN'''
        self.display_resolution: tuple = (self.width, self.height)
        self.screen = pygame.display.set_mode(self.display_resolution)
        pygame.display.set_caption(self.name)

        '''SET GAME FPS AND DT (TIME INTERVAL IN PHYSICS CALCULATION)'''
        self.fps = config["game"]["fps"]
        self.clock = pygame.time.Clock()
        self.dt = self.clock.tick(self.fps) * 0.001 * self.fps


    '''============== SETTINGS METHODS ================='''

    def load_map(self, level:dict) -> None:
        '''Load the map and the player. Must be called before the main loop.'''

        '''LOAD ENTITIES'''
        self.player = Joel(self.scale)

        '''LOAD MAP'''
        self.level = Level(level=level,
                           tile_size=self.tile_size,
                           scale=self.scale)
        print(f'Loaded {level["name"]}')

        self.level.add_entity(entity=self.player)

        '''INITIALIZE CAMERA (FOLLOW METHOD)'''
        self.camera = Camera(self.display_resolution)


    '''============== GAME LOOP METHODS ================'''

    def handle_events(self) -> None:
        '''Main function that handle game events such as quit button,
        user input, and etc.'''

        '''CATCH GAME EVENTS'''
        for event in pygame.event.get():

            '''QUIT GAME EVENT'''
            if event.type == QUIT:
                pygame.quit()
                exit()
            if event.type == KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit()

            '''PLAYER CONTROL'''
            self.player.control(event)

    def update(self) -> None:
        '''Calls update methods for every entity created and also level updates.'''

        self.player.update(self.dt, self.level.tiles)
        self.camera.scroll(target=self.player)

    def render(self) -> None:
        '''Control and call the rendering of every instance:
        player, enemies, and map.'''

        '''START FILLING THE SCREEN WITH BLACK BACKGROUND'''
        self.screen.fill((0,0,0))

        '''RENDER MAP'''
        self.level.render(self.screen, self.camera)

        '''RENDER ENTITIES'''
        self.player.render(self.screen, self.camera)

        '''UPDATE FULL DISPLAY SURFACE TO THE SCREEN'''
        pygame.display.flip()