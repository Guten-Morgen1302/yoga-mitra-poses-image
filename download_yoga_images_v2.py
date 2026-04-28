import json
import os
import requests
import sys
from pathlib import Path
from urllib.parse import urlparse
import time
from PIL import Image
from io import BytesIO
import glob
import difflib

# Configuration
WORKSPACE_DIR = r"c:\Users\harsh\OneDrive\Desktop\yoga_dataset_links"
OUTPUT_DIR = os.path.join(WORKSPACE_DIR, "yoga_poses_dataset")
MAX_IMAGES_PER_POSE = 6
TIMEOUT = 10
RETRY_ATTEMPTS = 2

os.makedirs(OUTPUT_DIR, exist_ok=True)

def is_valid_image(content):
    """Validate if content is a valid image"""
    try:
        img = Image.open(BytesIO(content))
        img.verify()
        return True
    except Exception as e:
        return False

def download_image(url, save_path, attempt=1):
    """Download and validate image"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, timeout=TIMEOUT, headers=headers, stream=True)
        response.raise_for_status()
        
        content = response.content
        
        # Validate it's a real image
        if not is_valid_image(content):
            if attempt < RETRY_ATTEMPTS:
                time.sleep(1)
                return download_image(url, save_path, attempt + 1)
            return False
        
        # Save image
        with open(save_path, 'wb') as f:
            f.write(content)
        return True
        
    except Exception as e:
        if attempt < RETRY_ATTEMPTS:
            time.sleep(1)
            return download_image(url, save_path, attempt + 1)
        return False

def normalize_text(text):
    """Normalize text for comparison"""
    return text.lower().replace('_', ' ').replace('-', ' ').replace('  ', ' ').strip()

def find_best_txt_file_match(pose_name, txt_files):
    """Find best matching text file using fuzzy matching"""
    norm_pose = normalize_text(pose_name)
    
    best_match = None
    best_ratio = 0
    
    for txt_file in txt_files:
        norm_txt = normalize_text(txt_file.replace('.txt', ''))
        ratio = difflib.SequenceMatcher(None, norm_pose, norm_txt).ratio()
        
        if ratio > best_ratio:
            best_ratio = ratio
            best_match = txt_file
    
    # Only return if match is reasonably good
    if best_ratio > 0.65:
        return best_match
    return None

def load_all_poses_from_json():
    """Load all 90 poses from yogabase.yoga.json"""
    json_path = os.path.join(WORKSPACE_DIR, "yogabase.yoga.json")
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            poses = json.load(f)
        
        print(f"✅ Loaded {len(poses)} poses from yogabase.yoga.json")
        return poses
    except Exception as e:
        print(f"❌ Error loading JSON: {e}")
        return []

def get_available_txt_files():
    """Get all available .txt files (excluding .json)"""
    txt_files = glob.glob(os.path.join(WORKSPACE_DIR, "*.txt"))
    txt_files = [os.path.basename(f) for f in txt_files]
    return txt_files

def download_from_text_file(text_file_path, pose_name, pose_dir):
    """Download images from a text file with URLs"""
    downloaded = 0
    failed = 0
    
    try:
        with open(text_file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        print(f"\n📂 {pose_name}")
        print(f"   📋 Found {len(lines)} URLs (taking first {MAX_IMAGES_PER_POSE})")
        
        for idx, line in enumerate(lines[:MAX_IMAGES_PER_POSE]):
            try:
                parts = line.strip().split('\t')
                if len(parts) < 2:
                    continue
                
                # Extract URL
                url = parts[1]
                
                # Generate filename
                filename = f"image_{idx + 1}.jpg"
                save_path = os.path.join(pose_dir, filename)
                
                # Skip if already downloaded
                if os.path.exists(save_path):
                    print(f"   ✓ {filename} (exists)")
                    downloaded += 1
                    continue
                
                # Download
                print(f"   ⬇️  {filename}...", end='', flush=True)
                if download_image(url, save_path):
                    print(" ✓")
                    downloaded += 1
                else:
                    print(" ✗")
                    failed += 1
                    # Clean up invalid file
                    if os.path.exists(save_path):
                        os.remove(save_path)
                
                time.sleep(0.3)  # Rate limiting
                
            except Exception as e:
                print(f"   ✗ Error")
                failed += 1
                continue
        
        return downloaded, failed
        
    except Exception as e:
        print(f"❌ Error reading {text_file_path}: {e}")
        return 0, 0

def main():
    print("\n🧘 YOGA POSE IMAGE DOWNLOADER v2")
    print("=" * 70)
    
    # Load poses from JSON
    all_poses = load_all_poses_from_json()
    if not all_poses:
        print("❌ Failed to load poses")
        return
    
    # Get available text files
    txt_files = get_available_txt_files()
    print(f"📄 Found {len(txt_files)} text files with URLs")
    print("=" * 70)
    
    total_downloaded = 0
    total_failed = 0
    poses_with_images = set()
    matches_found = {}
    
    # Download images for each pose
    print("\n🚀 Starting downloads with intelligent matching...\n")
    
    for pose in all_poses:
        pose_en_name = pose.get('name', {}).get('en', 'Unknown')
        pose_id = pose.get('id', 0)
        
        # Create pose folder
        pose_folder_name = f"{pose_id:02d}_{pose_en_name.replace(' ', '_').replace('/', '_')}"
        pose_dir = os.path.join(OUTPUT_DIR, pose_folder_name)
        os.makedirs(pose_dir, exist_ok=True)
        
        # Find best matching text file
        best_txt_file = find_best_txt_file_match(pose_en_name, txt_files)
        
        if best_txt_file:
            text_file_path = os.path.join(WORKSPACE_DIR, best_txt_file)
            downloaded, failed = download_from_text_file(
                text_file_path, 
                pose_en_name, 
                pose_dir
            )
            total_downloaded += downloaded
            total_failed += failed
            if downloaded > 0:
                poses_with_images.add(pose_en_name)
                matches_found[pose_en_name] = best_txt_file
        else:
            print(f"⚠️  No matching file for: {pose_en_name}")
            # Create empty folder for manual addition later
            open(os.path.join(pose_dir, "MANUAL_DOWNLOAD_NEEDED.txt"), 'w').close()
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 DOWNLOAD SUMMARY")
    print("=" * 70)
    print(f"✅ Total images downloaded: {total_downloaded}")
    print(f"❌ Total failed/invalid: {total_failed}")
    print(f"📂 Poses with images: {len(poses_with_images)}/{len(all_poses)}")
    print(f"⚠️  Poses needing manual images: {len(all_poses) - len(poses_with_images)}")
    print(f"\n📁 Output: {OUTPUT_DIR}")
    print(f"   Total folders: {len(all_poses)}")
    
    # Show which poses are missing
    missing = [p.get('name', {}).get('en', '?') for p in all_poses 
               if p.get('name', {}).get('en', '?') not in poses_with_images]
    
    if missing:
        print(f"\n⚠️  {len(missing)} poses need manual download")

if __name__ == "__main__":
    main()
