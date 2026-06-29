import math
import pygame
import random
from config import WIDTH, GREEN, HEIGHT, lane_pos, GRASS_GREEN, DARK_GREEN, RED, ORANGE, CYAN, BLUE, WHITE, PURPLE, YELLOW

class Background:
    def __init__(self):
        try:
            self.image = pygame.image.load('Assets/bg.png')
        except:
            self.image = pygame.Surface((WIDTH, HEIGHT))
            self.image.fill(GRASS_GREEN)
        self.y1 = 0
        self.y2 = -HEIGHT

    def update(self, speed, dt):
        movement = speed * dt
        self.y1 += movement
        self.y2 += movement
        if self.y1 >= HEIGHT:
            self.y1 = -HEIGHT
        if self.y2 >= HEIGHT:
            self.y2 = -HEIGHT

    def draw(self, win):
        win.blit(self.image, (0, self.y1))
        win.blit(self.image, (0, self.y2))


class Road:
    def __init__(self):
        try:
            self.image = pygame.image.load('Assets/road.png')
            self.image = pygame.transform.scale(self.image, (WIDTH - 60, HEIGHT))
        except:
            self.image = pygame.Surface((WIDTH - 60, HEIGHT))
            self.image.fill((50, 50, 50))
        self.x = 30
        self.y1 = 0
        self.y2 = -HEIGHT
        self.y3 = -HEIGHT * 2

    def update(self, speed, dt):
        movement = speed * dt
        self.y1 += movement
        self.y2 += movement
        self.y3 += movement
        if self.y1 >= HEIGHT:
            self.y1 = self.y3 - HEIGHT
        if self.y2 >= HEIGHT:
            self.y2 = self.y1 - HEIGHT
        if self.y3 >= HEIGHT:
            self.y3 = self.y2 - HEIGHT

    def draw(self, win):
        win.blit(self.image, (self.x, self.y1))
        win.blit(self.image, (self.x, self.y2))
        win.blit(self.image, (self.x, self.y3))


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, car_type):
        super(Player, self).__init__()
        self.car_type = car_type
        self.original_image = pygame.image.load(f'Assets/cars/{car_type}.png')
        self.original_image = pygame.transform.scale(self.original_image, (48, 82))
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 250
        self.invincible = False
        self.invincible_timer = 0
        self.invincible_flash = 0

    def update(self, left, right, dt):
        if left and self.rect.x > 40:
            self.rect.x -= self.speed * dt
        if right and self.rect.right < 250:
            self.rect.x += self.speed * dt

        if self.invincible:
            self.invincible_timer -= dt
            if self.invincible_timer <= 0:
                self.invincible = False
            self.invincible_flash += 60 * dt
            if int(self.invincible_flash) % 6 < 3:
                self.image.set_alpha(128)
            else:
                self.image.set_alpha(255)
        else:
            self.image.set_alpha(255)

        self.mask = pygame.mask.from_surface(self.image)

    def draw(self, win):
        win.blit(self.image, self.rect)


class Tree(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super(Tree, self).__init__()
        tree_type = random.randint(1, 4)
        try:
            self.image = pygame.image.load(f'Assets/trees/{tree_type}.png')
        except:
            self.image = pygame.Surface((30, 30))
            self.image.fill(DARK_GREEN)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self, speed, dt):
        self.rect.y += speed * dt
        if self.rect.y > HEIGHT:
            self.kill()


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, obs_type):
        super(Obstacle, self).__init__()
        self.type = obs_type
        dx = 0
        if obs_type == 1:
            ctype = random.randint(1, 8)
            try:
                self.image = pygame.image.load(f'Assets/cars/{ctype}.png')
                self.image = pygame.transform.flip(self.image, False, True)
                self.image = pygame.transform.scale(self.image, (48, 82))
            except:
                self.image = pygame.Surface((48, 82))
                self.image.fill(RED)
        elif obs_type == 2:
            try:
                self.image = pygame.image.load('Assets/barrel.png')
                self.image = pygame.transform.scale(self.image, (24, 36))
            except:
                self.image = pygame.Surface((24, 36))
                self.image.fill(ORANGE)
            dx = 10
        else:
            try:
                self.image = pygame.image.load('Assets/roadblock.png')
                self.image = pygame.transform.scale(self.image, (50, 25))
            except:
                self.image = pygame.Surface((50, 25))
                self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = random.choice(lane_pos) + dx
        self.rect.y = -100

    def update(self, speed, dt):
        self.rect.y += speed * dt
        if self.rect.y > HEIGHT:
            self.kill()
        self.mask = pygame.mask.from_surface(self.image)


class Fuel(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super(Fuel, self).__init__()
        try:
            self.image = pygame.image.load('Assets/fuel.png')
            self.image = pygame.transform.scale(self.image, (35, 35))
        except:
            self.image = pygame.Surface((35, 35))
            self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.animation_counter = 0
        self.direction = random.choice([-1, 1])
        self.move_speed = random.uniform(50, 100)

    def update(self, speed, dt):
        self.rect.y += speed * dt
        self.animation_counter += 60 * dt
        self.rect.x += self.direction * self.move_speed * dt
        if self.rect.x <= 45:
            self.rect.x = 45
            self.direction = 1
        if self.rect.x >= 205:
            self.rect.x = 205
            self.direction = -1
        self.rect.x += math.sin(self.animation_counter * 0.2) * 0.5 * (60 * dt)
        if self.rect.y > HEIGHT:
            self.kill()


class Booster(pygame.sprite.Sprite):
    def __init__(self, x, y, booster_type):
        super(Booster, self).__init__()
        self.type = booster_type
        if booster_type == 1:
            try:
                self.image = pygame.image.load('Assets/Скорость.png')
                self.image = pygame.transform.scale(self.image, (35, 35))
            except:
                self.image = pygame.Surface((35, 35))
                self.image.fill(CYAN)
                pygame.draw.circle(self.image, BLUE, (17, 17), 14)
                pygame.draw.circle(self.image, WHITE, (17, 17), 10)
                font = pygame.font.SysFont('Arial', 18, bold=True)
                text = font.render("S", True, WHITE)
                self.image.blit(text, (12, 8))
        else:
            try:
                self.image = pygame.image.load('Assets/shield.png')
                self.image = pygame.transform.scale(self.image, (35, 35))
            except:
                self.image = pygame.Surface((35, 35))
                self.image.fill(PURPLE)
                pygame.draw.circle(self.image, (255, 215, 0), (17, 17), 14)
                pygame.draw.circle(self.image, PURPLE, (17, 17), 10)
                font = pygame.font.SysFont('Arial', 18, bold=True)
                text = font.render("I", True, YELLOW)
                self.image.blit(text, (12, 8))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self, speed, dt):
        self.rect.y += speed * dt
        if self.rect.y > HEIGHT:
            self.kill()


class Explosion:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.frames = []
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 0.12
        self.finished = False

        for i in range(1, 5):
            surf = pygame.Surface((96, 96), pygame.SRCALPHA)
            radius = 20 + i * 10
            color = (255, 100 + i * 30, 0)
            pygame.draw.circle(surf, color, (48, 48), radius)

            inner_radius = radius - 10
            if inner_radius > 0:
                pygame.draw.circle(surf, YELLOW, (48, 48), inner_radius)

            for _ in range(8):
                angle = random.uniform(0, math.pi * 2)
                r = radius - 5
                x_spark = 48 + math.cos(angle) * r
                y_spark = 48 + math.sin(angle) * r
                pygame.draw.circle(surf, (255, 255, 200), (int(x_spark), int(y_spark)), 4)

            for _ in range(12):
                angle = random.uniform(0, math.pi * 2)
                r = radius + random.randint(-5, 10)
                x_spark = 48 + math.cos(angle) * r
                y_spark = 48 + math.sin(angle) * r
                pygame.draw.circle(surf, (255, 200, 100), (int(x_spark), int(y_spark)), 2)

            self.frames.append(surf)

    def update(self, dt):
        if not self.finished:
            self.animation_timer += dt
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                self.current_frame += 1
                if self.current_frame >= len(self.frames):
                    self.finished = True

    def draw(self, screen):
        if not self.finished and self.current_frame < len(self.frames):
            screen.blit(self.frames[self.current_frame], (self.x - 48, self.y - 48))

    def is_finished(self):
        return self.finished