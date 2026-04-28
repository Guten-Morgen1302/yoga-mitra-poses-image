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
                print(f"    ⚠️ Invalid image, retrying... (attempt {attempt + 1})")
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

def get_pose_name_from_filename(filename):
    """Extract pose name from text file"""
    # Remove .txt extension
    name = filename.replace('.txt', '')
    return name

def load_all_poses_from_json():
    """Load all 90 poses from yogabase.yoga.json"""
    json_path = os.path.join(WORKSPACE_DIR, "yogabase.yoga.json")
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            poses = json.load(f)
        
        # Create mapping of pose names
        pose_map = {}
        for pose in poses:
            sanskrit_name = pose.get('name_sanskrit', '')
            en_name = pose.get('name', {}).get('en', '')
            pose_map[en_name.lower()] = {
                'name': en_name,
                'sanskrit': sanskrit_name,
                'id': pose.get('id')
            }
        
        print(f"✅ Loaded {len(poses)} poses from yogabase.yoga.json")
        return poses, pose_map
    except Exception as e:
        print(f"❌ Error loading JSON: {e}")
        return [], {}

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
        
        print(f"\n📂 Processing: {pose_name}")
        print(f"   Found {len(lines)} URLs in file")
        
        for idx, line in enumerate(lines[:MAX_IMAGES_PER_POSE]):
            try:
                parts = line.strip().split('\t')
                if len(parts) < 2:
                    continue
                
                # Extract filename and URL
                filename_part = parts[0]
                url = parts[1]
                
                # Generate filename
                if '/' in filename_part:
                    filename = filename_part.split('/')[-1]
                else:
                    filename = f"image_{idx + 1}.jpg"
                
                # Ensure .jpg extension
                if not filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                    filename += '.jpg'
                
                save_path = os.path.join(pose_dir, filename)
                
                # Skip if already downloaded
                if os.path.exists(save_path):
                    print(f"   ✓ {filename} (already exists)")
                    downloaded += 1
                    continue
                
                # Download
                print(f"   ⬇️  Downloading {filename}...", end='', flush=True)
                if download_image(url, save_path):
                    print(" ✓")
                    downloaded += 1
                else:
                    print(" ✗ (invalid/broken link)")
                    failed += 1
                    # Clean up invalid file
                    if os.path.exists(save_path):
                        os.remove(save_path)
                
                time.sleep(0.5)  # Rate limiting
                
            except Exception as e:
                print(f"   ✗ Error on line {idx + 1}: {str(e)[:50]}")
                failed += 1
                continue
        
        return downloaded, failed
        
    except Exception as e:
        print(f"❌ Error reading {text_file_path}: {e}")
        return 0, 0

def main():
    print("🧘 YOGA POSE IMAGE DOWNLOADER")
    print("=" * 60)
    
    # Load poses from JSON
    all_poses, pose_map = load_all_poses_from_json()
    if not all_poses:
        print("❌ Failed to load poses")
        return
    
    # Get available text files
    txt_files = get_available_txt_files()
    print(f"📄 Found {len(txt_files)} text files with URLs\n")
    
    # Create mapping of txt files to poses
    txt_file_map = {}
    for txt_file in txt_files:
        pose_name = get_pose_name_from_filename(txt_file)
        txt_file_map[pose_name] = txt_file
    
    total_downloaded = 0
    total_failed = 0
    poses_with_images = set()
    
    # Download images for each pose
    print("Starting downloads...\n")
    
    for pose in all_poses:
        pose_en_name = pose.get('name', {}).get('en', 'Unknown')
        pose_id = pose.get('id', 0)
        
        # Create pose folder
        pose_folder_name = f"{pose_id:02d}_{pose_en_name.replace(' ', '_').replace('/', '_')}"
        pose_dir = os.path.join(OUTPUT_DIR, pose_folder_name)
        os.makedirs(pose_dir, exist_ok=True)
        
        # Try to find matching text file
        text_file_found = False
        for txt_key, txt_file in txt_file_map.items():
            if txt_key.lower() == pose_en_name.lower() or \
               pose_en_name.lower() in txt_key.lower() or \
               txt_key.lower() in pose_en_name.lower():
                
                text_file_path = os.path.join(WORKSPACE_DIR, txt_file)
                downloaded, failed = download_from_text_file(
                    text_file_path, 
                    pose_en_name, 
                    pose_dir
                )
                total_downloaded += downloaded
                total_failed += failed
                if downloaded > 0:
                    poses_with_images.add(pose_en_name)
                    text_file_found = True
                break
        
        if not text_file_found:
            print(f"⚠️  No text file found for: {pose_en_name}")
            # Create empty folder for manual addition later
            open(os.path.join(pose_dir, "MANUAL_DOWNLOAD_REQUIRED.txt"), 'w').close()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 DOWNLOAD SUMMARY")
    print("=" * 60)
    print(f"✅ Total images downloaded: {total_downloaded}")
    print(f"❌ Total failed downloads: {total_failed}")
    print(f"📂 Poses with images: {len(poses_with_images)}/{len(all_poses)}")
    print(f"⚠️  Poses needing manual download: {len(all_poses) - len(poses_with_images)}")
    print(f"\n📁 Output directory: {OUTPUT_DIR}")
    print(f"   Total folders created: {len(all_poses)}")
    
    # List poses that need manual download
    missing_poses = [p.get('name', {}).get('en', 'Unknown') for p in all_poses 
                     if p.get('name', {}).get('en', 'Unknown') not in poses_with_images]
    
    if missing_poses:
        print("\n⚠️  Poses requiring manual download:")
        for pose in missing_poses:
            print(f"   - {pose}")

if __name__ == "__main__":
    main()
