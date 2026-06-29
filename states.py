import pygame
import random
from config import WIDTH, HEIGHT, BLACK, YELLOW, GREEN, WHITE, RED, CYAN, PURPLE, BLUE, lane_pos, clock, engine_sound, play_transition_sound, draw_text_centered
from sprites import Background, Road, Player, Tree, Obstacle, Fuel, Booster, Explosion

class GameState:
    def handle_events(self, events):
        pass

    def update(self):
        pass

    def draw(self, screen):
        pass


class MenuScreen(GameState):
    def __init__(self, selected_car=1):
        self.selected_option = 0
        self.options = ["Start Game", "Select Car", "Exit"]
        self.selected_car = selected_car

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected_option = (self.selected_option - 1) % len(self.options)
                elif event.key == pygame.K_DOWN:
                    self.selected_option = (self.selected_option + 1) % len(self.options)
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    play_transition_sound()
                    if self.selected_option == 0:
                        return GameScreen(self.selected_car)
                    elif self.selected_option == 1:
                        return CarSelectionScreen(self.selected_car)
                    elif self.selected_option == 2:
                        return ExitScreen()
        return self

    def update(self):
        pass

    def draw(self, screen):
        screen.fill(BLACK)
        draw_text_centered(screen, "CAR RACING GAME", 30, YELLOW, 140)
        for i, option in enumerate(self.options):
            color = GREEN if i == self.selected_option else WHITE
            y_pos = 250 + i * 50
            draw_text_centered(screen, option, 32, color, y_pos)
        try:
            preview_car = pygame.image.load(f'Assets/cars/{self.selected_car}.png')
            preview_car = pygame.transform.scale(preview_car, (72, 120))
            screen.blit(preview_car, (WIDTH - 100, HEIGHT - 170))
            font = pygame.font.SysFont('Arial', 12)
            selected_text = font.render(f"Car {self.selected_car}", True, GREEN)
            text_x = WIDTH - 100 + 36 - selected_text.get_width() // 2
            text_y = HEIGHT - 170 + 125
            screen.blit(selected_text, (text_x, text_y))
        except:
            pass
        draw_text_centered(screen, "Use ARROW KEYS to navigate", 16, WHITE, HEIGHT - 50)
        draw_text_centered(screen, "Press ENTER to select", 16, WHITE, HEIGHT - 30)


class CarSelectionScreen(GameState):
    def __init__(self, current_car=1):
        self.current_car = current_car
        self.selected_car = current_car

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.selected_car = self.selected_car - 1
                    if self.selected_car < 1:
                        self.selected_car = 8
                elif event.key == pygame.K_RIGHT:
                    self.selected_car = self.selected_car + 1
                    if self.selected_car > 8:
                        self.selected_car = 1
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    play_transition_sound()
                    return MenuScreen(self.selected_car)
                elif event.key == pygame.K_ESCAPE:
                    play_transition_sound()
                    return MenuScreen(self.current_car)
        return self

    def update(self):
        pass

    def draw(self, screen):
        screen.fill(BLACK)
        draw_text_centered(screen, "SELECT YOUR CAR", 30, YELLOW, 80)
        try:
            car_image = pygame.image.load(f'Assets/cars/{self.selected_car}.png')
            car_image = pygame.transform.scale(car_image, (120, 200))
            car_x = WIDTH // 2 - 60
            car_y = HEIGHT // 2 - 120
            screen.blit(car_image, (car_x, car_y))
        except:
            pass
        draw_text_centered(screen, f"CAR {self.selected_car}/8", 28, WHITE, HEIGHT // 2 + 80)
        draw_text_centered(screen, "<     >", 28, YELLOW, HEIGHT // 2 + 115)
        draw_text_centered(screen, "Press ENTER to confirm", 20, GREEN, HEIGHT - 70)
        draw_text_centered(screen, "Press ESC to go back", 20, RED, HEIGHT - 45)


class GameScreen(GameState):
    def __init__(self, car_type):
        self.car_type = car_type
        self.move_left = False
        self.move_right = False
        self.base_speed = 100
        self.current_speed = 100
        self.spawn_timer = 0
        self.distance = 0
        self.fuel = 100
        self.fuel_spawn_timer = 0
        self.game_over = False
        self.engine_playing = False
        self.engine_channel = None
        self.explosion = None  # Анимация взрыва

        self.slow_motion = False
        self.slow_motion_timer = 0
        self.original_speed_multiplier = 1.0
        self.active_effects = []

        try:
            with open('highscore.txt', 'r') as f:
                self.high_score = int(f.read())
        except:
            self.high_score = 0

        self.background = Background()
        self.road = Road()
        self.player = Player(100, HEIGHT - 120, car_type)

        self.tree_group = pygame.sprite.Group()
        self.obstacle_group = pygame.sprite.Group()
        self.fuel_group = pygame.sprite.Group()
        self.booster_group = pygame.sprite.Group()

        self.FUEL_SPAWN_DELAY = 8
        self.BOOSTER_SPAWN_DELAY = 12
        self.booster_spawn_timer = 0
        self.MAX_SPEED = 350
        self.ACCELERATION = 0.04

    def save_record(self):
        if int(self.distance) > self.high_score:
            self.high_score = int(self.distance)
            with open('highscore.txt', 'w') as f:
                f.write(str(self.high_score))

    def apply_booster_effect(self, booster_type):
        if booster_type == 1:
            self.slow_motion = True
            self.slow_motion_timer = 5.0
            self.active_effects.append({"type": "Slow Motion", "timer": 5.0, "color": CYAN})
        elif booster_type == 2:
            self.player.invincible = True
            self.player.invincible_timer = 5.0
            self.active_effects.append({"type": "Invincible", "timer": 5.0, "color": PURPLE})

    def start_engine_sound(self):
        if engine_sound and not self.engine_playing and not self.game_over:
            self.engine_channel = pygame.mixer.find_channel()
            if self.engine_channel:
                self.engine_channel.play(engine_sound, loops=-1)
                self.engine_playing = True

    def stop_engine_sound(self):
        if self.engine_channel and self.engine_playing:
            self.engine_channel.stop()
            self.engine_playing = False
            self.engine_channel = None

    def update_engine_volume(self):
        if self.engine_channel and self.engine_playing:
            volume = 0.1 + (self.current_speed / self.MAX_SPEED) * 0.4
            self.engine_channel.set_volume(min(0.5, volume))

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if self.game_over:
                    if event.key == pygame.K_r:
                        play_transition_sound()
                        self.stop_engine_sound()
                        return GameScreen(self.car_type)
                    elif event.key == pygame.K_ESCAPE:
                        play_transition_sound()
                        self.stop_engine_sound()
                        return MenuScreen(self.car_type)
                else:
                    if event.key == pygame.K_ESCAPE:
                        play_transition_sound()
                        self.stop_engine_sound()
                        return PauseScreen(self)
                    if event.key == pygame.K_LEFT:
                        self.move_left = True
                    if event.key == pygame.K_RIGHT:
                        self.move_right = True
                    if event.key == pygame.K_r:
                        play_transition_sound()
                        self.stop_engine_sound()
                        return GameScreen(self.car_type)
            if event.type == pygame.KEYUP and not self.game_over:
                if event.key == pygame.K_LEFT:
                    self.move_left = False
                if event.key == pygame.K_RIGHT:
                    self.move_right = False
        return self

    def update(self):
        dt = clock.get_time() / 1000.0
        if dt > 0.05:
            dt = 0.05

        if self.explosion:
            self.explosion.update(dt)
            if self.explosion.is_finished():
                self.game_over = True
                self.explosion = None
                self.stop_engine_sound()
                self.save_record()
            return self

        if not self.game_over:
            self.start_engine_sound()
            self.update_engine_volume()

            speed_multiplier = 1.0
            if self.slow_motion:
                self.slow_motion_timer -= dt
                speed_multiplier = 0.5
                if self.slow_motion_timer <= 0:
                    self.slow_motion = False

            for effect in self.active_effects[:]:
                effect["timer"] -= dt
                if effect["timer"] <= 0:
                    self.active_effects.remove(effect)

            if self.current_speed < self.MAX_SPEED:
                self.current_speed += self.ACCELERATION * 60 * dt * speed_multiplier

            self.fuel -= 2 * (1 + (self.current_speed - self.base_speed) / 250) * dt * speed_multiplier
            if self.fuel <= 0:
                self.game_over = True
                self.stop_engine_sound()
                self.save_record()

            self.distance += self.current_speed * dt / 10

            self.background.update(self.current_speed * speed_multiplier, dt)
            self.road.update(self.current_speed * speed_multiplier, dt)

            self.spawn_timer += dt
            if self.spawn_timer >= 1.0:
                self.spawn_timer = 0
                tree = Tree(random.choice([-5, WIDTH - 35]), -20)
                self.tree_group.add(tree)

            if self.fuel_spawn_timer > 0:
                self.fuel_spawn_timer -= dt
            if self.fuel_spawn_timer <= 0 and len(self.fuel_group) < 2:
                self.fuel_spawn_timer = self.FUEL_SPAWN_DELAY
                fuel_x = random.randint(50, 200)
                new_fuel = Fuel(fuel_x, -50)
                self.fuel_group.add(new_fuel)

            if self.booster_spawn_timer > 0:
                self.booster_spawn_timer -= dt
            if self.booster_spawn_timer <= 0 and len(self.booster_group) < 3:
                self.booster_spawn_timer = self.BOOSTER_SPAWN_DELAY
                booster_x = random.choice(lane_pos) + 5
                booster_type = random.choice([1, 2])
                new_booster = Booster(booster_x, -50, booster_type)
                self.booster_group.add(new_booster)

            spawn_delay = max(0.8, 2.0 - (self.current_speed - self.base_speed) / 600)
            if random.random() < dt / spawn_delay:
                obs = random.choices([1, 2, 3], weights=[6, 2, 2], k=1)[0]
                obstacle = Obstacle(obs)
                self.obstacle_group.add(obstacle)

            self.obstacle_group.update(self.current_speed * speed_multiplier, dt)
            self.tree_group.update(self.current_speed * speed_multiplier, dt)
            self.fuel_group.update(self.current_speed * speed_multiplier, dt)
            self.booster_group.update(self.current_speed * speed_multiplier, dt)

            for obstacle in self.obstacle_group:
                if pygame.sprite.collide_mask(self.player, obstacle):
                    if not self.player.invincible:
                        self.explosion = Explosion(self.player.rect.centerx, self.player.rect.centery)
                        self.stop_engine_sound()
                        break
                    else:
                        obstacle.kill()
                        break

            collected_fuel = pygame.sprite.spritecollide(self.player, self.fuel_group, True)
            for fuel_item in collected_fuel:
                self.fuel += 40
                if self.fuel > 100:
                    self.fuel = 100

            collected_boosters = pygame.sprite.spritecollide(self.player, self.booster_group, True)
            for booster in collected_boosters:
                self.apply_booster_effect(booster.type)

            self.player.update(self.move_left, self.move_right, dt)

        return self

    def draw(self, screen):
        if not self.game_over:
            self.background.draw(screen)
            self.road.draw(screen)
            self.obstacle_group.draw(screen)
            self.tree_group.draw(screen)
            self.fuel_group.draw(screen)
            self.booster_group.draw(screen)
            self.player.draw(screen)

            if self.explosion:
                self.explosion.draw(screen)

            font = pygame.font.SysFont('Arial', 20)
            distance_text = font.render(f'Distance: {int(self.distance)}m', True, WHITE)
            if self.slow_motion:
                speed_color = CYAN
                speed_text = font.render(f'Speed: {int(self.current_speed / self.base_speed * 100)} (SLOW)', True, speed_color)
            else:
                speed_text = font.render(f'Speed: {int(self.current_speed / self.base_speed * 100)}', True, YELLOW)
            high_score_text = font.render(f'Best: {self.high_score}m', True, WHITE)
            fuel_text = font.render(f'Fuel: {int(self.fuel)}%', True, GREEN)

            screen.blit(distance_text, (10, 10))
            screen.blit(speed_text, (10, 35))
            screen.blit(high_score_text, (10, 60))
            screen.blit(fuel_text, (10, 85))

            fuel_bar_width = int((self.fuel / 100) * 100)
            pygame.draw.rect(screen, RED, (10, 105, 100, 12))
            pygame.draw.rect(screen, GREEN, (10, 105, fuel_bar_width, 12))
            pygame.draw.rect(screen, WHITE, (10, 105, 100, 12), 2)

            y_offset = 125
            for effect in self.active_effects:
                effect_text = font.render(f'{effect["type"]}: {int(effect["timer"])}s', True, effect["color"])
                screen.blit(effect_text, (10, y_offset))
                y_offset += 25

            if self.player.invincible:
                pygame.draw.rect(screen, PURPLE, (0, 0, WIDTH, HEIGHT), 5)
            pygame.draw.rect(screen, BLUE, (0, 0, WIDTH, HEIGHT), 3)
        else:
            screen.fill(BLACK)
            title_font = pygame.font.SysFont('Arial', 48, bold=True)
            title_text = title_font.render("GAME OVER", True, RED)
            screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 100))
            data_font = pygame.font.SysFont('Arial', 24)
            dist_text = data_font.render(f"Distance: {int(self.distance)} m", True, WHITE)
            screen.blit(dist_text, (WIDTH // 2 - dist_text.get_width() // 2, 200))
            record_text = data_font.render(f"Best: {self.high_score} m", True, YELLOW)
            screen.blit(record_text, (WIDTH // 2 - record_text.get_width() // 2, 250))
            hint_font = pygame.font.SysFont('Arial', 20)
            hint_text = hint_font.render("Press R to restart", True, GREEN)
            screen.blit(hint_text, (WIDTH // 2 - hint_text.get_width() // 2, 320))
            hint_text2 = hint_font.render("Press ESC for menu", True, WHITE)
            screen.blit(hint_text2, (WIDTH // 2 - hint_text2.get_width() // 2, 380))


class PauseScreen(GameState):
    def __init__(self, game_screen):
        self.game_screen = game_screen
        self.selected_option = 0
        self.options = ["Resume", "Restart", "Menu"]

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    play_transition_sound()
                    self.game_screen.start_engine_sound()
                    return self.game_screen
                elif event.key == pygame.K_UP:
                    self.selected_option = (self.selected_option - 1) % len(self.options)
                elif event.key == pygame.K_DOWN:
                    self.selected_option = (self.selected_option + 1) % len(self.options)
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    play_transition_sound()
                    if self.selected_option == 0:
                        self.game_screen.start_engine_sound()
                        return self.game_screen
                    elif self.selected_option == 1:
                        self.game_screen.stop_engine_sound()
                        return GameScreen(self.game_screen.car_type)
                    elif self.selected_option == 2:
                        self.game_screen.stop_engine_sound()
                        return MenuScreen(self.game_screen.car_type)
        return self

    def update(self):
        pass

    def draw(self, screen):
        self.game_screen.draw(screen)
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        draw_text_centered(screen, "PAUSED", 48, YELLOW, 150)
        for i, option in enumerate(self.options):
            color = GREEN if i == self.selected_option else WHITE
            y_pos = 280 + i * 50
            draw_text_centered(screen, option, 32, color, y_pos)


class ExitScreen(GameState):
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_y or event.key == pygame.K_RETURN:
                    play_transition_sound()
                    pygame.time.wait(200)
                    pygame.quit()
                    exit()
                elif event.key == pygame.K_n or event.key == pygame.K_ESCAPE:
                    play_transition_sound()
                    return MenuScreen()
        return self

    def update(self):
        pass

    def draw(self, screen):
        screen.fill(BLACK)
        draw_text_centered(screen, "ARE YOU SURE?", 35, YELLOW, 150)
        draw_text_centered(screen, "Press Y to exit", 28, WHITE, 250)
        draw_text_centered(screen, "Press N to return", 28, WHITE, 210)