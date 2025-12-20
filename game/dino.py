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
        self.jump_t = 0.0 # 0 to 1
        
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
    def jump(self):
        if not self.is_jumping and not self.is_crouching:
            self.is_jumping = True
            self.jump_t = 0.0

    def crouch(self):
        if not self.is_jumping:
            self.is_crouching = True
            self.height = CROUCH_HEIGHT
            self.y = self.ground_y - self.height
        elif self.is_jumping:
            # Interrupt jump
            self.is_jumping = False
            self.jump_t = 0.0
            self.y = self.ground_y - self.height

    def stop_crouch(self):
        self.is_crouching = False
        self.height = PLAYER_HEIGHT
        self.y = self.ground_y - self.height

    def update(self):
        if self.is_jumping:
            # Quadratic jump: height = 4 * jump_h * t * (1 - t)
            self.jump_t += 1.0 / JUMP_DURATION
            if self.jump_t >= 1.0:
                self.is_jumping = False
                self.jump_t = 0.0
                self.y = self.ground_y - self.height
            else:
                h = 4 * JUMP_HEIGHT * self.jump_t * (1 - self.jump_t)
                self.y = (self.ground_y - self.height) - h
        
        # Hitbox (inset)
        padding_x = 10
        padding_y = 5
        self.rect = pygame.Rect(self.x + padding_x, self.y + padding_y, self.width - 2*padding_x, self.height - 2*padding_y)

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
