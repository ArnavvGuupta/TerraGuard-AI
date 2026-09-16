import os
import random
import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio

from rasterio.transform import rowcol
from pyproj import Transformer
from shapely.geometry import Point


# ==========================================
# PATHS
# ==========================================

DEM_PATH = r"data/raw/P5_PAN_CD_N27_000_E088_000_30m/P5_PAN_CD_N27_000_E088_000_30m/P5_PAN_CD_N27_000_E088_000_DEM_30m.tif"

LANDSLIDE_PATH = (
    r"data\landslides"
    r"\Google_Earth_landslides_polygon_21Dec2021.shp"
)

SATELLITE_DIR = r"data\satellite\2026-08-14"

OUTPUT_PATH = r"data\training_data_balanced.csv"


# ==========================================
# SETTINGS
# ==========================================

POSITIVE_SAMPLES = 240
NEGATIVE_SAMPLES = 720

RANDOM_SEED = 42

random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)


# ==========================================
# FIND SATELLITE BANDS
# ==========================================

band_files = {}

for root, dirs, files in os.walk(SATELLITE_DIR):

    for file in files:

        if file.upper() == "BAND2.TIF":
            band_files["B2"] = os.path.join(root, file)

        elif file.upper() == "BAND3.TIF":
            band_files["B3"] = os.path.join(root, file)

        elif file.upper() == "BAND4.TIF":
            band_files["B4"] = os.path.join(root, file)

        elif file.upper() == "BAND5.TIF":
            band_files["B5"] = os.path.join(root, file)


required_bands = ["B2", "B3", "B4", "B5"]

for band in required_bands:

    if band not in band_files:
        raise FileNotFoundError(
            f"Could not find {band}.tif inside {SATELLITE_DIR}"
        )


print("Satellite bands found:")

for band in required_bands:
    print(f"{band}: {band_files[band]}")


# ==========================================
# LOAD LANDSLIDES
# ==========================================

print("\nLoading landslide polygons...")

landslides = gpd.read_file(LANDSLIDE_PATH)

print("Number of landslide polygons:", len(landslides))
print("CRS:", landslides.crs)


# ==========================================
# LOAD DEM
# ==========================================

print("\nLoading DEM...")

dem = rasterio.open(DEM_PATH)

dem_data = dem.read(1)

print("DEM size:", dem.width, "x", dem.height)
print("DEM CRS:", dem.crs)
print("DEM resolution:", dem.res)


# ==========================================
# COORDINATE TRANSFORMER
# ==========================================

transformer = Transformer.from_crs(
    "EPSG:4326",
    dem.crs,
    always_xy=True
)


# ==========================================
# LOAD SATELLITE DATA
# ==========================================

print("\nLoading satellite imagery...")

sat = {}

for band in required_bands:

    src = rasterio.open(band_files[band])

    sat[band] = src

    print(
        band,
        "CRS:", src.crs,
        "Size:", src.width, "x", src.height,
        "Resolution:", src.res
    )


# Satellite transformer
sat_transformer = Transformer.from_crs(
    "EPSG:4326",
    sat["B2"].crs,
    always_xy=True
)


# ==========================================
# FUNCTIONS
# ==========================================

def get_dem_value(lon, lat):

    try:

        x, y = transformer.transform(lon, lat)

        row, col = rowcol(
            dem.transform,
            x,
            y
        )

        if (
            row < 0
            or row >= dem.height
            or col < 0
            or col >= dem.width
        ):
            return np.nan

        value = dem_data[row, col]

        if not np.isfinite(value):
            return np.nan

        return float(value)

    except Exception:
        return np.nan


def get_slope_aspect(lon, lat):

    try:

        x, y = transformer.transform(lon, lat)

        row, col = rowcol(
            dem.transform,
            x,
            y
        )

        if row <= 0 or row >= dem.height - 1:
            return np.nan, np.nan

        if col <= 0 or col >= dem.width - 1:
            return np.nan, np.nan

        z1 = dem_data[row - 1, col]
        z2 = dem_data[row + 1, col]
        z3 = dem_data[row, col - 1]
        z4 = dem_data[row, col + 1]

        if not all(np.isfinite(v) for v in [z1, z2, z3, z4]):
            return np.nan, np.nan

        # Approximate meters per degree
        lat_factor = 111320.0
        lon_factor = 111320.0 * np.cos(np.radians(lat))

        dx = dem.res[0] * lon_factor
        dy = dem.res[1] * lat_factor

        dzdx = (z4 - z3) / (2 * dx)
        dzdy = (z2 - z1) / (2 * dy)

        slope = np.degrees(
            np.arctan(
                np.sqrt(
                    dzdx ** 2 + dzdy ** 2
                )
            )
        )

        aspect = np.degrees(
            np.arctan2(
                -dzdx,
                dzdy
            )
        )

        aspect = (aspect + 360) % 360

        return float(slope), float(aspect)

    except Exception:

        return np.nan, np.nan


def get_satellite_values(lon, lat):

    try:

        x, y = sat_transformer.transform(
            lon,
            lat
        )

        values = {}

        for band in required_bands:

            src = sat[band]

            row, col = rowcol(
                src.transform,
                x,
                y
            )

            if (
                row < 0
                or row >= src.height
                or col < 0
                or col >= src.width
            ):
                return None

            value = src.read(1)[row, col]

            if not np.isfinite(value):
                return None

            values[band] = float(value)

        return values

    except Exception:

        return None


def calculate_indices(values):

    B2 = values["B2"]
    B3 = values["B3"]
    B4 = values["B4"]
    B5 = values["B5"]

    # NDVI
    ndvi_denominator = B4 + B3

    if ndvi_denominator != 0:
        ndvi = (B4 - B3) / ndvi_denominator
    else:
        ndvi = np.nan

    # NDWI
    ndwi_denominator = B2 + B4

    if ndwi_denominator != 0:
        ndwi = (B2 - B4) / ndwi_denominator
    else:
        ndwi = np.nan

    # NBR
    nbr_denominator = B4 + B5

    if nbr_denominator != 0:
        nbr = (B4 - B5) / nbr_denominator
    else:
        nbr = np.nan

    return ndvi, ndwi, nbr


# ==========================================
# POSITIVE SAMPLES
# ==========================================

print("\nGenerating positive samples...")

positive_points = []

for geometry in landslides.geometry:

    if geometry is None or geometry.is_empty:
        continue

    try:

        point = geometry.representative_point()

        positive_points.append(
            (
                point.x,
                point.y
            )
        )

    except Exception:
        continue


# If more polygons than required, randomly select
if len(positive_points) > POSITIVE_SAMPLES:

    positive_points = random.sample(
        positive_points,
        POSITIVE_SAMPLES
    )


print(
    "Positive samples:",
    len(positive_points)
)


# ==========================================
# PREPARE LANDSLIDE GEOMETRIES
# ==========================================

landslide_geometries = list(
    landslides.geometry
)


def is_inside_landslide(lon, lat):

    point = Point(lon, lat)

    for geometry in landslide_geometries:

        if geometry is not None and not geometry.is_empty:

            if geometry.contains(point):

                return True

    return False


# ==========================================
# NEGATIVE SAMPLE BOUNDARY
# ==========================================

minx, miny, maxx, maxy = landslides.total_bounds

print("\nStudy area bounds:")

print("Min longitude:", minx)
print("Max longitude:", maxx)
print("Min latitude :", miny)
print("Max latitude :", maxy)


# ==========================================
# GENERATE NEGATIVE SAMPLES
# ==========================================

print("\nGenerating negative samples...")

negative_points = []

attempts = 0

max_attempts = NEGATIVE_SAMPLES * 100


while (
    len(negative_points) < NEGATIVE_SAMPLES
    and attempts < max_attempts
):

    attempts += 1

    lon = random.uniform(
        minx,
        maxx
    )

    lat = random.uniform(
        miny,
        maxy
    )

    # Reject points inside known landslides
    if is_inside_landslide(lon, lat):

        continue

    # Check DEM
    elevation = get_dem_value(
        lon,
        lat
    )

    if not np.isfinite(elevation):

        continue

    # Keep valid point
    negative_points.append(
        (
            lon,
            lat
        )
    )


print(
    "Negative samples:",
    len(negative_points)
)

print(
    "Sampling attempts:",
    attempts
)


# ==========================================
# EXTRACT FEATURES
# ==========================================

print("\nExtracting features...")

records = []


def process_point(
    lon,
    lat,
    label
):

    elevation = get_dem_value(
        lon,
        lat
    )

    slope, aspect = get_slope_aspect(
        lon,
        lat
    )

    satellite_values = get_satellite_values(
        lon,
        lat
    )

    if satellite_values is None:

        return None

    ndvi, ndwi, nbr = calculate_indices(
        satellite_values
    )

    return {
        "latitude": lat,
        "longitude": lon,
        "elevation": elevation,
        "slope": slope,
        "aspect": aspect,

        "B2": satellite_values["B2"],
        "B3": satellite_values["B3"],
        "B4": satellite_values["B4"],
        "B5": satellite_values["B5"],

        "NDVI": ndvi,
        "NDWI": ndwi,
        "NBR": nbr,

        "label": label
    }


# Positive
for i, (lon, lat) in enumerate(
    positive_points,
    start=1
):

    record = process_point(
        lon,
        lat,
        1
    )

    if record is not None:

        records.append(record)

    if i % 50 == 0:

        print(
            f"Processed positive: {i}/{len(positive_points)}"
        )


# Negative
for i, (lon, lat) in enumerate(
    negative_points,
    start=1
):

    record = process_point(
        lon,
        lat,
        0
    )

    if record is not None:

        records.append(record)

    if i % 100 == 0:

        print(
            f"Processed negative: {i}/{len(negative_points)}"
        )


# ==========================================
# CREATE DATAFRAME
# ==========================================

df = pd.DataFrame(records)


# ==========================================
# SHUFFLE
# ==========================================

df = df.sample(
    frac=1,
    random_state=RANDOM_SEED
).reset_index(drop=True)


# ==========================================
# SAVE
# ==========================================

df.to_csv(
    OUTPUT_PATH,
    index=False
)


# ==========================================
# SUMMARY
# ==========================================

print("\n===================================")
print("     DATASET CREATED")
print("===================================")

print("Output:", OUTPUT_PATH)

print("Shape:", df.shape)

print("\nClass distribution:")

print(
    df["label"].value_counts()
)

print("\nMissing values:")

print(
    df.isna().sum()
)

print("\nFirst 5 rows:")

print(
    df.head()
)