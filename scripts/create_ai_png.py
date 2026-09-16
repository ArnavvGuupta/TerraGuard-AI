from pathlib import Path

import numpy as np
import rasterio
from PIL import Image

INPUT = Path("data/processed/monitoring/ai_change_anomaly.tif")
OUTPUT = Path("frontend/public/ai_change_anomaly.png")

with rasterio.open(INPUT) as src:
    data = src.read(1)

valid = np.isfinite(data)
values = data[valid]

low = np.percentile(values, 2)
high = np.percentile(values, 98)

normalized = (data - low) / (high - low)
normalized = np.clip(normalized, 0, 1)

image = (normalized * 255).astype(np.uint8)

# Transparent/black for invalid pixels
image[~valid] = 0

OUTPUT.parent.mkdir(parents=True, exist_ok=True)

Image.fromarray(image).save(OUTPUT)

print("AI anomaly visualization created successfully!")
print(f"Output: {OUTPUT}")
print(f"Low percentile: {low:.4f}")
print(f"High percentile: {high:.4f}")
print(f"Valid pixels: {values.size:,}")