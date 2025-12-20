# -*- coding: utf-8 -*-
import random
import copy
from .brain import Genome, Gene
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

    def next_generation(self, fitnesses):
        results = list(zip(self.population, fitnesses))
        results.sort(key=lambda x: x[1], reverse=True)
        
        self.best_fitness = results[0][1]
        self.avg_fitness = sum(fitnesses) / len(fitnesses)
        self.history.append({"gen": self.generation, "best": self.best_fitness, "avg": self.avg_fitness})
        
        new_population = []
        for i in range(self.elitism_count):
            new_population.append(copy.deepcopy(results[i][0]))
            
        pool_size = int(self.population_size * self.selection_ratio)
        pool = [results[i][0] for i in range(max(1, pool_size))]
        
        while len(new_population) < self.population_size:
            parent1 = random.choice(pool)
            parent2 = random.choice(pool)
            
            child_genes = self.crossover(parent1, parent2)
            child = Genome(child_genes)
            child.mutate(self.mutation_rate)
            new_population.append(child)
            
        self.population = new_population
        self.generation += 1
        return self.population

    def crossover(self, p1, p2):
        new_genes = []
        for i in range(GENES_PER_GENOME):
            source_p = random.choice([p1, p2])
            gene = source_p.genes[i]
            new_genes.append(Gene(gene.source, gene.target, gene.weight))
        return new_genes

    def set_params(self, pop_size, mutation_rate, selection_ratio, elitism):
        self.population_size = pop_size
        self.mutation_rate = mutation_rate
        self.selection_ratio = selection_ratio
        self.elitism_count = elitism
        if len(self.population) < self.population_size:
            for _ in range(self.population_size - len(self.population)):
                self.population.append(Genome())
        elif len(self.population) > self.population_size:
            self.population = self.population[:self.population_size]
