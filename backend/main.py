from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import rasterio
from rasterio.warp import transform
import numpy as np
import os
from dotenv import load_dotenv
from  openai import OpenAI
import joblib
from pydantic import BaseModel
from typing import Optional,List
from pyproj import Transformer

import pandas as pd
app = FastAPI(
    title="Terrain Analyzer",
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

MODEL_PATH = r"data/xgboost_landslide_model_hard_negative.pkl"

model_artifact = joblib.load(MODEL_PATH)

landslide_model = model_artifact["model"]
landslide_imputer = model_artifact["imputer"]
MODEL_FEATURES = model_artifact["features"]

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


load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5.6-luna")

if OPENAI_API_KEY:
    openai_client = OpenAI(api_key=OPENAI_API_KEY)
else:
    openai_client = None


MODEL_PATH = r"data/xgboost_landslide_model_hard_negative.pkl"

SATELLITE_DIR = r"data/processed/satellite/2026-08-14"

BAND_PATHS = {
    "B2": os.path.join(SATELLITE_DIR, "BAND2.tif"),
    "B3": os.path.join(SATELLITE_DIR, "BAND3.tif"),
    "B4": os.path.join(SATELLITE_DIR, "BAND4.tif"),
    "B5": os.path.join(SATELLITE_DIR, "BAND5.tif"),
}

MODEL_FEATURES = [
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

landsilde_model = joblib.load(MODEL_PATH)

def normalized_difference(a, b):
    denominator = a + b

    if denominator == 0:
        return np.nan

    return (a - b) / denominator


def sample_raster(raster_path, longitude, latitude):
    with rasterio.open(raster_path) as src:

        # Transform WGS84 coordinates into raster CRS
        transformer = Transformer.from_crs(
            "EPSG:4326",
            src.crs,
            always_xy=True
        )

        x, y = transformer.transform(
            longitude,
            latitude
        )

        # Check coverage
        if not (
            src.bounds.left <= x <= src.bounds.right
            and
            src.bounds.bottom <= y <= src.bounds.top
        ):
            return np.nan

        value = list(
            src.sample([(x, y)])
        )[0][0]

        if src.nodata is not None and value == src.nodata:
            return np.nan

        if value == -32768:
            return np.nan

        if not np.isfinite(value):
            return np.nan

        return float(value)


def get_ml_features(latitude, longitude):

    elevation = sample_raster(
        DEM_PATH,
        longitude,
        latitude
    )

    slope = sample_raster(
        SLOPE_PATH,
        longitude,
        latitude
    )

    aspect = sample_raster(
        ASPECT_PATH,
        longitude,
        latitude
    )

    bands = {}

    for name, path in BAND_PATHS.items():

        bands[name] = sample_raster(
            path,
            longitude,
            latitude
        )

    ndvi = normalized_difference(
        bands["B4"],
        bands["B3"]
    )

    ndwi = normalized_difference(
        bands["B2"],
        bands["B4"]
    )

    nbr = normalized_difference(
        bands["B4"],
        bands["B5"]
    )

    return {
        "latitude": latitude,
        "longitude": longitude,
        "elevation": elevation,
        "slope": slope,
        "aspect": aspect,
        "B2": bands["B2"],
        "B3": bands["B3"],
        "B4": bands["B4"],
        "B5": bands["B5"],
        "NDVI": ndvi,
        "NDWI": ndwi,
        "NBR": nbr,
    }
def predict_ml_risk(latitude, longitude):

    features = get_ml_features(
        latitude,
        longitude
    )

    # Create DataFrame using the exact feature names
    # stored with the trained model
    model_input = pd.DataFrame(
        [[features[name] for name in MODEL_FEATURES]],
        columns=MODEL_FEATURES
    )

    # Apply the SAME imputer used during training
    transformed_input = landslide_imputer.transform(
        model_input
    )

    # Run XGBoost
    probability = landslide_model.predict_proba(
        transformed_input
    )[0][1]

    probability = float(
        np.clip(probability, 0, 1)
    )

    if probability >= 0.66:
        risk_level = "HIGH"

    elif probability >= 0.33:
        risk_level = "MEDIUM"

    else:
        risk_level = "LOW"

    return {
        **features,
        "landslide_probability": round(
            probability,
            4
        ),
        "risk_level": risk_level
    }


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
class ChatRequest(BaseModel):

    message: str

    latitude: Optional[float] = None

    longitude: Optional[float] = None

    history: Optional[List[dict]] = []


@app.post("/chat")
def chat(request: ChatRequest):

    if not openai_client:

        raise HTTPException(
            status_code=500,
            detail="OPENAI_API_KEY is not configured"
        )

    location_data = None

    # If the user selected a location on the map,
    # retrieve actual backend/model data.
    if (
        request.latitude is not None
        and
        request.longitude is not None
    ):

        try:

            location_data = predict_ml_risk(
                request.latitude,
                request.longitude
            )

        except Exception as e:

            raise HTTPException(
                status_code=500,
                detail=f"Unable to analyze location: {str(e)}"
            )

    system_prompt = """
You are the AI assistant for a Sikkim landslide
monitoring and terrain analysis dashboard.

You have access to backend-generated terrain,
satellite and machine-learning information.

IMPORTANT RULES:

1. Use the supplied backend data as the source of truth.
2. Never invent terrain measurements.
3. Explain risk in simple language.
4. The ML probability is an estimate, NOT a guarantee
   that a landslide will happen.
5. Do not claim that the model can predict the exact
   time of a landslide.
6. Explain which factors contribute to the risk.
7. If data is unavailable, clearly say so.
8. If the user asks about model accuracy, explain that
   validation is required before treating the model as
   scientifically reliable.
9. Keep answers concise but useful.
10. You are assisting with monitoring, not replacing
    field inspection or emergency authorities.
"""

    if location_data:

        backend_context = f"""
CURRENT SELECTED LOCATION

Latitude:
{location_data["latitude"]}

Longitude:
{location_data["longitude"]}

Elevation:
{location_data["elevation"]} meters

Slope:
{location_data["slope"]} degrees

Aspect:
{location_data["aspect"]} degrees

Satellite B2:
{location_data["B2"]}

Satellite B3:
{location_data["B3"]}

Satellite B4:
{location_data["B4"]}

Satellite B5:
{location_data["B5"]}

NDVI:
{location_data["NDVI"]}

NDWI:
{location_data["NDWI"]}

NBR:
{location_data["NBR"]}

XGBoost landslide probability:
{location_data["landslide_probability"]}

Risk level:
{location_data["risk_level"]}
"""

    else:

        backend_context = """
No specific map location was selected.

You can answer general questions about the
Sikkim terrain-analysis and landslide-monitoring
project, but do not invent location-specific
measurements.
"""

    user_input = f"""
BACKEND DATA:
{backend_context}

USER QUESTION:
{request.message}
"""

    messages = []

    for item in request.history[-8:]:

        role = item.get("role")

        content = item.get("content")

        if role in ["user", "assistant"] and content:

            messages.append({
                "role": role,
                "content": content
            })

    messages.append({
        "role": "user",
        "content": user_input
    })

    try:

        response = openai_client.responses.create(

            model=OPENAI_MODEL,

            instructions=system_prompt,

            input=messages
        )

        answer = response.output_text

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"OpenAI API error: {str(e)}"
        )

    return {
        "answer": answer,
        "location_data": location_data
    }