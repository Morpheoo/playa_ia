# -*- coding: utf-8 -*-
import numpy as np
import random
from config import *

# Strict MLP Architecture
# Input(6) -> Hidden(5) -> Output(2)

class Genome:
    def __init__(self, w1=None, b1=None, w2=None, b2=None):
        if w1 is None:
            # Random Initialization
            # W1: (HIDDEN, INPUT)
            self.w1 = np.random.uniform(-1, 1, (HIDDEN_SIZE, INPUT_SIZE))
            # B1: (HIDDEN)
            self.b1 = np.random.uniform(-1, 1, (HIDDEN_SIZE,))
            # W2: (OUTPUT, HIDDEN)
            self.w2 = np.random.uniform(-1, 1, (OUTPUT_SIZE, HIDDEN_SIZE))
            # B2: (OUTPUT)
            self.b2 = np.random.uniform(-1, 1, (OUTPUT_SIZE,))
        else:
            self.w1 = w1
            self.b1 = b1
            self.w2 = w2
            self.b2 = b2

    def mutate(self, rate):
        # Apply strict element-wise mutation
        # param += N(0, MUTATION_STD) * mask
        def apply_mutation(param):
            if random.random() < rate:
                noise = np.random.normal(0, MUTATION_STD, param.shape)
                param += noise
                # Clip to stay in reasonable bounds
                np.clip(param, -W_MAX, W_MAX, out=param)
        
        apply_mutation(self.w1)
        apply_mutation(self.b1)
        apply_mutation(self.w2)
        apply_mutation(self.b2)

class NeuralNetwork:
    def __init__(self, genome):
        self.genome = genome
        
    def relu(self, x):
        return np.maximum(0, x)
    
    def sigmoid(self, x):
        return 1 / (1 + np.exp(-x))
        
    def activate(self, inputs):
        # Strict MLP Forward Pass
        # inputs shape: (6,)
        
        # Layer 1: Input -> Hidden
        z1 = np.dot(self.genome.w1, inputs) + self.genome.b1
        h = self.relu(z1)
        
        # Layer 2: Hidden -> Output
        z2 = np.dot(self.genome.w2, h) + self.genome.b2
        
        # Multi-label Output (Sigmoid)
        output = self.sigmoid(z2)
        
        # output is [p_jump, p_crouch]
        # Return probability vector, user decides logic with thresholds
        return output
