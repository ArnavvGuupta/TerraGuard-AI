import rasterio
import numpy as np

input_file = r"data/raw\P5_PAN_CD_N27_000_E088_000_30m\P5_PAN_CD_N27_000_E088_000_30m\P5_PAN_CD_N27_000_E088_000_DEM_30m.tif"
output_file = r"data/processed/hillshade.tif"

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

    # Slope and aspect
    slope = np.arctan(np.sqrt(dzdx**2 + dzdy**2))
    aspect = np.arctan2(dzdy, -dzdx)

    # Sun position
    azimuth = np.radians(315)   # northwest
    altitude = np.radians(45)   # 45 degrees

    # Hillshade calculation
    hillshade = (
        np.sin(altitude) * np.cos(slope)
        + np.cos(altitude) * np.sin(slope)
        * np.cos(azimuth - aspect)
    )

    hillshade = 255 * hillshade
    hillshade = np.clip(hillshade, 0, 255)

    hillshade[~valid] = nodata
    hillshade = hillshade.astype("float32")

    profile.update(
        dtype="float32",
        count=1,
        nodata=nodata,
        compress="lzw"
    )

    with rasterio.open(output_file, "w", **profile) as dst:
        dst.write(hillshade, 1)

print("Hillshade generated successfully!")
print("Output:", output_file)
print("Minimum hillshade:", np.nanmin(hillshade[valid]))
print("Maximum hillshade:", np.nanmax(hillshade[valid]))
print("Mean hillshade:", np.nanmean(hillshade[valid]))