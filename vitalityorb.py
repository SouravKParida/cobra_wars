# Author: Rishi Patel
# Date: 12/10/2024
# Description: A small description in your own words that describes what

import pygame
import sys
from pygame.locals import *
from random import randint
import time

# Configuration Values
DISPLAY_WIDTH, DISPLAY_HEIGHT = 1200, 900  # Screen dimensions in pixels
FRAME_RATE = 30                            # FPS
REPTILE_DIMENSION = 20                     # Grid cell size
ACTION_WIDTH, ACTION_HEIGHT = 100, 50      # Action button dimensions
ORB_RADIUS = 10                            # Radius of the vitality orb
ORB_RESPAWN_TIME = 20                      # Time for orb to respawn

# Motion Directions
MOVE_RIGHT = {'x': 1, 'y': 0}
MOVE_LEFT = {'x': -1, 'y': 0}
MOVE_UP = {'x': 0, 'y': -1}
MOVE_DOWN = {'x': 0, 'y': 1}

# Palette
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_GRAY = (100, 100, 100)
COLOR_PINK = (255, 192, 203)
COLOR_YELLOW = (255, 223, 0)
COLOR_ORANGE = (255, 69, 0)
COLOR_GREEN = (173, 255, 47)
COLOR_GOLD = (255, 215, 0)

class VitalityOrb:
    """
    Represents a vitality orb in the game. The orb spawns at random coordinates
    within the grid and can be rendered on the game canvas.
    """

    def __init__(self):
        self.coordinates = self.regenerate()

    def regenerate(self):
        """
        Randomly generates new coordinates for the vitality orb within the grid.

        Returns:
            dict: A dictionary containing the 'x' and 'y' coordinates of the orb.
        """
        coord_x = randint(0, DISPLAY_WIDTH // REPTILE_DIMENSION - 1)
        coord_y = randint(0, DISPLAY_HEIGHT // REPTILE_DIMENSION - 1)
        return {'x': coord_x, 'y': coord_y}

    def render(self, canvas):
        """
        Renders the vitality orb as a circle on the given canvas.
        """
        pygame.draw.circle(
            canvas,
            COLOR_PINK,
            (
                self.coordinates['x'] * REPTILE_DIMENSION + REPTILE_DIMENSION // 2,  # Center X position
                self.coordinates['y'] * REPTILE_DIMENSION + REPTILE_DIMENSION // 2   # Center Y position
            ),
            ORB_RADIUS,  # Radius of the orb
        )
