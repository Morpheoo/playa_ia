# -*- coding: utf-8 -*-
import pygame
import json
import os
from PIL import Image, ImageFilter
from game.spritesheet import SpriteSheet
from game.animation import Animation

class AssetManager:
    @staticmethod
    def load_image(path):
        """Loads an image from a path and returns a pygame Surface."""
        try:
            # Open with PIL first to handle formats safely, then convert to bytes for Pygame
            img = Image.open(path)
            mode = img.mode
            size = img.size
            data = img.tobytes()
            surface = pygame.image.fromstring(data, size, mode).convert_alpha()
            return surface
        except Exception as e:
            print(f"Error loading image {path}: {e}")
            print(f"Error loading image {path}: {e}")
            return None

    @staticmethod
    def load_backgrounds(assets_dir):
        """
        Loads background_sunrise, background_sunset, background_night.
        Applies Gaussian Blur to each.
        Returns dictionary with keys 'sunrise', 'sunset', 'night'.
        """
        backgrounds = {}
        files = {
            "sunrise": "background_sunrise.png",
            "sunset": "background_sunset.png",
            "night": "background_night.png"
        }
        
        for key, filename in files.items():
            path = os.path.join(assets_dir, filename)
            if not os.path.exists(path):
                print(f"Background not found: {path}")
                continue
                
            try:
                img = Image.open(path)
                # Apply blur
                img = img.filter(ImageFilter.GaussianBlur(radius=3))
                
                mode = img.mode
                size = img.size
                data = img.tobytes()
                surface = pygame.image.fromstring(data, size, mode).convert()
                
                # Scale to screen size (800x400)
                surface = pygame.transform.scale(surface, (800, 400))
                backgrounds[key] = surface
            except Exception as e:
                print(f"Error loading background {filename}: {e}")
        
        return backgrounds

    @staticmethod
    def load_spritesheet(json_path, assets_dir):
        """
        Loads a spritesheet based on a JSON descriptor.
        Returns a list of pygame Surfaces (frames).
        """
        frames = []
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
            
            image_filename = data.get("image")
            image_path = os.path.join(assets_dir, image_filename)
            
            if not os.path.exists(image_path):
                print(f"Spritesheet image not found: {image_path}")
                return []
                
            sheet = AssetManager.load_image(image_path)
            if not sheet:
                return []
                
            frame_data_list = data.get("frames", [])
            
            # Sort frames by index if present, just in case
            frame_data_list.sort(key=lambda x: x.get("index", 0))
            
            for frame_data in frame_data_list:
                x = frame_data["x"]
                y = frame_data["y"]
                w = frame_data["w"]
                h = frame_data["h"]
                
                # Create a subsurface for the frame
                rect = pygame.Rect(x, y, w, h)
                try:
                    frame = sheet.subsurface(rect).copy() # Copy to separate from sheet
                    frames.append(frame)
                except ValueError:
                    print(f"Error cropping frame: {rect} is outside sheet bounds.")

            return frames

        except Exception as e:
            print(f"Error loading spritesheet {json_path}: {e}")
            return []

    @staticmethod
    def load_human_animation(assets_dir):
        """
        Loads the human character animation using the new system.
        """
        sprites_dir = os.path.join(assets_dir, "sprites_human")
        image_path = os.path.join(sprites_dir, "spritesheet.png")
        json_path = os.path.join(sprites_dir, "spritesheet.json")
        
        if not os.path.exists(image_path) or not os.path.exists(json_path):
            print(f"Human assets not found in {sprites_dir}")
            return None # Return none but signal type hint
            
        loader = SpriteSheet(image_path, json_path)
        frames = []
        try:
            # We don't know exact count easily without list, but loader data has it
            num_frames = len(loader.frames_data)
            for i in range(num_frames):
                raw_frame = loader.get_frame(i)
                # Scale down by 0.09 to fit game world (~11x23)
                w = int(raw_frame.get_width() * 0.09)
                h = int(raw_frame.get_height() * 0.09)
                scaled_frame = pygame.transform.scale(raw_frame, (w, h))
                frames.append(scaled_frame)
                
            return Animation(frames, fps=14, loop=True)
            
        except Exception as e:
            print(f"Error creating human animation: {e}")
            return None
