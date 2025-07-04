import random
from darwins_rockets.rocket import Rocket
import math
import numpy as np
from config import GENE_MIN_MAGNITUDE, GENE_MAX_MAGNITUDE

# --- DNA class for modular genetic operations ---
class DNA:
    def __init__(self, genes):
        self.genes = genes  # List of numpy arrays

    @staticmethod
    def random_gene():
        angle = random.uniform(0, 2 * math.pi)
        magnitude = random.uniform(GENE_MIN_MAGNITUDE, GENE_MAX_MAGNITUDE)
        return np.array([magnitude * math.cos(angle), magnitude * math.sin(angle)], dtype=float)

    @classmethod
    def random(cls, length):
        return cls([cls.random_gene() for _ in range(length)])

    def crossover(self, other):
        point = random.randint(0, len(self.genes) - 1)
        child_genes = self.genes[:point] + other.genes[point:]
        return DNA(child_genes)

    def mutate(self, mutation_rate):
        new_genes = []
        for gene in self.genes:
            if random.random() < mutation_rate:
                new_genes.append(DNA.random_gene())
            else:
                new_genes.append(gene.copy())
        return DNA(new_genes)

    def to_list(self):
        return [g.copy() for g in self.genes]

class Population:
    def __init__(self, start_positions, dna_length, mutation_rate):
        self.start_positions = start_positions
        self.dna_length = dna_length
        self.mutation_rate = mutation_rate
        self.dnas = [DNA.random(self.dna_length) for _ in start_positions]

    def get_fitness_sum(self, rockets):
        return sum(rocket.fitness for rocket in rockets)

    def _get_normalized_fitnesses(self, rockets):
        fitnesses = [rocket.fitness for rocket in rockets]
        min_fitness = min(fitnesses) if fitnesses else 0
        max_fitness = max(fitnesses) if fitnesses else 1
        if max_fitness > min_fitness:
            return [(f - min_fitness) / (max_fitness - min_fitness) for f in fitnesses]
        else:
            return [1.0] * len(fitnesses)

    def normalize_fitness_for_selection(self, rockets):
        normalized_fitnesses = self._get_normalized_fitnesses(rockets)
        for rocket, norm in zip(rockets, normalized_fitnesses):
            rocket.fitness = norm

    def roulette_wheel_select(self, rockets):
        if not rockets:
            return None
        normalized_fitnesses = self._get_normalized_fitnesses(rockets)
        fitness_sum = sum(normalized_fitnesses)
        if fitness_sum == 0:
            return random.randint(0, len(rockets) - 1)
        pick = random.uniform(0, fitness_sum)
        current = 0
        for i, rocket in enumerate(rockets):
            current += normalized_fitnesses[i]
            if current >= pick:
                return i
        return len(rockets) - 1

    def next_generation(self, rockets):
        new_dnas = []
        if not rockets:
            # If no rockets, generate random DNA for all
            for _ in self.start_positions:
                new_dnas.append(DNA.random(self.dna_length))
            self.dnas = new_dnas
            return
        for _ in self.start_positions:
            idx1 = self.roulette_wheel_select(rockets)
            idx2 = self.roulette_wheel_select(rockets)
            if idx1 is None or idx2 is None:
                child_dna = DNA.random(self.dna_length)
            else:
                dna1 = DNA(rockets[idx1].get_dna_copy())
                dna2 = DNA(rockets[idx2].get_dna_copy())
                child_dna = dna1.crossover(dna2).mutate(self.mutation_rate)
            new_dnas.append(child_dna)
        self.dnas = new_dnas

    def get_dnas(self):
        return [dna.to_list() for dna in self.dnas] 