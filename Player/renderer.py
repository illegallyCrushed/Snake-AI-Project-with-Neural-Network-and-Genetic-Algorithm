import pygame
import constants

game_objects = []
game_screen = ""
game_run = ""


def Init():
    global game_objects, game_screen, game_run
    # initialization
    pygame.init()
    pygame.display.set_caption('Snake Player')
    # screen
    game_screen = pygame.display.set_mode((constants.SCREEN_RESOLUTION))
    # run variable
    game_run = True


def Run():
    global game_objects, game_screen, game_run
    # runtime
    while game_run:
        # get event trigger
        for event in pygame.event.get():
            # pas pencet close
            if event.type == pygame.QUIT:
                game_run = False

        # rendering
        game_screen.fill(constants.COLOR_WHITE)
        pygame.display.flip()
