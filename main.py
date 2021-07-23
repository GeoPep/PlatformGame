from assets import *
from pygame.locals import *
from pygame import mixer


class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.load_sounds()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), HWSURFACE | DOUBLEBUF | RESIZABLE)
        self.fake_screen = self.screen.copy()
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        self.playing = True
        self.game_app_runs = True
        self.exit = False
        self.last_loading_screen_time = pygame.time.get_ticks()
        self.player_coins = 0
        self.player_lives = INITIAL_PLAYER_LIVES
        return

    def new(self, world_number):
        # Loading screen for smoothness
        self.loading_screen()

        # Playing music
        self.world_music = mixer.Sound(WORLD_MUSIC_DIRECTORY[world_number-1])
        self.world_music.play(-1)

        # Loading world objects
        self.load_world_objects(world_number)

        # Creating Assets
        self.assets = []

        self.background = WorldBackground(self.world_number, self.WORLD_BACKGROUND)
        self.assets.append(self.background)

        self.world = World(self.world_number, self.WORLD_TILES, True, WHITE)
        self.assets.append(self.world)

        self.door = Door(*self.DOOR)
        self.assets.append(self.door)

        self.player = Player(self.world_number)
        self.assets.append(self.player)
        self.player.coins_collected = self.player_coins

        self.player_miscbar = MiscBar(self.player)
        self.assets.append(self.player_miscbar)

        self.platforms = []
        for plat in self.PLATFORM_LIST:
            platform = Platform(*plat)
            self.platforms.append(platform)
            self.assets.append(platform)

        self.coins = []
        for coin in self.COIN_LIST:
            c = Coin(*coin)
            self.coins.append(c)
            self.assets.append(c)

        self.enemies = []
        for enemy_pos in self.ENEMY_LIST:
            enemy = Enemy(*enemy_pos)
            self.assets.append(enemy)
            self.enemies.append(enemy)

        # Empty list for fireballs storage
        self.fireballs = []
        self.fireball_trigger_time = pygame.time.get_ticks()

        # Empty list for enemy fire storage
        self.enemy_fire = []

        # Empty list for explosion objects
        self.explosions = []

        self.run()
        passed = False
        if self.door.opened:
            passed = True
            self.player_coins = self.player.coins_collected

        self.last_loading_screen_time = pygame.time.get_ticks()
        self.world_music.stop()
        return passed

    def load_world_objects(self, world_number):
        self.world_number = world_number
        self.WORLD_TILES = WORLD_TILES_DIRECTORY[self.world_number-1]
        self.WORLD_BACKGROUND = WORLD_BACKGROUND_DIRECTORY[self.world_number-1]
        self.PLATFORM_LIST = WORLD_PLATFORM_LIST_DIRECTORY[self.world_number-1]
        self.COIN_LIST = WORLD_COIN_LIST_DIRECTORY[self.world_number-1]
        self.ENEMY_LIST = WORLD_ENEMY_LIST_DIRECTORY[self.world_number-1]
        self.DOOR = WORLD_DOOR_DIRECTORY[self.world_number-1]
        self.WORLD_WIDTH = WORLD_WIDTH_DIRECTORY[self.world_number-1]
        self.WORLD_HEIGHT = WORLD_HEIGHT_DIRECTORY[self.world_number-1]
        return

    def run(self):
        # Game Loop
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()

            if self.player.life <= 0 or self.door.opened:
                self.playing = False
        return

    def events(self):
        # Game Loop - events
        for event in pygame.event.get():
            # check for closing window
            if event.type == pygame.QUIT:
                if self.playing:
                    self.exit = True
                    self.playing = False
                self.running = False
                self.game_app_runs = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.player.jump()
                    if self.player.can_jump:
                        self.jump_sound.play()
                if event.key == pygame.K_RETURN:
                    now = pygame.time.get_ticks()
                    if now - self.fireball_trigger_time > FIREBALL_SPAWN_TIME_INTERVAL:
                        self.fireball_trigger_time = now
                        fireball = Fireball(self.player.rect, self.player.direction_right)
                        self.assets.append(fireball)
                        self.fireballs.append(fireball)
                        self.fire_sound.play()
                if event.key == pygame.K_ESCAPE:
                    self.pause_time = pygame.time.get_ticks()
                    self.pause()
            if event.type == VIDEORESIZE:
                self.screen = pygame.display.set_mode(event.size, HWSURFACE | DOUBLEBUF | RESIZABLE)
        return

    def pause(self):
        self.paused = True
        self.pause_sound.play()
        self.world_music.stop()
        while self.paused:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    if self.playing:
                        self.exit = True
                        self.playing = False
                        self.game_app_runs = False
                    self.running = False
                    self.paused = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.pause_sound.play()
                        self.world_music.play(-1)
                        self.paused = False
                        self.pause_time = pygame.time.get_ticks() - self.pause_time
                        self.player.pass_pause_time(self.pause_time)
                        for fireball in self.fireballs:
                            fireball.pass_pause_time(self.pause_time)
                        for fire in self.enemy_fire:
                            fire.pass_pause_time(self.pause_time)
                        for enemy in self.enemies:
                            enemy.pass_pause_time(self.pause_time)
            # Pause text
            font = pygame.font.Font(GAME_FONT, PAUSE_TITLE_SIZE)
            text = font.render(PAUSE_TITLE_TITLE, True, PAUSE_TITLE_COLOR)
            self.screen.blit(text, (PAUSE_TITLE_POS_X, PAUSE_TITLE_POS_Y))
            pygame.display.flip()
        return

    def update(self):
        # Camera Movement
        self.scrolling_camera()
        # Game Loop - Update
        for asset in self.assets:
            asset.update(self.dx, self.dy)
        # Enemies fire management:
        for enemy in self.enemies:
            if enemy.active():
                if enemy.generate_fire():
                    # creates enemy fire object
                    enemy_fire = Enemy_Fireball(enemy.rect.centerx, enemy.rect.centery, self.player.rect.centerx, self.player.rect.centery)
                    self.enemy_fire.append(enemy_fire)
                    self.assets.append(enemy_fire)
                    self.fire_sound.play()
        # Collision detection
        self.collision_manager()
        # Delete dead objects
        self.objects_kill_manager()
        # Pass values to Assets
        self.player.world = self.world_number
        self.player.lives = self.player_lives
        self.player_miscbar.pass_values(self.player)
        for enemy in self.enemies:
            enemy.pass_values(self.player.rect.x, self.player.rect.y)
        return

    def scrolling_camera(self):
        self.dx = 0
        self.dy = 0

        # Moving Right
        if self.player.rect.x + PLAYER_WIDTH > WIDTH - CAMERA_SCROLL_GAP_X:
            if self.player.abs_pos_x + PLAYER_WIDTH < self.WORLD_WIDTH - CAMERA_SCROLL_GAP_X:
                self.dx = self.player.rect.x + PLAYER_WIDTH - (WIDTH - CAMERA_SCROLL_GAP_X)
            else:
                if self.player.abs_pos_x + PLAYER_WIDTH >= self.WORLD_WIDTH:
                    self.player.rect.x = WIDTH - PLAYER_WIDTH
                    self.player.abs_pos_x = self.WORLD_WIDTH - PLAYER_WIDTH

        # Moving Left
        if self.player.rect.x < CAMERA_SCROLL_GAP_X:
            if self.player.abs_pos_x > CAMERA_SCROLL_GAP_X:
                self.dx = self.player.rect.x - CAMERA_SCROLL_GAP_X
            else:
                if self.player.rect.x < 0:
                    self.player.rect.x = 0
                    self.player.abs_pos_x = 0

        # Moving Up
        if self.player.rect.y < CAMERA_SCROLL_GAP_Y:
            self.dy = self.player.rect.y - CAMERA_SCROLL_GAP_Y

        # Moving Down
        if self.player.rect.y + PLAYER_HEIGHT > HEIGHT - CAMERA_SCROLL_GAP_Y:
            if self.player.abs_pos_y + PLAYER_HEIGHT < self.WORLD_HEIGHT - CAMERA_SCROLL_GAP_Y:
                self.dy = self.player.rect.y + PLAYER_HEIGHT - (HEIGHT - CAMERA_SCROLL_GAP_Y)
        return

    def collision_manager(self):
        # Collisions between player and platforms
        self.player.can_jump = False
        gap = COLLISION_GAP
        for platform in self.platforms:
            if self.player.rect.colliderect(platform.rect):
                if platform.rect.left + gap < self.player.rect.right and platform.rect.right - gap > self.player.rect.left:
                    if self.player.vel_y > 0:
                        self.player.vel_y = 0
                        self.player.rect.y = platform.rect.top - PLAYER_HEIGHT + 1
                        if self.player.jumping:
                            splash = Splash(self.player.rect)
                            self.assets.append(splash)
                        self.player.jumping = False
                        self.player.can_jump = True
                    elif self.player.vel_y < 0:
                        self.player.vel_y = 0
                        self.player.rect.y = platform.rect.bottom
                else:
                    if self.player.vel_x > 0:
                        self.player.vel_x = 0
                        if self.player.rect.right > platform.rect.right:
                            self.player.rect.x = platform.rect.right
                        else:
                            self.player.rect.x = platform.rect.left - PLAYER_WIDTH
                    elif self.player.vel_x < 0:
                        self.player.vel_x = 0
                        if self.player.rect.right > platform.rect.right:
                            self.player.rect.x = platform.rect.right
                        else:
                            self.player.rect.x = platform.rect.left - PLAYER_WIDTH

        # Collisions between player and coins
        for coin in self.coins:
            if self.player.rect.colliderect(coin.rect):
                coin.kill = True
                self.coins.remove(coin)
                self.player.coins_collected += 1
                self.coin_sound.play()

        # Collisions between player and door
        if self.player.rect.colliderect(self.door.rect):
            self.door.check_if_door_is_open()

        # Collisions between fireballs and platforms
        for fireball in self.fireballs:
            for platform in self.platforms:
                if fireball.rect.colliderect(platform):
                    fireball.kill = True

        # collision between fireballs and enemies:
        for fireball in self.fireballs:
            for enemy in self.enemies:
                if enemy.active():
                    if fireball.rect.colliderect(enemy):
                        fireball.kill = True
                        enemy.damage()
                        self.hit_sound.play()
                        if enemy.life <= 0:
                            enemy.kill = True

        # collision between player and enemies:
        for enemy in self.enemies:
            if self.player.rect.colliderect(enemy.rect):
                if self.player.rect.x <= enemy.rect.centerx:
                    self.player.rect.x -= PLAYER_COLLISION_WITH_ENEMY_REPOSITION_OFFSET
                    self.player.abs_pos_x -= PLAYER_COLLISION_WITH_ENEMY_REPOSITION_OFFSET
                else:
                    self.player.rect.x += PLAYER_COLLISION_WITH_ENEMY_REPOSITION_OFFSET
                    self.player.abs_pos_x += PLAYER_COLLISION_WITH_ENEMY_REPOSITION_OFFSET
                self.player.life -= PLAYER_HIT_BY_ENEMY_DAMAGE
                self.hit_sound.play()

        # collision between player and enemy fire:
        for fire in self.enemy_fire:
            if self.player.rect.colliderect(fire.rect):
                self.player.life -= PLAYER_HIT_BY_ENEMY_DAMAGE
                fire.kill = True
                self.hit_sound.play()

        # collision between player's fireballs and enemy's fire
        for fire in self.enemy_fire:
            for fireball in self.fireballs:
                if fire.rect.colliderect(fireball.rect):
                    fire.kill = True
                    fireball.kill = True
                    explosion = Explosion(fireball.rect)
                    self.explosions.append(explosion)
                    self.assets.append(explosion)
                    self.explosion_sound.play()

        # Checks if player has fallen out of the world
        if self.player.abs_pos_y > self.WORLD_HEIGHT + 1:
            self.player.life = 0
        return

    def objects_kill_manager(self):
        for asset in self.assets:
            if asset.kill:
                self.assets.remove(asset)
        for fireball in self.fireballs:
            if fireball.kill:
                self.fireballs.remove(fireball)
        for enemy in self.enemies:
            if enemy.kill:
                self.enemies.remove(enemy)
        for fire in self.enemy_fire:
            if fire.kill:
                self.enemy_fire.remove(fire)
        return

    def draw(self):
        # Game Loop - Draw
        # Draw / render
        for asset in self.assets:
            asset.draw(self.fake_screen)
        self.screen.blit(pygame.transform.scale(self.fake_screen, self.screen.get_rect().size), (0, 0))
        # *after* drawing everything, flip the display
        pygame.display.flip()
        return

    def start_screen(self):
        self.menu_sound.play(-1)
        waiting = True
        selected_option = 0
        while waiting:
            image = pygame.image.load(MENU_BACKGROUND)
            self.fake_screen.blit(image, (0, 0))
            # Menu Text
            font = pygame.font.Font(GAME_FONT, MENU_TITLE_SIZE)
            text = font.render(MENU_TITLE_TITLE, True, MENU_TITLE_COLOR)
            self.fake_screen.blit(text, (MENU_TITLE_POS_X, MENU_TITLE_POS_Y))
            font = pygame.font.Font(GAME_FONT, MENU_PLAY_SIZE)
            if selected_option == 0:
                text = font.render(MENU_PLAY_TITLE, True, MENU_SELECT_COLOR)
            else:
                text = font.render(MENU_PLAY_TITLE, True, MENU_PLAY_COLOR)
            self.fake_screen.blit(text, (MENU_PLAY_POS_X, MENU_PLAY_POS_Y))
            font = pygame.font.Font(GAME_FONT, MENU_EXIT_SIZE)
            if selected_option == 1:
                text = font.render(MENU_EXIT_TITLE, True, MENU_SELECT_COLOR)
            else:
                text = font.render(MENU_EXIT_TITLE, True, MENU_EXIT_COLOR)
            self.fake_screen.blit(text, (MENU_EXIT_POS_X, MENU_EXIT_POS_Y))
            # Menu Animation
            self.screen.blit(pygame.transform.scale(self.fake_screen, self.screen.get_rect().size), (0, 0))
            pygame.display.flip()
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                    self.running = False
                    self.playing = False
                    self.exit = True
                    self.game_app_runs = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN or event.key == pygame.K_UP:
                        self.option_sound.play()
                        if selected_option == 0:
                            selected_option = 1
                        else:
                            selected_option = 0
                    if event.key == pygame.K_RETURN:
                        self.select_sound.play()
                        if selected_option == 0:
                            waiting = False
                            self.menu_sound.stop()
                        else:
                            waiting = False
                            self.exit = True
                            self.running = False
                            self.playing = False
                            self.game_app_runs = False
        return

    def game_over_screen(self):
        now = pygame.time.get_ticks()
        self.last_game_over_screen_time = now
        while now - self.last_game_over_screen_time < GAME_OVER_SCREEN_WAITING_TIME:
            self.fake_screen.fill(BLACK)
            font = pygame.font.Font(GAME_FONT, GAME_OVER_TITLE_SIZE)
            text = font.render(GAME_OVER_TITLE, True, GAME_OVER_COLOR)
            self.fake_screen.blit(text, (GAME_OVER_POS_X, GAME_OVER_POS_Y))
            self.screen.blit(pygame.transform.scale(self.fake_screen, self.screen.get_rect().size), (0, 0))
            pygame.display.flip()
            self.clock.tick(FPS)
            now = pygame.time.get_ticks()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    self.playing = False
                    self.exit = True
                    self.game_app_runs = False
                    now = self.last_game_over_screen_time + GAME_OVER_SCREEN_WAITING_TIME
        return

    def game_completed_screen(self):
        now = pygame.time.get_ticks()
        self.last_game_completed_screen_time = now
        while now - self.last_game_completed_screen_time < GAME_COMPLETED_SCREEN_WAITING_TIME:
            self.fake_screen.fill(BLACK)
            font = pygame.font.Font(GAME_FONT, GAME_COMPLETED_TITLE_SIZE)
            text = font.render(GAME_COMPLETED_TITLE, True, GAME_COMPLETED_COLOR)
            self.fake_screen.blit(text, (GAME_COMPLETED_POS_X, GAME_COMPLETED_POS_Y))
            self.screen.blit(pygame.transform.scale(self.fake_screen, self.screen.get_rect().size), (0, 0))
            pygame.display.flip()
            self.clock.tick(FPS)
            now = pygame.time.get_ticks()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    self.playing = False
                    self.exit = True
                    self.game_app_runs = False
                    now = self.last_game_completed_screen_time + GAME_COMPLETED_SCREEN_WAITING_TIME
        return

    def loading_screen(self):
        now = pygame.time.get_ticks()
        self.last_loading_screen_time = now
        while now - self.last_loading_screen_time < LOADING_SCREEN_WAITING_TIME:
            self.fake_screen.fill(BLACK)
            font = pygame.font.Font(GAME_FONT, LOADING_TITLE_SIZE)
            text = font.render(LOADING_TITLE, True, LOADING_COLOR)
            self.fake_screen.blit(text, (LOADING_POS_X, LOADING_POS_Y))
            self.screen.blit(pygame.transform.scale(self.fake_screen, self.screen.get_rect().size), (0, 0))
            pygame.display.flip()
            self.clock.tick(FPS)
            now = pygame.time.get_ticks()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    self.playing = False
                    self.exit = True
                    self.game_app_runs = False
                    now = self.last_loading_screen_time + LOADING_SCREEN_WAITING_TIME
        return

    def load_sounds(self):
        self.menu_sound = mixer.Sound(MENU_SOUND)
        self.option_sound = mixer.Sound(OPTION_SOUND)
        self.select_sound = mixer.Sound(SELECT_SOUND)
        self.jump_sound = mixer.Sound(JUMP_SOUND)
        self.explosion_sound = mixer.Sound(EXPLOSION_SOUND)
        self.pause_sound = mixer.Sound(PAUSE_SOUND)
        self.fire_sound = mixer.Sound(FIRE_SOUND)
        self.hit_sound = mixer.Sound(HIT_SOUND)
        self.coin_sound = mixer.Sound(COIN_SOUND)
        return


def main(game):
    while game.game_app_runs:
        game.start_screen()
        # Initializing Global Variables
        world = 1
        game.player_lives = INITIAL_PLAYER_LIVES
        game.player_coins = 0
        if not game.exit:
            game.playing = True
            game.running = True
        while game.running:
            while game.new(world):
                if game.door.opened:
                    if world < NUMBER_OF_WORLDS:
                        world += 1
                        game.playing = True
                    else:
                        game.game_completed_screen()
                        game.running = False
                        game.playing = False
            if game.player.life <= 0:
                game.playing = True
                game.player_lives -= 1
            if game.player_lives < 0:
                game.game_over_screen()
                game.running = False
                game.playing = False
    pygame.quit()
    return


game = Game()
main(game)
