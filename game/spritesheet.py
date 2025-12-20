import pygame
import json
import os

class SpriteSheet:
    def __init__(self, image_path, json_path):
        """
        Loads the PNG and parses the JSON.
        Stores frame metadata in order.
        """
        self.image = pygame.image.load(image_path).convert_alpha()
        
        with open(json_path, 'r') as f:
            self.data = json.load(f)
            
        self.frames_data = self.data["frames"] # Must be a list
        
    def get_frame(self, index) -> pygame.Surface:
        """
        Return a subsurface using pygame.Rect(x,y,w,h).
        Do NOT scale or filter the surface.
        """
        if index < 0 or index >= len(self.frames_data):
            raise IndexError("Frame index out of range")
            
        frame_data = self.frames_data[index]
        x = frame_data["x"]
        y = frame_data["y"]
        w = frame_data["w"]
        h = frame_data["h"]
        
        rect = pygame.Rect(x, y, w, h)
        return self.image.subsurface(rect)
