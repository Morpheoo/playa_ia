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

# Optional: Keyboard for manual play
try:
    import keyboard
except ImportError:
    keyboard = None

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

    st.session_state.assets = {} # Store pygame surfaces

# Load default assets from disk (Ensure this runs if assets are empty)
if 'assets' not in st.session_state or not st.session_state.assets:
    st.session_state.assets = {}
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

        # 1.7 Load Coachwalk Animation
        coachwalk_frames = AssetManager.load_coachwalk_animation(assets_dir)
        if coachwalk_frames:
             st.session_state.assets["coachwalk"] = coachwalk_frames

        # 2. Load Static Images
        asset_files = {
            "dino": "dino.png",
            # "dino_run1": "dino_run1.png", # Deprecated if spritesheet exists
            # "dino_run2": "dino_run2.png", 
            "dino_jump": "dino_jump.png",
            "car_0": "car_0.png",
            "car_1": "car_1.png",
            "car_2": "car_2.png",
            "car_3": "car_3.png",
            "car_4": "car_4.png",
            "dron": "dron.png",
            "cone": "cone.png",
            "beach_ball": "beach_ball.png",
            "cooler": "cooler.png",
            "dumbbell": "dumbbell.png",
            "surfboard": "surfboard.png",
            "dumbbell_box": "dumbbell_box.png",
            "ground": "ground.png",
            "beach_net": "beach_net.png",
            "bar_crouch": "bar_crouch.png"
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

st.sidebar.markdown("---")
manual_mode = st.sidebar.checkbox("🎮 Modo Manual (@Jared Play)", value=False)
debug_mode = st.sidebar.checkbox("🟥 Mostrar Hitboxes", value=False)

if manual_mode and keyboard is None:
    st.sidebar.error("Librería 'keyboard' no instalada. Ejecuta: pip install keyboard")

# --- DEBUG TOOLS (New) ---
st.sidebar.markdown("---")
st.sidebar.header("🛠️ Herramientas de Diseño")
obs_to_spawn = st.sidebar.selectbox("Seleccionar Obstáculo", 
    ["Tabla de Surf", "Coche", "Dron", "Cono", "Balón", "Nevera", "Mancuerna", "Caja Mancuernas", "Red Playa", "Barra Libre"])

col_d1, col_d2 = st.sidebar.columns(2)
with col_d1:
    if st.button("✨ Aparecer"):
        # Mapping names to classes
        from game.obstacle import (SurfboardObstacle, CarObstacle, Drone, ConeObstacle, BeachBall, 
                                 CoolerObstacle, DumbbellObstacle, DumbbellBoxObstacle,
                                 BeachNetObstacle, BarraLibreObstacle)
        obs_map = {
            "Tabla de Surf": SurfboardObstacle,
            "Coche": CarObstacle,
            "Dron": Drone,
            "Cono": ConeObstacle,
            "Balón": BeachBall,
            "Nevera": CoolerObstacle,
            "Mancuerna": DumbbellObstacle,
            "Caja Mancuernas": DumbbellBoxObstacle,
            "Red Playa": BeachNetObstacle,
            "Barra Libre": BarraLibreObstacle
        }
        new_obs = obs_map[obs_to_spawn](SCREEN_WIDTH // 2) # Spawn in the middle for visibility
        st.session_state.engine.obstacles.append(new_obs)
        st.session_state.render_trigger = time.time() # Force a render

with col_d2:
    if st.button("🗑️ Limpiar"):
        st.session_state.engine.clear_obstacles()
        st.session_state.render_trigger = time.time()
# -------------------------

# Manual uploaders removed as per user request. Assets are loaded from assets/ directory.

# Update parameters in GA
st.session_state.ga.set_params(pop_size, mutation_rate, selection_ratio, elitism)

# Controls
col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("Start / Resume", key="start_btn"):
        st.session_state.running = True
        
        # Enforce Manual Mode Setup
        if manual_mode:
            # If we are in manual mode but have wrong number of dinos or just switching
            if len(st.session_state.engine.dinos) != 1:
                st.session_state.engine.reset(num_dinos=1)
                st.session_state.networks = []
                st.session_state.generation_complete = False
        
        elif st.session_state.generation_complete or len(st.session_state.engine.dinos) == 0:
            # Start new generation (AI Mode)
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
        frame_start_time = time.time()

        
        # Simulation Loop
        for _ in range(sim_speed):
            if not st.session_state.running: break
            
            # 1. Get Game State
            state = st.session_state.engine.get_game_state()
            obs = state["next_obstacle"]
            
            # 2. AI Decision for each dino
            if manual_mode and keyboard:
                 # MANUAL CONTROL
                 for dino in st.session_state.engine.dinos:
                     if getattr(dino, "dead", False): continue
                     
                     if keyboard.is_pressed('up') or keyboard.is_pressed('space') or keyboard.is_pressed('w'):
                         dino.jump()
                     
                     if keyboard.is_pressed('down') or keyboard.is_pressed('s'):
                         dino.crouch()
                     else:
                         dino.stop_crouch()
                         
            elif st.session_state.networks and len(st.session_state.networks) == len(st.session_state.engine.dinos):
                # 2. Strict Input Definition (6 Normalized Features)
                # DistanceX_norm, ObsY_norm, ObsW_norm, ObsH_norm, PlayerY_norm, Speed_norm
                
                # Get next obstacle data
                dist_x = 0
                obs_y = 0
                obs_w = 0
                obs_h = 0
                
                if obs:
                    # distanceX = (ox - (px + pw))
                    # We assume dino is at PLAYER_X. ox is obs.x (left edge).
                    # Dino width is PLAYER_WIDTH (approx).
                    dist_raw = obs.x - (PLAYER_X + PLAYER_WIDTH)
                    dist_x = max(0, dist_raw)
                    obs_y = obs.y
                    obs_w = obs.width
                    obs_h = obs.height
                else:
                    # Null obstacle
                    dist_x = WORLD_W # Max distance
                    obs_y = 0
                    obs_w = 0
                    obs_h = 0

                # Normalize [0, 1]
                inputs = np.zeros(INPUT_SIZE) # Size 6
                inputs[0] = np.clip(dist_x / WORLD_W, 0, 1) # DistX
                inputs[1] = np.clip(obs_y / WORLD_H, 0, 1)  # ObsY
                inputs[2] = np.clip(obs_w / WORLD_W, 0, 1)  # ObsW
                inputs[3] = np.clip(obs_h / WORLD_H, 0, 1)  # ObsH
                
                # PlayerY and Speed are per dino / global
                norm_speed = np.clip((state["speed"] - SPEED_MIN) / (SPEED_MAX - SPEED_MIN), 0, 1)
                inputs[5] = norm_speed # Speed is idx 5
                
                for i, dino in enumerate(st.session_state.engine.dinos):
                    if getattr(dino, "dead", False): continue
                    
                    inputs[4] = np.clip(dino.y / WORLD_H, 0, 1) # PlayerY is idx 4
                    
                    # Activate NN (Returns [p_jump, p_crouch])
                    preds = st.session_state.networks[i].activate(inputs)
                    
                    # 3. Multi-label Decision Logic
                    jump = preds[0] > JUMP_THRESHOLD
                    crouch = preds[1] > CROUCH_THRESHOLD
                    
                    if jump:
                        dino.jump()
                    
                    if crouch:
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
             
             # Also update per-dino animations (coachwalk)
             for dino in st.session_state.engine.dinos:
                 if not getattr(dino, "dead", False):
                     # We can add a method to dino to handle its own animation state
                     if hasattr(dino, "update_animation"):
                        dino.update_animation(anim_dt)
        
        # 4. Render
        st.session_state.engine.draw(surface, st.session_state.assets, debug_mode)
        
        # Convert pygame surface to image
        img_data = pygame.surfarray.array3d(surface)
        img_data = img_data.transpose([1, 0, 2])
        img = Image.fromarray(img_data)
        
        # Update UI
        # Use numpy array directly for speed and avoid PIL overhead
        try:
            game_placeholder.image(img_data, channels="RGB", output_format="JPEG", width="stretch")
        except Exception:
            pass
        
        # Stats
        alive_count = sum(1 for d in st.session_state.engine.dinos if not getattr(d, "dead", False))
        gen_text.metric("Generación", st.session_state.ga.generation)
        alive_text.metric("Agentes Vivos", alive_count)
        nn_count_text.metric("Redes Neuronales Activas", len(st.session_state.networks))
        # Use Global Best for "Mejor Histórico"
        best_text.metric("Mejor Histórico", f"{int(st.session_state.ga.global_best_fitness)}")
        curr_fit_text.metric("Fitness Actual", f"{int(st.session_state.engine.distance_traveled)}")
        
        # Check Gen Completion
        if st.session_state.engine.game_over:
            if manual_mode:
                # Just reset for another run
                st.session_state.engine.reset(num_dinos=1)
                st.session_state.networks = []
                time.sleep(1)
            else:
                # Evolve (AI Mode)
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
                
                # Optional: Update Graph (Layered MLP Visualization)
                best_genome = st.session_state.ga.population[0]
                
                fig = plt.figure(figsize=(8, 6))
                ax = fig.add_subplot(111)
                ax.axis('off')
                
                # Layout Config
                layer_sizes = [INPUT_SIZE, HIDDEN_SIZE, OUTPUT_SIZE]
                layer_names = ["Input", "Hidden", "Output"]
                node_labels = [
                    ["DistX", "ObsY", "ObsW", "ObsH", "PlyY", "Spd"],
                    ["H1", "H2", "H3", "H4", "H5"],
                    ["Jump", "Crouch"]
                ]
                
                v_spacing = 1.0 / max(layer_sizes)
                h_spacing = 0.8
                
                # Node Positions
                # Dict: (layer_idx, node_idx) -> (x, y)
                positions = {}
                for l in range(len(layer_sizes)):
                    n = layer_sizes[l]
                    x = l * h_spacing
                    for i in range(n):
                        # Center vertically
                        y = 0.5 + (n - 1) * v_spacing / 2.0 - i * v_spacing
                        positions[(l, i)] = (x, y)
                        
                        # Draw Node
                        circle = plt.Circle((x, y), 0.04, color='skyblue', ec='black', zorder=4)
                        ax.add_patch(circle)
                        # Label
                        lbl = node_labels[l][i] if i < len(node_labels[l]) else ""
                        ax.text(x - 0.08 if l==0 else x + 0.08 if l==2 else x, y + 0.06, lbl, 
                                ha='center', fontsize=8, zorder=5)

                # Draw Connections strictly (Fully Connected)
                # Input -> Hidden (W1)
                w1 = best_genome.w1 #(Hidden, Input)
                max_w = np.max(np.abs(w1)) if w1.size > 0 else 1.0
                
                for i in range(INPUT_SIZE):
                    for h in range(HIDDEN_SIZE):
                        weight = w1[h, i]
                        # Alpha/Thickness based on magnitude
                        alpha = min(1.0, abs(weight) / max_w)
                        color = 'red' if weight < 0 else 'green'
                        linewidth = 0.5 + 2 * (abs(weight) / max_w)
                        
                        p1 = positions[(0, i)]
                        p2 = positions[(1, h)]
                        ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=color, alpha=alpha, linewidth=linewidth, zorder=1)

                # Hidden -> Output (W2)
                w2 = best_genome.w2 # (Output, Hidden)
                # We can re-calc max_w or use same scale. Let's re-calc strict per layer or global?
                # Per layer is fine.
                max_w2 = np.max(np.abs(w2)) if w2.size > 0 else 1.0
                
                for h in range(HIDDEN_SIZE):
                    for o in range(OUTPUT_SIZE):
                        weight = w2[o, h]
                        alpha = min(1.0, abs(weight) / max_w2)
                        color = 'red' if weight < 0 else 'green'
                        linewidth = 0.5 + 2 * (abs(weight) / max_w2)
                        
                        p1 = positions[(1, h)]
                        p2 = positions[(2, o)]
                        ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=color, alpha=alpha, linewidth=linewidth, zorder=1)

                graph_placeholder.pyplot(fig)
                plt.close(fig)
    
                time.sleep(1)
        
        # Cap FPS to 30 to avoid overloading Streamlit media storage
        elapsed_frame = time.time() - frame_start_time
        target_frame_time = 1.0 / 30.0
        if elapsed_frame < target_frame_time:
            time.sleep(target_frame_time - elapsed_frame)
        
else:
    # --- REAL-TIME PREVIEW WHEN PAUSED (New) ---
    surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    st.session_state.engine.draw(surface, st.session_state.assets, debug_mode)
    img_data = pygame.surfarray.array3d(surface)
    img_data = img_data.transpose([1, 0, 2])
    game_placeholder.image(img_data, channels="RGB", output_format="JPEG", width="stretch")
    # ------------------------------------------
    
    # Use a separate info call so it doesn't overwrite the image
    st.info("⏸️ Juego Pausado. Presiona 'Start' para continuar o usa las herramientas de diseño.")
    
    if st.session_state.ga.history:
        df = pd.DataFrame(st.session_state.ga.history)
        chart_placeholder.line_chart(df.set_index("gen"))
