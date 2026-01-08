# -*- coding: utf-8 -*-
# genetic_algo.py - El algoritmo de Selección Natural
# Aquí es donde ocurre la magia de la evolución: los mejores sobreviven y tienen hijos.

import random
import copy
import numpy as np
import pickle
import os
import glob
from .brain import Genome
from config import *

# Carpeta donde guardamos a los campeones
GENOMES_DIR = "saved_genomes"
# Archivo legacy (para compatibilidad con guardados anteriores)
BEST_GENOME_FILE = "best_genome.pkl"

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
        
        # --- OPTIMIZACIÓN: Limitar el historial para evitar lag en sesiones largas ---
        # Mantenemos solo las últimas 100 generaciones para que no se acumule memoria
        MAX_HISTORY = 100
        if len(self.history) > MAX_HISTORY:
            self.history = self.history[-MAX_HISTORY:]

        
        new_population = []
        
        # Si elegimos modo DYNAMIC y la IA no mejora, subimos la mutación para que "arriesgue" más
        eff_mutation = self.mutation_rate
        if self.strategy == "DYNAMIC" and self.stagnation_counter > 10:
             eff_mutation = min(0.5, self.mutation_rate + 0.2)
        
        # 1. Selección y Elitismo (Los campeones pasan directito)
        # Estrategias:
        # - HOF: Siempre pasa el mejor de TODOS los tiempos
        # - GEN: Solo usa los mejores de ESTA generación (más diversidad)
        # - DYNAMIC: Como HOF pero con mutación adaptativa
        
        if self.strategy == "HOF":
             if self.global_best_genome:
                 new_population.append(copy.deepcopy(self.global_best_genome))
        elif self.strategy == "GEN":
             # No agregamos el mejor histórico, solo usamos los de esta ronda
             # Esto permite más exploración y diversidad genética
             pass
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

    def save_best_genome(self, name=None):
        """
        Guarda el mejor genoma de todos los tiempos en la carpeta de campeones.
        El nombre incluye el fitness para fácil identificación.
        """
        if self.global_best_genome is None:
            return False, "No hay ningún genoma campeón para guardar todavía."
        
        # Crear carpeta si no existe
        if not os.path.exists(GENOMES_DIR):
            os.makedirs(GENOMES_DIR)
        
        try:
            # Generar nombre automático con fitness si no se proporciona
            if name is None:
                name = f"campeon_{int(self.global_best_fitness)}pts"
            
            filepath = os.path.join(GENOMES_DIR, f"{name}.pkl")
            
            data = {
                "genome": {
                    "w1": self.global_best_genome.w1,
                    "b1": self.global_best_genome.b1,
                    "w2": self.global_best_genome.w2,
                    "b2": self.global_best_genome.b2,
                },
                "fitness": self.global_best_fitness,
                "generation": self.generation,
                "name": name
            }
            with open(filepath, "wb") as f:
                pickle.dump(data, f)
            return True, f"¡Campeón guardado! {name}"
        except Exception as e:
            return False, f"Error al guardar: {str(e)}"

    def load_best_genome(self, filepath=None):
        """
        Carga un genoma campeón desde un archivo.
        Lo pone como el mejor histórico y también lo mete a la población actual.
        """
        if filepath is None:
            return False, "No se especificó archivo a cargar."
            
        if not os.path.exists(filepath):
            return False, "El archivo no existe."
        
        try:
            with open(filepath, "rb") as f:
                data = pickle.load(f)
            
            # Recreamos el genoma desde los datos guardados
            loaded_genome = Genome(
                w1=data["genome"]["w1"],
                b1=data["genome"]["b1"],
                w2=data["genome"]["w2"],
                b2=data["genome"]["b2"]
            )
            
            # Lo ponemos como el mejor histórico
            self.global_best_genome = loaded_genome
            self.global_best_fitness = data["fitness"]
            
            # También lo metemos a la población actual para que compita
            if len(self.population) > 0:
                self.population[0] = copy.deepcopy(loaded_genome)
            
            name = data.get("name", "desconocido")
            return True, f"¡Campeón '{name}' cargado! Fitness: {int(data['fitness'])}"
        except Exception as e:
            return False, f"Error al cargar: {str(e)}"

    def list_saved_genomes(self):
        """
        Lista todos los genomas guardados en la carpeta.
        Retorna lista de tuplas: (nombre_display, filepath, fitness)
        """
        saved = []
        
        # Buscar en la nueva carpeta
        if os.path.exists(GENOMES_DIR):
            for filepath in glob.glob(os.path.join(GENOMES_DIR, "*.pkl")):
                try:
                    with open(filepath, "rb") as f:
                        data = pickle.load(f)
                    name = data.get("name", os.path.basename(filepath))
                    fitness = data.get("fitness", 0)
                    saved.append((f"🏆 {name} ({int(fitness)} pts)", filepath, fitness))
                except:
                    pass
        
        # Buscar archivo legacy (best_genome.pkl en raíz)
        if os.path.exists(BEST_GENOME_FILE):
            try:
                with open(BEST_GENOME_FILE, "rb") as f:
                    data = pickle.load(f)
                fitness = data.get("fitness", 0)
                saved.append((f"📁 Legacy ({int(fitness)} pts)", BEST_GENOME_FILE, fitness))
            except:
                pass
        
        # Ordenar por fitness (mayor primero)
        saved.sort(key=lambda x: x[2], reverse=True)
        
        return saved

    def has_saved_genome(self):
        """Revisa si ya existe algún campeón guardado."""
        return len(self.list_saved_genomes()) > 0
    
    def get_saved_fitness(self):
        """Obtiene el fitness del mejor campeón guardado."""
        saved = self.list_saved_genomes()
        if saved:
            return saved[0][2]  # El primer elemento (mayor fitness)
        return None

    def rename_genome(self, old_filepath, new_name):
        """
        Renombra un genoma guardado.
        Actualiza tanto el nombre en el archivo como el nombre del archivo.
        """
        if not os.path.exists(old_filepath):
            return False, "El archivo no existe."
        
        try:
            # Cargar datos existentes
            with open(old_filepath, "rb") as f:
                data = pickle.load(f)
            
            # Actualizar el nombre interno
            data["name"] = new_name
            
            # Crear nuevo filepath
            new_filepath = os.path.join(GENOMES_DIR, f"{new_name}.pkl")
            
            # Guardar con nuevo nombre
            with open(new_filepath, "wb") as f:
                pickle.dump(data, f)
            
            # Eliminar archivo viejo si es diferente
            if old_filepath != new_filepath and os.path.exists(old_filepath):
                os.remove(old_filepath)
            
            return True, f"Renombrado a '{new_name}'"
        except Exception as e:
            return False, f"Error al renombrar: {str(e)}"

    def delete_genome(self, filepath):
        """
        Elimina un genoma guardado.
        """
        if not os.path.exists(filepath):
            return False, "El archivo no existe."
        
        try:
            # Obtener nombre para el mensaje
            with open(filepath, "rb") as f:
                data = pickle.load(f)
            name = data.get("name", os.path.basename(filepath))
            
            os.remove(filepath)
            return True, f"'{name}' eliminado"
        except Exception as e:
            return False, f"Error al eliminar: {str(e)}"
