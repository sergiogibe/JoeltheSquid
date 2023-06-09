

import pygame
from pygame.locals import *
from player import *
from level import Level
from camera import Camera


class Game:

    def __init__(self, config: dict) -> None:
        '''Create the main game instance that controls the flow of the game,
        such as: player and enemies construction, map contruction, update calls, and render
        to the screen.'''

        '''INIT SETUP'''
        self.config:       dict = config
        self.name:         str  = config["game"]["name"]
        self.scale:        int  = config["display"]["scale"]
        self.base_size:    int  = config["display"]["base-size"]
        self.width:        int  = self.base_size * self.scale * config["game"]["ntiles_width"]
        self.height:       int  = self.base_size * self.scale * config["game"]["ntiles_height"]

        '''CREATE MAIN SCREEN'''
        self.display_resolution = (self.width, self.height)
        self.screen = pygame.display.set_mode(self.display_resolution)
        pygame.display.set_caption(self.name)

        '''SET GAME FPS AND DT (TIME INTERVAL IN PHYSICS CALCULATION)'''
        self.fps = config["game"]["fps"]
        self.clock = pygame.time.Clock()
        self.dt = self.clock.tick(self.fps) * 0.001 * self.fps

        '''CAMERA SETUP'''
        self.target_player = None

        '''ENTITIES CONTROL'''
        self.group = []


    '''============== SETTINGS METHODS ================='''

    def load_map(self, level_name: str) -> None:
        '''Load the map and the player. Must be called before the main loop.'''

        '''LOAD ENTITIES'''
        self.player = Joel(self.config,init_x=64,init_y=0)
        #self.kittol = Kittol(self.config,init_x=580,init_y=230)

        '''CREATE GROUP OF ENTITIES'''
        self.group.append(self.player)
        #self.group.append(self.kittol)
        self.n_entities = len(self.group)

        '''LOAD MAP'''
        self.level = Level(config=self.config,
                           level_name=level_name,
                           print_load_message=True,
                           render_bg=True)

        '''ADD ENTITIES TO THE LEVEL'''
        for entity in self.group:
            self.level.add_entity(entity=entity)

        '''INITIALIZE CAMERA (FOLLOW METHOD)'''
        self.target_player = self.player
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

        '''UPDATE ENITIES POSITION AND CHECK FOR COLLISIONS'''
        ix = 0
        for entity in self.group:
            aux = []
            for i in range(self.n_entities):
                if i != ix:
                    aux.append(self.group[i].entity_hitbox)
            entity.update(self.dt, self.level.tiles_per_layer[-1], aux)
            ix += 1

        '''CAMERA SCROLL'''
        #self.camera.scroll(target=self.target_player)

        '''CHECK PLAYER DEATH POSITION (PLACEHOLDER)'''
        if self.player.position.y > self.height + 300:
            #self.player.reset()
            pass

    def render(self) -> None:
        '''Control and call the rendering of every instance:
        player, enemies, and map.'''

        '''START FILLING THE SCREEN WITH BLACK BACKGROUND'''
        self.screen.fill((0,0,0))

        '''RENDER MAP'''
        self.level.render(self.screen, self.camera)

        '''RENDER ENTITIES'''
        for entity in self.group:
            entity.render(self.screen, self.camera)

        '''UPDATE FULL DISPLAY SURFACE TO THE SCREEN'''
        pygame.display.flip()