# -*- coding: utf-8 -*-
import pygame
import math
from config import *

class Dino:
    def __init__(self):
        self.x = PLAYER_X
        self.y = GROUND_Y - PLAYER_HEIGHT
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.ground_y = GROUND_Y
        
        # State
        self.is_jumping = False
        self.is_crouching = False
        self.vel_y = 0.0
        
        # Coachwalk Animation State
        self.crouch_timer = 0.0
        self.crouch_frame_index = 0
        self.crouch_fps = 12 # 12 FPS target
        
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
    def jump(self):
        if not self.is_jumping:
            self.is_jumping = True
            self.vel_y = -13.5 # Initial jump velocity
            # If crouching, reset height
            if self.is_crouching:
                self.stop_crouch()

    def crouch(self):
        self.is_crouching = True
        self.height = CROUCH_HEIGHT
        # If in air, just flags crouching state. 
        # If we were on ground, adjust Y to sticky bottom? 
        # Actually easier to just change hitbox height.
        if not self.is_jumping:
            self.y = self.ground_y - self.height
        else:
            # Fast Fall
            self.vel_y += 2.0 # Push down

    def stop_crouch(self):
        self.is_crouching = False
        self.height = PLAYER_HEIGHT
        # If on ground, adjust Y up
        if not self.is_jumping:
            self.y = self.ground_y - self.height

    def update(self, target_ground_y=GROUND_Y):
        # Apply Gravity
        self.vel_y += GRAVITY
        self.y += self.vel_y
        
        hit_ground = False
        
        # Ground Collision
        if self.y + self.height >= target_ground_y:
            # Check if we were falling (vy > 0)
            if self.vel_y > 0:
                self.y = target_ground_y - self.height
                self.vel_y = 0.0
                self.is_jumping = False
                self.ground_y = target_ground_y
                hit_ground = True
        
        # If we are seemingly on ground but target_ground_y dropped (e.g. walked off platform)
        # Gravity above will naturally pull us down next frame
        if not hit_ground and self.y + self.height < target_ground_y:
            self.is_jumping = True # We are in air
        
        # Hitbox (inset)
        padding_x = 10
        padding_y = 5
        self.rect = pygame.Rect(self.x + padding_x, self.y + padding_y, self.width - 2*padding_x, self.height - 2*padding_y)

    def update_animation(self, dt):
        """
        Updates animation state based on real-time dt (seconds).
        """
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
        # Determine sprite
        sprite = None
        if assets:
            if self.is_jumping:
                if "dino_jump" in assets: sprite = assets["dino_jump"]
                elif "dino" in assets: sprite = assets["dino"]
            else:
                # Run animation
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
            # Check if sprite is a surface (it should be)
            if isinstance(sprite, pygame.Surface):
                scaled_sprite = pygame.transform.scale(sprite, (int(self.width), int(self.height))) 
                screen.blit(scaled_sprite, (self.x, self.y))
        
        # New Animation System Priority
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
                # Align bottom-center of sprite to bottom-center of hitbox
                # Sprite X: center of hitbox - half sprite width
                dest_x = (self.x + self.width / 2) - (frame.get_width() / 2)
                
                # Sprite Y: bottom of hitbox - sprite height
                # hitbox bottom is self.y + self.height
                dest_y = (self.y + self.height) - frame.get_height()
                
                screen.blit(frame, (dest_x, dest_y))
        
        else:
            color = (83, 83, 83) if not self.is_crouching else (150, 150, 150)
            pygame.draw.rect(screen, color, self.rect)
