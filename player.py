

import pygame


class Joel(pygame.sprite.Sprite):

    def __init__(self, screen_dimension: int) -> None:
        '''Creates player Joel.'''

        '''INIT SPRITE CLASS INHERITANCE'''
        pygame.sprite.Sprite.__init__(self)

        '''DIMENSIONS'''
        self.screen_dimension = screen_dimension #can i remove this?
        self.width = 64
        self.height = 64

        '''PHYSICAL PROPERTIES (PLACEHOLDER - NEEDS TO COME FROM THE LVL AND TILE PROPERTY)'''
        self.gravity = 10.0
        self.friction = -0.22  # standard normalized friction = -0.22
        self.traction = abs(self.friction)
        self.accel_correction = 1 - 3.0*(0.22 + self.friction)
        self.air_resistance = 0.0
        self.thrust = 0.0 # needs consistent implementation

        '''INIT POSITION/VELOCITY/ACCELERATION VECTORS'''
        self.init_x = 64
        self.init_y = 448 - self.height
        self.position = pygame.math.Vector2(self.init_x,self.init_y)
        self.velocity = pygame.math.Vector2(0,0)
        self.acceleration = pygame.math.Vector2(0,self.gravity)

        '''PLAYER INPUT'''
        self.left_key = False
        self.right_key = False
        self.facing_left = False

        '''PLAYER ACTIONS'''
        self.jumping = False
        self.on_ground = False
        self.is_running = False

        '''PLAYER STATS'''
        self.jumpY_velocity = 65
        self.jumpX_velocity = 10
        self.jump_control = 0.2

        self.walk_accel = 1.9 * self.accel_correction
        self.run_boost = 1.75 * self.accel_correction
        self.max_velocity  = 20

        self.mass = 0.11
        self.weight = self.mass * self.gravity
        self.slipperiness = 0.03


    def render(self, screen) -> None:
        '''Renders player on the screen given.'''

        pygame.draw.rect(screen, (255,255,255), pygame.Rect(self.position.x, self.position.y, self.width, self.height))

    def update(self, dt) -> None:
        '''Calls horizontal and vertical movement functions that calculates
        the increment on the X and Y position for a given dt.'''

        self.h_movement(dt)
        self.v_movement(dt)

    def h_movement(self, dt) -> None:
        '''Calculates horizontal movement increment for a given dt.'''

        '''RESETTING ACCELERATION'''
        self.acceleration.x = 0

        '''APPLYING RUNNING BOOST'''
        if self.is_running:
            rboost = self.run_boost
        else:
            rboost = 0.0

        '''APPLYING WALK ACCELERATION AND PLAYER TRACTION'''
        if self.left_key is True and self.velocity.x <= 0:
            self.acceleration.x -= (self.walk_accel + rboost)
        elif self.left_key is True and self.velocity.x > 0:
            self.acceleration.x -= (self.walk_accel + rboost - self.traction*abs(self.velocity.x))
        elif self.right_key is True and self.velocity.x >= 0:
            self.acceleration.x += (self.walk_accel + rboost)
        elif self.right_key is True and self.velocity.x < 0:
            self.acceleration.x += (self.walk_accel + rboost - self.traction*abs(self.velocity.x))

        '''INERTIA PRINCIPLE (ADDING GROUND AND AIR RESISTANCE)'''
        self.acceleration.x += self.velocity.x * self.weight*\
                               (self.friction + self.slipperiness * abs(self.velocity.x/30))
        self.acceleration.x += self.velocity.x * self.air_resistance

        '''NEWTON'S MOVEMENT EQUATION (VELOCITY)'''
        self.velocity.x += self.acceleration.x * dt

        '''LIMIT VELOCITY WHILE RUNNING'''
        self.limit_velocity()

        '''NEWTON'S MOVEMENT EQUATION (POSITION)'''
        self.position.x += self.velocity.x * dt + 0.5 * self.acceleration.x * dt**2

        '''ROUNDING THE POSITION'''
        self.position.x = round(self.position.x)

    def v_movement(self, dt) -> None:
        '''Calculates vertical movement increment for a given dt.'''

        '''MAINTAINING THE Y-AXIS VELOCITY UP TO A VALUE'''
        self.velocity.y += self.acceleration.y * dt

        '''SETTING THE MAX VALUE OF FALLING'''
        if self.velocity.y > self.jumpY_velocity + self.thrust:
            self.velocity.y = self.jumpY_velocity + self.thrust

        '''NEWTON'S MOVEMENT EQUATION (POSITION)'''
        self.position.y += self.velocity.y * dt + 0.5 * self.acceleration.y * dt**2

        '''ROUNDING THE POSITION'''
        self.position.x = round(self.position.x)

        '''PLACEHOLDER (COLLISIONS ARE NOT IMPLEMENTED  YET)'''
        if self.position.y >= self.init_y:
            self.on_ground = True
            self.velocity.y = 0
            self.position.y = self.init_y

    def jump(self) -> None:
        '''Calculates y position and velocity after jumping action.'''

        if self.on_ground:
            self.jumping = True

            '''Y-AXIS FORCE MOTION'''
            self.velocity.y -= (1/self.weight)*self.jumpY_velocity + self.thrust

            '''X-AXIS FORCE MOTION'''
            if self.velocity.x > 0:
                self.velocity.x += (1/self.weight)*self.jumpX_velocity
            if self.velocity.x < 0:
                self.velocity.x += -(1/self.weight)*self.jumpX_velocity

            '''NOT JUMP AGAIN UNTIL COMPLETE THE FALLING'''
            self.on_ground = False

    def limit_velocity(self) -> None:
        '''Limits player's max velocity. Also prevents drifting movement due to numerical
        small values of x-velocity when player stops.'''

        '''LIMITING THE X-AXIS VELOCITY'''
        if self.jumping is False and self.velocity.x < 0:
            self.velocity.x = -min(abs(self.velocity.x),self.max_velocity)
        if self.jumping is False and self.velocity.x >= 0:
            self.velocity.x = min(abs(self.velocity.x),self.max_velocity)

        '''PREVENT MOVEMENT WHEN TOO SLOW'''
        if abs(self.velocity.x) < .18:
            self.velocity.x = 0