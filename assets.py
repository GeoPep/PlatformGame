# Assets classes
import pygame
import math
from parameters import *


class World:
    def __init__(self, world_number, image_source, set_colorkey=False, colorkey=(0, 0, 0)):
        WORLD_WIDTH = WORLD_WIDTH_DIRECTORY[world_number-1]
        WORLD_HEIGHT = WORLD_HEIGHT_DIRECTORY[world_number-1]
        WORLD_INITIAL_X = WORLD_INITIAL_X_DIRECTORY[world_number-1]
        WORLD_INITIAL_Y = WORLD_INITIAL_Y_DIRECTORY[world_number-1]
        self.image = pygame.image.load(image_source)
        self.image = pygame.transform.scale(self.image, (WORLD_WIDTH, WORLD_HEIGHT))
        if set_colorkey:
            self.image.set_colorkey(colorkey)
        self.rect = self.image.get_rect()
        self.rect.left = WORLD_INITIAL_X
        self.rect.top = WORLD_INITIAL_Y
        self.kill = False
        return

    def update(self, dx, dy):
        self.rect.x -= dx
        self.rect.y -= dy
        return

    def draw(self, screen):
        screen.blit(self.image, self.rect)
        return


class WorldBackground:
    def __init__(self, world_number, image_source, set_colorkey=False, colorkey=(0, 0, 0)):
        self.DEPTH_FACTOR = WORLD_DEPTH_FACTOR_DIRECTORY[world_number-1]
        self.image = pygame.image.load(image_source)
        self.image = pygame.transform.scale(self.image, (1920, 1080))
        if set_colorkey:
            self.image.set_colorkey(colorkey)
        self.rect = self.image.get_rect()
        self.rect.left = 0
        self.rect.top = -300
        self.kill = False
        return

    def update(self, dx, dy):
        # DEPTH_FACTOR = 0 for static background
        # 0 < DEPTH_FACTOR < 1 for slower movement of background in order to give the sense of depth
        # DEPTH_FACTOR = 1 the background is fixed with the platforms and is moving with them
        self.rect.x -= int(self.DEPTH_FACTOR * dx)
        self.rect.y -= int(self.DEPTH_FACTOR * dy)
        return

    def draw(self, screen):
        screen.blit(self.image, self.rect)
        return


class Platform:
    def __init__(self, world_number, x, y, w, h):
        WORLD_INITIAL_X = WORLD_INITIAL_X_DIRECTORY[world_number-1]
        WORLD_INITIAL_Y = WORLD_INITIAL_Y_DIRECTORY[world_number - 1]
        self.image = pygame.Surface((w, h))
        self.image.fill(GREEN)
        self.rect = pygame.Rect(x, y, w, h)
        self.rect.x = WORLD_INITIAL_X + x
        self.rect.y = WORLD_INITIAL_Y + y
        self.show_rect = False
        self.kill = False
        return

    def update(self, dx, dy):
        self.rect.x -= dx
        self.rect.y -= dy
        return

    def draw(self, screen):
        if self.show_rect:
            screen.blit(self.image, self.rect)
        return


class Door:
    def __init__(self, world_number, x, y, w, h):
        WORLD_INITIAL_X = WORLD_INITIAL_X_DIRECTORY[world_number - 1]
        WORLD_INITIAL_Y = WORLD_INITIAL_Y_DIRECTORY[world_number - 1]
        self.image = pygame.Surface((w, h))
        self.image.fill(GREEN)
        self.rect = pygame.Rect(x, y, w, h)
        self.rect.x = WORLD_INITIAL_X + x
        self.rect.y = WORLD_INITIAL_Y + y
        self.show_rect = False
        self.kill = False
        self.opened = False
        return

    def update(self, dx, dy):
        self.rect.x -= dx
        self.rect.y -= dy
        return

    def check_if_door_is_open(self):
        # Check whether player opens the door
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.opened = True
        return

    def draw(self, screen):
        if self.show_rect:
            screen.blit(self.image, self.rect)
        return


class Player:
    def __init__(self, world_number):
        PLAYER_INITIAL_X = WORLD_PLAYER_INITIAL_X_DIRECTORY[world_number-1]
        PLAYER_INITIAL_Y = WORLD_PLAYER_INITIAL_Y_DIRECTORY[world_number-1]
        WORLD_HEIGHT = WORLD_HEIGHT_DIRECTORY[world_number-1]
        self.walking = False
        self.jumping = False
        self.jumping_up = True
        self.current_frame = 0
        self.last_update = 0
        self.load_images()
        self.image = self.standing_frames_r[0]
        self.rect = self.image.get_rect()
        self.rect.x = PLAYER_INITIAL_X
        self.rect.y = PLAYER_INITIAL_Y
        self.abs_pos_x = PLAYER_INITIAL_X
        self.abs_pos_y = WORLD_HEIGHT - (HEIGHT - PLAYER_INITIAL_Y)
        self.vel_x = 0
        self.vel_y = 0
        self.acc_x = 0
        self.acc_y = 0
        self.direction_right = True
        self.coins_collected = 0
        self.time_last_update = pygame.time.get_ticks()
        self.life = PLAYER_INITIAL_LIFE
        self.can_jump = False
        self.kill = False
        self.pause_time = 0
        self.lives = 0
        self.world = 0
        return

    def load_images(self):
        # Standing frames
        self.standing_frames_r = []
        self.standing_frames_l = []
        for frame in range(PLAYER_STANDING_FRAMES_NUMBER):
            self.standing_frames_r.append(pygame.image.load(f"assets/player/standing/{frame}.png"))
            self.standing_frames_r[frame] = pygame.transform.scale(self.standing_frames_r[frame], (PLAYER_WIDTH, PLAYER_HEIGHT))
            self.standing_frames_l.append(pygame.transform.flip(self.standing_frames_r[frame], True, False))

        # Walking frames
        self.walk_frames_r = []
        self.walk_frames_l = []
        for frame in range(PLAYER_WALK_FRAMES_NUMBER):
            self.walk_frames_r.append(pygame.image.load(f"assets/player/moving/{frame}.png"))
            self.walk_frames_r[frame] = pygame.transform.scale(self.walk_frames_r[frame], (PLAYER_WIDTH, PLAYER_HEIGHT))
            self.walk_frames_l.append(pygame.transform.flip(self.walk_frames_r[frame], True, False))

        # Jumping frames up
        self.jump_frames_up_r = []
        self.jump_frames_up_l = []
        for frame in range(PLAYER_JUMP_UP_FRAMES_NUMBER):
            self.jump_frames_up_r.append(pygame.image.load(f"assets/player/jumping_up/{frame}.png"))
            self.jump_frames_up_r[frame] = pygame.transform.scale(self.jump_frames_up_r[frame], (PLAYER_WIDTH, PLAYER_HEIGHT))
            self.jump_frames_up_l.append(pygame.transform.flip(self.jump_frames_up_r[frame], True, False))

        # Jumping frames up
        self.jump_frames_down_r = []
        self.jump_frames_down_l = []
        for frame in range(PLAYER_JUMP_DOWN_FRAMES_NUMBER):
            self.jump_frames_down_r.append(pygame.image.load(f"assets/player/jumping_down/{frame}.png"))
            self.jump_frames_down_r[frame] = pygame.transform.scale(self.jump_frames_down_r[frame], (PLAYER_WIDTH, PLAYER_HEIGHT))
            self.jump_frames_down_l.append(pygame.transform.flip(self.jump_frames_down_r[frame], True, False))
        return

    def update(self, dx, dy):
        self.rect.x -= dx
        self.rect.y -= dy
        self.animate()
        self.control_and_physics()
        return

    def pass_pause_time(self, pause_time):
        self.pause_time += pause_time
        return

    def control_and_physics(self):
        # Physics for movement
        current_time = pygame.time.get_ticks()
        current_time -= self.pause_time
        dt = (current_time - self.time_last_update) * 0.001  # converted from ms to s
        self.time_last_update = current_time
        T = 0
        F = 0
        keys = pygame.key.get_pressed()
        if self.vel_x > 0:
            if keys[pygame.K_RIGHT]:
                T = -FRICTION_COEFFICIENT * MASS * GRAVITY
                if self.vel_x > UMAX:
                    F = -T
                    self.vel_x = UMAX
                else:
                    F = F0
            elif keys[pygame.K_LEFT]:
                T = -FRICTION_COEFFICIENT * MASS * GRAVITY
                F = -2 * F0
            else:
                T = -FRICTION_COEFFICIENT * MASS * GRAVITY
                F = 0
        elif self.vel_x < 0:
            if keys[pygame.K_RIGHT]:
                T = FRICTION_COEFFICIENT * MASS * GRAVITY
                F = 2 * F0
            elif keys[pygame.K_LEFT]:
                T = FRICTION_COEFFICIENT * MASS * GRAVITY
                if self.vel_x < -UMAX:
                    F = -T
                    self.vel_x = -UMAX
                else:
                    F = -F0
            else:
                T = FRICTION_COEFFICIENT * MASS * GRAVITY
                F = 0
        else:
            if keys[pygame.K_RIGHT]:
                T = -FRICTION_COEFFICIENT * MASS * GRAVITY
                T = F0
            elif keys[pygame.K_LEFT]:
                T = FRICTION_COEFFICIENT * MASS * GRAVITY
                T = -F0
            else:
                T = 0
                F = 0

        # Equations of motion solved with Euler method for ODE
        self.acc_x = (F + T) / MASS
        self.acc_y = GRAVITY
        self.vel_x += self.acc_x * dt
        self.vel_y += self.acc_y * dt
        if abs(self.vel_x) <= UMIN and not (keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]):
            self.vel_x = 0
        if abs(self.vel_y) <= UMIN:
            self.vel_y = 0.1
        self.rect.x += int(self.vel_x * dt)
        self.rect.y += int(self.vel_y * dt)
        self.abs_pos_x += int(self.vel_x * dt)
        self.abs_pos_y += int(self.vel_y * dt)
        return

    def jump(self):
        # Jump only if standing on a platform
        if self.can_jump:
            self.vel_y = JUMP_INITIAL_VELOCITY

    def animate(self):
        now = pygame.time.get_ticks()
        keys = pygame.key.get_pressed()
        if self.vel_x > 0 or keys[pygame.K_RIGHT]:
            self.direction_right = True
        if self.vel_x < 0 or keys[pygame.K_LEFT]:
            self.direction_right = False

        if abs(self.vel_x) >= UMIN:
            if not self.walking:
                self.current_frame = 0
            self.walking = True
        else:
            if self.walking:
                self.current_frame = 0
            self.walking = False

        if self.vel_y != 0:
            self.jumping = True
        else:
            self.jumping = False

        if self.vel_y < 0:
            if not self.jumping_up:
                self.current_frame = 0
            self.jumping_up = True
        if self.vel_y > 0:
            if self.jumping_up:
                self.current_frame = 0
            self.jumping_up = False

        if not self.jumping and not self.walking:
            if self.current_frame >= PLAYER_STANDING_FRAMES_NUMBER:     # for debugging
                self.current_frame = 0

            if now - self.last_update > PLAYER_STAND_ANIMATION_FRAME_TIME:
                self.last_update = now
                if self.current_frame != PLAYER_STANDING_FRAMES_NUMBER - 1:
                    self.current_frame += 1
                else:
                    self.current_frame = 0
            if self.direction_right:
                self.image = self.standing_frames_r[self.current_frame]
            else:
                self.image = self.standing_frames_l[self.current_frame]
        elif self.walking and not self.jumping:
            if self.current_frame >= PLAYER_WALK_FRAMES_NUMBER:  # for debugging
                self.current_frame = 0

            if now - self.last_update > PLAYER_WALK_ANIMATION_FRAME_TIME:
                self.last_update = now
                if self.current_frame != PLAYER_WALK_FRAMES_NUMBER - 1:
                    self.current_frame += 1
                else:
                    self.current_frame = 0
            if self.direction_right:
                self.image = self.walk_frames_r[self.current_frame]
            else:
                self.image = self.walk_frames_l[self.current_frame]
        else:
            if self.jumping_up:
                if self.current_frame >= PLAYER_JUMP_UP_FRAMES_NUMBER:  # for debugging
                    self.current_frame = 0

                if now - self.last_update > PLAYER_JUMP_UP_ANIMATION_FRAME_TIME:
                    self.last_update = now
                    if self.current_frame != PLAYER_JUMP_UP_FRAMES_NUMBER - 1:
                        self.current_frame += 1
                    else:
                        self.current_frame = 0
                if self.direction_right:
                    self.image = self.jump_frames_up_r[self.current_frame]
                else:
                    self.image = self.jump_frames_up_l[self.current_frame]
            else:
                if self.current_frame >= PLAYER_JUMP_DOWN_FRAMES_NUMBER:  # for debugging
                    self.current_frame = 0

                if now - self.last_update > PLAYER_JUMP_DOWN_ANIMATION_FRAME_TIME:
                    self.last_update = now
                    if self.current_frame != PLAYER_JUMP_DOWN_FRAMES_NUMBER - 1:
                        self.current_frame += 1
                    else:
                        self.current_frame = 0
                if self.direction_right:
                    self.image = self.jump_frames_down_r[self.current_frame]
                else:
                    self.image = self.jump_frames_down_l[self.current_frame]
        return

    def draw(self, screen):
        screen.blit(self.image, self.rect)
        return


class Enemy:
    def __init__(self, world_number, x, y):
        WORLD_INITIAL_X = WORLD_INITIAL_X_DIRECTORY[world_number-1]
        WORLD_INITIAL_Y = WORLD_INITIAL_Y_DIRECTORY[world_number-1]
        self.current_frame = 0
        self.last_update = 0
        self.last_fire_time = pygame.time.get_ticks()
        self.pause_time = 0
        self.load_images()
        self.image = self.frames_l[0]
        self.rect = self.image.get_rect()
        self.rect.x = WORLD_INITIAL_X + x
        self.rect.y = WORLD_INITIAL_Y + y
        self.time_last_update = pygame.time.get_ticks()
        self.life = ENEMY_INITIAL_LIFE
        self.player_x = 0
        self.player_y = 0
        self.direction_right = False
        self.is_hit = False
        self.fires = False
        self.kill = False
        return

    def load_images(self):
        # Enemy frames
        self.frames_r = []
        self.frames_l = []
        for frame in range(ENEMY_FRAMES_NUMBER):
            self.frames_l.append(pygame.image.load(f"assets/enemy/ghost/{frame}.png"))
            self.frames_l[frame] = pygame.transform.scale(self.frames_l[frame], (ENEMY_WIDTH, ENEMY_HEIGHT))
            self.frames_r.append(pygame.transform.flip(self.frames_l[frame], True, False))
        # Adding extra frame for enemy hit
        self.frames_l.append(pygame.image.load(f"assets/enemy/ghost/hit.png"))
        self.frames_l[ENEMY_FRAMES_NUMBER] = pygame.transform.scale(self.frames_l[ENEMY_FRAMES_NUMBER], (ENEMY_WIDTH, ENEMY_HEIGHT))
        self.frames_r.append(pygame.transform.flip(self.frames_l[ENEMY_FRAMES_NUMBER], True, False))
        return

    def update(self, dx, dy):
        self.rect.x -= dx
        self.rect.y -= dy
        self.animate()
        return

    def damage(self):
        now = pygame.time.get_ticks()
        self.life -= ENEMY_DAMAGE_PER_FIREBALL
        self.last_update = now
        self.is_hit = True
        self.current_frame = ENEMY_FRAMES_NUMBER

    def animate(self):
        # Checks direction
        if self.direction_right:
            if self.player_x < self.rect.x:
                self.direction_right = False
        else:
            if self.player_x > self.rect.x + ENEMY_WIDTH:
                self.direction_right = True
        # Frame
        now = pygame.time.get_ticks()
        if not self.is_hit:
            if now - self.last_update > ENEMY_ANIMATION_FRAME_TIME:
                self.last_update = now
                if self.direction_right:
                    self.image = self.frames_r[self.current_frame]
                else:
                    self.image = self.frames_l[self.current_frame]
                self.current_frame += 1
                if self.current_frame == ENEMY_FRAMES_NUMBER:
                    self.current_frame = 0
        else:
            if self.direction_right:
                self.image = self.frames_r[self.current_frame]
            else:
                self.image = self.frames_l[self.current_frame]
            if now - self.last_update > ENEMY_ANIMATION_FRAME_TIME:
                self.last_update = now
                self.current_frame = 0
                self.is_hit = False
        return

    def pass_values(self, player_x, player_y):
        self.player_x = player_x
        self.player_y = player_y
        return

    def active(self):
        state = False
        if WIDTH >= self.rect.x + ENEMY_WIDTH >= 0:
            if self.rect.y + ENEMY_HEIGHT >= 0 and self.rect.y <= HEIGHT:
                state = True
        return state

    def generate_fire(self):
        state = False
        now = pygame.time.get_ticks()
        now -= self.pause_time
        if now - self.last_fire_time > ENEMY_FIRE_SPAWN_TIME_INTERVAL:
            self.last_fire_time = now
            state = True
        return state

    def pass_pause_time(self, pause_time):
        self.pause_time += pause_time
        return

    def draw(self, screen):
        screen.blit(self.image, self.rect)
        return


class Coin:
    def __init__(self, world_number, x, y):
        WORLD_INITIAL_X = WORLD_INITIAL_X_DIRECTORY[world_number-1]
        WORLD_INITIAL_Y = WORLD_INITIAL_Y_DIRECTORY[world_number-1]
        self.current_frame = 0
        self.last_update = 0
        self.load_images()
        self.image = self.frames[0]
        self.rect = self.image.get_rect()
        self.rect.x = WORLD_INITIAL_X + x
        self.rect.y = WORLD_INITIAL_Y + y
        self.kill = False
        return

    def load_images(self):
        self.frames = []
        for frame in range(COIN_FRAMES_NUMBER):
            self.frames.append(pygame.image.load(f"assets/coin/{frame}.png"))
            self.frames[frame] = pygame.transform.scale(self.frames[frame], (COIN_WIDTH, COIN_HEIGHT))
        return

    def update(self, dx, dy):
        self.rect.x -= dx
        self.rect.y -= dy
        self.animate()
        return

    def animate(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > COIN_ANIMATION_FRAME_TIME:
            self.last_update = now
            if self.current_frame != COIN_FRAMES_NUMBER - 1:
                self.current_frame += 1
            else:
                self.current_frame = 0
        self.image = self.frames[self.current_frame]
        return

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class Splash:
    def __init__(self, position_rect):
        self.current_frame = 0
        self.last_update = 0
        self.load_images()
        self.image = self.frames[0]
        self.rect = self.image.get_rect()
        self.rect.x = position_rect.x + SPLASH_OFFSET_X
        self.rect.y = position_rect.y + SPLASH_OFFSET_Y
        self.kill = False
        return

    def load_images(self):
        self.frames = []
        for frame in range(SPLASH_FRAMES_NUMBER):
            self.frames.append(pygame.image.load(f"assets/splash/{frame}.png"))
            self.frames[frame] = pygame.transform.scale(self.frames[frame], (SPLASH_WIDTH, SPLASH_HEIGHT))
        return

    def update(self, dx, dy):
        self.rect.x -= dx
        self.rect.y -= dy
        self.animate()
        return

    def animate(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > SPLASH_ANIMATION_FRAME_TIME:
            self.last_update = now
            self.image = self.frames[self.current_frame]
            self.current_frame += 1
            if self.current_frame == SPLASH_FRAMES_NUMBER:
                self.kill = True
        return

    def draw(self, screen):
        screen.blit(self.image, self.rect)
        return


class Fireball:
    def __init__(self, position_rect, player_direction_right):
        self.current_frame = 0
        self.last_update = 0
        self.last_motion_time_update = pygame.time.get_ticks()
        self.direction_right = player_direction_right
        self.load_images()
        self.image = self.frames[0]
        self.rect = self.image.get_rect()
        if self.direction_right:
            self.rect.x = position_rect.x + FIREBALL_RIGHT_OFFSET_X
        else:
            self.rect.x = position_rect.x + FIREBALL_LEFT_OFFSET_X
        self.rect.y = position_rect.y + FIREBALL_OFFSET_Y
        self.pause_time = 0
        self.kill = False

    def load_images(self):
        self.frames = []
        for frame in range(FIREBALL_FRAMES_NUMBER):
            self.frames.append(pygame.image.load(f"assets/fireball/{frame}.png"))
            self.frames[frame] = pygame.transform.scale(self.frames[frame], (FIREBALL_WIDTH, FIREBALL_HEIGHT))
            if not self.direction_right:
                self.frames[frame] = pygame.transform.flip(self.frames[frame], True, False)
        return

    def update(self, dx, dy):
        self.rect.x -= dx
        self.rect.y -= dy
        self.move()
        self.animate()
        return

    def move(self):
        now = pygame.time.get_ticks()
        now -= self.pause_time
        dt = now - self.last_motion_time_update
        self.last_motion_time_update = now
        if self.direction_right:
            self.rect.x += int(dt * FIREBALL_VELOCITY_X)
        else:
            self.rect.x -= int(dt * FIREBALL_VELOCITY_X)
        self.rect.y += int(FIREBALL_Y_MOTION_INITIAL_VELOCITY * dt + FIREBALL_Y_GRAVITY_FACTOR * dt * dt)
        return

    def animate(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > FIREBALL_ANIMATION_FRAME_TIME:
            self.last_update = now
            self.image = self.frames[self.current_frame]
            self.current_frame += 1
            if self.current_frame == FIREBALL_FRAMES_NUMBER:
                self.current_frame = 0
        return

    def pass_pause_time(self, pause_time):
        self.pause_time += pause_time
        return

    def draw(self, screen):
        screen.blit(self.image, self.rect)
        return


class Enemy_Fireball:
    def __init__(self, enemy_x, enemy_y, player_x, player_y,):
        self.current_frame = 0
        self.last_update = 0
        self.last_motion_time_update = pygame.time.get_ticks()
        self.pause_time = 0
        self.direction_right = True
        self.enemy_x = enemy_x
        self.enemy_y = enemy_y
        self.player_x = player_x
        self.player_y = player_y
        self.angle = 0
        self.calculate_angle()
        self.load_images()
        self.image = self.frames[0]
        self.rect = self.image.get_rect()
        if self.direction_right:
            self.rect.x = self.enemy_x + ENEMY_FIREBALL_RIGHT_OFFSET_X
        else:
            self.rect.x = self.enemy_x + ENEMY_FIREBALL_LEFT_OFFSET_X
        self.rect.y = self.enemy_y + ENEMY_FIREBALL_OFFSET_Y
        self.kill = False

    def calculate_angle(self):
        if self.player_x >= self.enemy_x:
            self.direction_right = True
        else:
            self.direction_right = False

        if self.direction_right:
            if self.player_x - self.enemy_x != 0:   # Divide by zero condition
                self.angle = math.atan(-(self.player_y - self.enemy_y) / (self.player_x - self.enemy_x))
        else:
            if self.enemy_x - self.player_x != 0:   # Divide by zero condition
                self.angle = math.atan((self.player_y - self.enemy_y) / (self.enemy_x - self.player_x))
        return

    def load_images(self):
        self.frames = []
        for frame in range(ENEMY_FIRE_FRAMES_NUMBER):
            self.frames.append(pygame.image.load(f"assets/enemy/ghost/fireball/{frame}.png"))
            self.frames[frame] = pygame.transform.scale(self.frames[frame], (ENEMY_FIRE_WIDTH, ENEMY_FIREBALL_HEIGHT))
            if not self.direction_right:
                self.frames[frame] = pygame.transform.flip(self.frames[frame], True, False)
            self.frames[frame] = pygame.transform.rotate(self.frames[frame], math.degrees(self.angle))
        return

    def update(self, dx, dy):
        self.rect.x -= dx
        self.rect.y -= dy
        self.move()
        self.animate()
        return

    def move(self):
        now = pygame.time.get_ticks()
        now -= self.pause_time
        dt = now - self.last_motion_time_update
        self.last_motion_time_update = now
        if self.direction_right:
            self.rect.x += int(dt * ENEMY_FIREBALL_VELOCITY_X * math.cos(self.angle))
            self.rect.y -= int(dt * ENEMY_FIREBALL_VELOCITY_X * math.sin(self.angle))
        else:
            self.rect.x -= int(dt * ENEMY_FIREBALL_VELOCITY_X * math.cos(self.angle))
            self.rect.y += int(dt * ENEMY_FIREBALL_VELOCITY_X * math.sin(self.angle))
        return

    def animate(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > ENEMY_FIRE_ANIMATION_FRAME_TIME:
            self.last_update = now
            self.image = self.frames[self.current_frame]
            self.current_frame += 1
            if self.current_frame == ENEMY_FIRE_FRAMES_NUMBER:
                self.current_frame = 0
        return

    def pass_pause_time(self, pause_time):
        self.pause_time += pause_time
        return

    def draw(self, screen):
        screen.blit(self.image, self.rect)
        return


class Explosion:
    def __init__(self, position_rect):
        self.current_frame = 0
        self.last_update = 0
        self.load_images()
        self.image = self.frames[0]
        self.rect = self.image.get_rect()
        self.rect.x = position_rect.x + EXPLOSION_OFFSET_X
        self.rect.y = position_rect.y + EXPLOSION_OFFSET_Y
        self.kill = False
        return

    def load_images(self):
        self.frames = []
        for frame in range(EXPLOSION_FRAMES_NUMBER):
            self.frames.append(pygame.image.load(f"assets/explosion/{frame}.png"))
            self.frames[frame] = pygame.transform.scale(self.frames[frame], (EXPLOSION_WIDTH, EXPLOSION_HEIGHT))
        return

    def update(self, dx, dy):
        self.rect.x -= dx
        self.rect.y -= dy
        self.animate()
        return

    def animate(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > EXPLOSION_ANIMATION_FRAME_TIME:
            self.last_update = now
            self.image = self.frames[self.current_frame]
            self.current_frame += 1
            if self.current_frame == EXPLOSION_FRAMES_NUMBER:
                self.kill = True
        return

    def draw(self, screen):
        screen.blit(self.image, self.rect)
        return


class MiscBar:
    def __init__(self, player):
        self.current_frame = 0
        self.last_update = 0
        self.life = player.life
        self.coin = player.coins_collected
        self.world = 0
        self.lives = 0
        self.load_images()
        self.kill = False
        return

    def load_images(self):
        self.player_head_image = pygame.image.load("assets/miscbar/head/head.png")
        self.player_head_image = pygame.transform.scale(self.player_head_image, (MISCBAR_PLAYER_HEAD_WIDTH, MISCBAR_PLAYER_HEAD_HEIGHT))

        self.coin_frames = []
        for frame in range(MISCBAR_COIN_FRAMES_NUMBER):
            self.coin_frames.append(pygame.image.load(f"assets/coin/{frame}.png"))
            self.coin_frames[frame] = pygame.transform.scale(self.coin_frames[frame], (MISCBAR_COIN_WIDTH, MISCBAR_COIN_HEIGHT))
        return

    def pass_values(self, player):
        self.life = player.life
        self.coin = player.coins_collected
        self.world = player.world
        self.lives = player.lives
        return

    def update(self, dx, dy):
        # Does not have anything to update
        return

    def draw_lifebar(self, screen):
        # Lifebar Background
        lifebar_background = pygame.Surface((MISCBAR_LIFEBAR_WIDTH + LIFEBAR_GAP, MISCBAR_LIFEBAR_HEIGHT + 2 * LIFEBAR_GAP))
        lifebar_background.fill(MISCBAR_LIFEBAR_BACKGROUND_COLOR)
        screen.blit(lifebar_background, (MISCBAR_LIFEBAR_POS_X, MISCBAR_LIFEBAR_POS_Y - LIFEBAR_GAP))

        # Lifebar Foreground
        # Bar color
        RED_VALUE = int(237 * (1 - self.life / PLAYER_INITIAL_LIFE))
        GREEN_VALUE = int(41 + (255 - 41) * (self.life / PLAYER_INITIAL_LIFE))
        BLUE_VALUE = int(56 + (127 - 56) * (self.life / PLAYER_INITIAL_LIFE))
        BAR_VALUE = (RED_VALUE, GREEN_VALUE, BLUE_VALUE)

        # Colored Bar
        life_percentage = int(MISCBAR_LIFEBAR_WIDTH * (self.life / PLAYER_INITIAL_LIFE))
        lifebar_foreground = pygame.Surface((life_percentage, MISCBAR_LIFEBAR_HEIGHT))
        lifebar_foreground.fill(BAR_VALUE)
        screen.blit(lifebar_foreground, (MISCBAR_LIFEBAR_POS_X, MISCBAR_LIFEBAR_POS_Y))

        # Player's head image
        screen.blit(self.player_head_image, (MISCBAR_PLAYERS_HEAD_POS_X, MISCBAR_PLAYERS_HEAD_POS_Y))
        return

    def draw_coins_collected(self, screen):
        # Coin Image Animation
        now = pygame.time.get_ticks()
        if now - self.last_update > MISCBAR_COIN_ANIMATION_FRAME_TIME:
            self.last_update = now
            if self.current_frame != MISCBAR_COIN_FRAMES_NUMBER - 1:
                self.current_frame += 1
            else:
                self.current_frame = 0
        screen.blit(self.coin_frames[self.current_frame], (MISCBAR_COIN_POSITION_X, MISCBAR_COIN_POSITION_Y))

        # Coin Number Text
        font = pygame.font.Font(GAME_FONT, MISCBAR_COIN_NUMBER_FONT_SIZE)
        text = font.render(str(self.coin), True, MISCBAR_COIN_NUMBER_FONT_COLOR)
        screen.blit(text, (MISCBAR_COIN_NUMBER_POS_X, MISCBAR_COIN_NUMBER_POS_Y))
        return

    def draw_lives_left(self, screen):
        font = pygame.font.Font(GAME_FONT, MISCBAR_LIVES_NUMBER_FONT_SIZE)
        text = font.render(f"LIVES {str(self.lives)}", True, MISCBAR_LIVES_NUMBER_FONT_COLOR)
        screen.blit(text, (MISCBAR_LIVES_NUMBER_POS_X, MISCBAR_LIVES_NUMBER_POS_Y))
        return

    def draw_world_name(self, screen):
        font = pygame.font.Font(GAME_FONT, MISCBAR_WORLD_NUMBER_FONT_SIZE)
        text = font.render(f"WORLD {str(self.world)}", True, MISCBAR_WORLD_NUMBER_FONT_COLOR)
        screen.blit(text, (MISCBAR_WORLD_NUMBER_POS_X + 200, MISCBAR_WORLD_NUMBER_POS_Y))
        return

    def draw(self, screen):
        self.draw_coins_collected(screen)
        self.draw_lifebar(screen)
        self.draw_lives_left(screen)
        self.draw_world_name(screen)
        return
