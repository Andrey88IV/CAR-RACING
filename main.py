import pygame
from config import win, clock
from states import MenuScreen, GameScreen

current_state = MenuScreen(selected_car=1)
running = True

while running:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            if isinstance(current_state, GameScreen):
                current_state.stop_engine_sound()
            running = False

    new_state = current_state.handle_events(events)
    if new_state != current_state:
        current_state = new_state

    current_state.update()
    current_state.draw(win)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()