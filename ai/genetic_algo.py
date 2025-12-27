# -*- coding: utf-8 -*-
import random
import copy
import numpy as np
from .brain import Genome
from config import *

class GeneticAlgorithm:
    def __init__(self):
        self.population_size = POPULATION_SIZE
        self.mutation_rate = MUTATION_RATE
        self.selection_ratio = SELECTION_RATIO
        self.elitism_count = ELITISM_COUNT
        
        self.population = [Genome() for _ in range(self.population_size)]
        self.generation = 1
        self.best_fitness = 0
        self.avg_fitness = 0
        self.history = []
        self.global_best_genome = None
        self.global_best_fitness = 0

    def next_generation(self, fitnesses):
        results = list(zip(self.population, fitnesses))
        results.sort(key=lambda x: x[1], reverse=True)
        
        current_best_fitness = results[0][1]
        current_best_genome = results[0][0]
        
        self.best_fitness = current_best_fitness
        self.avg_fitness = sum(fitnesses) / len(fitnesses)
        self.history.append({"gen": self.generation, "best": self.best_fitness, "avg": self.avg_fitness})
        
        # Check for Hall of Fame (Global Best)
        if current_best_fitness > self.global_best_fitness:
            self.global_best_fitness = current_best_fitness
            self.global_best_genome = copy.deepcopy(current_best_genome)
        
        new_population = []
        
        # 1. Hall of Fame injection: Ensure the All-Time Best is always in the population
        if self.global_best_genome:
            new_population.append(copy.deepcopy(self.global_best_genome))
            
        # 2. Standard Elitism (fill remaining slots up to elitism_count)
        # If we added global best, we take 1 less from current results (unless global best IS current best)
        # To be safe, just fill inputs until we hit elitism_count
        
        current_elite_idx = 0
        while len(new_population) < self.elitism_count and current_elite_idx < len(results):
            # Avoid duplicate if global best is same as current best? 
            # It's fine to have duplicates (higher weight for good genes).
            new_population.append(copy.deepcopy(results[current_elite_idx][0]))
            current_elite_idx += 1
            
        num_to_select = max(1, int(len(results) * self.selection_ratio))
        pool = [r[0] for r in results[:num_to_select]]
        
        while len(new_population) < self.population_size:
            parent1 = random.choice(pool)
            parent2 = random.choice(pool)
            
            child = self.crossover(parent1, parent2)
            child.mutate(self.mutation_rate)
            new_population.append(child)
            
        self.population = new_population
        self.generation += 1
        return self.population

    def crossover(self, p1, p2):
        # Uniform Crossover implementation for Matrices
        # Create new matrices mixing P1 and P2
        
        def mix_params(m1, m2):
            # Create mask: 0 or 1
            mask = np.random.randint(0, 2, m1.shape).astype(float)
            # Mix: m1 * mask + m2 * (1-mask)
            return m1 * mask + m2 * (1 - mask)
            
        new_w1 = mix_params(p1.w1, p2.w1)
        new_b1 = mix_params(p1.b1, p2.b1)
        new_w2 = mix_params(p1.w2, p2.w2)
        new_b2 = mix_params(p1.b2, p2.b2)
        
        return Genome(new_w1, new_b1, new_w2, new_b2)

    def set_params(self, pop_size, mutation_rate, selection_ratio, elitism):
        self.population_size = pop_size
        self.mutation_rate = mutation_rate
        self.selection_ratio = selection_ratio
        self.elitism_count = elitism
        
        # Resize pop if needed
        if len(self.population) < self.population_size:
            for _ in range(self.population_size - len(self.population)):
                self.population.append(Genome())
        elif len(self.population) > self.population_size:
            self.population = self.population[:self.population_size]
