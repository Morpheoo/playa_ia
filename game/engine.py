# -*- coding: utf-8 -*-
import pygame
import random
from config import *
from .dino import Dino
from .obstacle import Cactus, Bird

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
            
            if random.random() < BIRD_PROBABILITY:
                self.obstacles.append(Bird(SCREEN_WIDTH))
            else:
                self.obstacles.append(Cactus(SCREEN_WIDTH))

        alive_dinos = 0
        for dino in self.dinos:
            if not hasattr(dino, "dead"): dino.dead = False
            if dino.dead: continue
            
            dino.update()
            
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

    def draw(self, screen, assets=None):
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
