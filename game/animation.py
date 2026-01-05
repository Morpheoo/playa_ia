# -*- coding: utf-8 -*-
# animation.py - Sistema de animación simple
# Se encarga de pasar los cuadros de una animación según el tiempo.

import pygame

class Animation:
    def __init__(self, frames: list[pygame.Surface], fps: int, loop=True):
        self.frames = frames # Los dibujos (frames)
        self.fps = fps # Cuántos cuadros por segundo
        self.loop = loop # Si debe repetirse al terminar
        
        if fps > 0:
            self.frame_duration = 1.0 / fps # Duración de cada cuadro
        else:
            self.frame_duration = 0
            
        self.timer = 0.0 # Acumulador de tiempo
        self.index = 0 # Cuadro actual
        
    def update(self, dt):
        """
        Actualiza la animación basándose en el tiempo real (dt).
        Asegura que el paso de cuadros sea suave.
        """
        if self.frame_duration == 0 or not self.frames:
            return

        self.timer += dt
        
        # Mientras el tiempo acumulado sea mayor que la duración de un cuadro
        while self.timer >= self.frame_duration:
            self.timer -= self.frame_duration
            self.index += 1
            
            # Si llegamos al final, reiniciamos o nos quedamos en el último
            if self.loop:
                self.index = self.index % len(self.frames)
            else:
                if self.index >= len(self.frames):
                    self.index = len(self.frames) - 1

    def get_current_frame(self):
        """Devuelve el dibujo que toca mostrar ahora."""
        if not self.frames:
            return None
        return self.frames[self.index]
