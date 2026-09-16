from pathlib import Path
import rasterio

BASE = Path("data/satellite")
OUTPUT = Path("data/processed/satellite")

scene_dirs = {
    "2026-08-14": next((BASE / "2026-08-14").rglob("BAND2.tif")).parent,
    "2026-09-02": next((BASE / "2026-09-02").rglob("BAND2.tif")).parent,
}

for date, scene_dir in scene_dirs.items():

    output_dir = OUTPUT / date
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\nProcessing {date}")
    print(f"Source: {scene_dir}")

    for band in ["BAND2.tif", "BAND3.tif", "BAND4.tif", "BAND5.tif"]:

        source = scene_dir / band
        destination = output_dir / band

        if not source.exists():
            print(f"  WARNING: Missing {source}")
            continue

        with rasterio.open(source) as src:

            profile = src.profile.copy()

            # ISRO BAND_META confirms:
            # WGS84 / UTM Zone 45N
            profile["crs"] = "EPSG:32645"

            with rasterio.open(
                destination,
                "w",
                **profile
            ) as dst:

                dst.write(src.read())

        print(f"  Created: {destination}")

print("\nCRS correction complete.")