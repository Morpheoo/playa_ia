# -*- coding: utf-8 -*-
# assets.py - El encargado de la logística (imágenes y animaciones)
# Este archivo carga los dibujos, les aplica efectos y los prepara para el juego.

import pygame
import json
import os
from PIL import Image, ImageFilter
from game.spritesheet import SpriteSheet
from game.animation import Animation

class AssetManager:
    @staticmethod
    def load_image(path):
        """Carga una imagen desde el disco y la convierte para Pygame."""
        try:
            # Usamos PIL primero porque es más robusto con algunos formatos
            img = Image.open(path)
            
            # --- OPTIMIZACIÓN: Limitar resolución de origen ---
            # Si la imagen es gigante (como las de 2MB que vimos), la bajamos a un tamaño manejable.
            # Ningún obstáculo en el juego necesita más de 500px para verse bien.
            MAX_SIZE = 500
            if img.width > MAX_SIZE or img.height > MAX_SIZE:
                ratio = min(MAX_SIZE / img.width, MAX_SIZE / img.height)
                new_size = (int(img.width * ratio), int(img.height * ratio))
                img = img.resize(new_size, Image.Resampling.LANCZOS)

            mode = img.mode
            size = img.size
            data = img.tobytes()
            surface = pygame.image.fromstring(data, size, mode).convert_alpha()
            return surface
        except Exception as e:
            print(f"Error al cargar la imagen {path}: {e}")
            return None

    @staticmethod
    def load_backgrounds(assets_dir):
        """
        Carga los fondos (amanecer, atardecer, noche) y les pone un poco de desenfoque.
        Así los obstáculos se ven mejor y el fondo no distrae tanto.
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
                print(f"Fondo no encontrado: {path}")
                continue
                
            try:
                img = Image.open(path)
                # Ponemos el fondo un poco borroso (radius=3)
                img = img.filter(ImageFilter.GaussianBlur(radius=3))
                
                mode = img.mode
                size = img.size
                data = img.tobytes()
                surface = pygame.image.fromstring(data, size, mode).convert()
                
                # Lo ajustamos al tamaño de la ventana (800x400)
                surface = pygame.transform.scale(surface, (800, 400))
                backgrounds[key] = surface
            except Exception as e:
                print(f"Error al cargar el fondo {filename}: {e}")
        
        return backgrounds

    @staticmethod
    def load_spritesheet(json_path, assets_dir):
        """
        Carga una hoja de sprites (muchos dibujos en una sola imagen) usando un JSON.
        """
        frames = []
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
            
            image_filename = data.get("image")
            image_path = os.path.join(assets_dir, image_filename)
            
            if not os.path.exists(image_path):
                print(f"Imagen del spritesheet no encontrada: {image_path}")
                return []
                
            sheet = AssetManager.load_image(image_path)
            if not sheet:
                return []
                
            frame_data_list = data.get("frames", [])
            # Los ordenamos para que la animación no se vea desordenada
            frame_data_list.sort(key=lambda x: x.get("index", 0))
            
            for frame_data in frame_data_list:
                # Recortamos cada cuadradito de la imagen grande
                x, y, w, h = frame_data["x"], frame_data["y"], frame_data["w"], frame_data["h"]
                rect = pygame.Rect(x, y, w, h)
                try:
                    frame = sheet.subsurface(rect).copy()
                    frames.append(frame)
                except ValueError:
                    print(f"Error al recortar: {rect} está fuera de los límites.")

            return frames
        except Exception as e:
            print(f"Error al cargar spritesheet {json_path}: {e}")
            return []

    @staticmethod
    def load_human_animation(assets_dir):
        """Prepara la animación de correr del humano (nuestro corredor principal)."""
        sprites_dir = os.path.join(assets_dir, "sprites_human")
        image_path = os.path.join(sprites_dir, "spritesheet.png")
        json_path = os.path.join(sprites_dir, "spritesheet.json")
        
        if not os.path.exists(image_path) or not os.path.exists(json_path):
            print(f"No se encontraron los dibujos del humano en {sprites_dir}")
            return None
            
        loader = SpriteSheet(image_path, json_path)
        frames = []
        try:
            num_frames = len(loader.frames_data)
            for i in range(num_frames):
                raw_frame = loader.get_frame(i)
                # Lo hacemos más pequeño (10%) para que quepa bien en el mundo del juego
                w = int(raw_frame.get_width() * 0.10)
                h = int(raw_frame.get_height() * 0.10)
                scaled_frame = pygame.transform.scale(raw_frame, (w, h))
                frames.append(scaled_frame)
                
            return Animation(frames, fps=14, loop=True)
        except Exception as e:
            print(f"Error al crear la animación del humano: {e}")
            return None

    @staticmethod
    def load_coachwalk_animation(assets_dir):
        """Carga las imágenes de cuando el personaje camina agachado."""
        coachwalk_dir = os.path.join(assets_dir, "player", "coachwalk")
        if not os.path.exists(coachwalk_dir):
            print(f"No se encontraron dibujos de agachado en {coachwalk_dir}")
            return []

        frames = []
        try:
            files = [f for f in os.listdir(coachwalk_dir) if f.endswith(".png")]
            
            # Función para ordenar los archivos por número (ej: coachwalk_1.png)
            def extract_number(filename):
                import re
                match = re.search(r'\d+', filename)
                return int(match.group()) if match else 0
            
            files.sort(key=extract_number)
            
            for filename in files:
                path = os.path.join(coachwalk_dir, filename)
                img = AssetManager.load_image(path)
                if img:
                    # Ajustamos la altura para que la animación sea estable y no "salte"
                    target_h = 55
                    aspect_ratio = img.get_width() / img.get_height()
                    target_w = int(target_h * aspect_ratio)
                    
                    scaled_frame = pygame.transform.scale(img, (target_w, target_h))
                    frames.append(scaled_frame)
            
            return frames
        except Exception as e:
            print(f"Error al cargar la animación de agachado: {e}")
            return []
