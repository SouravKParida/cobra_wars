# Author: Sourav Kumar Parida, Rishi
# Date: 12/13/2024
# Description: This module contains the MatchController class which is responsible for the main game operations,
# including initialization, game state management, and rendering of game components.

import pygame
import sys
from pygame.locals import *
from random import randint
import time
from reptile import Reptile
from vitalityorb import VitalityOrb

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



class MatchController:
    """
       Controls the main game operations, including initialization, game state management, and rendering of game components.

       Attributes:
           canvas (pygame.Surface): The main display surface on which all the game graphics are drawn.
           timer (pygame.time.Clock): Clock used to manage the game's frame rate.
           isActive (bool): Flag to determine if the game loop should continue running.
           isInPlay (bool): Flag to check if the game is currently in active play mode.
           isPaused (bool): Indicates whether the game is paused.
           isOver (bool): True if the game has ended.
           scoresReady (bool): True if the scores have been calculated and are ready to be displayed.
           combatant1 (Reptile): First reptile controlled by the player or AI.
           combatant2 (Reptile): Second reptile controlled by another player or AI.
           restorativeOrbs (list): List of vitality orbs that appear in the game to restore vitality.
           lastOrbRegen (float): Timestamp for the last regeneration of a vitality orb.
           nourishment (dict): Current position of the nourishment item in the game.
           controls (dict): A dictionary to store references to on-screen buttons.
           creatureGraphic (pygame.Surface): Graphical representation of the nourishment in the game.
           logoGraphic (pygame.Surface): Game logo graphic.
           totalRounds (int): Total number of rounds in a game session.
           currentBattle (int): The current battle round number.
           isAcceptingInput (bool): True when the game is ready to accept input from the user.
           enteredText (str): Text currently entered by the user in input mode.
           battleScores (dict): Dictionary holding the scores of each combatant across rounds.

       Methods:
           generate_nourishment(): Generates a new nourishment item on the game field.
    """
    def __init__(self):
        """
            Initializes the game environment, loads necessary resources, and prepares the initial state of the game.
        """
        pygame.init()
        self.canvas = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
        pygame.display.set_caption("Cobra Wars")
        self.timer = pygame.time.Clock()
        self.isActive = True
        self.isInPlay = False
        self.isPaused = False
        self.isOver = False
        self.scoresReady = False  
        self.combatant1 = Reptile({'x': 5, 'y': DISPLAY_HEIGHT // REPTILE_DIMENSION // 2}, MOVE_RIGHT, COLOR_YELLOW)
        self.combatant2 = Reptile({'x': DISPLAY_WIDTH // REPTILE_DIMENSION - 5, 'y': DISPLAY_HEIGHT // REPTILE_DIMENSION // 2}, MOVE_LEFT, COLOR_ORANGE)
        self.restorativeOrbs = []
        self.lastOrbRegen = time.time()
        self.nourishment = self.generate_nourishment()
        self.controls = {}
        self.creatureGraphic = pygame.image.load('rat_image.jpg')
        self.creatureGraphic = pygame.transform.scale(self.creatureGraphic, (REPTILE_DIMENSION, REPTILE_DIMENSION))
        self.logoGraphic = pygame.image.load('cobra_wars_image.png')
        self.logoGraphic = pygame.transform.scale(self.logoGraphic, (600, 150))
        self.totalRounds = 0
        self.currentBattle = 1
        self.isAcceptingInput = False
        self.enteredText = ''
        self.battleScores = {"Combatant 1": [], "Combatant 2": []}


    def generate_nourishment(self):
        """
            Generates a new position for the nourishment item randomly on the game field.

            Returns:
                dict: A dictionary containing 'x' and 'y' keys with values set to random positions within the game boundaries.
        """
        return {
            'x': randint(0, DISPLAY_WIDTH // REPTILE_DIMENSION - 1),
            'y': randint(0, DISPLAY_HEIGHT // REPTILE_DIMENSION - 1),
        }

    def render_reptile(self, reptile):
        """
            Renders a reptile on the canvas based on its segments and color.

            Args:
                reptile (Reptile): The reptile object to be rendered, which includes its body segments and color.
        """
        for segment in reptile.segments:
            x_coord = segment['x'] * REPTILE_DIMENSION
            y_coord = segment['y'] * REPTILE_DIMENSION
            pygame.draw.rect(self.canvas, reptile.tint, pygame.Rect(x_coord, y_coord, REPTILE_DIMENSION, REPTILE_DIMENSION))

    def render_vitality_meter(self, xPos, yPos, vitality, max_vitality):
        """
            Draws a vitality meter on the canvas.

            Description:
                This method draws a horizontal bar that represents the reptile's current vitality
                as a fraction of its maximum vitality. It is colored green to indicate vitality left
                and bordered in gold.
        """
        if vitality > 0:
            filled_width = (vitality / max_vitality) * 100
            filled_rect = pygame.Rect(xPos, yPos, filled_width, 10)
            pygame.draw.rect(self.canvas, COLOR_GREEN, filled_rect)
            pygame.draw.rect(self.canvas, COLOR_GOLD, (xPos, yPos, 100, 10), 2)

    def replenish_vitality_orbs(self):
        """
           Checks if enough time has passed to regenerate a vitality orb and, if so, regenerates one.

           Description:
               This method appends a new VitalityOrb to the restorativeOrbs list and resets the
               lastOrbRegen timer if the current time is sufficiently greater than the last orb
               regeneration time based on ORB_RESPAWN_TIME.
        """
        currentTime = time.time()
        if currentTime - self.lastOrbRegen >= ORB_RESPAWN_TIME:
            self.restorativeOrbs.append(VitalityOrb())
            self.lastOrbRegen = currentTime

    def manage_interactions(self):
        """
            Processes all player interactions and system events, managing game state transitions, input handling, and player controls.

            Mouse Interactions:
            - Activates or deactivates text input mode when specific buttons are clicked.
            - Handles game state transitions such as starting, pausing, or restarting the game based on button interactions.
            - Quits the game if the quit button is clicked.

            Keyboard Interactions:
            - Manages text input for settings like the number of rounds.
            - Controls in-game movements of combatants based on keyboard arrow or WASD keys without allowing reverse direction movement to prevent self-collision.
        """
        for interaction in pygame.event.get():
            if interaction.type == pygame.QUIT:
                self.isActive = False
            elif interaction.type == pygame.MOUSEBUTTONDOWN:
                if self.isAcceptingInput:
                    if self.controls.get('confirm') and self.controls['confirm'].collidepoint(interaction.pos):
                        print("Confirm button clicked")
                        try:
                            self.totalRounds = int(self.enteredText)
                            print(f"Total battles set to: {self.totalRounds}")
                            self.enteredText = ''  # Clear the input field
                            self.isAcceptingInput = False
                            self.isInPlay = True  # Start the battle
                            print("Battle set to start")
                        except ValueError:
                            self.enteredText = ''
                            print("Invalid input for battles")
                elif self.controls.get('initiate') and self.controls['initiate'].collidepoint(interaction.pos):
                    self.isAcceptingInput = True
                    self.isInPlay = False

                elif self.isOver:
                    if self.controls.get('replay') and self.controls['replay'].collidepoint(interaction.pos):
                        self.restart_battle()
                    elif self.controls.get('end') and self.controls['end'].collidepoint(interaction.pos):
                        self.isActive = False
                else:
                    if not self.isInPlay and not self.isAcceptingInput:
                        if self.controls.get('initiate') and self.controls['initiate'].collidepoint(interaction.pos):
                            self.isAcceptingInput = True
                        elif self.controls.get('end') and self.controls['end'].collidepoint(interaction.pos):
                            self.isActive = False

            elif interaction.type == pygame.KEYDOWN:
                if self.isAcceptingInput:
                    if interaction.key == pygame.K_BACKSPACE:
                        self.enteredText = self.enteredText[:-1]
                    elif interaction.unicode.isdigit():
                        self.enteredText += interaction.unicode
                elif self.isInPlay and not self.isPaused:
                    # Combatant 1 Controls
                    if interaction.key == pygame.K_w and self.combatant1.move_direction != MOVE_DOWN:
                        self.combatant1.move_direction = MOVE_UP
                    elif interaction.key == pygame.K_a and self.combatant1.move_direction != MOVE_RIGHT:
                        self.combatant1.move_direction = MOVE_LEFT
                    elif interaction.key == pygame.K_s and self.combatant1.move_direction != MOVE_UP:
                        self.combatant1.move_direction = MOVE_DOWN
                    elif interaction.key == pygame.K_d and self.combatant1.move_direction != MOVE_LEFT:
                        self.combatant1.move_direction = MOVE_RIGHT
                    # Combatant 2 Controls
                    if interaction.key == pygame.K_UP and self.combatant2.move_direction != MOVE_DOWN:
                        self.combatant2.move_direction = MOVE_UP
                    elif interaction.key == pygame.K_LEFT and self.combatant2.move_direction != MOVE_RIGHT:
                        self.combatant2.move_direction = MOVE_LEFT
                    elif interaction.key == pygame.K_DOWN and self.combatant2.move_direction != MOVE_UP:
                        self.combatant2.move_direction = MOVE_DOWN
                    elif interaction.key == pygame.K_RIGHT and self.combatant2.move_direction != MOVE_LEFT:
                        self.combatant2.move_direction = MOVE_RIGHT

    def advance_game(self):
        """
           Advances the game by updating the positions of the combatants, checking for collisions, and managing game state transitions.

           Key operations include:
           - Moving each combatant and checking boundary collisions.
           - Replenishing vitality orbs periodically.
           - Handling interactions between combatants and nourishment, which increases their score and expands their size.
           - Checking for collisions between combatants and handling self-collisions, which deduct vitality.
           - Archiving scores and managing the transitions between battles or concluding the game if the conditions for the end are met.
        """
        self.replenish_vitality_orbs()
        self.combatant1.move()
        self.combatant2.move()

        # Checking for collisions with edges and reduce vitality if hit
        if self.combatant1.segments[0]['x'] <= 0:
            self.combatant1.vitality -= 5
        elif self.combatant1.segments[0]['x'] >= DISPLAY_WIDTH // REPTILE_DIMENSION:
            self.combatant1.vitality -= 5
        if self.combatant1.segments[0]['y'] <= 0:
            self.combatant1.vitality -= 5
        elif self.combatant1.segments[0]['y'] >= DISPLAY_HEIGHT // REPTILE_DIMENSION:
            self.combatant1.vitality -= 5

        if self.combatant2.segments[0]['x'] <= 0:
            self.combatant2.vitality -= 5
        elif self.combatant2.segments[0]['x'] >= DISPLAY_WIDTH // REPTILE_DIMENSION:
            self.combatant2.vitality -= 5
        if self.combatant2.segments[0]['y'] <= 0:
            self.combatant2.vitality -= 5
        elif self.combatant2.segments[0]['y'] >= DISPLAY_HEIGHT // REPTILE_DIMENSION:
            self.combatant2.vitality -= 5

        # Terminating the battle if any combatant's vitality reaches zero
        if self.combatant1.vitality <= 0 or self.combatant2.vitality <= 0:
            self.archive_scores()
            if self.currentBattle < self.totalRounds:
                self.currentBattle += 1
                self.initialize_next_battle()
            else:
                self.isOver = True

        # Managing interaction with vitality orbs
        for orb in self.restorativeOrbs[:]:
            if self.combatant1.detect_collision(orb.coordinates):
                self.restorativeOrbs.remove(orb)
                self.combatant1.vitality = min(self.combatant1.vitality + 30, 100)
            elif self.combatant2.detect_collision(orb.coordinates):
                self.restorativeOrbs.remove(orb)
                self.combatant2.vitality = min(self.combatant2.vitality + 30, 100)

        # Checking for collisions between combatants
        if self.combatant1.segments[0] in self.combatant2.segments:
            self.combatant1.vitality -= 5
        if self.combatant2.segments[0] in self.combatant1.segments:
            self.combatant2.vitality -= 5

        if self.combatant1.detect_collision(self.nourishment):
            self.nourishment = self.generate_nourishment()
            self.combatant1.tally += 5
            self.combatant1.expand()

        if self.combatant2.detect_collision(self.nourishment):
            self.nourishment = self.generate_nourishment()
            self.combatant2.tally += 5
            self.combatant2.expand()

    def initialize_next_battle(self):
        """
            Resets the game environment for a new battle within the same game session.

            Key operations include:
            - Re-setting each combatant's position and vitality to the start conditions.
            - Regenerating the nourishment position on the game field.
            - Clearing the list of restorative orbs and resetting the last orb regeneration timestamp.

        """

        # Reseting combatant positions and vitality
        self.combatant1 = Reptile({'x': 5, 'y': DISPLAY_HEIGHT // REPTILE_DIMENSION // 2}, MOVE_RIGHT, COLOR_YELLOW)
        self.combatant1.vitality = 100
        self.combatant2 = Reptile({'x': DISPLAY_WIDTH // REPTILE_DIMENSION - 5, 'y': DISPLAY_HEIGHT // REPTILE_DIMENSION // 2}, MOVE_LEFT,
                             COLOR_ORANGE)
        self.combatant2.vitality = 100
        # Reseting nourishment and vitality orbs
        self.nourishment = self.generate_nourishment()
        self.restorativeOrbs.clear()
        self.lastOrbRegen = time.time()
        def display(self):
        """
           Handles all rendering and display updates for the game based on the current game state.

           Operations:
           - Clears the screen and redraws game elements when the game is active.
           - Renders reptiles, nourishment, and vitality meters during active play.
           - Displays game controls and text input fields when in configuration or menu mode.
           - Shows the game's logo and menu options when the game is not in active play or configuration.
           - Transitions to a game over screen layout when the game has ended.
        """
        if not self.isOver:
            self.canvas.fill(COLOR_BLACK)  # Clear the screen for regular game updates

            if self.isInPlay:
                # Render game play elements like reptiles, nourishment, vitality etc.
                self.render_reptile(self.combatant1)
                self.render_reptile(self.combatant2)
                for orb in self.restorativeOrbs:
                    orb.render(self.canvas)
                self.canvas.blit(self.creatureGraphic, (self.nourishment['x'] * REPTILE_DIMENSION, self.nourishment['y'] * REPTILE_DIMENSION))
                self.render_vitality_meter(20, DISPLAY_HEIGHT - 20, self.combatant1.vitality, 100)
                self.render_vitality_meter(DISPLAY_WIDTH - 120, DISPLAY_HEIGHT - 20, self.combatant2.vitality, 100)
                self.display_scores()

                # Display current battle information
                font_style = pygame.font.Font(None, 36)  # Define font at the start of the method
                battle_info_text = f"Battle: {self.currentBattle}"
                battle_info_surface = font_style.render(battle_info_text, True, COLOR_GREEN)
                battle_info_rectangle = battle_info_surface.get_rect(center=(DISPLAY_WIDTH // 2, 20))
                self.canvas.blit(battle_info_surface, battle_info_rectangle)

            elif self.isAcceptingInput:
                # Display the input prompt and the current text input by the user
                font_style = pygame.font.Font(None, 36)
                prompt_surface = font_style.render("Enter number of battles:", True, COLOR_GREEN)
                prompt_rectangle = prompt_surface.get_rect(center=(DISPLAY_WIDTH // 2, DISPLAY_HEIGHT // 2 - 50))
                self.canvas.blit(prompt_surface, prompt_rectangle)

                input_surface = font_style.render(self.enteredText, True, COLOR_BLACK, COLOR_GREEN)
                input_rectangle = input_surface.get_rect(center=(DISPLAY_WIDTH // 2, DISPLAY_HEIGHT // 2))
                self.canvas.blit(input_surface, input_rectangle)

                # Render the Confirm button
                self.controls['confirm'] = self.render_button("Confirm", DISPLAY_WIDTH // 2 - 50,
                                                              DISPLAY_HEIGHT // 2 + 50)

            else:
                # Display the game logo and menu buttons when not in play
                logo_rectangle = self.logoGraphic.get_rect(center=(DISPLAY_WIDTH // 2, 150))
                self.canvas.blit(self.logoGraphic, logo_rectangle)
                self.controls['initiate'] = self.render_button("Start Battle", 550, 275)
                self.controls['replay'] = self.render_button("Restart", 550, 350)
                self.controls['end'] = self.render_button("Quit", 550, 425)

        else:
            # Only show battle over screen when battle is over
            self.display_battle_over_screen()

        pygame.display.update()  # Update the display at the end of the method

