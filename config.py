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

PLAYER_HEIGHT = 60

PLAYER_X = 50

GROUND_Y = SCREEN_HEIGHT - 50



# Player Mechanics

JUMP_DURATION = 35 # frames

CROUCH_HEIGHT = 40



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

# Neural Network
INPUT_SIZE = 6  # DistX, ObsY, ObsW, ObsH, PlayerY, Speed
HIDDEN_SIZE = 5
OUTPUT_SIZE = 2 # Jump, Crouch (Multi-label)

# NN Decision Thresholds
JUMP_THRESHOLD = 0.55
CROUCH_THRESHOLD = 0.45

# Normalization Constants
WORLD_W = SCREEN_WIDTH
WORLD_H = SCREEN_HEIGHT
SPEED_MIN = INITIAL_GAME_SPEED
SPEED_MAX = 20 # Cap for normalization

# Genetic Algo Weights
W_MAX = 2.0 # Clip range for weights
MUTATION_STD = 0.5 # Gaussian noise std

