# -*- coding: utf-8 -*-
# spritesheet.py - Manejador de hojas de sprites
# Permite extraer dibujos individuales de una imagen que contiene muchos.

import pygame
import json
import os

class SpriteSheet:
    def __init__(self, image_path, json_path):
        """
        Carga la imagen PNG y lee el archivo JSON que dice dónde está cada cuadro.
        """
        self.image = pygame.image.load(image_path).convert_alpha()
        
        with open(json_path, 'r') as f:
            self.data = json.load(f)
            
        self.frames_data = self.data["frames"] # Lista con la posición de cada dibujo
        
    def get_frame(self, index) -> pygame.Surface:
        """
        Extrae un cuadro específico usando su índice.
        Devuelve una "subsuperficie" de la imagen original.
        """
        if index < 0 or index >= len(self.frames_data):
            raise IndexError("Índice de cuadro fuera de rango")
            
        frame_data = self.frames_data[index]
        x, y, w, h = frame_data["x"], frame_data["y"], frame_data["w"], frame_data["h"]
        
        rect = pygame.Rect(x, y, w, h)
        return self.image.subsurface(rect)
