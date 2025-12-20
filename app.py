# -*- coding: utf-8 -*-
import streamlit as st
import os

# Set dummy video driver for headless pygame
os.environ["SDL_VIDEODRIVER"] = "dummy"

import pygame
import numpy as np
import time
from PIL import Image
import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd

# Initialize pygame display for surface conversion
pygame.init()
if pygame.display.get_surface() is None:
    pygame.display.set_mode((1, 1))

from game.engine import Engine
from game.assets import AssetManager
from ai.genetic_algo import GeneticAlgorithm
from ai.brain import NeuralNetwork
from config import *

# Set page config
st.set_page_config(page_title="AI Runner Evolution", layout="wide")

st.title("🏃 AI Runner Evolution: Algoritmo Genético")

# Initialize Session State
if 'engine' not in st.session_state:
    st.session_state.engine = Engine()
    st.session_state.ga = GeneticAlgorithm()
    st.session_state.running = False
    st.session_state.generation_complete = False
    st.session_state.networks = []
    st.session_state.start_time = time.time()
    st.session_state.frame_count = 0
    st.session_state.assets = {} # Store pygame surfaces

    # Load default assets from disk
    assets_dir = os.path.join(os.getcwd(), "assets")
    if os.path.exists(assets_dir):
        # 1. Load SpriteSheets
        spritesheet_json = os.path.join(assets_dir, "dino_run_spritesheet.json")
        if os.path.exists(spritesheet_json):
             frames = AssetManager.load_spritesheet(spritesheet_json, assets_dir)
             if frames:
                 st.session_state.assets["dino_run"] = frames
                 # Use first frame as default static dino if not present
                 if "dino" not in st.session_state.assets:
                     st.session_state.assets["dino"] = frames[0]

        # 1.5 Load Human Animation (New System)
        human_anim = AssetManager.load_human_animation(assets_dir)
        if human_anim:
            st.session_state.assets["human_anim"] = human_anim
            st.session_state.last_time = time.time()

        # 1.6 Load Backgrounds
        bg_surfs = AssetManager.load_backgrounds(assets_dir)
        if bg_surfs:
            st.session_state.assets["backgrounds"] = bg_surfs

        # 2. Load Static Images
        asset_files = {
            "dino": "dino.png",
            # "dino_run1": "dino_run1.png", # Deprecated if spritesheet exists
            # "dino_run2": "dino_run2.png", 
            "dino_jump": "dino_jump.png",
            "cactus": "cactus.png",
            "bird": "bird.png",
            "ground": "ground.png"
        }
        
        for key, filename in asset_files.items():
            path = os.path.join(assets_dir, filename)
            if os.path.exists(path):
                # Don't overwrite if spritesheet already provided dino static
                if key == "dino" and "dino" in st.session_state.assets:
                    continue
                    
                surf = AssetManager.load_image(path)
                if surf:
                    st.session_state.assets[key] = surf

# Sidebar - Parameters
st.sidebar.header("Parámetros de Entrenamiento")
pop_size = st.sidebar.slider("Población", 10, 100, POPULATION_SIZE, step=10)
mutation_rate = st.sidebar.slider("Tasa de Mutación", 0.0, 1.0, MUTATION_RATE, 0.01)
selection_ratio = st.sidebar.slider("Proporción de Selección", 0.01, 0.5, SELECTION_RATIO, 0.01)
elitism = st.sidebar.slider("Elitismo", 0, 50, ELITISM_COUNT, 1)

st.sidebar.header("Parámetros del Juego")
speed_init = st.sidebar.slider("Velocidad Inicial", 2.0, 15.0, float(INITIAL_GAME_SPEED), 0.5)
bird_prob = st.sidebar.slider("Probabilidad de Pájaros", 0.0, 0.5, BIRD_PROBABILITY, 0.05)

st.sidebar.header("Simulación")
sim_speed = st.sidebar.select_slider("Velocidad de Simulación", options=[1, 2, 4, 8, 16], value=1)

# Manual uploaders removed as per user request. Assets are loaded from assets/ directory.

# Update parameters in GA
st.session_state.ga.set_params(pop_size, mutation_rate, selection_ratio, elitism)

# Controls
col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("Start / Resume"):
        st.session_state.running = True
        if st.session_state.generation_complete or len(st.session_state.engine.dinos) == 0:
            # Start new generation
            genomes = st.session_state.ga.population
            st.session_state.engine.reset(num_dinos=len(genomes))
            st.session_state.networks = [NeuralNetwork(g) for g in genomes]
            st.session_state.generation_complete = False

with col2:
    if st.button("Pause"):
        st.session_state.running = False

with col3:
    if st.button("Reset All"):
        st.session_state.engine = Engine()
        st.session_state.ga = GeneticAlgorithm()
        st.session_state.running = False
        st.session_state.generation_complete = False
        st.session_state.networks = []
        st.session_state.assets = {} # Reset to clear manual overrides?
        # Re-load defaults? Simple way:
        st.cache_data.clear() # Maybe too aggressive. 
        # For now, just reset session state flags. User can refresh page to reload defaults.

with col4:
    if st.button("Next Gen (Skip)"):
        if not st.session_state.generation_complete:
            # Finish current gen forcibly
            fitnesses = [d.fitness if hasattr(d, "fitness") else st.session_state.engine.distance_traveled for d in st.session_state.engine.dinos]
            st.session_state.ga.next_generation(fitnesses)
            st.session_state.engine.reset(num_dinos=len(st.session_state.ga.population))
            st.session_state.networks = [NeuralNetwork(g) for i, g in enumerate(st.session_state.ga.population)]

# Main Layout
game_col, stats_col = st.columns([2, 1])

with game_col:
    game_placeholder = st.empty()
    
with stats_col:
    st.subheader("Estadísticas")
    gen_text = st.empty()
    alive_text = st.empty()
    nn_count_text = st.empty()
    best_text = st.empty()
    curr_fit_text = st.empty()
    
    st.subheader("Progreso de Fitness")
    chart_placeholder = st.empty()

# Graph Visualization
with st.expander("Ver Red Neuronal del Mejor Agente"):
    graph_placeholder = st.empty()

# Game Loop
if st.session_state.running:
    # Pygame Surface for rendering
    surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    
    while st.session_state.running:
        
        # Simulation Loop
        for _ in range(sim_speed):
            if not st.session_state.running: break
            
            # 1. Get Game State
            state = st.session_state.engine.get_game_state()
            obs = state["next_obstacle"]
            
            # 2. AI Decision for each dino
            if st.session_state.networks and len(st.session_state.networks) == len(st.session_state.engine.dinos):
                inputs = np.zeros(7)
                if obs:
                    inputs[0] = (obs.x - PLAYER_X) / SCREEN_WIDTH
                    inputs[1] = obs.x / SCREEN_WIDTH
                    inputs[2] = obs.y / SCREEN_HEIGHT
                    inputs[3] = obs.width / 100
                    inputs[4] = obs.height / 100
                else:
                    inputs[0] = 1.0 
                    inputs[1] = 1.0
                    inputs[2] = 1.0
                    inputs[3] = 0.0
                    inputs[4] = 0.0
                
                inputs[6] = state["speed"] / 10.0
                
                for i, dino in enumerate(st.session_state.engine.dinos):
                    if getattr(dino, "dead", False): continue
                    
                    inputs[5] = dino.y / SCREEN_HEIGHT
                    
                    # Activate NN
                    up_out, down_out = st.session_state.networks[i].activate(inputs)
                    
                    if up_out > 0.5:
                        dino.jump()
                    elif down_out > 0.5:
                        dino.crouch()
                    else:
                        dino.stop_crouch()
            
            # 3. Update Engine
            st.session_state.engine.update()
            
            if st.session_state.engine.game_over:
                 break
        
        # 3.5 Update Animation (Once per render frame)
        if "human_anim" in st.session_state.assets:
             # Calculate real dt for smooth animation
             now = time.time()
             # If last_time not in session (e.g. reload), init it
             if 'last_time' not in st.session_state: st.session_state.last_time = now
             
             anim_dt = now - st.session_state.last_time
             st.session_state.last_time = now
             # Cap dt to prevent huge jumps on lag
             if anim_dt > 0.1: anim_dt = 0.1
             
             st.session_state.assets["human_anim"].update(anim_dt)
        
        # 4. Render
        st.session_state.engine.draw(surface, st.session_state.assets)
        
        # Convert pygame surface to image
        img_data = pygame.surfarray.array3d(surface)
        img_data = img_data.transpose([1, 0, 2])
        img = Image.fromarray(img_data)
        
        # Update UI
        # Use numpy array directly for speed and avoid PIL overhead
        game_placeholder.image(img_data, channels="RGB", output_format="JPEG", width="stretch")
        
        # Stats
        alive_count = sum(1 for d in st.session_state.engine.dinos if not getattr(d, "dead", False))
        gen_text.metric("Generación", st.session_state.ga.generation)
        alive_text.metric("Agentes Vivos", alive_count)
        nn_count_text.metric("Redes Neuronales Activas", len(st.session_state.networks))
        best_text.metric("Mejor Histórico", f"{int(st.session_state.ga.best_fitness)}")
        curr_fit_text.metric("Fitness Actual", f"{int(st.session_state.engine.distance_traveled)}")
        
        # Check Gen Completion
        if st.session_state.engine.game_over:
            # Evolve
            fitnesses = [d.fitness for d in st.session_state.engine.dinos]
            st.session_state.ga.next_generation(fitnesses)
            
            # Plot progress
            if st.session_state.ga.history:
                df = pd.DataFrame(st.session_state.ga.history)
                chart_placeholder.line_chart(df.set_index("gen"))
            
            # Reset engine for next gen
            genomes = st.session_state.ga.population
            st.session_state.engine.reset(num_dinos=len(genomes))
            st.session_state.networks = [NeuralNetwork(g) for g in genomes]
            
            # Optional: Update Graph
            best_genome = st.session_state.ga.population[0]
            
            fig, ax = plt.subplots(figsize=(6, 4))
            G = nx.DiGraph()
            for g in best_genome.genes:
                G.add_edge(g.source, g.target, weight=g.weight)
            
            pos = {}
            for i in range(7): pos[i] = (0, i)
            for i in range(7, 14): pos[i] = (1, i-7)
            for i in range(14, 16): pos[i] = (2, (i-14)*3 + 2)
            
            nx.draw(G, pos, ax=ax, with_labels=True, node_color='skyblue', edge_color='gray', node_size=500, font_size=8)
            graph_placeholder.pyplot(fig)
            plt.close(fig)

            time.sleep(1)
        
        time.sleep(0.01)
        
else:
    game_placeholder.info("Presiona 'Start' para iniciar la evolución.")
    
    if st.session_state.ga.history:
        df = pd.DataFrame(st.session_state.ga.history)
        chart_placeholder.line_chart(df.set_index("gen"))
