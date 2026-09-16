from pathlib import Path

import numpy as np
import rasterio
from sklearn.ensemble import IsolationForest


BASE = Path("data/processed/satellite")
OUTPUT = Path("data/processed/monitoring")

AUG = BASE / "2026-08-14"
SEP = BASE / "2026-09-02"

OUTPUT.mkdir(parents=True, exist_ok=True)


def read_common_area(path_a, path_b):
    with rasterio.open(path_a) as a, rasterio.open(path_b) as b:
        left = max(a.bounds.left, b.bounds.left)
        right = min(a.bounds.right, b.bounds.right)
        bottom = max(a.bounds.bottom, b.bounds.bottom)
        top = min(a.bounds.top, b.bounds.top)

        window_a = rasterio.windows.from_bounds(
            left, bottom, right, top, transform=a.transform
        )

        window_b = rasterio.windows.from_bounds(
            left, bottom, right, top, transform=b.transform
        )

        data_a = a.read(
            1,
            window=window_a,
            out_dtype="float32",
        )

        data_b = b.read(
            1,
            window=window_b,
            out_dtype="float32",
        )

        height = min(data_a.shape[0], data_b.shape[0])
        width = min(data_a.shape[1], data_b.shape[1])

        data_a = data_a[:height, :width]
        data_b = data_b[:height, :width]

        transform = rasterio.windows.transform(
            rasterio.windows.Window(
                window_a.col_off,
                window_a.row_off,
                width,
                height,
            ),
            a.transform,
        )

        return data_a, data_b, transform


def robust_normalize(data):
    valid = np.isfinite(data)

    if not np.any(valid):
        return np.zeros_like(data, dtype=np.float32)

    low = np.percentile(data[valid], 2)
    high = np.percentile(data[valid], 98)

    if high <= low:
        return np.zeros_like(data, dtype=np.float32)

    result = (data - low) / (high - low)

    return np.clip(result, 0, 1).astype(np.float32)


print("Loading satellite bands...")

features = []

band_names = ["BAND2.tif", "BAND3.tif", "BAND4.tif", "BAND5.tif"]

transform = None

for band_name in band_names:

    aug_path = AUG / band_name
    sep_path = SEP / band_name

    print(f"Processing {band_name}")

    aug, sep, transform = read_common_area(
        aug_path,
        sep_path,
    )

    aug_norm = robust_normalize(aug)
    sep_norm = robust_normalize(sep)

    change = np.abs(sep_norm - aug_norm)

    features.append(change)


# Stack the four spectral changes
change_stack = np.stack(features, axis=-1)

height, width, num_features = change_stack.shape

print()
print("Feature shape:")
print(f"  Height: {height}")
print(f"  Width:  {width}")
print(f"  Features per pixel: {num_features}")


# Valid pixels
valid = np.all(np.isfinite(change_stack), axis=2)

X = change_stack[valid]

print()
print(f"Valid pixels: {len(X):,}")


# The dataset is large, so train on a representative sample.
rng = np.random.default_rng(42)

sample_size = min(100_000, len(X))

sample_indices = rng.choice(
    len(X),
    size=sample_size,
    replace=False,
)

X_sample = X[sample_indices]

print(f"Training samples: {len(X_sample):,}")


# Isolation Forest
print()
print("Training Isolation Forest...")

model = IsolationForest(
    n_estimators=100,
    contamination=0.05,
    random_state=42,
    n_jobs=-1,
)

model.fit(X_sample)


print("Model trained.")


# Calculate anomaly scores
print("Calculating anomaly scores...")

decision_scores = model.decision_function(X)

# Convert so larger = more anomalous
anomaly_scores = -decision_scores

# Normalize to 0-1
score_low = np.percentile(anomaly_scores, 2)
score_high = np.percentile(anomaly_scores, 98)

if score_high > score_low:
    anomaly_normalized = (
        (anomaly_scores - score_low)
        / (score_high - score_low)
    )
else:
    anomaly_normalized = np.zeros_like(anomaly_scores)

anomaly_normalized = np.clip(
    anomaly_normalized,
    0,
    1,
)


# Put scores back into raster
output = np.full(
    (height, width),
    np.nan,
    dtype=np.float32,
)

output[valid] = anomaly_normalized.astype(np.float32)


# Save
output_path = OUTPUT / "ai_change_anomaly.tif"

with rasterio.open(
    output_path,
    "w",
    driver="GTiff",
    height=height,
    width=width,
    count=1,
    dtype="float32",
    crs="EPSG:32645",
    transform=transform,
    nodata=np.nan,
) as dst:

    dst.write(output, 1)


print()
print("AI monitoring completed!")
print(f"Output: {output_path}")

print()
print("Anomaly statistics:")
print(f"  Minimum: {np.nanmin(output):.4f}")
print(f"  Mean:    {np.nanmean(output):.4f}")
print(f"  Maximum: {np.nanmax(output):.4f}")

print()
print("Interpretation:")
print("  0.0 → normal / lower change anomaly")
print("  1.0 → unusual spectral change")
print()
print("NOTE:")
print("This is an unsupervised change-anomaly detector.")
print("It does NOT confirm that an anomaly is a landslide.")