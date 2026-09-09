from pathlib import Path

import numpy as np
import rasterio
from rasterio.windows import from_bounds


BASE = Path("data/processed/satellite")
OUTPUT = Path("data/processed/monitoring")

AUG = BASE / "2026-08-14"
SEP = BASE / "2026-09-02"

OUTPUT.mkdir(parents=True, exist_ok=True)


def get_bounds(path):
    with rasterio.open(path) as src:
        return src.bounds


# ---------------------------------------------------------
# 1. Find the common geographic area
# ---------------------------------------------------------

with rasterio.open(AUG / "BAND2.tif") as aug_src:
    aug_bounds = aug_src.bounds

with rasterio.open(SEP / "BAND2.tif") as sep_src:
    sep_bounds = sep_src.bounds


left = max(aug_bounds.left, sep_bounds.left)
right = min(aug_bounds.right, sep_bounds.right)
bottom = max(aug_bounds.bottom, sep_bounds.bottom)
top = min(aug_bounds.top, sep_bounds.top)

if left >= right or bottom >= top:
    raise RuntimeError("The two satellite scenes do not overlap.")


print("Common area:")
print(f"  Left:   {left}")
print(f"  Right:  {right}")
print(f"  Bottom: {bottom}")
print(f"  Top:    {top}")


# ---------------------------------------------------------
# 2. Read both scenes using the common area
# ---------------------------------------------------------

bands = ["BAND2.tif", "BAND3.tif", "BAND4.tif", "BAND5.tif"]

aug_data = {}
sep_data = {}


with rasterio.open(AUG / "BAND2.tif") as reference:

    aug_window = from_bounds(
        left,
        bottom,
        right,
        top,
        reference.transform
    )

    aug_window = aug_window.round_offsets().round_lengths()

    aug_transform = reference.window_transform(aug_window)

    for band in bands:
        with rasterio.open(AUG / band) as src:
            aug_data[band] = src.read(1, window=aug_window).astype(
                np.float32
            )

    print(
        f"August common-area shape: "
        f"{aug_data['BAND2.tif'].shape}"
    )


with rasterio.open(SEP / "BAND2.tif") as reference:

    sep_window = from_bounds(
        left,
        bottom,
        right,
        top,
        reference.transform
    )

    sep_window = sep_window.round_offsets().round_lengths()

    sep_transform = reference.window_transform(sep_window)

    for band in bands:
        with rasterio.open(SEP / band) as src:
            sep_data[band] = src.read(1, window=sep_window).astype(
                np.float32
            )

    print(
        f"September common-area shape: "
        f"{sep_data['BAND2.tif'].shape}"
    )


# ---------------------------------------------------------
# 3. Make sure dimensions match
# ---------------------------------------------------------

height = min(
    aug_data["BAND2.tif"].shape[0],
    sep_data["BAND2.tif"].shape[0]
)

width = min(
    aug_data["BAND2.tif"].shape[1],
    sep_data["BAND2.tif"].shape[1]
)

for band in bands:
    aug_data[band] = aug_data[band][:height, :width]
    sep_data[band] = sep_data[band][:height, :width]


# ---------------------------------------------------------
# 4. Normalize each band
# ---------------------------------------------------------

def normalize(image):
    valid = np.isfinite(image) & (image > 0)

    if not np.any(valid):
        return np.zeros_like(image)

    values = image[valid]

    low = np.percentile(values, 2)
    high = np.percentile(values, 98)

    if high <= low:
        return np.zeros_like(image)

    result = (image - low) / (high - low)

    return np.clip(result, 0, 1)


aug_norm = {
    band: normalize(aug_data[band])
    for band in bands
}

sep_norm = {
    band: normalize(sep_data[band])
    for band in bands
}


# ---------------------------------------------------------
# 5. Calculate spectral change
# ---------------------------------------------------------

difference_layers = []

for band in bands:

    difference = np.abs(
        sep_norm[band] - aug_norm[band]
    )

    difference_layers.append(difference)


spectral_change = np.mean(
    difference_layers,
    axis=0
)


# ---------------------------------------------------------
# 6. Save change raster
# ---------------------------------------------------------

output_path = OUTPUT / "spectral_change.tif"

profile = {
    "driver": "GTiff",
    "height": height,
    "width": width,
    "count": 1,
    "dtype": "float32",
    "crs": "EPSG:32645",
    "transform": aug_transform,
    "compress": "deflate",
}

with rasterio.open(output_path, "w", **profile) as dst:
    dst.write(
        spectral_change.astype(np.float32),
        1
    )


# ---------------------------------------------------------
# 7. Basic statistics
# ---------------------------------------------------------

valid = spectral_change[
    np.isfinite(spectral_change)
]

print("\nChange statistics:")
print(f"  Minimum: {valid.min():.4f}")
print(f"  Mean:    {valid.mean():.4f}")
print(f"  Maximum: {valid.max():.4f}")

print(f"\nSaved:")
print(f"  {output_path}")