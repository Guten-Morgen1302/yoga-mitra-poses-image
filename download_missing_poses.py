#!/usr/bin/env python3
"""
Download images for the 8 missing yoga poses from multiple sources
"""
import os
import requests
from pathlib import Path
from PIL import Image
from io import BytesIO
import json
import time
import urllib.parse

# The 8 missing poses that need images
MISSING_POSES = {
    "20_Easy Pose": "easy pose yoga",
    "22_Extended Hand-To-Big-Toe Pose": "extended hand to big toe yoga",
    "24_Extended Side Angle Pose": "extended side angle pose yoga",
    "27_Fire Log Pose": "fire log pose yoga",
    "33_Half Frog Pose": "half frog pose yoga",
    "39_Hero Pose": "hero pose yoga",
    "41_High Lunge": "high lunge pose yoga",
    "42_High Lunge, Crescent Variation": "high lunge crescent yoga",
}

base_dir = "yoga_poses_dataset"
os.makedirs(base_dir, exist_ok=True)

total_downloaded = 0
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

def get_images_from_duckduckgo(search_query, num_images=6):
    """Scrape image URLs from DuckDuckGo search"""
    try:
        # DuckDuckGo image search - fetch the page first
        url = "https://duckduckgo.com/"
        params = {"q": f"{search_query} -site:pinterest.com", "iax": "images", "ia": "images"}
        
        headers = {
            "User-Agent": user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": "https://duckduckgo.com/"
        }
        
        # Get the page to extract image URLs
        response = requests.get(url, params=params, headers=headers, timeout=10)
        if response.status_code != 200:
            return []
        
        # Extract image URLs from the response (DDG uses JavaScript rendering)
        # Try alternative: use the JSON API that DDG uses internally
        import re
        images = []
        
        # Look for image URLs in the page
        pattern = r'src="(https://[^"]*\.(?:jpg|jpeg|png|webp|gif)[^"]*)"'
        matches = re.findall(pattern, response.text)
        
        for match in matches[:num_images]:
            if 'duckduckgo.com' not in match and 'external' not in match:
                images.append(match)
        
        return images[:num_images]
    except Exception as e:
        print(f"   DuckDuckGo scraping failed: {str(e)[:40]}")
        return []

def get_images_from_google_search(search_query, num_images=6):
    """Download images using Google Images indirect method"""
    try:
        # Use a simple Google Images URL pattern
        encoded_query = urllib.parse.quote(search_query)
        
        # Try to fetch from a results page and parse
        headers = {
            "User-Agent": user_agent,
            "Referer": "https://www.google.com/",
        }
        
        url = f"https://www.google.com/search?q={encoded_query}&tbm=isch"
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            return []
        
        # Extract image URLs from Google Images response
        import re
        images = []
        
        # Google stores image URLs in various formats in the HTML
        # Look for imgUrl patterns
        pattern = r'"imgUrl":"(https://[^"]+\.(?:jpg|jpeg|png|webp|gif|jpe)(?:\?[^"]*)?)"'
        matches = re.findall(pattern, response.text)
        
        for match in matches[:num_images]:
            if 'gstatic.com' not in match and 'google.com' not in match:
                images.append(match)
        
        return images[:num_images]
    except Exception as e:
        print(f"   Google Images fetch failed: {str(e)[:40]}")
        return []

def get_images_from_wikimedia(search_query, num_images=6):
    """Download yoga pose images from Wikimedia Commons"""
    try:
        # Wikimedia Commons has yoga images
        url = "https://commons.wikimedia.org/w/api.php"
        params = {
            "action": "query",
            "list": "search",
            "srsearch": search_query,
            "format": "json",
            "srnamespace": "6",  # File namespace
            "srlimit": num_images * 2
        }
        
        headers = {"User-Agent": user_agent}
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        if response.status_code != 200:
            return []
        
        data = response.json()
        images = []
        
        # Get actual file URLs
        for result in data.get('query', {}).get('search', [])[:num_images]:
            title = result['title']
            
            # Get the file info to get the download URL
            file_url = f"https://commons.wikimedia.org/wiki/File:{title.replace(' ', '_')}"
            
            # Try to get direct image URL
            try:
                file_resp = requests.get(file_url, headers=headers, timeout=10)
                import re
                # Look for the original file link
                match = re.search(r'href="(https://upload\.wikimedia\.org/wikipedia/commons/[^"]*\.(?:jpg|jpeg|png|webp))"', file_resp.text)
                if match:
                    images.append(match.group(1))
            except:
                pass
        
        return images[:num_images]
    except Exception as e:
        print(f"   Wikimedia fetch failed: {str(e)[:40]}")
        return []

for folder_name, search_query in MISSING_POSES.items():
    folder_path = os.path.join(base_dir, folder_name)
    os.makedirs(folder_path, exist_ok=True)
    
    # Check if folder already has images
    existing_images = len([f for f in os.listdir(folder_path) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))])
    if existing_images >= 5:
        print(f"✓ {folder_name}: Already has {existing_images} images, skipping")
        continue
    
    print(f"\nDownloading images for {folder_name}...")
    print(f"   Search query: {search_query}")
    
    # Try multiple sources
    image_urls = []
    
    # Try Wikimedia Commons first (most reliable)
    print(f"   Trying Wikimedia Commons...")
    image_urls.extend(get_images_from_wikimedia(search_query, 6))
    
    if len(image_urls) < 3:
        print(f"   Trying Google Images...")
        image_urls.extend(get_images_from_google_search(search_query, 6))
    
    if len(image_urls) < 3:
        print(f"   Trying DuckDuckGo...")
        image_urls.extend(get_images_from_duckduckgo(search_query, 6))
    
    # Download and validate images
    valid_count = 0
    for idx, img_url in enumerate(list(set(image_urls))[:10], 1):  # Remove duplicates
        if not img_url or not img_url.startswith('http'):
            continue
        
        try:
            # Download image with timeout
            headers = {"User-Agent": user_agent}
            response = requests.get(img_url, headers=headers, timeout=10, allow_redirects=True)
            response.raise_for_status()
            
            # Validate image
            img = Image.open(BytesIO(response.content))
            
            # Check size (must be reasonable)
            if img.size[0] < 200 or img.size[1] < 200:
                print(f"   Image {idx} too small: {img.size}")
                continue
            
            # Convert to RGB if needed
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Save image
            dest_name = f"{folder_name}_{valid_count + 1}.jpg"
            dest_path = os.path.join(folder_path, dest_name)
            img.save(dest_path, 'JPEG', quality=95)
            
            valid_count += 1
            total_downloaded += 1
            print(f"   [OK] Added: {dest_name}")
            
            if valid_count >= 6:
                break
            
            time.sleep(0.3)  # Be nice to servers
            
        except Exception as e:
            continue
    
    if valid_count > 0:
        print(f"   -> {valid_count} valid images added to {folder_name}")
    else:
        print(f"   [SKIP] No images could be downloaded for {folder_name}")
    
    time.sleep(0.5)

print(f"\n{'='*50}")
print(f"DONE! Download complete!")
print(f"  Total new images added: {total_downloaded}")
print(f"{'='*50}")
