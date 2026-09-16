import rasterio
import numpy as np
from scipy.ndimage import sobel

input_file = r"data/raw\P5_PAN_CD_N27_000_E088_000_30m\P5_PAN_CD_N27_000_E088_000_30m\P5_PAN_CD_N27_000_E088_000_DEM_30m.tif"
output_file = r"data/processed/slope.tif"

with rasterio.open(input_file) as src:
    dem = src.read(1).astype("float32")
    profile = src.profile.copy()
    nodata = src.nodata

    # Convert geographic pixel size from degrees to approximate metres
    lat = (src.bounds.top + src.bounds.bottom) / 2
    meters_per_degree_lat = 111320
    meters_per_degree_lon = 111320 * np.cos(np.radians(lat))

    pixel_x = src.res[0] * meters_per_degree_lon
    pixel_y = src.res[1] * meters_per_degree_lat

    # Handle NoData
    valid = dem != nodata
    dem_clean = np.where(valid, dem, np.nan)

    # Calculate elevation gradients
    dzdx = sobel(dem_clean, axis=1, mode="nearest") / (8 * pixel_x)
    dzdy = sobel(dem_clean, axis=0, mode="nearest") / (8 * pixel_y)

    # Calculate slope in degrees
    slope = np.degrees(np.arctan(np.sqrt(dzdx**2 + dzdy**2)))

    slope[~valid] = nodata
    slope = slope.astype("float32")

    profile.update(
        dtype="float32",
        count=1,
        nodata=nodata,
        compress="lzw"
    )

    with rasterio.open(output_file, "w", **profile) as dst:
        dst.write(slope, 1)

print("Slope generated successfully!")
print("Output:", output_file)
print("Minimum slope:", np.nanmin(slope[valid]))
print("Maximum slope:", np.nanmax(slope[valid]))
print("Mean slope:", np.nanmean(slope[valid]))
