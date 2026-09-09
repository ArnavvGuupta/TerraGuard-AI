import os
import random
from pathlib import Path

import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio
from shapely.geometry import Point


# ============================================================
# CONFIG
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

TRAINING_PATH = BASE_DIR / "data" / "training_data.csv"
LANDSLIDE_DIR = BASE_DIR / "data" / "landslides"

OUTPUT_PATH = BASE_DIR / "data" / "training_data_hard_negative.csv"

SATELLITE_DATE = "2026-08-14"

TARGET_NEGATIVES = 240
CANDIDATE_COUNT = 20000

RANDOM_SEED = 42

random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)


# ============================================================
# FIND DEM
# ============================================================

dem_files = list(
    (BASE_DIR / "data" / "raw").rglob("*_DEM_30m.tif")
)

if not dem_files:
    raise FileNotFoundError(
        "Could not find DEM file inside data/raw"
    )

DEM_PATH = dem_files[0]

print("=" * 60)
print("HARD NEGATIVE DATASET CREATION")
print("=" * 60)

print(f"DEM: {DEM_PATH}")


# ============================================================
# FIND SATELLITE BANDS
# ============================================================

satellite_dir = BASE_DIR / "data" / "processed" / "satellite" / SATELLITE_DATE

band_paths = {}

for band in ["BAND2.tif", "BAND3.tif", "BAND4.tif", "BAND5.tif"]:
    matches = list(satellite_dir.rglob(band))

    if not matches:
        raise FileNotFoundError(
            f"Could not find {band} under {satellite_dir}"
        )

    band_paths[band] = matches[0]

print("\nSatellite bands:")

for name, path in band_paths.items():
    print(f"  {name}: {path}")


# ============================================================
# LOAD ORIGINAL TRAINING DATA
# ============================================================

df = pd.read_csv(TRAINING_PATH)

positive_df = df[df["label"] == 1].copy()

print("\nOriginal dataset:")
print(f"Total samples: {len(df)}")
print(f"Positive samples: {len(positive_df)}")

if len(positive_df) != 240:
    print(
        f"WARNING: Expected 240 positive samples, "
        f"found {len(positive_df)}"
    )


# ============================================================
# POSITIVE FEATURE DISTRIBUTIONS
# ============================================================

positive_elevation_median = positive_df["elevation"].median()
positive_slope_median = positive_df["slope"].median()

positive_elevation_q25 = positive_df["elevation"].quantile(0.25)
positive_elevation_q75 = positive_df["elevation"].quantile(0.75)

positive_slope_q25 = positive_df["slope"].quantile(0.25)
positive_slope_q75 = positive_df["slope"].quantile(0.75)

elevation_iqr = positive_elevation_q75 - positive_elevation_q25
slope_iqr = positive_slope_q75 - positive_slope_q25

print("\nPositive sample characteristics:")

print(
    f"Elevation median : {positive_elevation_median:.2f}"
)

print(
    f"Elevation Q25-Q75: "
    f"{positive_elevation_q25:.2f} - "
    f"{positive_elevation_q75:.2f}"
)

print(
    f"Slope median     : {positive_slope_median:.2f}"
)

print(
    f"Slope Q25-Q75    : "
    f"{positive_slope_q25:.2f} - "
    f"{positive_slope_q75:.2f}"
)


# ============================================================
# LOAD LANDSLIDE POLYGONS
# ============================================================

polygon_files = list(
    LANDSLIDE_DIR.glob("*polygon*.shp")
)

if not polygon_files:
    raise FileNotFoundError(
        "Could not find landslide polygon shapefile."
    )

polygon_path = polygon_files[0]

landslides = gpd.read_file(polygon_path)

print("\nLandslide polygons:")
print(f"Count: {len(landslides)}")
print(f"CRS: {landslides.crs}")


# ============================================================
# LOAD DEM
# ============================================================

dem = rasterio.open(DEM_PATH)

print("\nDEM information:")
print(f"Size: {dem.width} x {dem.height}")
print(f"CRS: {dem.crs}")
print(f"Bounds: {dem.bounds}")


# ============================================================
# GENERATE CANDIDATE NEGATIVES
# ============================================================

min_lon = dem.bounds.left
max_lon = dem.bounds.right
min_lat = dem.bounds.bottom
max_lat = dem.bounds.top

print("\nGenerating candidate points...")

candidate_records = []

attempts = 0

while len(candidate_records) < CANDIDATE_COUNT:
    attempts += 1

    lon = random.uniform(min_lon, max_lon)
    lat = random.uniform(min_lat, max_lat)

    point = Point(lon, lat)

    # Skip points inside known landslide polygons
    inside_landslide = False

    for geom in landslides.geometry:
        if geom is not None and geom.contains(point):
            inside_landslide = True
            break

    if inside_landslide:
        continue

    try:
        row, col = dem.index(lon, lat)

        if (
            row < 0
            or row >= dem.height
            or col < 0
            or col >= dem.width
        ):
            continue

        elevation = dem.read(1)[row, col]

        if not np.isfinite(elevation):
            continue

        candidate_records.append(
            {
                "latitude": lat,
                "longitude": lon,
                "elevation": float(elevation),
            }
        )

    except Exception:
        continue

    if attempts % 5000 == 0:
        print(
            f"Candidates: {len(candidate_records)} / "
            f"{CANDIDATE_COUNT}"
        )


candidates = pd.DataFrame(candidate_records)

print(
    f"\nGenerated {len(candidates)} valid candidates."
)


# ============================================================
# CALCULATE SLOPE FOR CANDIDATES
# ============================================================

print("\nCalculating slope for candidates...")

dem_array = dem.read(1).astype(np.float32)

transform = dem.transform

pixel_x = abs(transform.a)
pixel_y = abs(transform.e)

# Approximate geographic distance conversion.
# At this latitude this gives a reasonable local slope estimate.
meters_per_degree_lat = 111320.0

mean_lat = candidates["latitude"].mean()

meters_per_degree_lon = (
    111320.0 * np.cos(np.radians(mean_lat))
)

dx = pixel_x * meters_per_degree_lon
dy = pixel_y * meters_per_degree_lat

grad_y, grad_x = np.gradient(
    dem_array,
    dy,
    dx
)

slope_radians = np.arctan(
    np.sqrt(grad_x ** 2 + grad_y ** 2)
)

slope_degrees = np.degrees(slope_radians)


candidate_slopes = []

for _, row in candidates.iterrows():

    try:
        dem_row, dem_col = dem.index(
            row["longitude"],
            row["latitude"]
        )

        slope_value = slope_degrees[
            dem_row,
            dem_col
        ]

        if np.isfinite(slope_value):
            candidate_slopes.append(
                float(slope_value)
            )
        else:
            candidate_slopes.append(np.nan)

    except Exception:
        candidate_slopes.append(np.nan)


candidates["slope"] = candidate_slopes

candidates = candidates.dropna(
    subset=["elevation", "slope"]
).reset_index(drop=True)


print(
    f"Valid candidates after slope calculation: "
    f"{len(candidates)}"
)


# ============================================================
# FILTER TOWARD LANDSLIDE-LIKE TERRAIN
# ============================================================

print("\nSelecting hard negatives...")


def hard_negative_score(row):

    elevation_distance = abs(
        row["elevation"] - positive_elevation_median
    ) / elevation_iqr

    slope_distance = abs(
        row["slope"] - positive_slope_median
    ) / slope_iqr

    return elevation_distance + slope_distance


candidates["hard_score"] = candidates.apply(
    hard_negative_score,
    axis=1
)


# Prefer candidates inside the broad positive elevation/slope
# ranges, while still allowing nearby values.

preferred = candidates[
    (candidates["elevation"] >= positive_elevation_q25)
    & (candidates["elevation"] <= positive_elevation_q75)
    & (candidates["slope"] >= positive_slope_q25)
    & (candidates["slope"] <= positive_slope_q75)
].copy()


print(
    f"Candidates inside positive Q25-Q75 terrain range: "
    f"{len(preferred)}"
)


if len(preferred) >= TARGET_NEGATIVES:

    hard_negatives = preferred.sort_values(
        "hard_score"
    ).head(TARGET_NEGATIVES).copy()

else:

    print(
        "Not enough candidates in the preferred range."
    )

    hard_negatives = candidates.sort_values(
        "hard_score"
    ).head(TARGET_NEGATIVES).copy()


print(
    f"Selected {len(hard_negatives)} hard negatives."
)


# ============================================================
# OPEN SATELLITE DATA
# ============================================================

print("\nLoading satellite bands...")

band_arrays = {}
band_transforms = {}
band_crs = {}

for band_name, path in band_paths.items():

    src = rasterio.open(path)

    band_arrays[band_name] = src.read(1)
    band_transforms[band_name] = src.transform
    band_crs[band_name] = src.crs

    print(
        f"{band_name}: "
        f"{src.width} x {src.height}, "
        f"CRS={src.crs}"
    )


# ============================================================
# EXTRACT FEATURES
# ============================================================

print("\nExtracting satellite features...")


def extract_satellite_features(lat, lon):

    values = {}

    for band_name in [
        "BAND2.tif",
        "BAND3.tif",
        "BAND4.tif",
        "BAND5.tif",
    ]:

        transform = band_transforms[band_name]

        # Satellite data is UTM, while our point is WGS84.
        # Convert the point to the satellite CRS.

        point_gdf = gpd.GeoDataFrame(
            geometry=[Point(lon, lat)],
            crs="EPSG:4326"
        )

        point_utm = point_gdf.to_crs(
            band_crs[band_name]
        )

        x = point_utm.geometry.iloc[0].x
        y = point_utm.geometry.iloc[0].y

        col, row = ~transform * (x, y)

        row = int(row)
        col = int(col)

        array = band_arrays[band_name]

        if (
            row < 0
            or row >= array.shape[0]
            or col < 0
            or col >= array.shape[1]
        ):
            return None

        value = array[row, col]

        if not np.isfinite(value):
            return None

        values[band_name] = float(value)

    b2 = values["BAND2.tif"]
    b3 = values["BAND3.tif"]
    b4 = values["BAND4.tif"]
    b5 = values["BAND5.tif"]

    # Avoid division by zero
    ndvi_den = b4 + b3
    ndwi_den = b2 + b4
    nbr_den = b4 + b5

    if (
        ndvi_den == 0
        or ndwi_den == 0
        or nbr_den == 0
    ):
        return None

    ndvi = (b4 - b3) / ndvi_den
    ndwi = (b2 - b4) / ndwi_den
    nbr = (b4 - b5) / nbr_den

    return {
        "B2": b2,
        "B3": b3,
        "B4": b4,
        "B5": b5,
        "NDVI": ndvi,
        "NDWI": ndwi,
        "NBR": nbr,
    }


# ============================================================
# BUILD NEGATIVE DATASET
# ============================================================

negative_records = []

for i, row in hard_negatives.iterrows():

    features = extract_satellite_features(
        row["latitude"],
        row["longitude"]
    )

    if features is None:
        continue

    record = {
        "latitude": row["latitude"],
        "longitude": row["longitude"],
        "elevation": row["elevation"],
        "slope": row["slope"],
        "aspect": 0.0,
        "label": 0,
    }

    record.update(features)

    negative_records.append(record)

    if len(negative_records) % 50 == 0:
        print(
            f"Processed {len(negative_records)} "
            f"hard negatives..."
        )


negative_df = pd.DataFrame(
    negative_records
)


print(
    f"\nValid hard negatives with spectral data: "
    f"{len(negative_df)}"
)


# ============================================================
# KEEP POSITIVE DATA
# ============================================================

positive_output = positive_df[
    [
        "latitude",
        "longitude",
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
        "label",
    ]
].copy()


# ============================================================
# COMBINE
# ============================================================

final_df = pd.concat(
    [
        positive_output,
        negative_df[
            [
                "latitude",
                "longitude",
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
                "label",
            ]
        ],
    ],
    ignore_index=True
)


# ============================================================
# REMOVE MISSING VALUES
# ============================================================

final_df = final_df.dropna().reset_index(drop=True)


# ============================================================
# SAVE
# ============================================================

final_df.to_csv(
    OUTPUT_PATH,
    index=False
)


# ============================================================
# SUMMARY
# ============================================================

# ============================================================
# SUMMARY
# ============================================================

print("\n" + "=" * 60)
print("HARD NEGATIVE DATASET CREATED")
print("=" * 60)

print(f"\nOutput:")
print(OUTPUT_PATH)

print(f"\nShape: {final_df.shape}")

print("\nClass distribution:")
print(final_df["label"].value_counts())

print("\nMissing values:")
print(final_df.isna().sum())

print("\nLandslide terrain:")
print(
    positive_output[["elevation", "slope"]].describe()
)

print("\nHard-negative terrain:")
print(
    negative_df[["elevation", "slope"]].describe()
)

print("\nDone.")