import os
import random
import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio

from rasterio.transform import rowcol
from pyproj import Transformer


# ============================================================
# PATHS
# ============================================================

DEM_PATH = r"data/raw/P5_PAN_CD_N27_000_E088_000_30m/P5_PAN_CD_N27_000_E088_000_30m/P5_PAN_CD_N27_000_E088_000_DEM_30m.tif"

LANDSLIDE_PATH = (
    r"data\landslides"
    r"\Google_Earth_landslides_polygon_21Dec2021.shp"
)

SATELLITE_DIR = (
    r"data\satellite\2026-08-14"
    r"\R2314AUG2026079496010700052PSANSTUC00GTDF"
    r"\R2314AUG2026079496010700052PSANSTUC00GTDF"
)

OUTPUT_PATH = r"data\training_data.csv"


# ============================================================
# SETTINGS
# ============================================================

NUM_POSITIVE = 240
NUM_NEGATIVE = 240

random.seed(42)
np.random.seed(42)


# ============================================================
# 1. LOAD LANDSLIDE POLYGONS
# ============================================================

print("Loading landslide polygons...")

landslides = gpd.read_file(LANDSLIDE_PATH)

print("Number of landslide polygons:", len(landslides))
print("Landslide CRS:", landslides.crs)


# Make sure landslides use the DEM CRS
if landslides.crs is None:
    landslides = landslides.set_crs("EPSG:4326")

landslides = landslides.to_crs("EPSG:4326")


# ============================================================
# 2. OPEN DEM
# ============================================================

print("\nOpening DEM...")

with rasterio.open(DEM_PATH) as dem:

    dem_data = dem.read(1).astype("float32")

    dem_crs = dem.crs
    dem_transform = dem.transform

    print("DEM CRS:", dem_crs)
    print("DEM size:", dem.width, "x", dem.height)
    print("DEM resolution:", dem.res)

    # DEM nodata handling
    if dem.nodata is not None:
        dem_data[dem_data == dem.nodata] = np.nan


# ============================================================
# 3. CALCULATE SLOPE AND ASPECT
# ============================================================

print("\nCalculating slope and aspect...")

# DEM is in EPSG:4326, so pixel resolution is in degrees.
# Convert approximate degree distance to meters.

height, width = dem_data.shape

center_lat = (
    dem_transform.f
    + (height / 2) * dem_transform.e
)

meters_per_degree_lat = 111320.0

meters_per_degree_lon = (
    111320.0 * np.cos(np.radians(center_lat))
)

pixel_x_m = abs(dem_transform.a) * meters_per_degree_lon
pixel_y_m = abs(dem_transform.e) * meters_per_degree_lat

# Calculate elevation gradients
dz_dy, dz_dx = np.gradient(
    dem_data,
    pixel_y_m,
    pixel_x_m
)

# Slope in degrees
slope = np.degrees(
    np.arctan(
        np.sqrt(dz_dx ** 2 + dz_dy ** 2)
    )
)

# Aspect
aspect = np.degrees(
    np.arctan2(-dz_dx, dz_dy)
)

aspect = (aspect + 360) % 360

print("Slope and aspect calculated successfully.")


# ============================================================
# 4. LOAD SATELLITE BANDS
# ============================================================

print("\nLoading satellite bands...")

band_paths = {
    "B2": os.path.join(SATELLITE_DIR, "BAND2.tif"),
    "B3": os.path.join(SATELLITE_DIR, "BAND3.tif"),
    "B4": os.path.join(SATELLITE_DIR, "BAND4.tif"),
    "B5": os.path.join(SATELLITE_DIR, "BAND5.tif"),
}


satellite_data = {}
satellite_crs = None
satellite_transform = None
satellite_shape = None


for band_name, band_path in band_paths.items():

    print("Opening", band_name)

    with rasterio.open(band_path) as src:

        data = src.read(1).astype("float32")

        # Store CRS/transform from first band
        if satellite_crs is None:
            satellite_crs = src.crs
            satellite_transform = src.transform
            satellite_shape = data.shape

        # Check that all bands match
        if src.crs != satellite_crs:
            raise ValueError(
                f"{band_name} CRS does not match other bands."
            )

        if src.shape != satellite_shape:
            raise ValueError(
                f"{band_name} shape does not match other bands."
            )

        if src.transform != satellite_transform:
            raise ValueError(
                f"{band_name} transform does not match other bands."
            )

        # Handle nodata
        if src.nodata is not None:
            data[data == src.nodata] = np.nan

        satellite_data[band_name] = data


print("Satellite CRS:", satellite_crs)
print("Satellite size:", satellite_shape)
print("Satellite bands loaded successfully.")


# ============================================================
# 5. TRANSFORMER
# ============================================================

print("\nPreparing coordinate transformation...")

# Training points are latitude/longitude EPSG:4326.
# Satellite imagery is UTM Zone 45N EPSG:32645.

transformer = Transformer.from_crs(
    "EPSG:4326",
    satellite_crs,
    always_xy=True
)


# ============================================================
# 6. HELPER FUNCTION
# ============================================================

def extract_features(latitude, longitude):
    """
    Extract DEM and satellite features for a
    latitude/longitude location.
    """

    # --------------------------------------------------------
    # DEM pixel
    # --------------------------------------------------------

    with rasterio.open(DEM_PATH) as dem:

        row, col = rowcol(
            dem.transform,
            longitude,
            latitude
        )

        if (
            row < 0
            or row >= dem.height
            or col < 0
            or col >= dem.width
        ):
            return None

        elevation = dem_data[row, col]
        slope_value = slope[row, col]
        aspect_value = aspect[row, col]

    # Check DEM values
    if not np.isfinite(elevation):
        return None

    if not np.isfinite(slope_value):
        return None

    if not np.isfinite(aspect_value):
        return None


    # --------------------------------------------------------
    # Transform coordinates to satellite CRS
    # --------------------------------------------------------

    x, y = transformer.transform(
        longitude,
        latitude
    )


    # --------------------------------------------------------
    # Satellite pixel
    # --------------------------------------------------------

    sat_row, sat_col = rowcol(
        satellite_transform,
        x,
        y
    )

    sat_height, sat_width = satellite_shape

    if (
        sat_row < 0
        or sat_row >= sat_height
        or sat_col < 0
        or sat_col >= sat_width
    ):
        return None

    # --------------------------------------------------------
    # Extract B2-B5
    # --------------------------------------------------------

    B2 = satellite_data["B2"][sat_row, sat_col]
    B3 = satellite_data["B3"][sat_row, sat_col]
    B4 = satellite_data["B4"][sat_row, sat_col]
    B5 = satellite_data["B5"][sat_row, sat_col]

    # --------------------------------------------------------
    # Make sure satellite values are valid
    # --------------------------------------------------------

    if not all(
        np.isfinite(v)
        for v in [B2, B3, B4, B5]
    ):
        return None

    # --------------------------------------------------------
    # Calculate spectral indices
    # --------------------------------------------------------

    # NDVI = (NIR - Red) / (NIR + Red)
    # B4 = NIR
    # B3 = Red
    if (B4 + B3) != 0:
        NDVI = (B4 - B3) / (B4 + B3)
    else:
        NDVI = np.nan

    # NDWI = (Green - NIR) / (Green + NIR)
    # B2 = Green
    # B4 = NIR
    if (B2 + B4) != 0:
        NDWI = (B2 - B4) / (B2 + B4)
    else:
        NDWI = np.nan

    # NBR = (NIR - SWIR) / (NIR + SWIR)
    # B4 = NIR
    # B5 = SWIR
    if (B4 + B5) != 0:
        NBR = (B4 - B5) / (B4 + B5)
    else:
        NBR = np.nan

    # --------------------------------------------------------
    # Return all features
    # --------------------------------------------------------

    return {
        "latitude": latitude,
        "longitude": longitude,
        "elevation": float(elevation),
        "slope": float(slope_value),
        "aspect": float(aspect_value),
        "B2": float(B2),
        "B3": float(B3),
        "B4": float(B4),
        "B5": float(B5),
        "NDVI": float(NDVI),
        "NDWI": float(NDWI),
        "NBR": float(NBR),
    }
# ============================================================
# 7. CREATE POSITIVE SAMPLES
# ============================================================

print("\nExtracting landslide samples...")

positive_samples = []

# Shuffle polygons so samples aren't always from
# exactly the same ordering.
landslide_indices = list(landslides.index)
random.shuffle(landslide_indices)

for idx in landslide_indices:

    if len(positive_samples) >= NUM_POSITIVE:
        break

    geometry = landslides.loc[idx].geometry

    if geometry is None or geometry.is_empty:
        continue

    # Representative point is guaranteed to be inside polygon
    point = geometry.representative_point()

    latitude = point.y
    longitude = point.x

    features = extract_features(
        latitude,
        longitude
    )

    if features is None:
        continue

    features["label"] = 1

    positive_samples.append(features)


# ============================================================
# 8. CREATE NEGATIVE SAMPLES
# ============================================================

print("\nGenerating non-landslide samples...")

negative_samples = []

# Get DEM bounds
with rasterio.open(DEM_PATH) as dem:

    bounds = dem.bounds

    valid_dem_mask = np.isfinite(dem_data)

    valid_rows, valid_cols = np.where(
        valid_dem_mask
    )


while len(negative_samples) < NUM_NEGATIVE:

    # Pick a random valid DEM pixel
    random_index = random.randint(
        0,
        len(valid_rows) - 1
    )

    row = valid_rows[random_index]
    col = valid_cols[random_index]

    # Convert pixel → longitude/latitude
    longitude, latitude = rasterio.transform.xy(
        dem_transform,
        row,
        col,
        offset="center"
    )

    # Create point
    point = gpd.points_from_xy(
        [longitude],
        [latitude],
        crs="EPSG:4326"
    )[0]

    # Reject if point is inside known landslide
    inside_landslide = landslides.geometry.contains(
        point
    ).any()

    if inside_landslide:
        continue

    features = extract_features(
        latitude,
        longitude
    )

    if features is None:
        continue

    features["label"] = 0

    negative_samples.append(features)


# ============================================================
# 9. COMBINE DATASET
# ============================================================

print("\nPositive samples:", len(positive_samples))
print("Negative samples:", len(negative_samples))

all_samples = (
    positive_samples +
    negative_samples
)

random.shuffle(all_samples)

df = pd.DataFrame(all_samples)


# ============================================================
# 10. SAVE DATASET
# ============================================================

print("\nFinal dataset:")

print(
    df["label"].value_counts()
)


print("\nDataset columns:")

print(
    df.columns.tolist()
)


print("\nFirst few rows:")

print(
    df.head()
)


df.to_csv(
    OUTPUT_PATH,
    index=False
)


print("\nTraining dataset saved to:")

print(
    os.path.abspath(OUTPUT_PATH)
)


# ============================================================
# 11. BASIC STATISTICS
# ============================================================

print("\nFeature statistics:")

print(
    df.describe()
)