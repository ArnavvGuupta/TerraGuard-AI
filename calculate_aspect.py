import rasterio
import numpy as np

input_file = r"data/raw\P5_PAN_CD_N27_000_E088_000_30m\P5_PAN_CD_N27_000_E088_000_30m\P5_PAN_CD_N27_000_E088_000_DEM_30m.tif"
output_file = r"data/processed/aspect.tif"

with rasterio.open(input_file) as src:
    dem = src.read(1).astype("float32")
    profile = src.profile.copy()
    nodata = src.nodata

    lat = (src.bounds.top + src.bounds.bottom) / 2

    meters_per_degree_lat = 111320
    meters_per_degree_lon = 111320 * np.cos(np.radians(lat))

    pixel_x = src.res[0] * meters_per_degree_lon
    pixel_y = src.res[1] * meters_per_degree_lat

    valid = dem != nodata
    dem_clean = np.where(valid, dem, np.nan)

    # Calculate gradients
    dzdx = np.gradient(dem_clean, axis=1) / pixel_x
    dzdy = np.gradient(dem_clean, axis=0) / pixel_y

    # Calculate aspect
    aspect = np.degrees(np.arctan2(dzdy, -dzdx))

    # Convert to compass direction: 0 = North, 90 = East
    aspect = 90.0 - aspect
    aspect = np.where(aspect < 0, aspect + 360, aspect)
    aspect = np.where(aspect >= 360, aspect - 360, aspect)

    aspect[~valid] = nodata
    aspect = aspect.astype("float32")

    profile.update(
        dtype="float32",
        count=1,
        nodata=nodata,
        compress="lzw"
    )

    with rasterio.open(output_file, "w", **profile) as dst:
        dst.write(aspect, 1)

print("Aspect generated successfully!")
print("Output:", output_file)
print("Minimum aspect:", np.nanmin(aspect[valid]))
print("Maximum aspect:", np.nanmax(aspect[valid]))
print("Mean aspect:", np.nanmean(aspect[valid]))