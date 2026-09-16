import os
import joblib
import numpy as np
import pandas as pd
import rasterio
from rasterio.warp import reproject, Resampling


# ============================================================
# PATHS
# ============================================================

TRAINING = r"data/training_data_hard_negative.csv"
MODEL = r"data/xgboost_landslide_model_hard_negative.pkl"

DEM = r"data/raw/P5_PAN_CD_N27_000_E088_000_30m/P5_PAN_CD_N27_000_E088_000_30m/P5_PAN_CD_N27_000_E088_000_DEM_30m.tif"
SLOPE = r"data/processed/slope.tif"
ASPECT = r"data/processed/aspect.tif"

SAT_ROOT = r"data/processed/satellite/2026-09-02"


FEATURES = [
    "elevation",
    "slope",
    "aspect",
    "B2",
    "B3",
    "B4",
    "B5",
    "NDVI",
    "NDWI",
    "NBR",
]


# ============================================================
# HELPERS
# ============================================================

def print_stats(name, values):
    values = np.asarray(values, dtype=np.float64)
    values = values[np.isfinite(values)]

    print(f"\n{name}")
    print("-" * 70)
    print(f"Count : {len(values):,}")
    print(f"Min   : {np.min(values):.4f}")
    print(f"Q01   : {np.percentile(values, 1):.4f}")
    print(f"Q25   : {np.percentile(values, 25):.4f}")
    print(f"Median: {np.median(values):.4f}")
    print(f"Mean  : {np.mean(values):.4f}")
    print(f"Q75   : {np.percentile(values, 75):.4f}")
    print(f"Q99   : {np.percentile(values, 99):.4f}")
    print(f"Max   : {np.max(values):.4f}")


def find_band(root, band_name):
    candidates = [
        f"{band_name}.tif",
        f"BAND{band_name.replace('B', '')}.tif"
    ]

    for candidate in candidates:
        path = os.path.join(root, candidate)
        if os.path.exists(path):
            return path

    raise FileNotFoundError(
        f"Could not find {band_name}.tif or BAND*.tif inside {root}"
    )

# ============================================================
# HEADER
# ============================================================

print("=" * 70)
print("AI LANDSLIDE RISK DIAGNOSTIC")
print("=" * 70)


# ============================================================
# 1. LOAD TRAINING DATA
# ============================================================

print("\nLoading training data...")

df = pd.read_csv(TRAINING)

print(f"Training samples: {len(df):,}")
print(f"Columns: {list(df.columns)}")


# ============================================================
# 2. TRAINING FEATURE DISTRIBUTIONS
# ============================================================

print("\n")
print("=" * 70)
print("1. TRAINING DATA FEATURE RANGES")
print("=" * 70)

for feature in FEATURES:
    print_stats(
        f"TRAINING - {feature}",
        df[feature].values
    )


# ============================================================
# 3. LOAD MODEL
# ============================================================

print("\n")
print("=" * 70)
print("2. LOADING MODEL")
print("=" * 70)

artifact = joblib.load(MODEL)

model = artifact["model"]
imputer = artifact["imputer"]

print("Model loaded successfully.")


# ============================================================
# 4. LOAD DEM / SLOPE / ASPECT
# ============================================================

print("\n")
print("=" * 70)
print("3. LOADING TERRAIN DATA")
print("=" * 70)

with rasterio.open(DEM) as src:
    elevation = src.read(1).astype(np.float32)
    dem_profile = src.profile.copy()
    dem_transform = src.transform
    dem_crs = src.crs
    dem_shape = elevation.shape

with rasterio.open(SLOPE) as src:
    slope = src.read(1).astype(np.float32)

with rasterio.open(ASPECT) as src:
    aspect = src.read(1).astype(np.float32)

print(f"DEM shape: {elevation.shape}")
print(f"DEM CRS: {dem_crs}")


# ============================================================
# 5. LOAD AND ALIGN SATELLITE BANDS
# ============================================================

print("\n")
print("=" * 70)
print("4. LOADING SATELLITE DATA")
print("=" * 70)

bands = {}

for band_name in ["B2", "B3", "B4", "B5"]:

    path = find_band(SAT_ROOT, band_name)

    print(f"\n{band_name}: {path}")

    with rasterio.open(path) as src:

        destination = np.full(
            dem_shape,
            np.nan,
            dtype=np.float32
        )

        reproject(
            source=rasterio.band(src, 1),
            destination=destination,
            src_transform=src.transform,
            src_crs=src.crs,
            dst_transform=dem_transform,
            dst_crs=dem_crs,
            resampling=Resampling.bilinear,
        )

        bands[band_name] = destination


# ============================================================
# 6. CALCULATE INDICES
# ============================================================

print("\n")
print("=" * 70)
print("5. CALCULATING SPECTRAL INDICES")
print("=" * 70)

B2 = bands["B2"]
B3 = bands["B3"]
B4 = bands["B4"]
B5 = bands["B5"]


def safe_ratio(a, b):
    denominator = a + b

    result = np.full_like(a, np.nan, dtype=np.float32)

    valid = (
        np.isfinite(a)
        & np.isfinite(b)
        & (np.abs(denominator) > 1e-10)
    )

    result[valid] = (
        (a[valid] - b[valid])
        / denominator[valid]
    )

    return result


NDVI = safe_ratio(B4, B3)
NDWI = safe_ratio(B2, B4)
NBR = safe_ratio(B4, B5)


# ============================================================
# 7. BUILD RASTER FEATURE DATA
# ============================================================

raster_features = {
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
# 8. RASTER FEATURE DISTRIBUTIONS
# ============================================================

print("\n")
print("=" * 70)
print("6. FULL RASTER FEATURE RANGES")
print("=" * 70)

for feature in FEATURES:
    print_stats(
        f"RASTER - {feature}",
        raster_features[feature]
    )


# ============================================================
# 9. COMPARE TRAINING RANGE VS RASTER RANGE
# ============================================================

print("\n")
print("=" * 70)
print("7. DISTRIBUTION SHIFT CHECK")
print("=" * 70)

print(
    "\nPercentage of valid raster pixels outside "
    "the training-data min/max range:"
)

print("-" * 70)

valid_base = np.ones(dem_shape, dtype=bool)

for feature in FEATURES:

    values = raster_features[feature]

    valid_base &= np.isfinite(values)

for feature in FEATURES:

    train_values = df[feature].values
    train_values = train_values[np.isfinite(train_values)]

    train_min = np.min(train_values)
    train_max = np.max(train_values)

    raster_values = raster_features[feature][valid_base]

    outside = (
        (raster_values < train_min)
        | (raster_values > train_max)
    )

    percentage = (
        np.count_nonzero(outside)
        / len(raster_values)
        * 100
    )

    print(
        f"{feature:10s} "
        f"Train [{train_min:.4f}, {train_max:.4f}] | "
        f"Outside: {percentage:6.2f}%"
    )


# ============================================================
# 10. BUILD MODEL INPUT
# ============================================================

print("\n")
print("=" * 70)
print("8. TESTING MODEL PROBABILITIES")
print("=" * 70)

valid_indices = np.where(valid_base)

rows = valid_indices[0]
cols = valid_indices[1]

X_raster = np.column_stack([
    raster_features[feature][valid_base]
    for feature in FEATURES
])

print(f"Valid raster pixels: {len(X_raster):,}")


# Apply the same imputer used during training
X_imputed = imputer.transform(X_raster)


# ============================================================
# 11. PREDICT IN CHUNKS
# ============================================================

probabilities = []

chunk_size = 100_000

for start in range(0, len(X_imputed), chunk_size):

    end = min(
        start + chunk_size,
        len(X_imputed)
    )

    probs = model.predict_proba(
        X_imputed[start:end]
    )[:, 1]

    probabilities.append(probs)

    print(
        f"Processed {end:,} / {len(X_imputed):,}"
    )

probabilities = np.concatenate(probabilities)


# ============================================================
# 12. PROBABILITY DISTRIBUTION
# ============================================================

print("\n")
print("=" * 70)
print("9. MODEL PROBABILITY DISTRIBUTION")
print("=" * 70)

print(f"Minimum : {np.min(probabilities):.6f}")
print(f"Q01     : {np.percentile(probabilities, 1):.6f}")
print(f"Q05     : {np.percentile(probabilities, 5):.6f}")
print(f"Q10     : {np.percentile(probabilities, 10):.6f}")
print(f"Q25     : {np.percentile(probabilities, 25):.6f}")
print(f"Median  : {np.median(probabilities):.6f}")
print(f"Q75     : {np.percentile(probabilities, 75):.6f}")
print(f"Q90     : {np.percentile(probabilities, 90):.6f}")
print(f"Q95     : {np.percentile(probabilities, 95):.6f}")
print(f"Q99     : {np.percentile(probabilities, 99):.6f}")
print(f"Mean    : {np.mean(probabilities):.6f}")
print(f"Maximum : {np.max(probabilities):.6f}")


# ============================================================
# 13. CURRENT THRESHOLD DISTRIBUTION
# ============================================================

print("\n")
print("=" * 70)
print("10. CURRENT 0.33 / 0.66 THRESHOLDS")
print("=" * 70)

low = np.count_nonzero(probabilities < 0.33)

medium = np.count_nonzero(
    (probabilities >= 0.33)
    & (probabilities < 0.66)
)

high = np.count_nonzero(probabilities >= 0.66)

total = len(probabilities)

print(
    f"LOW    : {low:,} "
    f"({low / total * 100:.2f}%)"
)

print(
    f"MEDIUM : {medium:,} "
    f"({medium / total * 100:.2f}%)"
)

print(
    f"HIGH   : {high:,} "
    f"({high / total * 100:.2f}%)"
)


# ============================================================
# FINISHED
# ============================================================

print("\n")
print("=" * 70)
print("DIAGNOSTIC COMPLETE")
print("=" * 70)

