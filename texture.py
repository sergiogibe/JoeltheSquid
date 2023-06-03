

import pygame


class SpriteSheet:

    def __init__(self,
                 filename: str,
                 tile_size: tuple[int, int],
                 scale: int,
                 dimension: tuple[int, int]) -> None:
        '''Creates an object that handles a given sprite sheet. Contains methods to locate and
        load all its textures and add them to a pygame surfaces list.'''

        self._filename = filename
        self._tile_size = tile_size
        self._scale = scale
        self._dimension = dimension
        self._sprite_sheet = pygame.image.load(filename).convert()
        self.textures = []
        self.load()

    def _get_texture(self, x_pos: int, y_pos: int, texture_width: int, texture_height: int) -> pygame.Surface:
        '''Gets the texture from the spritesheet file and return it as a textured surface.
        x_pos and y_pos are the positions of the left upper vertice in relation to the spritesheet file
        (not the final position in the window -> this is done by a TileMap object)'''

        texture = pygame.Surface(size=(texture_width, texture_height))
        texture.set_colorkey((0, 0, 0))
        texture.blit(source=self._sprite_sheet,
                     dest=(0, 0),
                     area=(x_pos, y_pos, texture_width, texture_height))
        return texture

    def load(self):
        '''Loads all textures from spritesheet to a list of textures.'''

        for y in range(0, self._dimension[0]):
            for x in range(0, self._dimension[1]):
                self.textures.append(pygame.transform.scale(self._get_texture(x * self._tile_size[0],
                                                                              y * self._tile_size[1],
                                                                              self._tile_size[0],
                                                                              self._tile_size[1]),
                                                            (self._tile_size[0] * self._scale,
                                                             self._tile_size[1] * self._scale)))

        # for x in range(0, self._dimension[1]):
        #     for y in range(0, self._dimension[0]):
        #         self.textures.append(pygame.transform.scale(self._get_texture(x * self._tile_size[0],
        #                                                                       y * self._tile_size[1],
        #                                                                       self._tile_size[0],
        #                                                                       self._tile_size[1]),
        #                                                     (self._tile_size[0] * self._scale,
        #                                                      self._tile_size[1] * self._scale)))
