# -*- coding: utf-8 -*-
# dino.py - El personaje principal (aunque ahora es un humano corredor)
# Aquí controlamos sus saltos, sus agachadas y su animación.

import pygame
import math
from config import *

class Dino:
    def __init__(self):
        # Posición inicial y tamaño (vienen de config.py)
        self.x = PLAYER_X
        self.y = GROUND_Y - PLAYER_HEIGHT
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.ground_y = GROUND_Y
        
        # Estados del personaje
        self.is_jumping = False
        self.is_crouching = False
        self.vel_y = 0.0 # Velocidad vertical (para saltar y caer)
        
        # Para controlar la animación de cuando se agacha (coachwalk)
        self.crouch_timer = 0.0
        self.crouch_frame_index = 0
        self.crouch_fps = 12 
        
        # Caja de colisión (hitbox)
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
    def jump(self):
        """Hace que el personaje salte si está en el suelo."""
        if not self.is_jumping:
            self.is_jumping = True
            self.vel_y = -13.5 # Impulso hacia arriba
            # If crouching, reset height
            if self.is_crouching:
                self.stop_crouch()

    def crouch(self):
        """Hace que el personaje se agache."""
        self.is_crouching = True
        self.height = CROUCH_HEIGHT
        # If in air, just flags crouching state. 
        # If we were on ground, adjust Y to sticky bottom? 
        # Actually easier to just change hitbox height.
        if not self.is_jumping:
            # Si está en el suelo, ajustamos su posición Y
            self.y = self.ground_y - self.height
        else:
            # "Caída rápida": si se agacha en el aire, cae más rápido
            self.vel_y += 2.0 

    def stop_crouch(self):
        """Vuelve a la altura normal."""
        self.is_crouching = False
        self.height = PLAYER_HEIGHT
        # If on ground, adjust Y up
        if not self.is_jumping:
            self.y = self.ground_y - self.height

    def update(self, target_ground_y=GROUND_Y):
        """Actualiza la posición del personaje según la gravedad y el suelo."""
        # Aplicamos gravedad
        self.vel_y += GRAVITY
        self.y += self.vel_y
        
        hit_ground = False
        
        # Revisamos si tocó el suelo (o el techo de un coche)
        if self.y + self.height >= target_ground_y:
            # Check if we were falling (vy > 0)
            if self.vel_y > 0: # Solo si estaba cayendo
                self.y = target_ground_y - self.height
                self.vel_y = 0.0
                self.is_jumping = False
                self.ground_y = target_ground_y
                hit_ground = True
        
        # Si se sale de una plataforma, vuelve a estar en el aire
        # Gravity above will naturally pull us down next frame
        if not hit_ground and self.y + self.height < target_ground_y:
            self.is_jumping = True 
        
        # Ajustamos el hitbox (un poco más pequeño que el dibujo para ser justos)
        padding_x = 10
        padding_y = 12
        self.rect = pygame.Rect(self.x + padding_x, self.y + padding_y, self.width - 2*padding_x, self.height - 2*padding_y)

    def update_animation(self, dt):
        """Actualiza el contador de tiempo para saber qué cuadro del dibujo mostrar."""
        if self.is_crouching:
            self.crouch_timer += dt
            frame_duration = 1.0 / self.crouch_fps
            
            while self.crouch_timer >= frame_duration:
                self.crouch_timer -= frame_duration
                self.crouch_frame_index += 1
                # Loop handled in draw or by limiting index max later?
                # Better to keep it unbounded here or modulo if we know length.
                # But we don't know asset length HERE. 
                # So we just increment. The draw function will modulo it.
        else:
            # Reset
            self.crouch_timer = 0.0
            self.crouch_frame_index = 0

    def draw(self, screen, assets=None, frame_count=0):
        """Dibuja al corredor en la pantalla."""
        sprite = None
        if assets:
            if self.is_jumping:
                if "dino_jump" in assets: sprite = assets["dino_jump"]
                elif "dino" in assets: sprite = assets["dino"]
            else:
                # Animación de correr
                if "dino_run" in assets and isinstance(assets["dino_run"], list) and len(assets["dino_run"]) > 0:
                     # Calculate frame index based on global frame count (distance)
                     # Speed of animation: change frame every 5 units of distance?
                     frames = assets["dino_run"]
                     idx = (frame_count // 10) % len(frames)
                     sprite = frames[idx]
                elif "dino_run1" in assets and "dino_run2" in assets:
                    # Legacy 2-frame individual files
                    if (frame_count // 10) % 2 == 0:
                        sprite = assets["dino_run1"]
                    else:
                        sprite = assets["dino_run2"]
                elif "dino" in assets:
                   sprite = assets["dino"]
        
        if sprite:
            target_size = (int(self.width), int(self.height))
            
            # --- OPTIMIZACIÓN: Caché de escalado ---
            # Como los dinos tienen animaciones, guardamos la versión escalada de cada frame
            if not hasattr(self, "_sprite_cache"):
                self._sprite_cache = {}
            
            sprite_id = id(sprite) # Usamos el ID del objeto para identificar el frame
            if sprite_id not in self._sprite_cache or self._sprite_cache[sprite_id][1] != target_size:
                # Solo escalamos si es un frame nuevo o el tamaño cambió
                self._sprite_cache[sprite_id] = (pygame.transform.scale(sprite, target_size), target_size)
            
            scaled_sprite = self._sprite_cache[sprite_id][0]
            screen.blit(scaled_sprite, (self.x, self.y))
        
        # Nuevo sistema de animación para humanos
        elif assets and "human_anim" in assets:
            
            # Decide on frame based on state
            frame = None
            
            if self.is_crouching and "coachwalk" in assets and assets["coachwalk"]:
                frames = assets["coachwalk"]
                # Modulo index to loop
                idx = self.crouch_frame_index % len(frames)
                frame = frames[idx]
            else:
                # Default Idle/Run
                anim = assets["human_anim"]
                frame = anim.get_current_frame()
            
            if frame:
                # Centramos el dibujo en la caja de colisión
                # Sprite X: center of hitbox - half sprite width
                dest_x = (self.x + self.width / 2) - (frame.get_width() / 2)
                
                # Sprite Y: bottom of hitbox - sprite height
                # hitbox bottom is self.y + self.height
                dest_y = (self.y + self.height) - frame.get_height()
                
                screen.blit(frame, (dest_x, dest_y))
        
        else:
            # Si no hay dibujos, dibujamos un rectángulo gris
            color = (83, 83, 83) if not self.is_crouching else (150, 150, 150)
            pygame.draw.rect(screen, color, self.rect)
