import rasterio
import numpy as np
from PIL import Image

DEM = r"data/raw/P5_PAN_CD_N27_000_E088_000_30m/P5_PAN_CD_N27_000_E088_000_30m/P5_PAN_CD_N27_000_E088_000_DEM_30m.tif"
SLOPE = r"data/processed/slope.tif"
OUTPUT = r"frontend/public/risk.png"


with rasterio.open(DEM) as dem_src, rasterio.open(SLOPE) as slope_src:

    elevation = dem_src.read(1).astype(np.float32)
    slope = slope_src.read(1).astype(np.float32)

    if elevation.shape != slope.shape:
        raise ValueError(
            f"DEM and slope dimensions do not match: "
            f"{elevation.shape} vs {slope.shape}"
        )

    # Valid pixels
    valid = np.isfinite(elevation) & np.isfinite(slope)

    if dem_src.nodata is not None:
        valid &= elevation != dem_src.nodata

    # -----------------------------------
    # Calculate terrain risk score
    # Same thresholds as the backend
    # -----------------------------------

    score = np.zeros_like(elevation, dtype=np.float32)

    # Slope contribution
    score += np.where(
        slope >= 45,
        60,
        np.where(
            slope >= 30,
            45,
            np.where(
                slope >= 20,
                30,
                np.where(slope >= 10, 15, 0)
            )
        )
    )

    # Elevation contribution
    score += np.where(
        elevation >= 5000,
        40,
        np.where(
            elevation >= 3500,
            30,
            np.where(
                elevation >= 2000,
                20,
                np.where(elevation >= 1000, 10, 0)
            )
        )
    )

    score = np.minimum(score, 100)

    # -----------------------------------
    # Classify risk
    #
    # 1 = LOW
    # 2 = MEDIUM
    # 3 = HIGH
    # -----------------------------------

    risk = np.zeros_like(elevation, dtype=np.uint8)

    risk[(score < 40) & valid] = 1
    risk[(score >= 40) & (score < 70) & valid] = 2
    risk[(score >= 70) & valid] = 3

    # -----------------------------------
    # Create RGBA image
    # -----------------------------------

    rgba = np.zeros(
        (elevation.shape[0], elevation.shape[1], 4),
        dtype=np.uint8
    )

    # LOW = green
    low = risk == 1
    rgba[low] = [34, 197, 94, 150]

    # MEDIUM = yellow
    medium = risk == 2
    rgba[medium] = [250, 204, 21, 160]

    # HIGH = red
    high = risk == 3
    rgba[high] = [239, 68, 68, 170]

    # NoData stays transparent
    rgba[~valid, 3] = 0

    image = Image.fromarray(rgba, "RGBA")
    image.save(OUTPUT)

    # -----------------------------------
    # Print statistics
    # -----------------------------------

    total = np.count_nonzero(valid)
    low_count = np.count_nonzero(risk == 1)
    medium_count = np.count_nonzero(risk == 2)
    high_count = np.count_nonzero(risk == 3)

    print("Risk visualization created successfully!")
    print(f"Output: {OUTPUT}")
    print(f"Valid pixels: {total:,}")
    print(f"Low risk: {low_count:,}")
    print(f"Medium risk: {medium_count:,}")
    print(f"High risk: {high_count:,}")