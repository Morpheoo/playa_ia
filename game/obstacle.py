# -*- coding: utf-8 -*-
import pygame
import math
import random
from config import *

class Obstacle:
    def __init__(self, x, width, height, type_name):
        self.x = x
        self.width = width
        self.height = height
        self.type_name = type_name
        self.y = GROUND_Y - self.height
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.removed = False

    def update(self, speed):
        self.x -= speed
        # Refined hitbox: shrink slightly to be forgiving
        padding_x = 5
        padding_y = 5
        self.rect = pygame.Rect(self.x + padding_x, self.y + padding_y, self.width - 2*padding_x, self.height - 2*padding_y)
        if self.x < -self.width:
            self.removed = True

    def draw(self, screen, assets=None):
        img_key = None
        if "cactus" in self.type_name:
            # We could map specific cactus types to specific keys if needed
            # For now, just use generic 'cactus' or 'cactus_small' / 'cactus_large' if available
            img_key = "cactus" 
        elif "car" in self.type_name:
            # type_name is like "car_0", "car_1", etc.
            img_key = self.type_name 
        elif "cone" in self.type_name:
            img_key = "cone"
        elif "beach_ball" in self.type_name:
            img_key = "beach_ball"
        elif "cooler" in self.type_name:
            img_key = "cooler"
        elif "dumbbell_box" in self.type_name:
            img_key = "dumbbell_box"
        elif "dumbbell" in self.type_name:
            img_key = "dumbbell"
        elif "surfboard" in self.type_name:
            img_key = "surfboard"
        elif "dron" in self.type_name:
            img_key = "dron"
            
        if assets and img_key and img_key in assets and assets[img_key]:
            sprite = pygame.transform.scale(assets[img_key], (int(self.width), int(self.height)))
            screen.blit(sprite, (self.x, self.y)) # Draw at x,y (visual) -- hitbox is separate
        else:
            color = (130, 130, 130)
            pygame.draw.rect(screen, color, self.rect) # Debug: draws the hitbox if no sprite, or sprite if not found

class CarObstacle(Obstacle):
    def __init__(self, x):
        variant = random.randint(0, 4)
        # Dimensions for cars based on player size
        # Formula: Double the previous size (1.8 -> 3.6)
        height = int(PLAYER_HEIGHT * 0.95 * 3.6)
        width = int(height * 1.5) # Widened from 1.2
        type_name = f"car_{variant}"
            
        super().__init__(x, width, height, type_name)
        
        # User Feedback: Cars are floating and too hard to jump.
        # Solution: Sink them 50px into the ground.
        self.y += 50
        self.rect.y = int(self.y)

    def update(self, speed):
        # Move
        self.x -= speed
        if self.x < -self.width:
            self.removed = True
            
        # Custom Hitbox for Car: Lower the top to allow "safe roof"
        # We want the hitbox to be only the bottom 70% of the sprite (30% safe top)
        # This covers doors/body as deadly, but allows roof walking.
        self.safe_top_pct = 0.3
        self.roof_offset = int(self.height * self.safe_top_pct)
        
        # Custom Hitbox for Car
        # Refined: Add horizontal padding to prevent "invisible death".
        # Player must clearly touch the car body (tires width).
        padding_x = 65
        
        # Rect(x, y, w, h)
        self.rect = pygame.Rect(self.x + padding_x, self.y + self.roof_offset, self.width - (2 * padding_x), self.height - self.roof_offset)

class Drone(Obstacle):
    def __init__(self, x):
        height_level = random.randint(0, 2)
        width = 46
        height = 40
        type_name = f"dron_{height_level}"
        
        super().__init__(x, width, height, type_name)
        
        if height_level == 0:
            self.base_y = GROUND_Y - height - 10
        elif height_level == 1:
            self.base_y = GROUND_Y - height - 50
        else:
            self.base_y = GROUND_Y - height - 90
            
        self.y = self.base_y
        
        # Reduced Hitbox for Drone
        # User requested smaller hitbox to make it easier to dodge
        padding = 10
        self.rect = pygame.Rect(self.x + padding, self.y + padding, self.width - 2*padding, self.height - 2*padding)
        self.float_timer = 0.0

    def update(self, speed):
        self.x -= speed
        if self.x < -self.width:
            self.removed = True
            
        # Float logic
        self.float_timer += 0.1
        self.y = self.base_y + math.sin(self.float_timer) * 20
        
        # Update hitbox with padding
        padding = 10
        self.rect.x = int(self.x + padding)
        self.rect.y = int(self.y + padding)

class ConeObstacle(Obstacle):
    def __init__(self, x):
        # Cone is small. Let's make it roughly half player height.
        height = int(PLAYER_HEIGHT * 0.7) # approx 47 * 0.7 = 33px. Maybe a bit bigger?
        # Let's try explicit pixels for clarity as requested -> "Small Lethal Obstacle"
        height = 50 
        width = 40 # Standard cone proportion
        
        type_name = "cone"
        super().__init__(x, width, height, type_name)
        
        # Grounded
        # Lowered by 10px to fix floating appearance
        self.y = GROUND_Y - self.height + 15
        
        # Exact Hitbox with heavy padding to be fair
        # Shrinking hitbox as requested (padding 5 -> 10)
        padding = 10
        self.rect = pygame.Rect(self.x + padding, self.y + padding, self.width - 2*padding, self.height - padding)

    def update(self, speed):
        self.x -= speed
        if self.x < -self.width:
            self.removed = True
        
        # Update rect position with padding
        padding = 10
        self.rect.x = int(self.x + padding)
        # y is static relative to ground

class BeachBall(Obstacle):
    def __init__(self, x):
        # Increased size as requested (60 -> 70)
        width = 70
        height = 70
        type_name = "beach_ball"
        super().__init__(x, width, height, type_name)
        
        # STRICT Ground Alignment + sink 10px
        # Lowered 10px to avoid floating
        self.y = GROUND_Y - self.height + 18
        
        # Hitbox: Padded to match contour (removed empty corners)
        padding = 19
        self.rect = pygame.Rect(self.x + padding, self.y + padding, self.width - 2*padding, self.height - padding)
        
    def update(self, speed):
        self.x -= speed
        if self.x < -self.width:
            self.removed = True
            
        padding = 19
        self.rect.x = int(self.x + padding)
        # rect.y stays constant at self.y + padding

class CoolerObstacle(Obstacle):
    def __init__(self, x):
        # Cooler dimensions (Medium-Small, Boxy)
        width = 60
        height = 50
        type_name = "cooler"
        super().__init__(x, width, height, type_name)
        
        # Grounded
        self.y = GROUND_Y - self.height
        
        # Hitbox
        padding = 5
        self.rect = pygame.Rect(self.x + padding, self.y + padding, self.width - 2*padding, self.height - padding)
        
    def update(self, speed):
        self.x -= speed
        if self.x < -self.width:
            self.removed = True
            
        padding = 5
        self.rect.x = int(self.x + padding)

class DumbbellObstacle(Obstacle):
    def __init__(self, x):
        # Dumbbell: Small, low obstacle
        width = 40
        height = 30
        type_name = "dumbbell"
        super().__init__(x, width, height, type_name)
        self.y = GROUND_Y - self.height
        
        # Padded hitbox
        padding = 5
        self.rect = pygame.Rect(self.x + padding, self.y + padding, self.width - 2*padding, self.height - padding)

    def update(self, speed):
        self.x -= speed
        if self.x < -self.width: self.removed = True
        padding = 5
        self.rect.x = int(self.x + padding)

class SurfboardObstacle(Obstacle):
    def __init__(self, x):
        # Surfboard: Tall, thin obstacle
        width = 30
        height = 80 # Quite tall, hard to jump over?
        type_name = "surfboard"
        super().__init__(x, width, height, type_name)
        self.y = GROUND_Y - self.height
        
        # Padded hitbox
        padding = 5
        self.rect = pygame.Rect(self.x + padding, self.y + padding, self.width - 2*padding, self.height - padding)

    def update(self, speed):
        self.x -= speed
        if self.x < -self.width: self.removed = True
        padding = 5
        self.rect.x = int(self.x + padding)

class DumbbellBoxObstacle(Obstacle):
    def __init__(self, x):
        # Box: Heavy, bit larger than cooler
        width = 70
        height = 60
        type_name = "dumbbell_box"
        super().__init__(x, width, height, type_name)
        self.y = GROUND_Y - self.height
        
        # Padded hitbox
        padding = 5
        self.rect = pygame.Rect(self.x + padding, self.y + padding, self.width - 2*padding, self.height - padding)

    def update(self, speed):
        self.x -= speed
        if self.x < -self.width: self.removed = True
        padding = 5
        self.rect.x = int(self.x + padding)
