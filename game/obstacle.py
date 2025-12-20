# -*- coding: utf-8 -*-
import pygame
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
        elif "bird" in self.type_name:
            img_key = "bird"
            
        if assets and img_key and img_key in assets and assets[img_key]:
            sprite = pygame.transform.scale(assets[img_key], (int(self.width), int(self.height)))
            screen.blit(sprite, (self.x, self.y)) # Draw at x,y (visual) -- hitbox is separate
        else:
            color = (130, 130, 130)
            pygame.draw.rect(screen, color, self.rect) # Debug: draws the hitbox if no sprite, or sprite if not found

class Cactus(Obstacle):
    def __init__(self, x):
        variant = random.randint(0, 5)
        if variant < 3: # small
            width = 20 + variant * 5
            height = 35 + variant * 5
            type_name = f"cactus_small_{variant}"
        else: # large
            width = 40 + (variant-3) * 10
            height = 60 + (variant-3) * 5
            type_name = f"cactus_large_{variant}"
            
        super().__init__(x, width, height, type_name)

class Bird(Obstacle):
    def __init__(self, x):
        height_level = random.randint(0, 2)
        width = 46
        height = 40
        type_name = f"bird_{height_level}"
        
        super().__init__(x, width, height, type_name)
        
        if height_level == 0:
            self.y = GROUND_Y - height - 10
        elif height_level == 1:
            self.y = GROUND_Y - height - 50
        else:
            self.y = GROUND_Y - height - 90
            
        self.rect.y = self.y
