# -*- coding: utf-8 -*-
# brain.py - El "cerebro" de nuestros agentes. 
# Aquí definimos la Red Neuronal que permite a los corredores aprender qué hacer.

import numpy as np
import random
from config import *

# Arquitectura MLP (Perceptrón Multicapa):
# 6 Entradas -> 5 Neuronas Ocultas -> 2 Salidas (Salto y Agacharse)

class Genome:
    """
    El Genoma es como el ADN de cada corredor. 
    Contiene los pesos y sesgos que definen cómo reacciona el cerebro.
    """
    def __init__(self, w1=None, b1=None, w2=None, b2=None):
        if w1 is None:
            # Si no nos dan ADN, creamos uno al azar (primera generación)
            # W1: Conecta la entrada con la capa oculta
            self.w1 = np.random.uniform(-1, 1, (HIDDEN_SIZE, INPUT_SIZE))
            # B1: Sesgos de la primera capa
            self.b1 = np.random.uniform(-1, 1, (HIDDEN_SIZE,))
            # W2: Conecta la capa oculta con la salida
            self.w2 = np.random.uniform(-1, 1, (OUTPUT_SIZE, HIDDEN_SIZE))
            # B2: Sesgos de la salida
            self.b2 = np.random.uniform(-1, 1, (OUTPUT_SIZE,))
        else:
            # Si ya tenemos ADN (por herencia o cruce), lo usamos
            self.w1 = w1
            self.b1 = b1
            self.w2 = w2
            self.b2 = b2

    def mutate(self, rate):
        """
        La mutación es lo que permite a la IA probar cosas nuevas.
        Es como un error en la copia del ADN que a veces ayuda.
        """
        def apply_mutation(param):
            if random.random() < rate:
                # Metemos un poco de ruido gaussiano para cambiar los valores
                noise = np.random.normal(0, MUTATION_STD, param.shape)
                param += noise
                # Evitamos que los números se vuelvan locos (los limitamos)
                np.clip(param, -W_MAX, W_MAX, out=param)
        
        apply_mutation(self.w1)
        apply_mutation(self.b1)
        apply_mutation(self.w2)
        apply_mutation(self.b2)

class NeuralNetwork:
    """
    Esta es la red que procesa la información en tiempo real durante el juego.
    """
    def __init__(self, genome):
        self.genome = genome # Le ponemos su ADN
        
    def relu(self, x):
        # Función de activación: si el valor es negativo, lo vuelve 0.
        return np.maximum(0, x)
    
    def sigmoid(self, x):
        # Función de activación: convierte cualquier número en una probabilidad entre 0 y 1.
        return 1 / (1 + np.exp(-x))
        
    def activate(self, inputs):
        """
        Aquí es donde el cerebro "piensa". Le entran los datos del juego 
        y nos dice qué acción tomar.
        """
        # inputs shape: (6,)
        
        # Capa 1: Procesamos la entrada hacia la capa oculta
        z1 = np.dot(self.genome.w1, inputs) + self.genome.b1
        h = self.relu(z1) # Usamos ReLU para que aprenda cosas complejas
        
        # Capa 2: De la capa oculta a la salida final
        z2 = np.dot(self.genome.w2, h) + self.genome.b2
        
        # Usamos Sigmoid para tener probabilidades de saltar o agacharse
        output = self.sigmoid(z2)
        
        # El resultado es un vector [probabilidad_saltar, probabilidad_agacharse]
        return output
