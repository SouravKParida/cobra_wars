# Author: Sourav Kumar Parida
# Date: 12/12/2024
# Description: This program contains class functions for managing reptile behavior, including movement, expansion, and collision detection.

import pygame
import sys
from pygame.locals import *
from random import randint
import time

# Configuration Values
DISPLAY_WIDTH, DISPLAY_HEIGHT = 1200, 900
FRAME_RATE = 30
REPTILE_DIMENSION = 20
ACTION_WIDTH, ACTION_HEIGHT = 100, 50
ORB_RADIUS = 10
ORB_RESPAWN_TIME = 20  # in seconds

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




class Reptile:
    """
        Represents a reptile(i.e., cobra snake) in the game which moves across the battle area and interacts with various game elements.

        Attributes:
            segments (list): A list of dictionaries defining the positions of segments that make up the reptile's body.
            move_direction (dict): The current movement direction of the reptile as a dictionary with 'x' and 'y' keys.
            tint (tuple): RGB color tuple for the reptile's color.
            vitality (int): The health of the reptile, starts at 100.
            tally (int): The score tally for the reptile, incremented during the game.

        Methods:
            move(): Updates the reptile's position based on its current direction.
            expand(): Increases the length of the reptile by adding a segment at its tail.
            detect_collision(item): Checks if the reptile's head has collided with an item.
            detect_self_impact(): Checks if the reptile has collided with itself.
    """
    def __init__(self, start_position, move_direction, tint):
        """
         Initializes a new instance of the Reptile class.
         :param start_position: The starting position of the reptile's head as a dictionary with 'x' and 'y' keys.
         :type start_position: dict
         :param move_direction: Initial movement direction of the reptile as a dictionary.
         :type move_direction: dict
         :param tint: The color of the reptile, given as an RGB tuple.
         :type tint: tuple
        """
        # Initializing a new Reptile instance with a starting position, movement direction, and color.
        self.segments = [start_position]
        self.move_direction = move_direction
        self.tint = tint
        self.vitality = 100
        self.tally = 0

    def move(self):
        """
         Updates the reptile's head position based on its current direction,
         adding a new segment at the front and removing the last segment, simulating movement.
        """
        # Updating the reptile's position by calculating new head position and adjusting the body.
        new_head = {
            'x': (self.segments[0]['x'] + self.move_direction['x']) % (DISPLAY_WIDTH // REPTILE_DIMENSION),
            'y': (self.segments[0]['y'] + self.move_direction['y']) % (DISPLAY_HEIGHT // REPTILE_DIMENSION),
        }
        self.segments.insert(0, new_head)
        # Removing the last segment of the body.
        self.segments.pop()

    def expand(self):
        """ Adds a new segment at the end of the reptile's body, increasing its length by one segment. """
        # Adding a new segment at the tail of the reptile.
        self.segments.append(self.segments[-1])

    def detect_collision(self, item):
        """
          Determines if the reptile's head is at the same position as a given item.
         :param item: An item with 'x' and 'y' coordinates.
         :type item: dict
         :return: True if there's a collision; otherwise, False.
        """
        # Checking if the reptile's head is at the same coordinates as another game item
        return self.segments[0]['x'] == item['x'] and self.segments[0]['y'] == item['y']

    def detect_self_impact(self):
        """
         Checks if the reptile's head has collided with any other part of its body, indicating a self-collision.
         :return: True if the head collides with any other body segment; otherwise, False.
        """
        # Checking if the reptile's head has collided with any other part of its body.
        return self.segments[0] in self.segments[1:]
