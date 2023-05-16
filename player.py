

import pygame
from texture import SpriteSheet


class Joel:

    def __init__(self, scale, init_x = 64, init_y = 250) -> None:
        '''Creates player Joel.'''

        '''PLAYER DIMENSIONS'''
        self.width = 16 * scale
        self.height = 16 * scale

        '''LOAD TEXTURES'''
        self.walk_sprites = SpriteSheet(filename='assets/joel.png',
                                        tile_size=(16,16),
                                        scale=scale,
                                        dimension=(1, 10))
        self.n_walk_sprites = len(self.walk_sprites.textures)
        self.curent_walk_sprite = 0
        self.atk_sprites = SpriteSheet(filename='./assets/joel-atk.png',
                                       tile_size=(48,16),
                                       scale=scale,
                                       dimension=(1,5))
        self.n_atk_sprites = len(self.atk_sprites.textures)
        self.current_atk_sprite = 0

        self.joel_image = self.walk_sprites.textures[self.curent_walk_sprite]
        self.joel_hitbox = self.joel_image.get_rect()
        self.hitbox_color = (255,0,0)

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
        self.is_colliding = False
        self.is_sticked = False
        self.facing_left = False
        self.is_attacking = False
        self.ready_to_atk = True

        '''PLAYER STATS'''
        self.jump_force = 11
        self.jumpX_velocity = 1
        self.jump_control = 0.25
        self.walk_accel = 0.3
        self.run_boost = 0.3
        self.max_x_velocity = 8
        self.max_y_velocity = 15
        self.mass = 0.8
        self.slipperiness = 0.03

        '''LEVEL ATTRIBUTES (MUST BE OVERRIDEN BY ADDING THE PLAYER TO THE LEVEL)'''
        self.gravity = None
        self.friction = None
        self.traction = None
        self.weight = None
        self.acceleration = None


    '''=============  PUBLIC METHODS ==============='''

    def render(self, screen, camera, show_hitbox=True) -> None:
        '''Renders player on the screen given.'''

        self._animate()
        if self.is_attacking and self.facing_left:
            screen.blit(self.joel_image, (self.joel_hitbox.x - camera.offset.x - 128, self.joel_hitbox.y))
        else:
            screen.blit(self.joel_image, (self.joel_hitbox.x - camera.offset.x, self.joel_hitbox.y))

        if show_hitbox and self.is_colliding:
            rect = pygame.Rect(self.joel_hitbox.x - camera.offset.x,
                               self.joel_hitbox.y,
                               self.joel_hitbox.w,
                               self.joel_hitbox.h)
            pygame.draw.rect(screen,
                             self.hitbox_color,
                             rect,
                             border_radius=1,
                             width=1)

    def update(self, dt, tiles) -> None:
        '''Calls horizontal and vertical movement functions that calculates
        the increment on the X and Y position for a given dt.'''

        '''MOVEMENT UPDATE'''
        self._horizontal_movement(dt)
        self._handle_collisions_x(tiles)
        self._vertical_movement(dt)
        self._handle_collisions_y(tiles)

    def jump(self) -> None:
        '''Calculates y position and velocity after jumping action.'''

        if self.on_ground:
            self.jumping = True

            '''Y-AXIS FORCE MOTION'''
            self.velocity.y -= self.jump_force/self.weight
            if self.is_running and abs(self.velocity.x) > 0.75 * self.max_x_velocity:
                self.velocity.y *= abs(self.velocity.x * 0.14)

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
            self.is_attacking = True
            self.ready_to_atk = False

    def control(self, event) -> None:

        '''USER INPUT EVENTS'''
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


    '''=============  PRIVATE METHODS ==============='''

    def _animate(self) -> None:
        '''Controls character several animations.'''

        '''LEFT AND RIGHT ANIMATION'''
        if self.left_key or self.right_key:
            if self.curent_walk_sprite > 9:
                self.curent_walk_sprite = 0  #avoid getting too big, although modulo handles list index
            if self.is_running:
                self.curent_walk_sprite += 1
            else:
                self.curent_walk_sprite += 0.5
            self.curent_walk_sprite = self.curent_walk_sprite % self.n_walk_sprites
        if self.left_key is False and self.right_key is False:
            self.curent_walk_sprite = 0

        '''JUMPING ANIMATION'''
        if self.jumping:
            self.curent_walk_sprite = 5

        '''FACING LEFT-RIGHT ANIMATION'''
        if self.left_key:
            self.facing_left = True
        elif self.right_key:
            self.facing_left = False

        '''ATTACK ANIMATION'''
        if self.is_attacking:
            if self.current_atk_sprite > 3:
                self.current_atk_sprite = 0
            self.current_atk_sprite += 0.6
            self.current_atk_sprite = self.current_atk_sprite % self.n_walk_sprites
        else:
            self.current_atk_sprite = 0

        '''CREATE IMAGE'''
        if self.is_attacking is False:
            self.joel_image = pygame.transform.flip(self.walk_sprites.textures[int(self.curent_walk_sprite)],
                                                    flip_x=self.facing_left,
                                                    flip_y=False)
        if self.is_attacking is True:
            self.joel_image = pygame.transform.flip(self.atk_sprites.textures[int(self.current_atk_sprite)],
                                                    flip_x=self.facing_left,
                                                    flip_y=False)

    def _handle_collisions_x(self, tiles) -> None:
        tiles_collided = self._get_hits(tiles)

        if len(tiles_collided) > 0:
            self.is_colliding = True
        else:
            self.is_colliding = False

        for tile in tiles_collided:
            if self.velocity.x > 0:    # Hit tile moving right
                self.position.x = tile.rect.left - self.joel_hitbox.w
                self.joel_hitbox.x = self.position.x
            elif self.velocity.x < 0:  # Hit tile moving left
                self.position.x = tile.rect.right
                self.joel_hitbox.x = self.position.x
            self.velocity.x = 0

    def _handle_collisions_y(self, tiles):
        self.on_ground = False
        self.joel_hitbox.bottom += 1
        tiles_collided = self._get_hits(tiles)

        if len(tiles_collided) > 0:
            self.is_colliding = True
        else:
            self.is_colliding = False

        for tile in tiles_collided:
            if self.velocity.y > 0:  # Hit tile from the top
                self.on_ground = True
                self.is_jumping = False
                self.velocity.y = 0
                self.position.y = tile.rect.top
                self.joel_hitbox.bottom = self.position.y
            elif self.velocity.y < 0:  # Hit tile from the bottom
                self.velocity.y = 0
                self.position.y = tile.rect.bottom + self.joel_hitbox.h
                self.joel_hitbox.bottom = self.position.y

    def _get_hits(self, tiles: list) -> list:
        hits = []
        for tile in tiles:
            if self.joel_hitbox.colliderect(tile):
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
        self.joel_hitbox.x = self.position.x

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
        self.joel_hitbox.bottom = self.position.y

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
