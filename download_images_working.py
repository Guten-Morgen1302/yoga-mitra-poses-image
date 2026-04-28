#!/usr/bin/env python3
import os
import requests
import json
from pathlib import Path
from PIL import Image
from io import BytesIO
import sys

# Load the yoga dataset JSON to get proper pose names
with open("yogabase.yoga.json", "r", encoding="utf-8") as f:
    yoga_data = json.load(f)

# Create mapping from pose names to proper formatted names
pose_mapping = {}
for pose in yoga_data:
    pose_id = pose.get('id', 0)
    pose_name_en = pose.get('name', {}).get('en', 'Unknown')
    pose_mapping[pose_name_en.lower()] = f"{pose_id:02d}_{pose_name_en}"

# Create output directory
base_dir = "yoga_poses_dataset"
os.makedirs(base_dir, exist_ok=True)

# Get all text files in current directory
txt_files = [f for f in os.listdir(".") if f.endswith(".txt") and f != "yogabase.yoga.json"]

total_downloaded = 0
total_failed = 0
poses_completed = 0

print(f"Found {len(txt_files)} text files with URLs\n")

for txt_file in sorted(txt_files):
    if txt_file == "yogabase.yoga.json":
        continue
    
    try:
        with open(txt_file, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
        
        if not lines:
            print(f"⊘ {txt_file}: Empty file, skipping")
            continue
        
        # Extract pose name from filename
        pose_name = txt_file.replace(".txt", "")
        
        # Find matching folder name from yoga dataset
        folder_name = None
        best_match = None
        best_match_len = 0
        
        for key, value in pose_mapping.items():
            if key in pose_name.lower():
                if len(key) > best_match_len:
                    folder_name = value
                    best_match = key
                    best_match_len = len(key)
        
        # If not found, try to find via alternate names
        if not folder_name:
            for pose in yoga_data:
                pose_name_en = pose.get('name', {}).get('en', '').lower()
                alternate_names = [name.lower() for name in pose.get('alternate_names', [])]
                
                if any(alt in pose_name.lower() for alt in alternate_names):
                    pose_id = pose.get('id', 0)
                    folder_name = f"{pose_id:02d}_{pose.get('name', {}).get('en', 'Unknown')}"
                    break
        
        # If still not found, create folder with cleaned name
        if not folder_name:
            folder_name = pose_name.replace("_or_", " - ").replace("_", " ").strip()
        
        pose_dir = os.path.join(base_dir, folder_name)
        os.makedirs(pose_dir, exist_ok=True)
        
        # Download up to 6 images
        downloaded_count = 0
        failed_count = 0
        
        for line in lines:
            if downloaded_count >= 6:
                break
            
            try:
                parts = line.strip().split("\t")
                if len(parts) != 2:
                    continue
                
                filename_part, url = parts
                
                # Clean up URL
                url = url.strip()
                if not url.startswith("http"):
                    continue
                
                # Extract file extension from URL or filename
                if "." in filename_part:
                    ext = "." + filename_part.split(".")[-1]
                else:
                    ext = ".jpg"
                
                img_filename = f"{downloaded_count + 1}{ext}"
                img_path = os.path.join(pose_dir, img_filename)
                
                # Download image with timeout
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                
                response = requests.get(url, timeout=5, headers=headers)
                response.raise_for_status()
                
                # Validate it's actually an image
                try:
                    img = Image.open(BytesIO(response.content))
                    img.verify()
                    
                    # Re-open since verify() exhausts the file
                    img = Image.open(BytesIO(response.content))
                    img.save(img_path)
                    
                    downloaded_count += 1
                    total_downloaded += 1
                    print(f"✓ {folder_name}: Downloaded {img_filename}")
                    
                except Exception as e:
                    print(f"✗ {folder_name}: Invalid image - {url}")
                    failed_count += 1
                    
            except requests.exceptions.Timeout:
                print(f"✗ {folder_name}: Timeout - {url}")
                failed_count += 1
            except requests.exceptions.ConnectionError:
                print(f"✗ {folder_name}: Connection error - {url}")
                failed_count += 1
            except Exception as e:
                print(f"✗ {folder_name}: Error - {str(e)}")
                failed_count += 1
        
        if downloaded_count > 0:
            poses_completed += 1
            print(f"\n✓ {folder_name}: {downloaded_count} images downloaded\n")
        else:
            print(f"\n⊘ {folder_name}: No images downloaded\n")
        
        total_failed += failed_count
        
    except Exception as e:
        print(f"ERROR processing {txt_file}: {str(e)}")

print(f"\n{'='*60}")
print(f"DOWNLOAD SUMMARY")
print(f"{'='*60}")
print(f"Total images downloaded: {total_downloaded}")
print(f"Total poses with images: {poses_completed}")
print(f"Total download failures: {total_failed}")
print(f"{'='*60}")
