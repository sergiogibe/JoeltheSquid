

import pygame
import csv
import os

BLACK = (0, 0, 0)

class SpriteSheet:

    def __init__(self,
                 filename: str,
                 tile_size: int,
                 amp_factor: int,
                 dimension: tuple[int,int]) -> None:
        '''Creates an object that handles a given sprite sheet. Contains methods to locate and
        load all its textures and add them to a pygame surfaces list.'''

        self.filename = filename
        self.tile_size = tile_size
        self.amp_factor = amp_factor
        self.dimension = dimension
        self.sprite_sheet = pygame.image.load(filename).convert()
        self.textures = []
        self.load()

    def get_texture(self, x_pos: int, y_pos: int, texture_width: int, texture_height: int) -> pygame.Surface:
        '''Gets the texture from the spritesheet file and return it as a textured surface.
        x_pos and y_pos are the positions of the left upper vertice in relation to the spritesheet file
        (not the final position in the window -> this is done by a TileMap object)'''

        texture = pygame.Surface(size=(texture_width, texture_height))
        texture.set_colorkey(BLACK)
        texture.blit(source=self.sprite_sheet,
                     dest=(0, 0),
                     area=(x_pos, y_pos, texture_width, texture_height))
        return texture

    def load(self):
        '''Loads all textures from spritesheet to a list of textures.'''

        for y in range(0, self.dimension[0]):
            for x in range(0, self.dimension[1]):
                self.textures.append(pygame.transform.scale(self.get_texture(x * self.tile_size,
                                                                             y * self.tile_size,
                                                                             self.tile_size,
                                                                             self.tile_size),
                                                            (16 * self.amp_factor, 16 * self.amp_factor)))


class Tile:

    def __init__(self, x_pos: int, y_pos: int, texture: pygame.Surface) -> None:
        '''Creates tile adding texture to a pygame rect. Also contains a method
        that renders it in a given surface.
        x_pos and y_pos are the positions of the left upper vertice in relation to the level.'''

        self.texture = texture
        self.rect = self.texture.get_rect()
        self.rect.x = x_pos
        self.rect.y = y_pos

    def render(self, surface: pygame.Surface) -> None:
        '''Renders the tile in a given surface.'''

        surface.blit(self.texture, (self.rect.x, self.rect.y))


class Level:

    def __init__(self,
                 filename_sp: str,
                 filename_map: str,
                 tile_size: int,
                 amp_factor:int,
                 spritesheet_size: tuple[int, int]) -> None:
        '''Creates and map the tiles to the specified level given the spritesheet and the
        filename_map.csv containing the level tiles layout.'''

        '''LOAD SPRITESHEET, CORRECT TEXTURES SIZE, AND ADD TEXTURES TO A LIST'''
        self.spritesheet = SpriteSheet(filename=filename_sp,
                                       tile_size=tile_size,
                                       amp_factor=amp_factor,
                                       dimension=spritesheet_size)

        '''KEEP TRACK OF THE TILE SIZE AFTER AMPLIFICATION'''
        self.tile_size = tile_size * amp_factor
        self.amp_factor = amp_factor

        '''CONSTRUCT LEVEL BY MAPPING ALL TILES'''
        self.tiles = []
        self.level_width, self.level_height = None, None
        self.level_blueprint = Level.read_csv(filename_map)
        self.construct_level()

        '''CREATE LEVEL SURFACE TO RENDER TILES ON TOP OF IT'''
        self.level_surface = pygame.Surface(size=(self.level_width, self.level_height))
        self.level_surface.set_colorkey(BLACK)
        self.render_tiles_to_surface()

    def render(self, screen) -> None:
        '''Renders level surface to the game screen.'''

        screen.blit(self.level_surface, (0, 0))

    def render_tiles_to_surface(self) -> None:
        '''Renders each mapped tile to the level surface.'''

        for tile in self.tiles:
            tile.render(self.level_surface)

    def construct_level(self) -> None:
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
    def read_csv(filename_map: str) -> list:
        '''Reads level instructions layout csv file.'''

        level_blueprint = []

        with open(os.path.join(filename_map)) as data:
            data = csv.reader(data, delimiter=',')
            for row in data:
                level_blueprint.append(list(row))

        return level_blueprint
