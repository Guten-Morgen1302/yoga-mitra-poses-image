# Quick Start Guide - Using the Yoga Dataset

## 📂 Dataset Location
```
c:\Users\harsh\OneDrive\Desktop\yoga_dataset_links\yoga_poses_dataset\
```

### JSON Dataset
```
c:\Users\harsh\OneDrive\Desktop\yoga_dataset_links\yoga_pose_dataset.json
```

## 🎯 What You Have

- **90 yoga pose folders** with 540 images
- **yoga_pose_dataset.json** - Production-ready reference dataset
- **492 real images** downloaded from provided URLs
- **48 placeholder images** (can be replaced later)
- **Organized structure** ready for ML training

---

## 🚀 Using the JSON Dataset

### Load the Dataset
```python
import json

# Load the complete dataset
with open("yoga_pose_dataset.json", "r", encoding="utf-8") as f:
    dataset = json.load(f)

# Access dataset info
print(f"Total poses: {dataset['total_poses']}")
print(f"Version: {dataset['version']}")
```

### Access Individual Poses
```python
# Get first pose
pose = dataset['poses'][0]

print(f"ID: {pose['id']}")
print(f"Name (EN): {pose['name']['en']}")
print(f"Name (HI): {pose['name']['hi']}")
print(f"Name (MR): {pose['name']['mr']}")
print(f"Difficulty: {pose['difficulty']}")
print(f"Hold time: {pose['hold_time']}s")
print(f"Threshold: {pose['threshold']}")
```

### Use Reference Vectors for ML
```python
import numpy as np
from sklearn.preprocessing import StandardScaler

# Extract all reference vectors
vectors = np.array([pose['reference_vector'] for pose in dataset['poses']])
labels = np.array([pose['id'] for pose in dataset['poses']])

# Standardize for ML
scaler = StandardScaler()
vectors_scaled = scaler.fit_transform(vectors)

print(f"Shape: {vectors_scaled.shape}")  # (90, 68)
```

### Get Pose Corrections
```python
# Get correction suggestions for a pose
pose = dataset['poses'][0]

print(f"Corrections for {pose['name']['en']}:")
for area, advice in pose['corrections'].items():
    print(f"  {area}: {advice}")
```

### Train/Test Split with JSON Data
```python
from sklearn.model_selection import train_test_split

# Create feature matrix and labels
X = np.array([pose['reference_vector'] for pose in dataset['poses']])
y = np.array([pose['difficulty'] for pose in dataset['poses']])

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print(f"Training: {len(X_train)} samples")
print(f"Testing: {len(X_test)} samples")
```

### Build Classification Model
```python
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

# Get training data
X = np.array([pose['reference_vector'] for pose in dataset['poses']])
y = np.array([pose['id'] for pose in dataset['poses']])

# Train classifier
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X, y)

# Predict
predictions = clf.predict(X)
accuracy = accuracy_score(y, predictions)

print(f"Model Accuracy: {accuracy:.2%}")
```

### Export Specific Pose Data
```python
# Get all beginner poses
beginner_poses = [pose for pose in dataset['poses'] if pose['difficulty'] == 'beginner']

print(f"Beginner poses: {len(beginner_poses)}")
for pose in beginner_poses:
    print(f"  - {pose['name']['en']} (Hold: {pose['hold_time']}s)")
```

### Extract Angles Database
```python
# Create angle reference database
angles_db = {}
for pose in dataset['poses']:
    angles_db[pose['id']] = {
        'name': pose['name']['en'],
        'angles': pose['ideal_angles'],
        'threshold': pose['threshold']
    }

# Use for pose detection validation
pose_id = 1
expected_angles = angles_db[pose_id]
print(f"Expected angles for {expected_angles['name']}:")
print(expected_angles['angles'])
```

---

## 🚀 Using the Dataset

### Quick Check - Verify Dataset
```python
import os
from pathlib import Path

dataset_path = "yoga_poses_dataset"

# Count folders and images
folders = len([d for d in os.listdir(dataset_path) if os.path.isdir(os.path.join(dataset_path, d))])
total_images = sum([len(files) for _, _, files in os.walk(dataset_path)])

print(f"Folders: {folders}/90")
print(f"Images: {total_images}")
```

### Load All Images
```python
import os
import cv2
import numpy as np

dataset_path = "yoga_poses_dataset"
images = []
labels = []

for pose_folder in sorted(os.listdir(dataset_path)):
    folder_path = os.path.join(dataset_path, pose_folder)
    pose_id = int(pose_folder.split("_")[0])
    
    for img_file in sorted(os.listdir(folder_path)):
        if img_file.endswith(".jpg"):
            img_path = os.path.join(folder_path, img_file)
            img = cv2.imread(img_path)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            images.append(img)
            labels.append(pose_id)

images = np.array(images)
labels = np.array(labels)
```

### Using with PIL
```python
from PIL import Image
import os

dataset_path = "yoga_poses_dataset"

for pose_folder in sorted(os.listdir(dataset_path)):
    folder_path = os.path.join(dataset_path, pose_folder)
    
    for img_file in sorted(os.listdir(folder_path)):
        if img_file.endswith(".jpg"):
            img_path = os.path.join(folder_path, img_file)
            img = Image.open(img_path)
            # Use img for your processing
            img.close()
```

### Train/Test Split
```python
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    images, labels, 
    test_size=0.2, 
    random_state=42,
    stratify=labels
)

print(f"Training set: {len(X_train)} images")
print(f"Test set: {len(X_test)} images")
```

---

## 🎬 Extract Landmarks (MediaPipe)

```python
import mediapipe as mp
import cv2
import numpy as np

mp_pose = mp.solutions.pose
pose = mp_pose.Pose(
    static_image_mode=True,
    model_complexity=1,
    smooth_landmarks=True
)

def extract_landmarks(image):
    """Extract pose landmarks from an image"""
    results = pose.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    
    if results.pose_landmarks:
        landmarks = []
        for lm in results.pose_landmarks.landmark:
            landmarks.extend([lm.x, lm.y, lm.z, lm.visibility])
        return np.array(landmarks)
    return None

# Extract for all images
landmark_vectors = []
valid_labels = []

for i, image in enumerate(images):
    landmarks = extract_landmarks(image)
    if landmarks is not None:
        landmark_vectors.append(landmarks)
        valid_labels.append(labels[i])

landmark_vectors = np.array(landmark_vectors)
valid_labels = np.array(valid_labels)
```

---

## 📊 Dataset Stats

| Stat | Value |
|------|-------|
| Total Poses | 90 |
| Total Images | 540 |
| Real Images | 492 |
| Placeholders | 48 |
| Images/Pose | 6 (avg) |
| Format | JPEG |
| Resolution | Variable |

---

## 🗂️ Folder Names (Sample)

```
01_Akarna Dhanurasana
02_Bharadvajas Twist Pose
03_Boat Pose
04_Bound Angle Pose
05_Bow Pose
...
90_Warrior Pose III
```

## 📝 Pose List

View all 90 poses in `yogabase.yoga.json`

```python
import json

with open("yogabase.yoga.json", "r", encoding="utf-8") as f:
    poses = json.load(f)

for pose in poses:
    print(f"{pose['id']}: {pose['name']['en']}")
```

---

## ⚠️ Placeholder Poses (Need Real Images)

These 8 poses currently have placeholder images:

- Easy Pose
- Extended Hand-To-Big-Toe Pose
- Extended Side Angle Pose
- Fire Log Pose
- Half Frog Pose
- Hero Pose
- High Lunge
- High Lunge Crescent Variation

**To replace:** Download real images and save them with the same naming convention in the respective folders.

---

## 🔧 Common Tasks

### Get All Image Paths
```python
image_paths = []
for pose_folder in sorted(os.listdir("yoga_poses_dataset")):
    folder_path = os.path.join("yoga_poses_dataset", pose_folder)
    for img_file in sorted(os.listdir(folder_path)):
        if img_file.endswith(".jpg"):
            image_paths.append(os.path.join(folder_path, img_file))
```

### Resize All Images
```python
import cv2
from pathlib import Path

target_size = (224, 224)  # For ResNet50, MobileNet, etc.

for pose_folder in os.listdir("yoga_poses_dataset"):
    folder_path = os.path.join("yoga_poses_dataset", pose_folder)
    for img_file in os.listdir(folder_path):
        if img_file.endswith(".jpg"):
            img_path = os.path.join(folder_path, img_file)
            img = cv2.imread(img_path)
            resized = cv2.resize(img, target_size)
            cv2.imwrite(img_path, resized)
```

### Count Images per Pose
```python
for pose_folder in sorted(os.listdir("yoga_poses_dataset")):
    folder_path = os.path.join("yoga_poses_dataset", pose_folder)
    count = len([f for f in os.listdir(folder_path) if f.endswith(".jpg")])
    print(f"{pose_folder}: {count} images")
```

### Identify Placeholder Images
```python
placeholder_poses = []
for pose_folder in sorted(os.listdir("yoga_poses_dataset")):
    folder_path = os.path.join("yoga_poses_dataset", pose_folder)
    
    # Check if first image is placeholder (check file size or content)
    img_files = [f for f in os.listdir(folder_path) if f.endswith(".jpg")]
    if img_files:
        first_img_path = os.path.join(folder_path, img_files[0])
        file_size = os.path.getsize(first_img_path)
        
        # Placeholder images are typically smaller (~3-5KB)
        if file_size < 10000:  # Less than 10KB = likely placeholder
            placeholder_poses.append(pose_folder)

print("Placeholder poses detected:")
for pose in placeholder_poses:
    print(f"  - {pose}")
```

---

## 📚 Full Documentation

See **DOCUMENTATION.md** for complete technical information:
- Download process details
- Quality validation
- File organization
- Processing pipeline
- Performance metrics
- Verification commands

---

## 🎓 Example: Simple Yoga Pose Classifier

```python
import os
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import cv2

# Load images
def load_images():
    images, labels = [], []
    for pose_folder in sorted(os.listdir("yoga_poses_dataset")):
        folder_path = os.path.join("yoga_poses_dataset", pose_folder)
        pose_id = int(pose_folder.split("_")[0])
        
        for img_file in os.listdir(folder_path):
            if img_file.endswith(".jpg"):
                img = cv2.imread(os.path.join(folder_path, img_file))
                img = cv2.resize(img, (100, 100))  # Resize
                img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # Grayscale
                images.append(img.flatten())  # Flatten for ML
                labels.append(pose_id)
    
    return np.array(images), np.array(labels)

# Train classifier
X, y = load_images()
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

clf = RandomForestClassifier(n_estimators=100)
clf.fit(X_train, y_train)

accuracy = clf.score(X_test, y_test)
print(f"Model Accuracy: {accuracy:.2%}")
```

---

**Happy coding! 🧘‍♀️**
