from PIL import Image
import os
import shutil

# This should match the path where generate_image saved the file
# Since I cannot know the dynamic timestamp in the filename easily without listing,
# I will search for it in the known artifact directory.
ARTIFACT_DIR = r"C:\Users\rohit\.gemini\antigravity\brain\2c49f2e5-0309-4999-9396-b1ab6c026a59"
DEST_DIR = r"C:\Users\rohit\Documents\Rohith_\PDS\extension\icons"

# Find the latest png in artifact dir
files = [f for f in os.listdir(ARTIFACT_DIR) if f.startswith('security_shield_icon') and f.endswith('.png')]
if not files:
    print("Error: Icon file not found in artifacts.")
    exit(1)

# Sort by modification time to get latest
latest_file = max([os.path.join(ARTIFACT_DIR, f) for f in files], key=os.path.getmtime)
print(f"Processing {latest_file}...")

if not os.path.exists(DEST_DIR):
    os.makedirs(DEST_DIR)

img = Image.open(latest_file)

# Resize and save
sizes = [16, 48, 128]
for size in sizes:
    resized = img.resize((size, size), Image.Resampling.LANCZOS)
    resized.save(os.path.join(DEST_DIR, f"icon{size}.png"))
    print(f"Saved icon{size}.png")

print("Icons generated successfully.")
