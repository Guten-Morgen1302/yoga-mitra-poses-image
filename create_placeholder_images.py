#!/usr/bin/env python3
"""
Create placeholder images for the 8 missing yoga poses
These can be replaced with actual images later
"""
import os
from PIL import Image, ImageDraw, ImageFont
import random

# The 8 missing poses that need placeholder images
MISSING_POSES = {
    "20_Easy Pose": "Easy Pose",
    "22_Extended Hand-To-Big-Toe Pose": "Extended Hand-To-Big-Toe",
    "24_Extended Side Angle Pose": "Extended Side Angle",
    "27_Fire Log Pose": "Fire Log Pose",
    "33_Half Frog Pose": "Half Frog Pose",
    "39_Hero Pose": "Hero Pose",
    "41_High Lunge": "High Lunge",
    "42_High Lunge, Crescent Variation": "High Lunge Crescent",
}

base_dir = "yoga_poses_dataset"
os.makedirs(base_dir, exist_ok=True)

total_created = 0

# Color palette for variety
colors = [
    (70, 130, 180),   # Steel Blue
    (60, 140, 100),   # Teal
    (139, 90, 43),    # Brown
    (128, 0, 128),    # Purple
    (184, 134, 11),   # Dark Goldenrod
    (25, 25, 112),    # Midnight Blue
    (100, 149, 237),  # Cornflower
    (70, 200, 150),   # Light Green
]

for folder_name, pose_display_name in MISSING_POSES.items():
    folder_path = os.path.join(base_dir, folder_name)
    os.makedirs(folder_path, exist_ok=True)
    
    # Check if folder already has images
    existing_images = len([f for f in os.listdir(folder_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
    if existing_images >= 5:
        print(f"SKIP: {folder_name} already has {existing_images} images")
        continue
    
    print(f"\nCreating placeholder images for {folder_name}...")
    
    # Create 6 placeholder images with different background colors
    for i in range(1, 7):
        # Create a new image with size 300x400 (portrait for yoga poses)
        color = random.choice(colors)
        img = Image.new('RGB', (300, 400), color=color)
        draw = ImageDraw.Draw(img)
        
        # Add pose name text in the middle
        text = f"{pose_display_name}\n(Placeholder {i})"
        try:
            # Try to use a default font
            font = ImageFont.load_default()
        except:
            font = None
        
        # Draw text (center it)
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        x = (300 - text_width) // 2
        y = (400 - text_height) // 2
        
        draw.text((x, y), text, fill=(255, 255, 255), font=font)
        
        # Add a border to indicate it's a placeholder
        draw.rectangle([5, 5, 295, 395], outline=(255, 255, 255), width=3)
        
        # Save the image
        dest_name = f"{folder_name}_{i}.jpg"
        dest_path = os.path.join(folder_path, dest_name)
        img.save(dest_path, 'JPEG', quality=95)
        
        total_created += 1
        print(f"   Created: {dest_name}")

print(f"\n{'='*50}")
print(f"DONE! {total_created} placeholder images created")
print(f"Poses: {len(MISSING_POSES)}")
print(f"Images per pose: 6")
print(f"{'='*50}")
print(f"\nNote: These are placeholder images.")
print(f"Replace them with real yoga pose images when available.")
