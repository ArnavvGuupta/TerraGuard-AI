import rasterio
import numpy as np
from PIL import Image

INPUT = r"data/processed/slope.tif"
OUTPUT = r"frontend/public/slope.png"

with rasterio.open(INPUT) as src:
    slope = src.read(1)

    nodata = src.nodata

    # Replace NoData with 0
    if nodata is not None:
        slope = np.where(slope == nodata, 0, slope)

    # Limit visualization to 0-60 degrees
    slope = np.clip(slope, 0, 60)

    # Normalize
    normalized = slope / 60.0

    # Create RGB terrain heatmap
    # Green = low
    # Yellow = moderate
    # Red = steep

    r = np.clip(normalized * 255 * 1.5, 0, 255)
    g = np.clip(255 - normalized * 255 * 1.5, 0, 255)
    b = np.zeros_like(r)

    rgb = np.dstack([
        r,
        g,
        b
    ]).astype(np.uint8)

    # Transparent where slope is essentially zero
    alpha = np.where(slope > 0.5, 150, 0).astype(np.uint8)

    rgba = np.dstack([
        rgb,
        alpha
    ])

    image = Image.fromarray(rgba, "RGBA")

    image.save(OUTPUT)

print(f"Slope visualization created: {OUTPUT}")