import pygame

# Инициализация Pygame
pygame.init()
pygame.mixer.init()

SCREEN = WIDTH, HEIGHT = 288, 512

info = pygame.display.Info()
width = info.current_w
height = info.current_h

if width >= height:
    win = pygame.display.set_mode(SCREEN, pygame.NOFRAME)
else:
    win = pygame.display.set_mode(SCREEN, pygame.NOFRAME | pygame.SCALED | pygame.FULLSCREEN)

clock = pygame.time.Clock()

lane_pos = [50, 95, 142, 190]

# COLORS
WHITE = (255, 255, 255)
BLUE = (30, 144, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 20)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
GRASS_GREEN = (34, 139, 34)
DARK_GREEN = (0, 150, 0)
LIGHT_GREEN = (100, 255, 100)
PURPLE = (138, 43, 226)
CYAN = (0, 255, 255)

# Загрузка звуков
try:
    engine_sound = pygame.mixer.Sound('Газ.mp3')
    engine_sound.set_volume(1)
    transition_sound = pygame.mixer.Sound('click.mp3')
    transition_sound.set_volume(0.5)
    pygame.mixer.music.load('music.mp3')
    pygame.mixer.music.set_volume(0.2)
    pygame.mixer.music.play(-1)
except FileNotFoundError as e:
    print(f"Не найден звуковой файл: {e}")
    engine_sound = None
    transition_sound = None
except Exception as e:
    print(f"Ошибка загрузки звука: {e}")
    engine_sound = None
    transition_sound = None


def play_transition_sound():
    if transition_sound:
        transition_sound.play()


def draw_text_centered(screen, text, size=36, color=WHITE, y=0):
    font = pygame.font.SysFont('Arial', size)
    text_surface = font.render(text, True, color)
    text_x = WIDTH // 2 - text_surface.get_width() // 2
    screen.blit(text_surface, (text_x, y))