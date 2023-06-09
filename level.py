

import pygame
import csv
import os
from texture import SpriteSheet


class Tile:

    def __init__(self, x_pos: int, y_pos: int, texture: pygame.Surface) -> None:
        '''Creates tile adding texture to a pygame rect. Also contains a method
        that renders it in a given surface.
        x_pos and y_pos are the positions of the left upper vertice in relation to the level.'''

        self._texture = texture
        self.rect = self._texture.get_rect()
        self.rect.x = x_pos
        self.rect.y = y_pos

    def render(self, surface: pygame.Surface) -> None:
        '''Renders the tile in a given surface.'''

        surface.blit(self._texture, (self.rect.x, self.rect.y))


class Level:

    def __init__(self,
                 config: dict,
                 level_name: str,
                 print_load_message: bool = False,
                 render_bg: bool = False) -> None:
        '''Creates and map the tiles to the specified level given the spritesheet and the
        filename_map.csv containing the level tiles layout. This class handle multiple layers,
        however keep in my that it should render the foreground(where the code check
        collisions) lastly. You can do this by simply setting the foreground lastly in the
        settings.json.'''

        self.config = config
        self.level = config[level_name]
        self.scale = config['display']['scale']
        self.original_tile_size = config[level_name]['tile-size']
        self.tile_size = self.original_tile_size * self.scale

        self.gravity = self.level['physics']['gravity']
        self.friction = self.level['physics']['friction']

        '''LOOP THROUGH LAYERS'''
        self.tiles_per_layer = []
        for layer in self.level['layers']:

            '''LOAD SPRITESHEET, SCALE SIZE, AND ADD TEXTURES TO A LIST'''
            spritesheet = SpriteSheet(filename=layer['sp'],
                                      tile_size=(self.original_tile_size,self.original_tile_size),
                                      scale=self.scale,
                                      dimension=(layer['sp_w'],layer['sp_h']) )

            '''CONSTRUCT LEVEL BY MAPPING ALL TILES'''
            level_blueprint = Level._read_csv(layer['mapping'])
            tiles = self._construct_level(spritesheet, level_blueprint)
            self.tiles_per_layer.append(tiles)

        '''CREATE LEVEL SURFACE TO RENDER TILES ON TOP OF THE BACKGROUND'''
        self.level_surface = pygame.Surface(size=(self.level['size_in_tiles'][0]*self.tile_size,
                                                  self.level['size_in_tiles'][1]*self.tile_size))
        self.level_surface.set_colorkey((0,0,0))
        self.bg = pygame.transform.scale(pygame.image.load(self.level['bg']).convert(),
                                         (self.level["size_in_tiles"][0]*self.tile_size,
                                          self.level["size_in_tiles"][1]*self.tile_size))
        self._render_tiles_to_surface(render_bg=render_bg)

        '''LOADED MESSAGE'''
        if print_load_message:
            print(f'{self.level["name"]} successfully loaded')

    def render(self, screen, camera) -> None:
        '''Renders level surface to the game screen.'''

        screen.blit(self.level_surface, (0 - camera.offset.x, 0 - camera.offset.y))

    def add_entity(self, entity) -> None:
        '''Applies physical properties to every entity added.
        This function override some attributes of the object "entity".'''

        '''APPLY LEVEL PHYSICS'''
        entity.gravity = self.gravity
        entity.friction = self.friction

        '''SOME INITIAL/PLAYER CONDITIONS'''
        entity.traction = abs(self.friction)
        entity.weight = entity.mass * self.gravity
        entity.acceleration = pygame.math.Vector2(0, self.gravity)

    def _render_tiles_to_surface(self, render_bg=True) -> None:
        '''Renders each mapped tile to the level background.'''

        '''RENDER BG TO THE SURFACE'''
        if render_bg:
            self.level_surface.blit(self.bg, (0, 0))

        '''RENDER TILES ON TOP OF IT'''
        for tile_layer in self.tiles_per_layer:
            for tile in tile_layer:
                tile.render(self.level_surface)

    def _construct_level(self,
                         spritesheet: object,
                         level_blueprint: list) -> list:
        '''Constructs level by creating and mapping all tiles.'''

        '''TILES SWEEP LEVEL CONSTRUCTION'''
        n_rows = len(level_blueprint)
        n_cols = len(level_blueprint[0])
        x, y = 0, 0
        tiles = []
        for i in range(n_rows):
            x = 0
            for j in range(n_cols):
                if level_blueprint[i][j] != '-1':
                    tiles.append(Tile(x * self.tile_size, y * self.tile_size,
                                        spritesheet.textures[int(level_blueprint[i][j])]))
                x += 1
            y += 1

        return tiles

    @staticmethod
    def _read_csv(filename_map: str) -> list:
        '''Reads level instructions layout csv file.'''

        level_blueprint = []

        with open(os.path.join(filename_map)) as data:
            data = csv.reader(data, delimiter=',')
            for row in data:
                level_blueprint.append(list(row))

        return level_blueprint