# -*- coding: utf-8 -*-

# config.py - Aquí guardamos todas las "reglas" y números del juego
# Lo hicimos así para no tener que andar buscando entre todo el código si queremos cambiar algo

# Constantes de la pantalla (Tamaño de la ventana)
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 400
FPS = 60 # Cuadros por segundo para que se vea fluido

# Físicas del juego (Para que el salto se sienta real)
GRAVITY = 0.8
JUMP_HEIGHT = 100 # Qué tan alto salta nuestro personaje (aprox 2 veces su altura)
PLAYER_WIDTH = 44 # Ancho del monigote
PLAYER_HEIGHT = 95 # Alto del monigote
PLAYER_X = 50 # Posición fija en X del jugador
GROUND_Y = SCREEN_HEIGHT - 50 # Altura del suelo

# Mecánicas del jugador
JUMP_DURATION = 35 # Cuántos frames dura el salto
CROUCH_HEIGHT = 60 # Altura cuando se agacha (para esquivar drones)

# Obstáculos y dificultad
INITIAL_GAME_SPEED = 5 # Empezamos lentito
SPEED_INCREMENT = 0.003 # Va subiendo la velocidad poco a poco para que sea difícil (aumentado de 0.001)
BIRD_PROBABILITY = 0.1 # Probabilidad de que aparezca un dron
MIN_SPAWN_DIST = 400 # Distancia mínima entre obstáculos
MAX_SPAWN_DIST = 800 # Distancia máxima para que no sea imposible

# Parámetros de la IA y el Algoritmo Genético (La parte "inteligente")
POPULATION_SIZE = 50 # Cuántos agentes entrenamos por generación
GENES_PER_GENOME = 16 # Esto define el tamaño del "ADN" de cada agente
MUTATION_RATE = 0.1 # Qué tanto cambian los hijos respecto a los padres
SELECTION_RATIO = 0.1 # Nos quedamos con el mejor 10% para la siguiente ronda
ELITISM_COUNT = 5 # Los 5 mejores pasan directito sin cambios

# Red Neuronal (El "cerebro" de cada corredor)
INPUT_SIZE = 6  # Lo que ve: Distancia al obstáculo, su altura, ancho, etc.
HIDDEN_SIZE = 5 # Capa interna de neuronas para procesar la info
OUTPUT_SIZE = 2 # Lo que decide: Salto o Agacharse

# Umbrales de decisión (Si la neurona dice más de esto, el mono actúa)
JUMP_THRESHOLD = 0.55
CROUCH_THRESHOLD = 0.45

# Constantes para normalizar los datos (Para que la IA no se confunda con números grandes)
WORLD_W = SCREEN_WIDTH
WORLD_H = SCREEN_HEIGHT
SPEED_MIN = INITIAL_GAME_SPEED
SPEED_MAX = 20 # El tope de velocidad para los cálculos

# Pesos del Algoritmo Genético
W_MAX = 2.0 # Rango máximo de los pesos de las neuronas
MUTATION_STD = 0.5 # Qué tanto ruido le metemos al mutar (ruido gaussiano)
