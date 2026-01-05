# -*- coding: utf-8 -*-
# genetic_algo.py - El algoritmo de Selección Natural
# Aquí es donde ocurre la magia de la evolución: los mejores sobreviven y tienen hijos.

import random
import copy
import numpy as np
from .brain import Genome
from config import *

class GeneticAlgorithm:
    def __init__(self):
        # Cargamos la configuración que definimos en config.py
        self.population_size = POPULATION_SIZE
        self.mutation_rate = MUTATION_RATE
        self.selection_ratio = SELECTION_RATIO
        self.elitism_count = ELITISM_COUNT
        
        # Creamos la primera generación con ADN aleatorio
        self.population = [Genome() for _ in range(self.population_size)]
        self.generation = 1
        self.best_fitness = 0
        self.avg_fitness = 0
        self.history = []
        self.global_best_genome = None
        self.global_best_fitness = 0
        
        # Estrategias para cuando la IA se queda "trabada"
        self.strategy = "HOF" # Por defecto: Guardar al mejor de siempre (Hall of Fame)
        self.stagnation_counter = 0

    def next_generation(self, fitnesses):
        """
        Esta función crea la siguiente generación basándose en qué tan bien le fue a cada uno.
        """
        # Juntamos a cada dino con su puntuación (fitness)
        results = list(zip(self.population, fitnesses))
        # Los ordenamos de mejor a peor
        results.sort(key=lambda x: x[1], reverse=True)
        
        current_best_fitness = results[0][1]
        current_best_genome = results[0][0]
        
        # Revisamos si hemos mejorado el récord histórico
        if current_best_fitness <= self.global_best_fitness:
            self.stagnation_counter += 1
        else:
            self.stagnation_counter = 0
            self.global_best_fitness = current_best_fitness
            self.global_best_genome = copy.deepcopy(current_best_genome)
            
        self.best_fitness = current_best_fitness
        self.avg_fitness = sum(fitnesses) / len(fitnesses)
        # Guardamos el progreso para la gráfica
        self.history.append({"gen": self.generation, "best": self.best_fitness, "avg": self.avg_fitness})
        
        new_population = []
        
        # Si elegimos modo DYNAMIC y la IA no mejora, subimos la mutación para que "arriesgue" más
        eff_mutation = self.mutation_rate
        if self.strategy == "DYNAMIC" and self.stagnation_counter > 10:
             eff_mutation = min(0.5, self.mutation_rate + 0.2)
        
        # 1. Selección y Elitismo (Los campeones pasan directito)
        if self.strategy == "HOF":
             if self.global_best_genome:
                 new_population.append(copy.deepcopy(self.global_best_genome))
        elif self.strategy == "DYNAMIC" and self.stagnation_counter < 15:
             if self.global_best_genome:
                 new_population.append(copy.deepcopy(self.global_best_genome))
            
        # 2. Llenamos los espacios de "élite" con los mejores de esta ronda
        current_elite_idx = 0
        while len(new_population) < self.elitism_count and current_elite_idx < len(results):
            new_population.append(copy.deepcopy(results[current_elite_idx][0]))
            current_elite_idx += 1
            
        # 3. Cruzamos a los sobrevivientes para crear al resto de la población
        num_to_select = max(1, int(len(results) * self.selection_ratio))
        pool = [r[0] for r in results[:num_to_select]] # Grupo de padres potenciales
        
        while len(new_population) < self.population_size:
            # En modo DYNAMIC, a veces metemos "sangre nueva" (agentes al azar)
            if self.strategy == "DYNAMIC" and self.stagnation_counter > 15 and random.random() < 0.15:
                 new_population.append(Genome())
                 continue

            # Elegimos dos padres al azar del grupo de los mejores
            parent1 = random.choice(pool)
            parent2 = random.choice(pool)
            
            # Tienen un hijo (mezcla de sus ADNs)
            child = self.crossover(parent1, parent2)
            # El hijo puede mutar un poquito
            child.mutate(eff_mutation)
            new_population.append(child)
            
        self.population = new_population
        self.generation += 1
        return self.population

    def crossover(self, p1, p2):
        """
        Cruce uniforme: para cada conexión neuronal, 
        el hijo elige al azar si hereda la del padre 1 o la del padre 2.
        """
        def mix_params(m1, m2):
            # Creamos una máscara de 0s y 1s para elegir de quién heredar
            mask = np.random.randint(0, 2, m1.shape).astype(float)
            return m1 * mask + m2 * (1 - mask)
            
        new_w1 = mix_params(p1.w1, p2.w1)
        new_b1 = mix_params(p1.b1, p2.b1)
        new_w2 = mix_params(p1.w2, p2.w2)
        new_b2 = mix_params(p1.b2, p2.b2)
        
        return Genome(new_w1, new_b1, new_w2, new_b2)

    def set_params(self, pop_size, mutation_rate, selection_ratio, elitism):
        # Para cambiar los números desde la interfaz de Streamlit
        self.population_size = pop_size
        self.mutation_rate = mutation_rate
        self.selection_ratio = selection_ratio
        self.elitism_count = elitism
        
        # Ajustamos el tamaño de la población si es necesario
        if len(self.population) < self.population_size:
            for _ in range(self.population_size - len(self.population)):
                self.population.append(Genome())
        elif len(self.population) > self.population_size:
            self.population = self.population[:self.population_size]
