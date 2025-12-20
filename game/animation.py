import pygame

class Animation:
    def __init__(self, frames: list[pygame.Surface], fps: int, loop=True):
        self.frames = frames
        self.fps = fps
        self.loop = loop
        
        if fps > 0:
            self.frame_duration = 1.0 / fps
        else:
            self.frame_duration = 0
            
        self.timer = 0.0
        self.index = 0
        
    def update(self, dt):
        """
        Update logic (NON-NEGOTIABLE)
        Use delta time (dt) in seconds
        Use a time accumulator
        Advance frames based on 1 / fps
        Loop cleanly without repeating the last frame
        """
        if self.frame_duration == 0 or not self.frames:
            return

        self.timer += dt
        
        while self.timer >= self.frame_duration:
            self.timer -= self.frame_duration
            self.index += 1
            
            if self.loop:
                self.index = self.index % len(self.frames)
            else:
                if self.index >= len(self.frames):
                    self.index = len(self.frames) - 1

    def get_current_frame(self):
        if not self.frames:
            return None
        return self.frames[self.index]
