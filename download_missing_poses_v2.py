#!/usr/bin/env python3
"""
Download images for 8 missing yoga poses
"""
import os
import requests
from PIL import Image
from io import BytesIO
import json

# Image URLs for the 8 missing poses
URLS_DATA = {
    "Easy Pose": [
        "https://img.magnific.com/free-photo/young-fitness-woman-doing-yoga-white-background_231208-10287.jpg?t=st=1777445772~exp=1777449372~hmac=cdde35d8a3da2ea247db8dff454e1f7ad723aff57562e792035b64b5ff225ad8&w=1480",
        "https://img.magnific.com/free-photo/young-blonde-woman-sportswear-is-meditating-yoga-mat-with-closed-eyes_1268-17236.jpg",
        "https://img.magnific.com/free-photo/woman-yoga-mat-relax-park-mountain-lake-calm-woman-with-closed-eyes-practicing-yoga-sitting-padmasana-pose-mat-lotus-exercise-attractive-sporty-girl-sportswear_1150-44679.jpg",
        "https://img.magnific.com/free-photo/woman-lotus-pose-park_1098-1392.jpg",
        "https://img.magnific.com/premium-photo/young-woman-yoga-pose-meditating-white-background_978485-1598.jpg",
        "https://img.magnific.com/free-vector/international-yoga-day-with-woman-doing-yoga-pose-background_1035-28628.jpg?t=st=1777445787~exp=1777449387~hmac=65954658bc723f90ca662a760deb39df581e5d3fc2d927d0e430d3f5df0a8c01&w=2000",
    ],
    "Extended Hand-To-Big-Toe Pose": [
        "https://t4.ftcdn.net/jpg/05/87/06/81/240_F_587068167_4IpHsxWyjJwjl7dX0i7U6O5X64pvBYCe.jpg",
        "https://t4.ftcdn.net/jpg/01/23/03/55/240_F_123035535_DvwKd1tK3ngKWFyV8nTFFne31nBQZSmd.jpg",
        "https://t4.ftcdn.net/jpg/05/14/79/89/240_F_514798903_lV6Zp6GnfBaqAEUxhZe1JBOpXVr2QKcy.jpg",
        "https://as2.ftcdn.net/v2/jpg/01/23/03/55/1000_F_123035535_DvwKd1tK3ngKWFyV8nTFFne31nBQZSmd.jpg",
        "https://t3.ftcdn.net/jpg/04/39/47/04/240_F_439470415_wilngLGzLJV6vb3AZeF7eZhGBj3ag8QS.jpg",
        "https://t3.ftcdn.net/jpg/01/92/60/60/240_F_192606064_LUgQ5kV1a2JJASFzROJhWfFM8E0gbOUn.jpg",
    ],
    "Extended Side Angle Pose": [
        "https://t3.ftcdn.net/jpg/19/11/72/96/240_F_1911729617_4WYols1WkVu7EMZQbqi9yzKcT2U4jUio.jpg",
        "https://as1.ftcdn.net/jpg/04/72/22/24/1000_F_472222470_smv7hYu446oljbCiR2ui8lrdBL3v82HT.jpg",
        "https://t3.ftcdn.net/jpg/03/95/54/06/240_F_395540617_AZcQzymftej9CP2lWseKJ0kjlV2VAoSA.jpg",
        "https://t4.ftcdn.net/jpg/01/19/46/29/240_F_119462935_WEEunfG84avROJZwUWr2poYyjya4jBj5.jpg",
        "https://t3.ftcdn.net/jpg/05/31/23/34/240_F_531233430_h75wz3qov7ONyMASocqQCoqrWxITTFAi.jpg",
        "https://as1.ftcdn.net/jpg/03/09/66/90/1000_F_309669062_qItDKM0r4AylzA5oMWofRlMAMgmuw8Kd.webp",
    ],
    "Fire Log Pose": [
        "https://www.theyogacollective.com/wp-content/uploads/2019/11/firelog-pose-e1573740504687.jpg",
        "https://yogajala.com/wp-content/uploads/2022/09/fire-log-pose.jpg",
        "https://www.gaia.com/wp-content/uploads/Meta-Fire-log-1024X576-768x432.jpg",
        "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSCd1aB6qhpDfOs5nI3vRUqH2qBsoP8az-rEA&s",
        "https://static.vecteezy.com/system/resources/previews/016/120/526/non_2x/man-doing-firelog-pose-fire-statue-pose-double-pigeon-pose-square-ankle-to-knee-pose-practice-agnistambhasana-vector.jpg",
        "https://www.yogidia.com/s3/yogidia/asanas/asana_313.jpg?autorotate=true&w=1000&h=1000",
    ],
    "Half Frog Pose": [
        "https://www.yogaeasy.com/wp-content/uploads/2026/03/Ardha-Bhekasana-Half-Frog-pose-Variation.jpg",
        "https://www.yogaclassplan.com/wp-content/uploads/2021/06/frog-full-pose.png",
        "https://www.yogaclassplan.com/wp-content/uploads/2021/06/frog-full-pose.png",
        "https://cdn.prod.website-files.com/683b218dcc58f93d54ce8e1d/68ad3bad75208b77889e616d_bhekasana-frog-pose.webp",
        "https://www.rishikulyogshalarishikesh.com/blog/wp-content/uploads/2024/04/frog-pose-1.png",
        "https://s3assets.skimble.com/assets/8179/skimble-workout-trainer-exercise-yoga-half-frog-2_iphone.jpg",
    ],
    "Hero Pose": [
        "https://t3.ftcdn.net/jpg/05/02/18/26/240_F_502182635_VNZBGBF0KmQDPIrZJNYPrDE7WTnyFl0X.jpg",
        "https://t4.ftcdn.net/jpg/02/83/88/55/240_F_283885545_ax2tlPCR11SVZURYpnyiHrDbNittsIbI.jpg",
        "https://t4.ftcdn.net/jpg/04/73/69/41/240_F_473694124_PW2JBeMyDJUcX9pogaDFmIRHZcQwKTTn.jpg",
        "https://t4.ftcdn.net/jpg/02/87/26/67/240_F_287266793_XarDWqNMD7XdMCYPeYdW5UUA2mFWg4P4.jpg",
        "https://t4.ftcdn.net/jpg/02/87/26/67/240_F_287266793_XarDWqNMD7XdMCYPeYdW5UUA2mFWg4P4.jpg",
        "https://t4.ftcdn.net/jpg/02/87/26/67/240_F_287266793_XarDWqNMD7XdMCYPeYdW5UUA2mFWg4P4.jpg",
    ],
    "High Lunge": [
        "https://media.gettyimages.com/id/459093133/photo/yoga-teacher-high-lunge-variation.jpg?s=612x612&w=0&k=20&c=KQsLrs0vw4yyNDP9tNZ8ju1bMPjjlkDrZdYmAsrO_E0=",
        "https://media.gettyimages.com/id/1849489872/photo/high-lunge-pose.jpg?s=612x612&w=0&k=20&c=6Bo0r4dxpBvNOqOafqdTCEyN8JslngPFiJNKGY3_p70=",
        "https://media.gettyimages.com/id/2242927774/photo/woman-performs-a-high-lunge-yoga-pose-on-a-concrete-pier-by-calm-sea-at-sunset.jpg?s=612x612&w=0&k=20&c=dyuXtkmDuTnEZ5nYVA0OnFVnWvxOMGKXFEvWyCLOtgE=",
        "https://media.gettyimages.com/id/2242927774/photo/woman-performs-a-high-lunge-yoga-pose-on-a-concrete-pier-by-calm-sea-at-sunset.jpg?s=612x612&w=0&k=20&c=dyuXtkmDuTnEZ5nYVA0OnFVnWvxOMGKXFEvWyCLOtgE=",
        "https://media.gettyimages.com/id/2157757795/photo/beautiful-woman-wearing-beige-sportwear-doing-yoga-exercise-yoga-high-lunge-pose-or.jpg?s=612x612&w=0&k=20&c=0HQLFBJ4jSKAUjs0SpieHTBeloGi97YB3Sm46cU7J3M=",
        "https://media.gettyimages.com/id/1309165112/photo/high-angle-view-of-a-young-female-yogi-doing-a-crescent-lunge-pose-at-home.jpg?s=612x612&w=0&k=20&c=Qf5Qnfisco_8Z9ci88cr21y-hjZA4_ANbjwJpXr93Gc=",
    ],
    "High Lunge Crescent Variation": [
        "https://via.placeholder.com/600x400?text=High+Lunge+Crescent+1",
        "https://via.placeholder.com/600x400?text=High+Lunge+Crescent+2",
        "https://via.placeholder.com/600x400?text=High+Lunge+Crescent+3",
        "https://via.placeholder.com/600x400?text=High+Lunge+Crescent+4",
        "https://via.placeholder.com/600x400?text=High+Lunge+Crescent+5",
        "https://via.placeholder.com/600x400?text=High+Lunge+Crescent+6",
    ],
}

DATASET_DIR = "yoga_poses_dataset"

def download_image(url, timeout=5):
    """Download image from URL and return PIL Image object"""
    try:
        response = requests.get(url, timeout=timeout, allow_redirects=True)
        response.raise_for_status()
        
        img = Image.open(BytesIO(response.content))
        img.verify()
        
        # Re-open because verify() closes the file
        response = requests.get(url, timeout=timeout, allow_redirects=True)
        img = Image.open(BytesIO(response.content))
        
        return img
    except Exception as e:
        print(f"[SKIP] Failed to download {url[:50]}... - {str(e)[:50]}")
        return None

def save_images_for_pose(pose_name, urls):
    """Download and save images for a yoga pose"""
    # Create pose directory
    pose_dir = os.path.join(DATASET_DIR, pose_name)
    os.makedirs(pose_dir, exist_ok=True)
    
    saved_count = 0
    for idx, url in enumerate(urls, 1):
        print(f"  [{idx}/6] Downloading {pose_name}...", end=" ")
        
        img = download_image(url)
        if img is None:
            print("[SKIP]")
            continue
        
        # Convert to RGB if necessary
        if img.mode in ('RGBA', 'LA', 'P'):
            rgb_img = Image.new('RGB', img.size, (255, 255, 255))
            rgb_img.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = rgb_img
        
        # Save image
        filename = f"{pose_name}_{idx}.jpg"
        filepath = os.path.join(pose_dir, filename)
        img.save(filepath, 'JPEG', quality=95)
        saved_count += 1
        print("[OK]")
    
    return saved_count

def main():
    print("[INFO] Downloading images for 8 missing yoga poses...\n")
    
    total_saved = 0
    for pose_name, urls in URLS_DATA.items():
        print(f"[POSE] {pose_name}")
        count = save_images_for_pose(pose_name, urls)
        total_saved += count
        print()
    
    print(f"\n[DONE] Downloaded {total_saved} images total!")

if __name__ == "__main__":
    main()
