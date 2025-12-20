import os
import glob
import json
from PIL import Image

def generate_spritesheet():
    # Configuration
    INPUT_DIR = os.path.join("assets", "sprites_human")
    OUTPUT_PNG = os.path.join(INPUT_DIR, "spritesheet.png")
    OUTPUT_JSON = os.path.join(INPUT_DIR, "spritesheet.json")
    
    # Get files - strict numerical sort
    files = glob.glob(os.path.join(INPUT_DIR, "human_sprite_*.png"))
    # Extract number from filename to sort strictly numerically: human_sprite_1.png -> 1
    files.sort(key=lambda f: int(os.path.splitext(os.path.basename(f))[0].split('_')[-1]))
    
    if not files:
        print("No input files found!")
        return

    print(f"Found {len(files)} frames.")

    images = [Image.open(f) for f in files]
    
    # Calculate dimensions
    max_w = 0
    max_h = 0
    for img in images:
        max_w = max(max_w, img.width)
        max_h = max(max_h, img.height)
    
    print(f"Frame dimensions: {max_w}x{max_h}")
    
    # Create spritesheet
    sheet_width = max_w * len(images)
    sheet_height = max_h
    sheet = Image.new("RGBA", (sheet_width, sheet_height), (0, 0, 0, 0))
    
    frames_data = []
    
    for i, img in enumerate(images):
        x = i * max_w
        # Bottom-center alignment
        # H alignment: Center
        # V alignment: Bottom
        
        # Calculate offset to center the image in the frame
        offset_x = (max_w - img.width) // 2
        offset_y = (max_h - img.height) # Align to bottom
        
        sheet.paste(img, (x + offset_x, offset_y))
        
        # Prepare JSON data
        frame_name = os.path.splitext(os.path.basename(files[i]))[0]
        # Rename to match standard if needed, or keep original. 
        # User example used "human_run_01", let's stick to the file basename for now or mapped if requested.
        # User request example: "human_run_01". My files are "human_sprite_1".
        # I will keep the file basename to avoid confusion unless remapping is commanded.
        
        frames_data.append({
            "name": frame_name,
            "x": x,
            "y": 0,
            "w": max_w,
            "h": max_h
        })

    # Save PNG - preserve pixel art (no specific option needed for save, just avoid resizing)
    sheet.save(OUTPUT_PNG)
    print(f"Saved {OUTPUT_PNG}")
    
    # Save JSON - Strict format
    json_output = {
        "image": "spritesheet.png",
        "frame_width": max_w,
        "frame_height": max_h,
        "pivot": {
            "x": max_w // 2,
            "y": max_h
        },
        "frames": frames_data
    }
    
    with open(OUTPUT_JSON, 'w') as f:
        json.dump(json_output, f, indent=4)
    print(f"Saved {OUTPUT_JSON}")

if __name__ == "__main__":
    generate_spritesheet()
