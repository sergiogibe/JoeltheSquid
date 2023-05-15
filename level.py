

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
                 level: dict,
                 tile_size: int,
                 scale: int) -> None:
        '''Creates and map the tiles to the specified level given the spritesheet and the
        filename_map.csv containing the level tiles layout.'''

        self.gravity = level['physics']['gravity']
        self.friction = level['physics']['friction']

        '''LOAD SPRITESHEET, CORRECT TEXTURES SIZE, AND ADD TEXTURES TO A LIST'''
        self.spritesheet = SpriteSheet(filename=level['sp'],
                                       tile_size=tile_size,
                                       scale=scale,
                                       dimension=(level['sp_w'],level['sp_h']) )

        '''KEEP TRACK OF THE TILE SIZE AFTER AMPLIFICATION'''
        self.tile_size = tile_size * scale
        self.scale = scale

        '''CONSTRUCT LEVEL BY MAPPING ALL TILES'''
        self.tiles = []
        self.level_width, self.level_height = None, None
        self.level_blueprint = Level._read_csv(level['mapping'])
        self._construct_level()

        '''CREATE LEVEL SURFACE TO RENDER TILES ON TOP OF THE BACKGROUND'''
        self.level_surface = pygame.Surface(size=(self.level_width, self.level_height))
        self.level_surface.set_colorkey((0,0,0))
        self.bg = pygame.image.load(level['bg']).convert()
        self._render_tiles_to_surface(render_bg=False)

    def render(self, screen, camera) -> None:
        '''Renders level surface to the game screen.'''

        screen.blit(self.level_surface, (0 - camera.offset.x, 0))

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
        for tile in self.tiles:
            tile.render(self.level_surface)

    def _construct_level(self) -> None:
        '''Constructs level by creating and mapping all tiles.'''

        '''TILES SWEEP LEVEL CONSTRUCTION'''
        n_rows = len(self.level_blueprint)
        n_cols = len(self.level_blueprint[0])
        x, y = 0, 0
        for i in range(n_rows):
            x = 0
            for j in range(n_cols):
                if self.level_blueprint[i][j] != '-1':
                    self.tiles.append(Tile(x * self.tile_size,
                                           y * self.tile_size,
                                           self.spritesheet.textures[int(self.level_blueprint[i][j])]))
                x += 1
            y += 1

        '''FIND LEVEL DIMENSIONS'''
        self.level_width, self.level_height = x*self.tile_size, y*self.tile_size

    @staticmethod
    def _read_csv(filename_map: str) -> list:
        '''Reads level instructions layout csv file.'''

        level_blueprint = []

        with open(os.path.join(filename_map)) as data:
            data = csv.reader(data, delimiter=',')
            for row in data:
                level_blueprint.append(list(row))

        return level_blueprint