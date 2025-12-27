# -*- coding: utf-8 -*-
import pygame
import random
from config import *
from .dino import Dino
from .obstacle import (CarObstacle, Drone, ConeObstacle, BeachBall, CoolerObstacle, 
                         DumbbellObstacle, SurfboardObstacle, DumbbellBoxObstacle,
                         BeachNetObstacle, BarraLibreObstacle)

class Engine:
    def __init__(self):
        self.dinos = []
        self.obstacles = []
        self.game_speed = INITIAL_GAME_SPEED
        self.score = 0
        self.spawn_timer = 0
        self.next_spawn_dist = random.randint(MIN_SPAWN_DIST, MAX_SPAWN_DIST)
        self.distance_traveled = 0
        self.game_over = False

    def reset(self, num_dinos=1):
        self.dinos = [Dino() for _ in range(num_dinos)]
        self.obstacles = []
        self.game_speed = INITIAL_GAME_SPEED
        self.score = 0
        self.spawn_timer = 0
        self.next_spawn_dist = random.randint(MIN_SPAWN_DIST, MAX_SPAWN_DIST)
        self.distance_traveled = 0
        self.game_over = False

    def clear_obstacles(self):
        self.obstacles = []

    def update(self):
        if self.game_over:
            return

        self.game_speed += SPEED_INCREMENT
        self.distance_traveled += self.game_speed
        self.score = int(self.distance_traveled / 10)

        for obs in self.obstacles:
            obs.update(self.game_speed)
        
        self.obstacles = [obs for obs in self.obstacles if not obs.removed]

        self.spawn_timer += self.game_speed
        if self.spawn_timer >= self.next_spawn_dist:
            self.spawn_timer = 0
            self.next_spawn_dist = random.randint(MIN_SPAWN_DIST, MAX_SPAWN_DIST)
            
            r = random.random()
            # Probability Distribution (Total 1.0)
            # Birds/Drones: ~10% (BIRD_PROBABILITY)
            # Cars: Remaining (Default)
            
            if r < BIRD_PROBABILITY:
                self.obstacles.append(Drone(SCREEN_WIDTH))
            elif r < BIRD_PROBABILITY + 0.10: # 10% Red Playa
                self.obstacles.append(BeachNetObstacle(SCREEN_WIDTH))
            elif r < BIRD_PROBABILITY + 0.20: # 10% Barra Libre
                self.obstacles.append(BarraLibreObstacle(SCREEN_WIDTH))
            elif r < BIRD_PROBABILITY + 0.35: # 15% Cono
                self.obstacles.append(ConeObstacle(SCREEN_WIDTH))
            elif r < BIRD_PROBABILITY + 0.45: # 10% Pelota
                self.obstacles.append(BeachBall(SCREEN_WIDTH))
            elif r < BIRD_PROBABILITY + 0.55: # 10% Nevera
                self.obstacles.append(CoolerObstacle(SCREEN_WIDTH))
            elif r < BIRD_PROBABILITY + 0.65: # 10% Mancuerna
                self.obstacles.append(DumbbellObstacle(SCREEN_WIDTH))
            elif r < BIRD_PROBABILITY + 0.75: # 10% Tabla Surf
                self.obstacles.append(SurfboardObstacle(SCREEN_WIDTH))
            elif r < BIRD_PROBABILITY + 0.85: # 10% Caja Mancuernas
                self.obstacles.append(DumbbellBoxObstacle(SCREEN_WIDTH))
            else:
                self.obstacles.append(CarObstacle(SCREEN_WIDTH))

        alive_dinos = 0
        for dino in self.dinos:
            if not hasattr(dino, "dead"): dino.dead = False
            if dino.dead: continue
            
            target_ground = GROUND_Y
            
            # Check for Platform Collision (Car Roof)
            for obs in self.obstacles:
                if isinstance(obs, CarObstacle):
                    # Check horizontal overlap
                    # Dino is fixed at PLAYER_X to PLAYER_X + WIDTH
                    # Obs is moving.
                    dino_right = dino.x + dino.width
                    
                    # FIX: Use Hitbox (rect) boundaries for platform width, not sprite width.
                    # This ensures platform matches the deadly zone width exactly.
                    obs_left_hitbox = obs.rect.x
                    obs_right_hitbox = obs.rect.x + obs.rect.width
                    
                    if (dino.x < obs_right_hitbox and dino_right > obs_left_hitbox):
                        # Horizontal overlap. Now check if vertical position allows "landing"
                        # We land if we are above the deadly part?
                        # Actually, we land if we are roughly at or above the roof level.
                        # Roof level is determined by safe_top_pct logic in CarObstacle.
                        # update: hitbox_top_offset = height * 0.6
                        # so roof y = obs.y + (height * 0.6)
                        
                        # We land if we are roughly at or above the roof level.
                        # Roof level is determined by safe_top_pct logic in CarObstacle.
                        # Now exposed as obs.roof_offset

                        roof_offset = getattr(obs, 'roof_offset', 0)
                        roof_y = obs.y + roof_offset
                        
                        # If dino bottom is close to roof_y or above it, snap to it?
                        # Let's say if dino.y + dino.height <= roof_y + 30 (tolerance)
                        # We use a slightly generous tolerance so you don't fall through if you are just skimming the edge
                        if (dino.y + dino.height) <= (roof_y + 30):
                             target_ground = roof_y
            
            dino.update(target_ground)
            for obs in self.obstacles:
                if dino.rect.colliderect(obs.rect):
                    dino.dead = True
                    dino.fitness = self.distance_traveled
                    break
            
            if not dino.dead:
                alive_dinos += 1
        
        if alive_dinos == 0:
            self.game_over = True

    def get_game_state(self):
        next_obs = None
        for obs in self.obstacles:
            if obs.x + obs.width > PLAYER_X:
                next_obs = obs
                break
        
        return {
            "speed": self.game_speed,
            "next_obstacle": next_obs,
            "distance": self.distance_traveled
        }

    def draw(self, screen, assets=None, debug_mode=False):
        if assets and "backgrounds" in assets:
            backgrounds = assets["backgrounds"]
            # Cycling logic
            # 0-7000: set 0 (sunrise)
            # 7000-14000: set 1 (sunset)
            # 14000-21000: set 2 (night)
            # etc.
            
            CYCLE_POINTS = 3333
            TRANSITION_POINTS = 1000 # Increased for smoother/longer transition
            
            # Use distance_traveled directly as it matches the "Fitness" displayed to user
            stage = int(self.distance_traveled / CYCLE_POINTS) % 3
            offset = self.distance_traveled % CYCLE_POINTS
            
            bg_keys = ["sunrise", "sunset", "night"]
            current_key = bg_keys[stage]
            
            # Draw current
            if current_key in backgrounds:
                 screen.blit(backgrounds[current_key], (0, 0))
            else:
                 screen.fill((255, 255, 255))
            
            # Transition from previous if at start of cycle
            # Wait, user said "Once achieved, makes a light transition".
            # So if we just passed 7000 (offset is small), we want to fade FROM prev TO current.
            # So draw Prev, then blend Current on top? 
            # Or draw Current, then blend Prev on top with fading alpha?
            # Let's draw Prev opaque, then Current with Alpha increasing 0->1.
            
            if offset < TRANSITION_POINTS and self.distance_traveled > 500: # Skip transition at very start
                prev_stage = (stage - 1) % 3
                prev_key = bg_keys[prev_stage]
                
                alpha = int(255 * (offset / TRANSITION_POINTS))
                
                # We need to draw PREV opaque first
                if prev_key in backgrounds:
                     screen.blit(backgrounds[prev_key], (0, 0))
                
                # Then CURRENT with alpha
                if current_key in backgrounds:
                     curr_surf = backgrounds[current_key]
                     curr_surf.set_alpha(alpha)
                     screen.blit(curr_surf, (0, 0))
                     curr_surf.set_alpha(255) # Restore opaque for next frame/other uses
            
            
        else:
            screen.fill((255, 255, 255))
        
        # Ground
        if assets and "ground" in assets:
            ground_img = assets["ground"]
            g_width = ground_img.get_width()
            # Scroll offset based on distance
            # We need to compute offset % g_width
            offset = int(self.distance_traveled) % g_width
            
            # Draw 2 or more tiles to cover screen
            # x = -offset
            x = -offset
            while x < SCREEN_WIDTH:
                screen.blit(ground_img, (x, GROUND_Y))
                x += g_width
        else:
            pygame.draw.line(screen, (83, 83, 83), (0, GROUND_Y), (SCREEN_WIDTH, GROUND_Y), 2)
        
        for obs in self.obstacles:
            obs.draw(screen, assets)
            
        # Global frame count for animation
        frame_count = int(self.distance_traveled) # Use distance as proxy for frames or pass actual frames
        
        for dino in self.dinos:
            if not getattr(dino, "dead", False):
                dino.draw(screen, assets, frame_count)

        # DEBUG: Hitboxes
        if debug_mode:
            for obs in self.obstacles:
                # Red for obstacles
                pygame.draw.rect(screen, (255, 0, 0), obs.rect, 2)
                
                if isinstance(obs, CarObstacle):
                    # Blue for Safe Roof
                    # Draw a line or rect showing where the platform is
                    roof_y = obs.y + getattr(obs, 'roof_offset', 0)
                    start_x = obs.rect.x
                    end_x = obs.rect.x + obs.rect.width
                    pygame.draw.line(screen, (0, 0, 255), (start_x, roof_y), (end_x, roof_y), 3)
            
            for dino in self.dinos:
                if not getattr(dino, "dead", False):
                    # Green for dino
                    pygame.draw.rect(screen, (0, 255, 0), dino.rect, 2)
