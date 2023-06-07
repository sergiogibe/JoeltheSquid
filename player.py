

import pygame
from texture import SpriteSheet
from abc import ABC, abstractmethod


class Entity(ABC):

    def __init__(self, config, init_x, init_y) -> None:
        '''Creates Entity. '''

        '''PLAYER DIMENSIONS'''
        self.scale = config['joel']['scale']
        self.width = config['joel']['tile-size'] * self.scale
        self.height = config['joel']['tile-size'] * self.scale

        '''LOAD TEXTURES'''
        self._load_textures(config)
        self.entity_image = self.walk_sprites.textures[self.curent_walk_sprite]
        self.entity_hitbox = self.entity_image.get_rect()
        self.atk_hitbox = self.entity_image.get_rect()

        '''INIT POSITION/VELOCITY VECTORS'''
        self.init_x = init_x
        self.init_y = init_y
        self.position = pygame.math.Vector2(self.init_x, self.init_y)
        self.velocity = pygame.math.Vector2(0, 0)

        '''PLAYER INPUT'''
        self.left_key = False
        self.right_key = False

        '''PLAYER ACTIONS'''
        self.jumping = False
        self.on_ground = False
        self.is_running = False
        self.is_colliding_tiles = False
        self.is_colliding_entities = False
        self.facing_left = False
        self.is_attacking = False
        self.ready_to_atk = True

        '''PLAYER STATS'''
        self.jump_force = 12
        self.jumpX_velocity = 0.9
        self.jump_control = 0.25
        self.walk_accel = 0.3
        self.run_boost = 0.3
        self.max_x_velocity = 11
        self.max_y_velocity = 18
        self.mass = 0.8
        self.slipperiness = 0.03

        '''LEVEL ATTRIBUTES (MUST BE OVERRIDEN BY ADDING THE PLAYER TO THE LEVEL)'''
        self.gravity = None
        self.friction = None
        self.traction = None
        self.weight = None
        self.acceleration = None

        '''RENDER ATTRIBUTES'''
        self.render_pos = pygame.math.Vector2(self.init_x, self.init_y)
        self.trigger_atk_anim = False
        self.trigger_deatk_anim = False
        self.atk_sprite_count = 0

    '''=============  PUBLIC METHODS ==============='''

    def render(self, screen, camera=None, show_hitbox=True) -> None:
        '''Renders player on the screen.'''

        '''SET RENDER POSITION (CAMERA[only if player] AND ATTACK ADJUSTMENT)'''
        if camera is not None:
            self.render_pos.x = self.entity_hitbox.x - camera.offset.x
            self.render_pos.y = self.entity_hitbox.y - camera.offset.y
        if self.facing_left and (self.trigger_atk_anim or self.trigger_deatk_anim):
            self.render_pos.x -= (self.scale * 32)

        '''CREATE IMAGE'''
        self._create_image()

        '''SPRITE COUNT CONTROL'''
        self._animate()

        '''RENDER CALL'''
        screen.blit(self.entity_image, self.render_pos)

        '''DRAW HITBOX (GOOD FOR DEBUG PURPOSES)'''
        if show_hitbox:
            rect = pygame.Rect(self.entity_hitbox.x - camera.offset.x,
                               self.entity_hitbox.y - camera.offset.y,
                               self.entity_hitbox.w,
                               self.entity_hitbox.h)
            rect2 = pygame.Rect(self.atk_hitbox.x - camera.offset.x,
                                self.atk_hitbox.y - camera.offset.y -1,
                                self.atk_hitbox.w,
                                self.atk_hitbox.h)
            if self.is_colliding_tiles:
                pygame.draw.rect(screen,(255,0,0),rect2,border_radius=1,width=1)
            if self.is_colliding_entities:
                pygame.draw.rect(screen,(0,0,255),rect2,border_radius=1,width=1)

    def update(self, dt, tiles, entities) -> None:
        '''Calls horizontal and vertical movement functions that calculates
        the increment on the X and Y position for a given dt.'''

        '''MOVEMENT UPDATE'''
        self._horizontal_movement(dt)
        self._handle_collisions_x(tiles)
        self._vertical_movement(dt)
        self._handle_collisions_y(tiles)

        '''COLLISION WITH ENTITIES'''
        self._handle_entity_collisions(entities)

    def jump(self) -> None:
        '''Calculates y position and velocity after jumping action.'''

        if self.on_ground:
            self.jumping = True

            '''Y-AXIS FORCE MOTION'''
            self.velocity.y -= self.jump_force/self.weight
            if self.is_running and abs(self.velocity.x) > 0.75 * self.max_x_velocity:
                self.velocity.y *= abs(self.velocity.x * 0.11)

            '''X-AXIS FORCE MOTION'''
            if self.velocity.x > 0:
                self.velocity.x += (1/self.weight)*self.jumpX_velocity
            elif self.velocity.x < 0:
                self.velocity.x -= (1/self.weight)*self.jumpX_velocity
            elif self.velocity.x < 1 and self.velocity.x > 1:
                self.velocity += 0

            '''NOT JUMP AGAIN UNTIL COMPLETE THE FALLING'''
            self.on_ground = False

    def reset(self) -> None:
        self.position.x, self.position.y = self.init_x, self.init_y
        self.facing_left = False
        self.curent_walk_sprite = 0
        self.velocity.x, self.velocity.y = 0, 0

    def attack(self):
        if self.ready_to_atk:
            self.atk_sprite_count = 0
            self.is_attacking = True
            self.trigger_atk_anim = True
            self.ready_to_atk = False
            self.atk_hitbox.w = self.width*2.2

    @abstractmethod
    def control(self, event) -> None:
        pass

    '''=============  PRIVATE METHODS ==============='''

    @abstractmethod
    def _load_textures(self, config) -> None:
        pass

    def _animate(self) -> None:
        '''Controls character several animations.'''

        '''LEFT AND RIGHT ANIMATION'''
        if self.left_key or self.right_key:
            if self.curent_walk_sprite > self.n_walk_sprites:
                self.curent_walk_sprite = 0  #avoid getting too big, although modulo handles list index
            if self.is_running:
                self.curent_walk_sprite += 0.25
            else:
                self.curent_walk_sprite += 0.15
            self.curent_walk_sprite = self.curent_walk_sprite % self.n_walk_sprites
        if self.left_key is False and self.right_key is False:
            self.curent_walk_sprite = 0

        '''JUMPING ANIMATION'''
        if self.jumping is True and self.on_ground is False:
            self.curent_walk_sprite = self.n_walk_sprites-1

        '''FACING LEFT-RIGHT ANIMATION'''
        if self.left_key:
            self.facing_left = True
        elif self.right_key:
            self.facing_left = False

        '''ATTACK ANIMATION'''
        if self.trigger_atk_anim:
            if self.atk_sprite_count < self.n_atk_sprites-1:
                self.atk_sprite_count += 0.4
                self.current_atk_sprite = self.atk_sprite_count
            else:
                self.current_atk_sprite = 0
                self.trigger_atk_anim = False
                self.trigger_deatk_anim = True
        else:
            self.current_atk_sprite = 0

        '''DE-ATTACK ANIMATION'''
        if self.trigger_deatk_anim:
            if self.atk_sprite_count > 0:
                self.atk_sprite_count -= 0.6
                self.current_atk_sprite = self.atk_sprite_count
            else:
                self.current_atk_sprite = 0
                self.trigger_deatk_anim = False
                self.atk_hitbox.w = self.entity_hitbox.w

    def _create_image(self) -> None:
        '''Creates the image of Joel based on which sprite is activated.'''

        self.entity_image = pygame.transform.flip(self.walk_sprites.textures[int(self.curent_walk_sprite)],
                                                  flip_x=self.facing_left,
                                                  flip_y=False)

        if self.trigger_atk_anim or self.trigger_deatk_anim:
            self.entity_image = pygame.transform.flip(self.atk_sprites.textures[int(self.current_atk_sprite)],
                                                      flip_x=self.facing_left,
                                                      flip_y=False)

    def _handle_collisions_x(self, tiles) -> None:
        tiles_collided = self._get_hits(self.entity_hitbox,tiles)

        if len(tiles_collided) > 0:
            self.is_colliding_tiles = True
        else:
            self.is_colliding_tiles = False

        for tile in tiles_collided:
            if self.velocity.x > 0:    # Hit tile moving right
                self.position.x = tile.rect.left - self.entity_hitbox.w
                self.entity_hitbox.x = self.position.x
            elif self.velocity.x < 0:  # Hit tile moving left
                self.position.x = tile.rect.right
                self.entity_hitbox.x = self.position.x
            self.velocity.x = 0

    def _handle_collisions_y(self, tiles):
        self.on_ground = False
        self.entity_hitbox.bottom += 1
        tiles_collided = self._get_hits(self.entity_hitbox,tiles)

        if len(tiles_collided) > 0:
            self.is_colliding_tiles = True
        else:
            self.is_colliding_tiles = False

        for tile in tiles_collided:
            if self.velocity.y > 0:  # Hit tile from the top
                self.on_ground = True
                self.is_jumping = False
                self.velocity.y = 0
                self.position.y = tile.rect.top
                self.entity_hitbox.bottom = self.position.y
            elif self.velocity.y < 0:  # Hit tile from the bottom
                self.velocity.y = 0
                self.position.y = tile.rect.bottom + self.entity_hitbox.h
                self.entity_hitbox.bottom = self.position.y

    def _handle_entity_collisions(self, entities) -> None:
        entities_collided = self._get_hits(self.atk_hitbox,entities)
        if len(entities_collided) > 0:
            self.is_colliding_entities = True
        else:
            self.is_colliding_entities = False

    def _get_hits(self, hitbox, tiles: list) -> list:
        hits = []
        for tile in tiles:
            if hitbox.colliderect(tile):
                hits.append(tile)
        return hits

    def _horizontal_movement(self, dt) -> None:
        '''Calculates horizontal movement increment for a given dt.'''

        '''RESETTING ACCELERATION'''
        self.acceleration.x = 0

        '''APPLYING RUNNING BOOST'''
        if self.is_running:
            run_boost = self.run_boost
        else:
            run_boost = 0.0

        '''APPLYING WALK ACCELERATION AND PLAYER TRACTION'''
        if self.left_key is True and self.velocity.x <= 0:
            self.acceleration.x -= (self.walk_accel + run_boost)
        elif self.left_key is True and self.velocity.x > 0:
            self.acceleration.x -= abs(self.walk_accel + run_boost - self.traction*abs(self.velocity.x))
        elif self.right_key is True and self.velocity.x >= 0:
            self.acceleration.x += (self.walk_accel + run_boost)
        elif self.right_key is True and self.velocity.x < 0:
            self.acceleration.x += abs(self.walk_accel + run_boost - self.traction*abs(self.velocity.x))

        '''INERTIA PRINCIPLE (ADDING GROUND FRICTION)'''
        self.acceleration.x += self.velocity.x * self.weight * (self.friction + self.slipperiness * abs(self.velocity.x/30))

        '''NEWTON'S MOVEMENT EQUATION (VELOCITY)'''
        self.velocity.x += self.acceleration.x * dt

        '''LIMIT VELOCITY WHILE RUNNING'''
        self._limit_horizontal_velocity()

        '''NEWTON'S MOVEMENT EQUATION (POSITION)'''
        self.position.x += self.velocity.x * dt + 0.5 * self.acceleration.x * dt**2

        '''ROUNDING THE POSITION'''
        self.position.x = round(self.position.x)

        '''UPDATE HITBOX POSITION'''
        self.entity_hitbox.x = self.position.x
        self.atk_hitbox.x = self.position.x

    def _vertical_movement(self, dt) -> None:
        '''Calculates vertical movement increment for a given dt.'''

        '''MAINTAINING THE Y-AXIS VELOCITY UP TO A VALUE'''
        self.velocity.y += self.acceleration.y * dt

        '''SETTING THE MAX VALUE OF FALLING'''
        if self.velocity.y > self.max_y_velocity:
            self.velocity.y = self.max_y_velocity

        '''NEWTON'S MOVEMENT EQUATION (POSITION)'''
        self.position.y += self.velocity.y * dt + 0.5 * self.acceleration.y * dt**2

        '''UPDATE HITBOX POSITION'''
        self.entity_hitbox.bottom = self.position.y
        self.atk_hitbox.bottom = self.position.y

    def _limit_horizontal_velocity(self) -> None:
        '''Limits player's max horizontal velocity. Also prevents drifting movement
        due to numerical small values of x-velocity when player stops.'''

        '''LIMITING THE X-AXIS VELOCITY'''
        if self.jumping is False and self.velocity.x < 0:
            self.velocity.x = -min(abs(self.velocity.x), self.max_x_velocity)
        if self.jumping is False and self.velocity.x >= 0:
            self.velocity.x = min(abs(self.velocity.x), self.max_x_velocity)

        '''PREVENT MOVEMENT WHEN TOO SLOW'''
        if abs(self.velocity.x) < .18:
            self.velocity.x = 0


class Joel(Entity):
    def __init__(self, config, init_x, init_y):
        super().__init__(config, init_x, init_y)

    def control(self, event) -> None:
        '''Controls user input player events.'''

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.left_key = True
            elif event.key == pygame.K_RIGHT:
                self.right_key = True
            elif event.key == pygame.K_SPACE:
                self.jump()
            elif event.key == pygame.K_z:
                self.is_running = True
            elif event.key == pygame.K_r:
                self.reset()
            elif event.key == pygame.K_f:
                self.attack()

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                self.left_key = False
            elif event.key == pygame.K_RIGHT:
                self.right_key = False
            elif event.key == pygame.K_SPACE:
                if self.jumping:
                    self.velocity.y *= self.jump_control
                    self.jumping = False
            elif event.key == pygame.K_z:
                self.is_running = False
            elif event.key == pygame.K_f:
                if self.is_attacking:
                    self.is_attacking = False
                    self.ready_to_atk = True

    def _load_textures(self, config) -> None:
        '''Loads player's textures.'''

        self.walk_sprites = SpriteSheet(filename=config['joel']['walk_sheet'],
                                        tile_size=(config['joel']['tile-size'], config['joel']['tile-size']),
                                        scale=self.scale,
                                        dimension=(1, config['joel']['walk-sheet-size']))
        self.n_walk_sprites = len(self.walk_sprites.textures)
        self.curent_walk_sprite = 0
        self.atk_sprites = SpriteSheet(filename=config['joel']['atk_sheet'],
                                       tile_size=(48, config['joel']['tile-size']),
                                       scale=self.scale,
                                       dimension=(1, 5))
        self.n_atk_sprites = len(self.atk_sprites.textures)
        self.current_atk_sprite = 0



class Kittol(Entity):
    def __init__(self, config, init_x, init_y):
        super().__init__(config, init_x, init_y)

    def control(self) -> None:
        '''Override Entity built-in function as the player can not control enemies.'''
        pass

    def _load_textures(self, config) -> None:
        '''Loads enemy's textures.'''

        self.walk_sprites = SpriteSheet(filename=config['kittol']['walk_sheet'],
                                        tile_size=(config['kittol']['tile-size'],
                                                   config['kittol']['tile-size']),
                                        scale=self.scale,
                                        dimension=(1, 1))
        self.n_walk_sprites = len(self.walk_sprites.textures)
        self.curent_walk_sprite = 0

