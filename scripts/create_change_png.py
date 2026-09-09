from pathlib import Path

import numpy as np
import rasterio
from PIL import Image


INPUT = Path("data/processed/monitoring/spectral_change.tif")
OUTPUT = Path("frontend/public/spectral_change.png")


with rasterio.open(INPUT) as src:
    data = src.read(1)

valid = np.isfinite(data)

values = data[valid]

low = np.percentile(values, 2)
high = np.percentile(values, 98)

normalized = (data - low) / (high - low)
normalized = np.clip(normalized, 0, 1)

# Convert to 8-bit grayscale
image = (normalized * 255).astype(np.uint8)

# Mask invalid pixels
image[~valid] = 0

OUTPUT.parent.mkdir(parents=True, exist_ok=True)

Image.fromarray(image).save(OUTPUT)

print(f"Saved: {OUTPUT}")
print(f"Low percentile: {low:.4f}")
print(f"High percentile: {high:.4f}")