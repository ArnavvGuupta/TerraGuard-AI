# 🌍 TerraGuard AI
<img width="1333" height="1052" alt="Screenshot 2026-09-16 112247" src="https://github.com/user-attachments/assets/5e9c54a9-d2f4-4350-8075-ba19275238f9" />


### AI-Powered Landslide Risk Monitoring & Early Warning System

> **Turning terrain and satellite data into actionable landslide risk intelligence.**

TerraGuard AI is an AI-powered geospatial monitoring platform designed to analyze **terrain characteristics, satellite imagery, and environmental changes** to identify areas with potential landslide risk.

The system combines **Machine Learning, GIS, Digital Elevation Models (DEM), satellite spectral analysis, and an AI chatbot** into a single interactive monitoring platform.

---

## 🚨 Why TerraGuard AI?

Landslides can cause significant damage to **roads, infrastructure, settlements, and lives**, particularly in mountainous regions such as Northeast India.

Traditional monitoring systems can be difficult to scale across large geographic areas.

**TerraGuard AI aims to provide:**

* 🗺️ Interactive geospatial risk visualization
* 🤖 AI-assisted landslide risk analysis
* 🛰️ Satellite-based change detection
* ⛰️ Terrain and elevation analysis
* ⚠️ Risk classification and risk scoring
* 💬 Natural-language interaction through an AI chatbot

---

# ✨ Key Features


### 🧠 AI-Based Risk Analysis

TerraGuard analyzes terrain and environmental characteristics to estimate landslide susceptibility.

The system considers features such as:

* Elevation
* Slope
* Aspect
* Terrain characteristics
* Satellite-derived spectral change
* Spatial characteristics

---

### 🗺️ Interactive Risk Map

The web dashboard provides an interactive map for exploring different geospatial layers.

Users can visualize:

* ⛰️ Terrain
* 📐 Slope
* ⚠️ Landslide Risk
* 🛰️ Satellite Spectral Change
* 📍 Coordinate-based risk analysis

---

### 🛰️ Satellite Change Detection

TerraGuard uses **Resourcesat-2 LISS-III satellite imagery** from different time periods to identify changes in surface spectral characteristics.

This enables the system to detect areas where significant surface changes may warrant further investigation.

---

### 📊 Terrain Intelligence

A **30-meter Digital Elevation Model (DEM)** is processed to generate:

* Elevation
* Slope
* Aspect
* Hillshade
* Terrain-based risk indicators

The processed terrain data contains approximately **13 million raster cells** across the study region.

---

### 🤖 AI Chatbot
<img width="1822" height="992" alt="image" src="https://github.com/user-attachments/assets/62a001ed-a475-4768-abcf-7d4251b0d64c" />



TerraGuard includes an **AI-powered chatbot** that allows users to interact with the monitoring system using natural language.

Users can ask questions about:

* Landslide risk
* Terrain conditions
* Risk factors
* Geographic locations
* System-generated analysis
* Interpretation of risk information

This makes complex geospatial information easier for non-technical users to understand.

---

# 📈 Project Statistics

| Metric                |                                   Value |
| --------------------- | --------------------------------------: |
| Training Samples      |                                 **480** |
| Landslide Samples     |                                 **240** |
| Non-Landslide Samples |                                 **240** |
| Engineered Features   |                                 **12+** |
| DEM Resolution        |                                **30 m** |
| DEM Raster Size       |                       **3,600 × 3,600** |
| Terrain Cells         |                         **~13 million** |
| Satellite Data        |              **Resourcesat-2 LISS-III** |
| Study Region          | **Northeast India / Himalayan terrain** |

---

# 🧪 Machine Learning Dataset

A balanced **hard-negative dataset** was created for spatially robust model development.

```text
Total Samples:        480
Landslide:            240
Non-Landslide:        240
Class Balance:        50 / 50
Features:             12+
```

The dataset incorporates spatial separation to reduce overly optimistic validation caused by neighboring samples with similar terrain characteristics.

---

# 🛰️ Data Sources

TerraGuard AI works with multiple geospatial data sources:

### Digital Elevation Model

**30m DEM data** is used to derive terrain characteristics such as:

* Elevation
* Slope
* Aspect
* Hillshade

### Satellite Imagery

**Resourcesat-2 LISS-III** imagery is used for multi-temporal spectral analysis.

Satellite scenes from **August and September 2026** were processed to generate spectral-change information.

---

# 🏗️ System Architecture

```text
                 ┌─────────────────────────┐
                 │     Geospatial Data     │
                 │                         │
                 │  DEM + Satellite Data   │
                 └────────────┬────────────┘
                              │
                              ▼
                 ┌─────────────────────────┐
                 │   Data Preprocessing    │
                 │                         │
                 │ Slope • Aspect • DEM    │
                 │ Spectral Change         │
                 └────────────┬────────────┘
                              │
                              ▼
                 ┌─────────────────────────┐
                 │   ML Risk Assessment    │
                 │                         │
                 │ Feature Engineering     │
                 │ Risk Classification     │
                 └────────────┬────────────┘
                              │
                              ▼
                 ┌─────────────────────────┐
                 │      FastAPI Backend    │
                 │                         │
                 │ Terrain Analysis API    │
                 │ Risk Scoring             │
                 └────────────┬────────────┘
                              │
                ┌─────────────┴─────────────┐
                ▼                           ▼
      ┌──────────────────┐        ┌──────────────────┐
      │ Interactive Map  │        │    AI Chatbot    │
      │                  │        │                  │
      │ Next.js          │        │ Natural Language │
      │ React Leaflet    │        │ Risk Assistance  │
      └──────────────────┘        └──────────────────┘
```

---

# 🛠️ Tech Stack

### Frontend

* **Next.js**
* **React**
* **TypeScript**
* **React Leaflet**
* **Tailwind CSS**
* **Lucide Icons**

### Backend

* **Python**
* **FastAPI**
* **Uvicorn**

### Machine Learning & Data Processing

* **Python**
* **Pandas**
* **NumPy**
* **Scikit-learn**
* **Rasterio**
* **GeoPandas**

### Geospatial & Remote Sensing

* Digital Elevation Models
* Resourcesat-2 LISS-III
* Raster processing
* Spectral change detection
* GIS-based spatial analysis

---

# 📂 Project Structure

```text
TerraGuard-AI/
│
├── backend/
│   ├── main.py
│   ├── terrain/
│   └── ...
│
├── data/
│   ├── raw/
│   ├── processed/
│   ├── landslides/
│   └── ...
│
├── frontend/
│   ├── app/
│   ├── components/
│   └── ...
│
├── scripts/
│   ├── data_processing/
│   ├── spatial_validation/
│   └── ...
│
├── models/
│
├── requirements.txt
├── package.json
└── README.md
```

---

# 🚀 Getting Started

## 1. Clone the Repository

```bash
git clone https://github.com/ArnavvGuupta/TerraGuard-AI.git
cd TerraGuard-AI
```

---

## 2. Backend Setup

Create and activate a Python virtual environment:

### Windows

```powershell
python -m venv venv
.\venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the FastAPI server:

```bash
uvicorn backend.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

---

## 3. Frontend Setup

Install dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

Open:

```text
http://localhost:3000
```

---

# 🔎 Example API Request

TerraGuard can analyze a geographic coordinate and return terrain and risk information.

```text
GET /terrain/analyze?latitude=27.5&longitude=88.5
```

Example response:

```json
{
  "elevation": 1702.59,
  "slope": 23.45,
  "aspect": 141.42,
  "risk_score": 40,
  "risk_level": "MEDIUM"
}
```

---

# ⚠️ Risk Classification

TerraGuard converts terrain and environmental indicators into an interpretable risk score.

Example:

```text
LOW
│
├── Stable / lower-risk terrain
│
MEDIUM
│
├── Moderately susceptible terrain
│
HIGH
│
└── Potentially unstable terrain
```

The risk output is intended as a **decision-support indicator**, not a replacement for field surveys or official disaster-management systems.

---

# 💡 Future Improvements

TerraGuard AI can be extended with:

* 📡 Real-time weather integration
* 🌧️ Rainfall and soil-moisture analysis
* 🛰️ More frequent satellite monitoring
* 🧠 Advanced deep-learning models
* 📱 Mobile alerts
* 🔔 Automated risk notifications
* 🗺️ Larger geographic coverage
* 🏘️ Infrastructure and population exposure analysis
* 📈 Historical landslide trend analysis
* 🚨 Automated early-warning workflows

---

# 🎯 Use Cases

TerraGuard AI can support:

* Disaster management teams
* Government agencies
* Researchers
* Infrastructure monitoring
* Mountain road monitoring
* Environmental monitoring
* Geospatial analysis
* Community awareness

---

# 👨‍💻 Built By

**Arnav Gupta** 

---

## ⭐ Project Vision

> **From satellite pixels to actionable intelligence — TerraGuard AI helps transform
