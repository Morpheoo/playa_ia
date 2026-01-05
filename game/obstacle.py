# -*- coding: utf-8 -*-
# obstacle.py - Todos los peligros que hay que esquivar
# Aquí definimos desde coches hasta drones y tablas de surf.

import pygame
import math
import random
from config import *

class Obstacle:
    """Clase base para todos los obstáculos."""
    def __init__(self, x, width, height, type_name):
        self.x = x
        self.width = width
        self.height = height
        self.type_name = type_name
        self.y = GROUND_Y - self.height
        # El rect es para las colisiones
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.removed = False

    def update(self, speed):
        """Mueve el obstáculo hacia la izquierda."""
        self.x -= speed
        # Ajustamos el hitbox para que sea un poco más permisivo
        padding_x = 5
        padding_y = 5
        self.rect = pygame.Rect(self.x + padding_x, self.y + padding_y, self.width - 2*padding_x, self.height - 2*padding_y)
        if self.x < -self.width:
            self.removed = True

    def draw(self, screen, assets=None):
        """Dibuja el obstáculo usando su imagen (sprite)."""
        img_key = None
        # Mapeamos el nombre del tipo con la imagen que cargamos en app.py
        if "car" in self.type_name:
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
        elif "beach_net" in self.type_name:
            img_key = "beach_net"
        elif "bar_crouch" in self.type_name:
            img_key = "bar_crouch"
        elif "surfboard" in self.type_name:
            img_key = "surfboard"
        elif "dron" in self.type_name:
            img_key = "dron"
            
        if assets and img_key and img_key in assets and assets[img_key]:
            # --- OPTIMIZACIÓN: Caché de escalado ---
            target_size = (int(self.width), int(self.height))
            if not hasattr(self, "_cached_sprite") or self._cached_size != target_size:
                self._cached_sprite = pygame.transform.scale(assets[img_key], target_size)
                self._cached_size = target_size
            
            screen.blit(self._cached_sprite, (self.x, self.y)) # Dibuja la imagen (visual)
        else:
            # Si no hay imagen, dibujamos un rectángulo gris
            color = (130, 130, 130)
            pygame.draw.rect(screen, color, self.rect)

class CarObstacle(Obstacle):
    """Coches: son grandes y se pueden pisar por arriba (el techo es seguro)."""
    def __init__(self, x):
        variant = random.randint(0, 4)
        # Dimensions for cars based on player size
        # Formula: Double the previous size (1.8 -> 3.6)
        height = int(PLAYER_HEIGHT * 0.55 * 3.6)
        width = int(height * 1.5) # Widened from 1.2
        type_name = f"car_{variant}"
            
        super().__init__(x, width, height, type_name)
        
        # Los hundimos un poco en el suelo para que no parezca que flotan
        self.y += 50
        self.rect.y = int(self.y)

    def update(self, speed):
        # Move
        self.x -= speed
        if self.x < -self.width:
            self.removed = True
            
        # El techo es seguro (safe roof)
        self.safe_top_pct = 0.3
        self.roof_offset = int(self.height * self.safe_top_pct)
        
        # El hitbox mortal solo está en la parte de abajo del coche
        padding_x = 65
        
        # Rect(x, y, w, h)
        self.rect = pygame.Rect(self.x + padding_x, self.y + self.roof_offset, self.width - (2 * padding_x), self.height - self.roof_offset)

class Drone(Obstacle):
    """Drones: vuelan a diferentes alturas y flotan arriba y abajo."""
    def __init__(self, x):
        height_level = random.randint(0, 2)
        width = 46
        height = 40
        type_name = f"dron_{height_level}"
        
        super().__init__(x, width, height, type_name)
        
        # Diferentes alturas según el nivel elegido
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
            
        # Lógica para que suba y baje (seno)
        self.float_timer += 0.1
        self.y = self.base_y + math.sin(self.float_timer) * 20
        
        # Update hitbox with padding
        padding = 10
        self.rect.x = int(self.x + padding)
        self.rect.y = int(self.y + padding)

class ConeObstacle(Obstacle):
    """Cono: obstáculo pequeño en el suelo."""
    def __init__(self, x):
        # Cone is small. Let's make it roughly half player height.
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
    """Pelota de playa: ancha pero bajita."""
    def __init__(self, x):
        # Increased size as requested (60 -> 70)
        width = 100
        height = 70
        type_name = "beach_ball"
        super().__init__(x, width, height, type_name)
        
        # STRICT Ground Alignment + sink 10px
        # Lowered 10px to avoid floating
        self.y = GROUND_Y - self.height + 20
        
       # Padded hitbox: Narrower and shorter (very low profile)
        # Horizontal: 10px each side -> 50px width
        # Top: 45px padding -> 25px height (stops at ground)
        self.padding_x = 30
        self.padding_top = 15
        
        hitbox_y = self.y + self.padding_top
        hitbox_height = GROUND_Y - hitbox_y
        
        self.rect = pygame.Rect(self.x + self.padding_x, hitbox_y, 
                               self.width - 2*self.padding_x, hitbox_height)

    def update(self, speed):
        self.x -= speed
        if self.x < -self.width: self.removed = True
        
        # Sync hitbox
        self.rect.x = int(self.x + self.padding_x)

class CoolerObstacle(Obstacle):
    """Nevera: obstáculo rectangular medio."""
    def __init__(self, x):
        # Cooler dimensions (Medium-Small, Boxy)
        # Resized: 60x50 -> 80x70
        width = 100
        height = 70
        type_name = "cooler"
        super().__init__(x, width, height, type_name)
        
        # Grounded: Sink +10px
        self.y = GROUND_Y - self.height + 20
        
        # Hitbox: Adjusted to match bulk of the cooler
        self.padding_x = 25
        self.padding_top = 20
        
        hitbox_y = self.y + self.padding_top
        hitbox_height = GROUND_Y - hitbox_y
        
        self.rect = pygame.Rect(self.x + self.padding_x, hitbox_y, 
                               self.width - 2*self.padding_x, hitbox_height)
        
    def update(self, speed):
        self.x -= speed
        if self.x < -self.width:
            self.removed = True
            
        self.rect.x = int(self.x + self.padding_x)

class DumbbellObstacle(Obstacle):
    """Mancuerna: muy pequeña y difícil de ver si vas rápido."""
    def __init__(self, x):
        # Dumbbell: Small, low obstacle
        # Resized: 70x70
        width = 70
        height = 70
        type_name = "dumbbell"
        super().__init__(x, width, height, type_name)
        
        # Grounded: Sink +30px to sit on the sand
        self.y = GROUND_Y - self.height + 30
        
        # Padded hitbox: Narrower and shorter (very low profile)
        # Horizontal: 10px each side -> 50px width
        # Top: 45px padding -> 25px height (stops at ground)
        self.padding_x = 15
        self.padding_top = 22
        
        hitbox_y = self.y + self.padding_top
        hitbox_height = GROUND_Y - hitbox_y
        
        self.rect = pygame.Rect(self.x + self.padding_x, hitbox_y, 
                               self.width - 2*self.padding_x, hitbox_height)

    def update(self, speed):
        self.x -= speed
        if self.x < -self.width: self.removed = True
        
        # Sync hitbox
        self.rect.x = int(self.x + self.padding_x)

class SurfboardObstacle(Obstacle):
    """Tabla de surf: alta y delgada."""
    def __init__(self, x):
        # Surfboard: Tall, thin obstacle
        # Resized: 30x80 -> 60x120
        width = 60
        height = 120
        type_name = "surfboard"
        super().__init__(x, width, height, type_name)
        
        # Grounded: Sink +45px to "stick" to the sand better
        self.y = GROUND_Y - self.height + 35
        
        # Padded hitbox: Narrower and shorter to match surfboard shape
        # Left/Right padding: 22px each -> 16px center
        # Top padding: 10px (to reach the blue tip)
        self.padding_x = 22
        self.padding_top = 20
        
        # Height adjustment: Make hitbox stop at the ground level (GROUND_Y)
        # Rect Y is self.y + padding_top
        # Ground is at GROUND_Y
        # So height = GROUND_Y - (self.y + padding_top)
        hitbox_y = self.y + self.padding_top
        hitbox_height = GROUND_Y - hitbox_y
        
        self.rect = pygame.Rect(self.x + self.padding_x, hitbox_y, 
                               self.width - 2 * self.padding_x, hitbox_height)

    def update(self, speed):
        self.x -= speed
        if self.x < -self.width: self.removed = True
        
        # Sync hitbox position
        self.rect.x = int(self.x + self.padding_x)

class DumbbellBoxObstacle(Obstacle):
    """Caja de mancuernas: pesada y grande."""
    def __init__(self, x):
        # Box: Heavy, bit larger than cooler
        # Resized: 120x120
        width = 120
        height = 120
        type_name = "dumbbell_box"
        super().__init__(x, width, height, type_name)
        
        # Grounded: Sink +30px to sit on the sand
        self.y = GROUND_Y - self.height + 45
        
        # Padded hitbox: Narrower and shorter (very low profile)
        # Horizontal: 10px each side -> 50px width
        # Top: 45px padding -> 25px height (stops at ground)
        self.padding_x = 30
        self.padding_top = 30
        
        hitbox_y = self.y + self.padding_top
        hitbox_height = GROUND_Y - hitbox_y
        
        self.rect = pygame.Rect(self.x + self.padding_x, hitbox_y, 
                               self.width - 2*self.padding_x, hitbox_height)

    def update(self, speed):
        self.x -= speed
        if self.x < -self.width: self.removed = True
        
        # Sync hitbox
        self.rect.x = int(self.x + self.padding_x)

class BeachNetObstacle(Obstacle):
    """Red de playa: está alta, así que HAY que agacharse."""
    def __init__(self, x):
        # Beach Net: Taller, suspended. Must crouch.
        width = 300
        height = 200
        type_name = "beach_net"
        super().__init__(x, width, height, type_name)
        
        # Position: Suspended. Bottom of sprite should be at GROUND_Y - offset.
        # But image might have poles. Let's assume the "lethal" part starts high.
        # Standing head is at GROUND_Y - 95.
        # Crouching head is at GROUND_Y - 40.
        # Let's place the bottom of the lethal zone at GROUND_Y - 55.
        self.y = GROUND_Y - height + 60 # Visual sink
        
        # Hitbox (Top zone)
        # Lethal padding from bottom: we want the bottom of the hitbox to be GROUND_Y - 55
        # hitbox_bottom = y + height - padding_bottom = GROUND_Y - 55
        # (GROUND_Y - height + 10) + height - padding_bottom = GROUND_Y - 55
        # GROUND_Y + 10 - padding_bottom = GROUND_Y - 55 => padding_bottom = 65
        self.padding_bottom = 160
        self.padding_x = 35
        self.padding_top = 40
        
        self.rect = pygame.Rect(self.x + self.padding_x, self.y + self.padding_top,
                               self.width - 2*self.padding_x, self.height - self.padding_bottom)

    def update(self, speed):
        self.x -= speed
        if self.x < -self.width: self.removed = True
        self.rect.x = int(self.x + self.padding_x)

class BarraLibreObstacle(Obstacle):
    """Barra libre: igual que la red, obliga a agacharse."""
    def __init__(self, x):
        # Bar: Thin, suspended. Must crouch.
        # User defined size
        width = 250
        height = 145
        type_name = "bar_crouch"
        super().__init__(x, width, height, type_name)
        
        # Grounded: Sink slightly to sit on sand
        self.y = GROUND_Y - height + 45

        # Hitbox: Elevated to the horizontal bar
        # Horizontal: 20px padding
        # Top: 10px padding to reach the bar
        # Height: 15px for the bar thickness
        self.padding_x = 70
        self.padding_top = 25
        self.hitbox_height = 15
        
        self.rect = pygame.Rect(self.x + self.padding_x, self.y + self.padding_top,
                               self.width - 2*self.padding_x, self.hitbox_height)

    def update(self, speed):
        self.x -= speed
        if self.x < -self.width: self.removed = True
        
        # Sync hitbox
        self.rect.x = int(self.x + self.padding_x)
