
import pygame

class Camera:
    def __init__(self, resolution):
        self.offset = pygame.math.Vector2(0, 0)
        self.offset_float = pygame.math.Vector2(0, 0)
        self.display_width, self.display_height = resolution[0], resolution[1]
        #self.const = vec(-self.display_width / 2 + player.rect.w / 2, -self.player.ground_y + 20)

    def scroll(self, target):
        '''Finds the offset of the camera in relation to the player.
        It follows the FOLLOW method.'''

        self.offset_float.x += (target.position.x - self.offset_float.x - self.display_width/2)
        self.offset_float.y += (target.position.y - self.offset_float.y - self.display_height/2)

        '''CAST IT TO INT FOR DISPLAY PURPOSES'''
        self.offset.x, self.offset.y = int(self.offset_float.x), int(self.offset_float.y)
