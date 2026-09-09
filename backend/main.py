from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import rasterio
from rasterio.warp import transform
import numpy as np

app = FastAPI(
    title="Sikkim Terrain Analysis API",
    description="Backend API for terrain and hazard analysis",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
AI_ANOMALY_PATH = r"data/processed/monitoring/ai_change_anomaly.tif"

SPECTRAL_CHANGE_PATH = r"data/processed/monitoring/spectral_change.tif"

DEM_PATH = r"data/raw/P5_PAN_CD_N27_000_E088_000_30m/P5_PAN_CD_N27_000_E088_000_30m/P5_PAN_CD_N27_000_E088_000_DEM_30m.tif"

SLOPE_PATH = r"data/processed/slope.tif"

ASPECT_PATH = r"data/processed/aspect.tif"


@app.get("/")
def root():
    return {
        "message": "Sikkim Terrain Analysis API",
        "status": "running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.get("/terrain/info")
def terrain_info():

    with rasterio.open(DEM_PATH) as dem:

        return {
            "crs": str(dem.crs),
            "width": dem.width,
            "height": dem.height,
            "resolution": dem.res,
            "bounds": {
                "left": dem.bounds.left,
                "bottom": dem.bounds.bottom,
                "right": dem.bounds.right,
                "top": dem.bounds.top
            },
            "bands": dem.count
        }
@app.get("/monitoring/analyze")
def analyze_monitoring(latitude: float, longitude: float):

    with rasterio.open(AI_ANOMALY_PATH) as ai_src:

        # Convert clicked GPS coordinates
        # EPSG:4326 -> satellite raster CRS (EPSG:32645)
        x, y = transform(
            "EPSG:4326",
            ai_src.crs,
            [longitude],
            [latitude]
        )

        x = x[0]
        y = y[0]

        # Check whether location is inside satellite coverage
        if not (
            ai_src.bounds.left <= x <= ai_src.bounds.right
            and ai_src.bounds.bottom <= y <= ai_src.bounds.top
        ):
            return {
                "latitude": latitude,
                "longitude": longitude,
                "spectral_change": 0,
                "ai_anomaly": 0,
                "combined_change": 0,
                "status": "SATELLITE DATA UNAVAILABLE",
                "recommendation": "This location is outside the available satellite monitoring area."
            }

        ai_anomaly = list(
            ai_src.sample([(x, y)])
        )[0][0]

    with rasterio.open(SPECTRAL_CHANGE_PATH) as spectral_src:

        # Use the same transformed UTM coordinates
        spectral_change = list(
            spectral_src.sample([(x, y)])
        )[0][0]

    if not np.isfinite(ai_anomaly):
        ai_anomaly = 0.0

    if not np.isfinite(spectral_change):
        spectral_change = 0.0

    ai_anomaly = float(np.clip(ai_anomaly, 0, 1))
    spectral_change = float(np.clip(spectral_change, 0, 1))

    combined_change = (
        ai_anomaly * 0.6
        + spectral_change * 0.4
    )

    if combined_change >= 0.7:
        status = "HIGH CHANGE"
        recommendation = (
            "Potential unusual change detected — "
            "requires inspection."
        )

    elif combined_change >= 0.4:
        status = "MODERATE CHANGE"
        recommendation = (
            "Moderate unusual change detected."
        )

    else:
        status = "LOW CHANGE"
        recommendation = (
            "No significant unusual change detected."
        )

    return {
        "latitude": latitude,
        "longitude": longitude,
        "spectral_change": round(spectral_change, 3),
        "ai_anomaly": round(ai_anomaly, 3),
        "combined_change": round(combined_change, 3),
        "status": status,
        "recommendation": recommendation,
    }


def calculate_risk(
    slope_degrees,
    elevation_m,
    aspect_degrees
):

    score = 0

    factors = []


    # -------------------------
    # SLOPE
    # -------------------------

    if slope_degrees >= 45:

        score += 60
        factors.append("Very steep slope")

    elif slope_degrees >= 30:

        score += 45
        factors.append("Steep slope")

    elif slope_degrees >= 20:

        score += 30
        factors.append("Moderately steep slope")

    elif slope_degrees >= 10:

        score += 15
        factors.append("Moderate slope")

    else:

        factors.append("Low slope")


    # -------------------------
    # ELEVATION
    # -------------------------

    if elevation_m >= 5000:

        score += 40
        factors.append("Very high elevation")

    elif elevation_m >= 3500:

        score += 30
        factors.append("High elevation")

    elif elevation_m >= 2000:

        score += 20
        factors.append("Moderate elevation")

    elif elevation_m >= 1000:

        score += 10
        factors.append("Elevated terrain")


    # -------------------------
    # ASPECT
    # -------------------------

    if 315 <= aspect_degrees or aspect_degrees < 45:

        factors.append("North-facing terrain")

    elif 45 <= aspect_degrees < 135:

        factors.append("East-facing terrain")

    elif 135 <= aspect_degrees < 225:

        factors.append("South-facing terrain")

    else:

        factors.append("West-facing terrain")


    # -------------------------
    # FINAL SCORE
    # -------------------------

    score = min(score, 100)


    if score >= 70:

        risk = "HIGH"

    elif score >= 40:

        risk = "MEDIUM"

    else:

        risk = "LOW"


    return score, risk, factors


@app.get("/terrain/analyze")
def analyze_terrain(
    latitude: float,
    longitude: float
):

    try:

        with rasterio.open(DEM_PATH) as dem, \
             rasterio.open(SLOPE_PATH) as slope, \
             rasterio.open(ASPECT_PATH) as aspect:


            # Check coordinate coverage

            if not (
                dem.bounds.left <= longitude <= dem.bounds.right
                and
                dem.bounds.bottom <= latitude <= dem.bounds.top
            ):

                raise HTTPException(
                    status_code=400,
                    detail="Coordinates are outside the available DEM area"
                )


            # Convert coordinates to raster pixel

            row, col = dem.index(
                longitude,
                latitude
            )


            # Read values

            elevation = dem.read(1)[row, col]

            slope_value = slope.read(1)[row, col]

            aspect_value = aspect.read(1)[row, col]


            # Check NoData

            if elevation == dem.nodata:

                raise HTTPException(
                    status_code=404,
                    detail="No terrain data available at this location"
                )


            # Convert to Python floats

            elevation_float = float(elevation)

            slope_float = float(slope_value)

            aspect_float = float(aspect_value)


            # Calculate risk

            score, risk, factors = calculate_risk(
                slope_float,
                elevation_float,
                aspect_float
            )


            # Return response

            return {

                "latitude": latitude,

                "longitude": longitude,

                "elevation_m": round(
                    elevation_float,
                    2
                ),

                "slope_degrees": round(
                    slope_float,
                    2
                ),

                "aspect_degrees": round(
                    aspect_float,
                    2
                ),

                "risk_score": score,

                "risk_level": risk,

                "risk_factors": factors

            }


    except HTTPException:

        raise


    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )