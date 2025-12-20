import pygame
import os
from game.assets import AssetManager

def verify():
    pygame.init()
    screen = pygame.display.set_mode((400, 400))
    pygame.display.set_caption("Animation Verification")
    clock = pygame.time.Clock()
    
    # Path to assets
    assets_dir = os.path.join(os.path.dirname(__file__), "assets")
    
    print("Loading animation...")
    human_anim = AssetManager.load_human_animation(assets_dir)
    
    if not human_anim:
        print("Failed to load animation!")
        return

    print(f"Loaded animation with {len(human_anim.frames)} frames.")
    
    running = True
    while running:
        dt = clock.tick(60) / 1000.0 # dt in seconds
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
        human_anim.update(dt)
        frame = human_anim.get_current_frame()
        
        screen.fill((50, 50, 50))
        
        if frame:
            # Draw centered
            rect = frame.get_rect(center=(200, 200))
            screen.blit(frame, rect)
            
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    verify()
