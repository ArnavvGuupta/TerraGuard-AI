import rasterio
import numpy as np
from PIL import Image
import joblib
from rasterio.warp import reproject, Resampling


# ============================================================
# PATHS
# ============================================================

DEM = r"data/raw/P5_PAN_CD_N27_000_E088_000_30m/P5_PAN_CD_N27_000_E088_000_30m/P5_PAN_CD_N27_000_E088_000_DEM_30m.tif"

SLOPE = r"data/processed/slope.tif"
ASPECT = r"data/processed/aspect.tif"

MODEL = r"data/xgboost_landslide_model_hard_negative.pkl"

OUTPUT = r"frontend/public/ai_risk.png"

SATELLITE_BANDS = {
    "B2": r"data/processed/satellite/2026-08-14/BAND2.tif",
    "B3": r"data/processed/satellite/2026-08-14/BAND3.tif",
    "B4": r"data/processed/satellite/2026-08-14/BAND4.tif",
    "B5": r"data/processed/satellite/2026-08-14/BAND5.tif",
}


# ============================================================
# START
# ============================================================

print("=" * 60)
print("AI LANDSLIDE RISK MAP GENERATION")
print("=" * 60)


# ============================================================
# LOAD MODEL
# ============================================================

print("\nLoading hard-negative XGBoost model...")

artifact = joblib.load(MODEL)

model = artifact["model"]
imputer = artifact["imputer"]
features = artifact["features"]

print("Model loaded successfully.")

print("\nFeatures used by model:")

for feature in features:
    print(f"  - {feature}")


# ============================================================
# LOAD DEM
# ============================================================

print("\nLoading DEM...")

with rasterio.open(DEM) as src:

    elevation = src.read(1).astype(np.float32)

    dem_transform = src.transform
    dem_crs = src.crs

    dem_height = src.height
    dem_width = src.width

    dem_nodata = src.nodata

print(f"DEM size: {dem_width} x {dem_height}")
print(f"DEM CRS: {dem_crs}")


# ============================================================
# LOAD SLOPE
# ============================================================

print("\nLoading slope...")

with rasterio.open(SLOPE) as src:
    slope = src.read(1).astype(np.float32)

print(f"Slope size: {slope.shape}")


# ============================================================
# LOAD ASPECT
# ============================================================

print("\nLoading aspect...")

with rasterio.open(ASPECT) as src:
    aspect = src.read(1).astype(np.float32)

print(f"Aspect size: {aspect.shape}")


# ============================================================
# CHECK DIMENSIONS
# ============================================================

if elevation.shape != slope.shape:

    raise ValueError(
        f"DEM and slope dimensions do not match: "
        f"{elevation.shape} vs {slope.shape}"
    )


if elevation.shape != aspect.shape:

    raise ValueError(
        f"DEM and aspect dimensions do not match: "
        f"{elevation.shape} vs {aspect.shape}"
    )


# ============================================================
# VALID TERRAIN PIXELS
# ============================================================

valid = (
    np.isfinite(elevation)
    & np.isfinite(slope)
    & np.isfinite(aspect)
)

if dem_nodata is not None:
    valid &= elevation != dem_nodata


# ============================================================
# LOAD SATELLITE BANDS
# ============================================================

print("\nLoading satellite imagery...")

satellite_arrays = {}


for band_name, path in SATELLITE_BANDS.items():

    print(f"  Processing {band_name}...")

    with rasterio.open(path) as src:

        destination = np.full(
            (dem_height, dem_width),
            np.nan,
            dtype=np.float32
        )

        reproject(
            source=src.read(1),
            destination=destination,

            src_transform=src.transform,
            src_crs=src.crs,

            dst_transform=dem_transform,
            dst_crs=dem_crs,

            resampling=Resampling.bilinear,

            src_nodata=src.nodata,
            dst_nodata=np.nan
        )

        satellite_arrays[band_name] = destination


print("Satellite bands aligned with DEM.")


# ============================================================
# EXTRACT BANDS
# ============================================================

B2 = satellite_arrays["B2"]
B3 = satellite_arrays["B3"]
B4 = satellite_arrays["B4"]
B5 = satellite_arrays["B5"]


# ============================================================
# CALCULATE NDVI
# ============================================================

print("\nCalculating NDVI...")

NDVI = np.divide(
    B4 - B3,
    B4 + B3,

    out=np.zeros_like(B4, dtype=np.float32),

    where=(B4 + B3) != 0
)


# ============================================================
# CALCULATE NDWI
# ============================================================

print("Calculating NDWI...")

NDWI = np.divide(
    B2 - B4,
    B2 + B4,

    out=np.zeros_like(B2, dtype=np.float32),

    where=(B2 + B4) != 0
)


# ============================================================
# CALCULATE NBR
# ============================================================

print("Calculating NBR...")

NBR = np.divide(
    B4 - B5,
    B4 + B5,

    out=np.zeros_like(B4, dtype=np.float32),

    where=(B4 + B5) != 0
)


# ============================================================
# UPDATE VALID MASK
# ============================================================

valid &= (
    np.isfinite(B2)
    & np.isfinite(B3)
    & np.isfinite(B4)
    & np.isfinite(B5)

    & np.isfinite(NDVI)
    & np.isfinite(NDWI)
    & np.isfinite(NBR)
)


# ============================================================
# FEATURE ARRAYS
# ============================================================

feature_arrays = {

    "elevation": elevation,

    "slope": slope,

    "aspect": aspect,

    "B2": B2,
    "B3": B3,
    "B4": B4,
    "B5": B5,

    "NDVI": NDVI,
    "NDWI": NDWI,
    "NBR": NBR,
}


# ============================================================
# CREATE PROBABILITY ARRAY
# ============================================================

print("\nRunning XGBoost predictions...")

probability = np.zeros(
    (dem_height, dem_width),
    dtype=np.float32
)


# ============================================================
# PREDICT IN CHUNKS
# ============================================================

CHUNK_ROWS = 100

for start_row in range(
    0,
    dem_height,
    CHUNK_ROWS
):

    end_row = min(
        start_row + CHUNK_ROWS,
        dem_height
    )

    chunk_valid = valid[
        start_row:end_row
    ]

    if not np.any(chunk_valid):
        continue


    # Build feature matrix.

    X_chunk = np.column_stack(
        [
            feature_arrays[feature][
                start_row:end_row
            ][chunk_valid]

            for feature in features
        ]
    )


    # Apply training-time imputer.

    X_chunk = imputer.transform(
        X_chunk
    )


    # Predict probability of landslide.

    probabilities = model.predict_proba(
        X_chunk
    )[:, 1]


    probability_chunk = probability[
        start_row:end_row
    ]

    probability_chunk[chunk_valid] = probabilities

    probability[
        start_row:end_row
    ] = probability_chunk


    if start_row % 500 == 0:

        print(
            f"Processed rows "
            f"{start_row:,} - {end_row:,} "
            f"of {dem_height:,}"
        )


# ============================================================
# CLASSIFY RISK
# ============================================================

print("\nClassifying AI risk...")


# Probability:
#
# 0.00 - 0.33 = LOW
# 0.33 - 0.66 = MEDIUM
# 0.66 - 1.00 = HIGH


risk = np.zeros(
    (dem_height, dem_width),
    dtype=np.uint8
)


low = (
    (probability < 0.33)
    & valid
)


medium = (
    (probability >= 0.33)
    & (probability < 0.66)
    & valid
)


high = (
    (probability >= 0.66)
    & valid
)


risk[low] = 1
risk[medium] = 2
risk[high] = 3


# ============================================================
# CREATE RGBA IMAGE
# ============================================================

rgba = np.zeros(
    (
        dem_height,
        dem_width,
        4
    ),
    dtype=np.uint8
)


# LOW = GREEN

rgba[low] = [
    34,
    197,
    94,
    150
]


# MEDIUM = YELLOW

rgba[medium] = [
    250,
    204,
    21,
    160
]


# HIGH = RED

rgba[high] = [
    239,
    68,
    68,
    170
]


# NODATA = TRANSPARENT

rgba[~valid, 3] = 0


# ============================================================
# SAVE IMAGE
# ============================================================

image = Image.fromarray(
    rgba,
    "RGBA"
)

image.save(OUTPUT)


# ============================================================
# STATISTICS
# ============================================================

total = np.count_nonzero(valid)

low_count = np.count_nonzero(
    risk == 1
)

medium_count = np.count_nonzero(
    risk == 2
)

high_count = np.count_nonzero(
    risk == 3
)


valid_probabilities = probability[
    valid
]


# ============================================================
# FINAL OUTPUT
# ============================================================

print("\n" + "=" * 60)
print("AI RISK VISUALIZATION CREATED SUCCESSFULLY")
print("=" * 60)

print(f"\nOutput: {OUTPUT}")

print(
    f"Valid pixels: "
    f"{total:,}"
)

print(
    f"Low risk: "
    f"{low_count:,}"
)

print(
    f"Medium risk: "
    f"{medium_count:,}"
)

print(
    f"High risk: "
    f"{high_count:,}"
)

print("\nProbability statistics:")

print(
    f"Minimum: "
    f"{valid_probabilities.min():.4f}"
)

print(
    f"Mean: "
    f"{valid_probabilities.mean():.4f}"
)

print(
    f"Median: "
    f"{np.median(valid_probabilities):.4f}"
)

print(
    f"Maximum: "
    f"{valid_probabilities.max():.4f}"
)

print("\nDone.")