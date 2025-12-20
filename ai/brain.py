# -*- coding: utf-8 -*-
import numpy as np
import random
from config import *

class Gene:
    def __init__(self, source, target, weight):
        self.source = source
        self.target = target
        self.weight = weight

class Genome:
    def __init__(self, genes=None):
        if genes is None:
            self.genes = []
            for _ in range(GENES_PER_GENOME):
                source = random.randint(0, 13)
                target = random.randint(max(source + 1, 7), 15)
                weight = random.uniform(-1, 1)
                self.genes.append(Gene(source, target, weight))
        else:
            self.genes = genes

    def mutate(self, rate):
        for gene in self.genes:
            if random.random() < rate:
                if random.random() < 0.8:
                    gene.weight += random.gauss(0, 0.1)
                else:
                    gene.source = random.randint(0, 13)
                    gene.target = random.randint(max(gene.source + 1, 7), 15)
                    gene.weight = random.uniform(-1, 1)

class NeuralNetwork:
    def __init__(self, genome):
        self.genome = genome
        self.neurons = np.zeros(16)
        
    def activate(self, inputs):
        self.neurons.fill(0)
        self.neurons[0:7] = inputs
        sorted_genes = sorted(self.genome.genes, key=lambda g: g.target)
        for gene in sorted_genes:
            val = self.neurons[gene.source]
            if gene.source >= 7:
                val = max(0, val)
            self.neurons[gene.target] += val * gene.weight
        return self.neurons[14], self.neurons[15]
