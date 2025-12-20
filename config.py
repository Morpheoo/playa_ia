# -*- coding: utf-8 -*-

# config.py



# Game Constants

SCREEN_WIDTH = 800

SCREEN_HEIGHT = 400

FPS = 60



# Physics

GRAVITY = 0.8

JUMP_HEIGHT = 100 # Approx 2x player height (player is 50x50)

PLAYER_WIDTH = 44

PLAYER_HEIGHT = 47

PLAYER_X = 50

GROUND_Y = SCREEN_HEIGHT - 50



# Player Mechanics

JUMP_DURATION = 35 # frames

CROUCH_HEIGHT = 30



# Obstacles

INITIAL_GAME_SPEED = 5

SPEED_INCREMENT = 0.001

BIRD_PROBABILITY = 0.1

MIN_SPAWN_DIST = 400

MAX_SPAWN_DIST = 800



# AI/GA Constants

POPULATION_SIZE = 50

GENES_PER_GENOME = 16

MUTATION_RATE = 0.1

SELECTION_RATIO = 0.1 # Top 10%

ELITISM_COUNT = 5



# Neural Network

INPUT_SIZE = 7  # distance, obs_x, obs_y, obs_w, obs_h, player_y, speed

HIDDEN_SIZE = 7

OUTPUT_SIZE = 2 # Jump (Up), Crouch (Down)

