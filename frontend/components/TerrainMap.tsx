"use client";

import {
    MapContainer,
    TileLayer,
    Marker,
    Popup,
    Rectangle,
    ImageOverlay,
    LayersControl,
    useMapEvents,
} from "react-leaflet";

import "leaflet/dist/leaflet.css";
import L from "leaflet";
import { useState } from "react";

/* =========================================================
   TYPES
========================================================= */

type TerrainData = {
    latitude: number;
    longitude: number;
    elevation_m: number;
    slope_degrees: number;
    aspect_degrees: number;
    risk_score: number;
    risk_level: string;
    risk_factors: string[];
};

type MonitoringData = {
    spectral_change: number;
    ai_anomaly: number;
    combined_change: number;
    status: string;
    recommendation: string;
};

/* =========================================================
   LEAFLET MARKER
========================================================= */

const markerIcon = L.icon({
    iconUrl:
        "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",

    iconRetinaUrl:
        "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",

    shadowUrl:
        "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",

    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
});

/* =========================================================
   MAP CLICK HANDLER
========================================================= */

function MapClickHandler({
    onLocationSelect,
}: {
    onLocationSelect: (lat: number, lon: number) => void;
}) {
    useMapEvents({
        click(event) {
            onLocationSelect(
                event.latlng.lat,
                event.latlng.lng
            );
        },
    });

    return null;
}

/* =========================================================
   RISK CONFIG
========================================================= */

function getRiskConfig(level: string) {
    const value = level?.toUpperCase();

    if (value === "HIGH") {
        return {
            label: "HIGH RISK",
            color: "#ef4444",
            bg: "rgba(239, 68, 68, 0.10)",
            border: "rgba(239, 68, 68, 0.35)",
            dot: "#ef4444",
        };
    }

    if (value === "MEDIUM") {
        return {
            label: "MEDIUM RISK",
            color: "#facc15",
            bg: "rgba(250, 204, 21, 0.10)",
            border: "rgba(250, 204, 21, 0.35)",
            dot: "#facc15",
        };
    }

    return {
        label: "LOW RISK",
        color: "#34d399",
        bg: "rgba(52, 211, 153, 0.10)",
        border: "rgba(52, 211, 153, 0.35)",
        dot: "#34d399",
    };
}

/* =========================================================
   MONITORING CONFIG
========================================================= */

function getMonitoringConfig(status: string) {
    const value = status?.toLowerCase() || "";

    if (
        value.includes("high") ||
        value.includes("warning") ||
        value.includes("alert")
    ) {
        return {
            color: "#ef4444",
            bg: "rgba(239, 68, 68, 0.10)",
            border: "rgba(239, 68, 68, 0.35)",
            dot: "#ef4444",
        };
    }

    if (
        value.includes("moderate") ||
        value.includes("medium")
    ) {
        return {
            color: "#facc15",
            bg: "rgba(250, 204, 21, 0.10)",
            border: "rgba(250, 204, 21, 0.35)",
            dot: "#facc15",
        };
    }

    return {
        color: "#34d399",
        bg: "rgba(52, 211, 153, 0.10)",
        border: "rgba(52, 211, 153, 0.35)",
        dot: "#34d399",
    };
}

/* =========================================================
   MAIN COMPONENT
========================================================= */

export default function TerrainMap({
    onTerrainData,
    onLoading,
    onError,
}: {
    onTerrainData: (data: TerrainData) => void;
    onLoading: (loading: boolean) => void;
    onError: (error: string | null) => void;
}) {
    const [position, setPosition] = useState<[number, number] | null>(null);

    const [terrainData, setTerrainData] =
        useState<TerrainData | null>(null);

    const [monitoringData, setMonitoringData] =
        useState<MonitoringData | null>(null);

    /* =====================================================
       LOCATION ANALYSIS
    ===================================================== */

    async function handleLocationSelect(
        lat: number,
        lon: number
    ) {
        setPosition([lat, lon]);

        localStorage.setItem(
            "selectedTerrainLocation",
            JSON.stringify({
                latitude: lat,
                longitude: lon,
            })
        );

        onLoading(true);
        onError(null);

        try {
            /* =================================================
               TERRAIN ANALYSIS
            ================================================= */

            const response = await fetch(
                `http://127.0.0.1:8000/terrain/analyze?latitude=${lat}&longitude=${lon}`
            );

            if (!response.ok) {
                throw new Error(
                    `Terrain API error: ${response.status}`
                );
            }

            const data: TerrainData =
                await response.json();

            setTerrainData(data);

            onTerrainData(data);

            /* =================================================
               SATELLITE + AI MONITORING
            ================================================= */

            try {
                const monitoringResponse =
                    await fetch(
                        `http://127.0.0.1:8000/monitoring/analyze?latitude=${lat}&longitude=${lon}`
                    );

                if (monitoringResponse.ok) {
                    const monitoringResult: MonitoringData =
                        await monitoringResponse.json();

                    setMonitoringData(
                        monitoringResult
                    );
                } else {
                    setMonitoringData(null);
                }
            } catch (monitoringError) {
                console.error(
                    "Monitoring request failed:",
                    monitoringError
                );

                setMonitoringData(null);
            }
        } catch (error) {
            console.error(
                "Terrain analysis failed:",
                error
            );

            onError(
                "Unable to analyze this location."
            );

            setTerrainData(null);
            setMonitoringData(null);
        } finally {
            onLoading(false);
        }
    }

    /* =====================================================
       CONFIG
    ===================================================== */

    const riskConfig = terrainData
        ? getRiskConfig(terrainData.risk_level)
        : null;

    const monitoringConfig = monitoringData
        ? getMonitoringConfig(
              monitoringData.status
          )
        : null;

    /* =====================================================
       UI
    ===================================================== */

    return (
        <div className="terrain-dashboard relative overflow-hidden rounded-2xl border border-cyan-400/10 bg-[#020617] shadow-[0_0_60px_rgba(8,145,178,0.08)]">

            {/* =================================================
               ANIMATED ATMOSPHERE
            ================================================= */}

            <div className="pointer-events-none absolute inset-0 z-[1] overflow-hidden">

                <div className="terrain-glow terrain-glow-one" />

                <div className="terrain-glow terrain-glow-two" />

                <div className="terrain-grid" />

                <div className="terrain-scanline" />

            </div>

            {/* =================================================
               TOP HUD
            ================================================= */}

            <div className="absolute left-4 right-4 top-4 z-[1000]">

                <div className="-ml-2 -mt-2 flex flex-col gap-4 rounded-xl border border-white/10 bg-slate-950/85 p-4 shadow-2xl backdrop-blur-xl md:flex-row md:items-center md:justify-between">

                    {/* BRAND */}

                    <div className="flex items-center gap-3">

                        <div className="flex h-11 w-11 items-center justify-center rounded-xl border border-cyan-400/20 bg-cyan-400/10 text-xl shadow-[0_0_25px_rgba(34,211,238,0.12)]">

                            🛰️

                        </div>

                        <div>

                            <div className="flex items-center gap-2">

                                <p className="text-sm font-bold tracking-wide text-white">
                                    TERRAIN INTELLIGENCE
                                </p>

                                <span className="rounded-full border border-emerald-400/20 bg-emerald-400/10 px-2 py-0.5 text-[9px] font-bold tracking-widest text-emerald-400">
                                    LIVE
                                </span>

                            </div>

                            <p className="mt-1 text-[11px] text-slate-400">
                                Sikkim • Geospatial Risk Monitoring
                            </p>

                        </div>

                    </div>

                    {/* PIPELINE */}

                    <div className="hidden items-center gap-2 lg:flex">

                        <div className="rounded-lg border border-white/10 bg-white/[0.03] px-3 py-2">

                            <p className="text-[9px] uppercase tracking-wider text-slate-500">
                                Input
                            </p>

                            <p className="text-xs font-semibold text-slate-200">
                                Satellite
                            </p>

                        </div>

                        <span className="text-slate-600">
                            →
                        </span>

                        <div className="rounded-lg border border-white/10 bg-white/[0.03] px-3 py-2">

                            <p className="text-[9px] uppercase tracking-wider text-slate-500">
                                Terrain
                            </p>

                            <p className="text-xs font-semibold text-slate-200">
                                DEM
                            </p>

                        </div>

                        <span className="text-slate-600">
                            →
                        </span>

                        <div className="rounded-lg border border-cyan-400/20 bg-cyan-400/5 px-3 py-2">

                            <p className="text-[9px] uppercase tracking-wider text-cyan-500">
                                Intelligence
                            </p>

                            <p className="text-xs font-semibold text-cyan-300">
                                AI Analysis
                            </p>

                        </div>

                        <span className="text-slate-600">
                            →
                        </span>

                        <div className="rounded-lg border border-red-400/20 bg-red-400/5 px-3 py-2">

                            <p className="text-[9px] uppercase tracking-wider text-red-400">
                                Output
                            </p>

                            <p className="text-xs font-semibold text-red-300">
                                Risk
                            </p>

                        </div>

                    </div>

                    {/* STATUS */}

                    <div className="hidden items-center gap-2 md:flex">

                        <div className="h-2 w-2 animate-pulse rounded-full bg-emerald-400 shadow-[0_0_10px_rgba(52,211,153,0.9)]" />

                        <span className="text-[10px] font-medium uppercase tracking-widest text-slate-400">
                            Monitoring Active
                        </span>

                    </div>

                </div>

            </div>

            {/* =================================================
               MAP CONTAINER
            ================================================= */}

            <div className="relative z-[5] overflow-hidden rounded-2xl">

                <MapContainer
                    center={[27.5, 88.5]}
                    zoom={9}
                    scrollWheelZoom={true}
                    style={{
                        height: "600px",
                        width: "100%",
                    }}
                >

                    {/* =================================================
                       MAP LAYERS
                    ================================================= */}

                    <LayersControl position="bottomleft">

                        {/* BASE MAP */}

                        <LayersControl.BaseLayer
                            checked
                            name="OpenStreetMap"
                        >

                            <TileLayer
                                attribution="&copy; OpenStreetMap contributors"
                                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                            />

                        </LayersControl.BaseLayer>

                        {/* TERRAIN / SLOPE */}

                        <LayersControl.Overlay
                            checked={false}
                            name="🟢 Terrain / Slope"
                        >

                            <ImageOverlay
                                url="/slope.png"
                                bounds={[
                                    [27.0, 88.0],
                                    [28.0, 89.0],
                                ]}
                                opacity={0.35}
                                zIndex={10}
                            />

                        </LayersControl.Overlay>

                        {/* TERRAIN RISK */}

                        <LayersControl.Overlay
                            checked={false}
                            name="🔴 Terrain Risk"
                        >

                            <ImageOverlay
                                url="/risk.png"
                                bounds={[
                                    [27.0, 88.0],
                                    [28.0, 89.0],
                                ]}
                                opacity={0.5}
                                zIndex={20}
                            />

                        </LayersControl.Overlay>

                        {/* SPECTRAL CHANGE */}

                        <LayersControl.Overlay
                            checked={false}
                            name="🟡 Spectral Change"
                        >

                            <ImageOverlay
                                url="/spectral_change.png"
                                bounds={[
                                    [26.6366, 86.7203],
                                    [28.1833, 88.6157],
                                ]}
                                opacity={0.55}
                                zIndex={30}
                            />

                        </LayersControl.Overlay>

                        {/* AI ANOMALY */}

                        <LayersControl.Overlay
                            checked={false}
                            name="🤖 AI Anomaly"
                        >

                            <ImageOverlay
                                url="/ai_change_anomaly.png"
                                bounds={[
                                    [26.6366, 86.7203],
                                    [28.1833, 88.6157],
                                ]}
                                opacity={0.65}
                                zIndex={40}
                            />

                        </LayersControl.Overlay>

                        {/* DEM COVERAGE */}

                        <LayersControl.Overlay
                            checked
                            name="🔷 DEM Coverage"
                        >

                            <Rectangle
                                bounds={[
                                    [27.0, 88.0],
                                    [28.0, 89.0],
                                ]}
                                pathOptions={{
                                    color: "#22d3ee",
                                    weight: 2,
                                    fillOpacity: 0,
                                    dashArray: "8 6",
                                }}
                            />

                        </LayersControl.Overlay>

                    </LayersControl>

                    {/* =================================================
                       MAP CLICK
                    ================================================= */}

                    <MapClickHandler
                        onLocationSelect={
                            handleLocationSelect
                        }
                    />

                    {/* =================================================
                       SELECTED LOCATION MARKER
                    ================================================= */}

                    {position && (

                        <Marker
                            position={position}
                            icon={markerIcon}
                        >

                            <Popup>

                                <div
                                    style={{
                                        minWidth: "285px",
                                        fontFamily:
                                            "Inter, system-ui, sans-serif",
                                    }}
                                >

                                    {/* POPUP HEADER */}

                                    <div
                                        style={{
                                            marginBottom: "12px",
                                            paddingBottom: "10px",
                                            borderBottom:
                                                "1px solid #e2e8f0",
                                        }}
                                    >

                                        <div
                                            style={{
                                                display: "flex",
                                                alignItems:
                                                    "center",
                                                gap: "8px",
                                            }}
                                        >

                                            <span
                                                style={{
                                                    fontSize:
                                                        "18px",
                                                }}
                                            >
                                                📍
                                            </span>

                                            <div>

                                                <div
                                                    style={{
                                                        fontWeight:
                                                            800,
                                                        fontSize:
                                                            "15px",
                                                        color:
                                                            "#0f172a",
                                                    }}
                                                >
                                                    Selected Location
                                                </div>

                                                <div
                                                    style={{
                                                        fontSize:
                                                            "11px",
                                                        color:
                                                            "#64748b",
                                                    }}
                                                >
                                                    AI terrain assessment
                                                </div>

                                            </div>

                                        </div>

                                    </div>

                                    {/* =================================================
                                       COORDINATES
                                    ================================================= */}

                                    <div
                                        style={{
                                            display: "grid",
                                            gridTemplateColumns:
                                                "1fr 1fr",
                                            gap: "8px",
                                            marginBottom:
                                                "12px",
                                        }}
                                    >

                                        <div
                                            style={{
                                                background:
                                                    "#f8fafc",
                                                borderRadius:
                                                    "8px",
                                                padding:
                                                    "8px",
                                            }}
                                        >

                                            <div
                                                style={{
                                                    fontSize:
                                                        "9px",
                                                    color:
                                                        "#64748b",
                                                    textTransform:
                                                        "uppercase",
                                                }}
                                            >
                                                Latitude
                                            </div>

                                            <div
                                                style={{
                                                    fontWeight:
                                                        700,
                                                    fontSize:
                                                        "12px",
                                                    color:
                                                        "#0f172a",
                                                }}
                                            >
                                                {position[0].toFixed(
                                                    5
                                                )}
                                            </div>

                                        </div>

                                        <div
                                            style={{
                                                background:
                                                    "#f8fafc",
                                                borderRadius:
                                                    "8px",
                                                padding:
                                                    "8px",
                                            }}
                                        >

                                            <div
                                                style={{
                                                    fontSize:
                                                        "9px",
                                                    color:
                                                        "#64748b",
                                                    textTransform:
                                                        "uppercase",
                                                }}
                                            >
                                                Longitude
                                            </div>

                                            <div
                                                style={{
                                                    fontWeight:
                                                        700,
                                                    fontSize:
                                                        "12px",
                                                    color:
                                                        "#0f172a",
                                                }}
                                            >
                                                {position[1].toFixed(
                                                    5
                                                )}
                                            </div>

                                        </div>

                                    </div>

                                    {/* =================================================
                                       TERRAIN DATA
                                    ================================================= */}

                                    {terrainData && (

                                        <>

                                            <div
                                                style={{
                                                    fontSize:
                                                        "10px",
                                                    fontWeight:
                                                        800,
                                                    color:
                                                        "#64748b",
                                                    textTransform:
                                                        "uppercase",
                                                    letterSpacing:
                                                        "0.08em",
                                                    marginBottom:
                                                        "8px",
                                                }}
                                            >
                                                Terrain Metrics
                                            </div>

                                            {/* METRICS */}

                                            <div
                                                style={{
                                                    display:
                                                        "grid",
                                                    gridTemplateColumns:
                                                        "repeat(3, 1fr)",
                                                    gap: "6px",
                                                }}
                                            >

                                                {/* ELEVATION */}

                                                <div
                                                    style={{
                                                        border:
                                                            "1px solid #e2e8f0",
                                                        borderRadius:
                                                            "8px",
                                                        padding:
                                                            "8px",
                                                        background:
                                                            "#ffffff",
                                                    }}
                                                >

                                                    <div
                                                        style={{
                                                            fontSize:
                                                                "9px",
                                                            color:
                                                                "#64748b",
                                                        }}
                                                    >
                                                        Elevation
                                                    </div>

                                                    <strong
                                                        style={{
                                                            fontSize:
                                                                "13px",
                                                            color:
                                                                "#0f172a",
                                                        }}
                                                    >
                                                        {terrainData.elevation_m.toFixed(
                                                            0
                                                        )}{" "}
                                                        m
                                                    </strong>

                                                </div>

                                                {/* SLOPE */}

                                                <div
                                                    style={{
                                                        border:
                                                            "1px solid #e2e8f0",
                                                        borderRadius:
                                                            "8px",
                                                        padding:
                                                            "8px",
                                                        background:
                                                            "#ffffff",
                                                    }}
                                                >

                                                    <div
                                                        style={{
                                                            fontSize:
                                                                "9px",
                                                            color:
                                                                "#64748b",
                                                        }}
                                                    >
                                                        Slope
                                                    </div>

                                                    <strong
                                                        style={{
                                                            fontSize:
                                                                "13px",
                                                            color:
                                                                "#0f172a",
                                                        }}
                                                    >
                                                        {terrainData.slope_degrees.toFixed(
                                                            1
                                                        )}
                                                        °
                                                    </strong>

                                                </div>

                                                {/* ASPECT */}

                                                <div
                                                    style={{
                                                        border:
                                                            "1px solid #e2e8f0",
                                                        borderRadius:
                                                            "8px",
                                                        padding:
                                                            "8px",
                                                        background:
                                                            "#ffffff",
                                                    }}
                                                >

                                                    <div
                                                        style={{
                                                            fontSize:
                                                                "9px",
                                                            color:
                                                                "#64748b",
                                                        }}
                                                    >
                                                        Aspect
                                                    </div>

                                                    <strong
                                                        style={{
                                                            fontSize:
                                                                "13px",
                                                            color:
                                                                "#0f172a",
                                                        }}
                                                    >
                                                        {terrainData.aspect_degrees.toFixed(
                                                            1
                                                        )}
                                                        °
                                                    </strong>

                                                </div>

                                            </div>

                                            {/* =================================================
                                               RISK CARD
                                            ================================================= */}

                                            {riskConfig && (

                                                <div
                                                    style={{
                                                        marginTop:
                                                            "10px",
                                                        border: `1px solid ${riskConfig.border}`,
                                                        borderRadius:
                                                            "10px",
                                                        padding:
                                                            "10px",
                                                        background:
                                                            riskConfig.bg,
                                                    }}
                                                >

                                                    <div
                                                        style={{
                                                            display:
                                                                "flex",
                                                            justifyContent:
                                                                "space-between",
                                                            alignItems:
                                                                "center",
                                                        }}
                                                    >

                                                        <div>

                                                            <div
                                                                style={{
                                                                    fontSize:
                                                                        "9px",
                                                                    color:
                                                                        "#64748b",
                                                                    textTransform:
                                                                        "uppercase",
                                                                }}
                                                            >
                                                                Terrain Risk
                                                            </div>

                                                            <strong
                                                                style={{
                                                                    fontSize:
                                                                        "20px",
                                                                    color:
                                                                        "#0f172a",
                                                                }}
                                                            >
                                                                {terrainData.risk_score.toFixed(
                                                                    1
                                                                )}
                                                            </strong>

                                                        </div>

                                                        <div
                                                            style={{
                                                                display:
                                                                    "flex",
                                                                alignItems:
                                                                    "center",
                                                                gap:
                                                                    "6px",
                                                                borderRadius:
                                                                    "999px",
                                                                padding:
                                                                    "5px 9px",
                                                                background:
                                                                    riskConfig.bg,
                                                            }}
                                                        >

                                                            <span
                                                                style={{
                                                                    width:
                                                                        "7px",
                                                                    height:
                                                                        "7px",
                                                                    borderRadius:
                                                                        "50%",
                                                                    background:
                                                                        riskConfig.dot,
                                                                    boxShadow: `0 0 8px ${riskConfig.dot}`,
                                                                }}
                                                            />

                                                            <strong
                                                                style={{
                                                                    fontSize:
                                                                        "10px",
                                                                    color:
                                                                        riskConfig.color,
                                                                }}
                                                            >
                                                                {
                                                                    riskConfig.label
                                                                }
                                                            </strong>

                                                        </div>

                                                    </div>

                                                </div>

                                            )}

                                            {/* =================================================
                                               RISK FACTORS
                                            ================================================= */}

                                            {terrainData.risk_factors?.length >
                                                0 && (

                                                <div
                                                    style={{
                                                        marginTop:
                                                            "10px",
                                                    }}
                                                >

                                                    <div
                                                        style={{
                                                            fontSize:
                                                                "10px",
                                                            fontWeight:
                                                                800,
                                                            color:
                                                                "#64748b",
                                                            textTransform:
                                                                "uppercase",
                                                            marginBottom:
                                                                "5px",
                                                        }}
                                                    >
                                                        Risk Drivers
                                                    </div>

                                                    <ul
                                                        style={{
                                                            margin:
                                                                0,
                                                            paddingLeft:
                                                                "17px",
                                                            fontSize:
                                                                "11px",
                                                            lineHeight:
                                                                "1.6",
                                                            color:
                                                                "#475569",
                                                        }}
                                                    >

                                                        {terrainData.risk_factors.map(
                                                            (
                                                                factor,
                                                                index
                                                            ) => (

                                                                <li
                                                                    key={
                                                                        index
                                                                    }
                                                                >
                                                                    {
                                                                        factor
                                                                    }
                                                                </li>

                                                            )
                                                        )}

                                                    </ul>

                                                </div>

                                            )}

                                        </>

                                    )}

                                    {/* =================================================
                                       SATELLITE INTELLIGENCE
                                    ================================================= */}

                                    {monitoringData && (

                                        <div
                                            style={{
                                                marginTop:
                                                    "14px",
                                                paddingTop:
                                                    "12px",
                                                borderTop:
                                                    "1px solid #e2e8f0",
                                            }}
                                        >

                                            <div
                                                style={{
                                                    display:
                                                        "flex",
                                                    justifyContent:
                                                        "space-between",
                                                    alignItems:
                                                        "center",
                                                    marginBottom:
                                                        "8px",
                                                }}
                                            >

                                                <strong
                                                    style={{
                                                        fontSize:
                                                            "12px",
                                                        color:
                                                            "#0f172a",
                                                    }}
                                                >
                                                    🛰️ Satellite Intelligence
                                                </strong>

                                                {monitoringConfig && (

                                                    <span
                                                        style={{
                                                            fontSize:
                                                                "9px",
                                                            fontWeight:
                                                                800,
                                                            color:
                                                                monitoringConfig.color,
                                                        }}
                                                    >
                                                        ●{" "}
                                                        {
                                                            monitoringData.status
                                                        }
                                                    </span>

                                                )}

                                            </div>

                                            {/* MONITORING METRICS */}

                                            <div
                                                style={{
                                                    display:
                                                        "grid",
                                                    gridTemplateColumns:
                                                        "1fr 1fr 1fr",
                                                    gap: "5px",
                                                }}
                                            >

                                                {/* SPECTRAL */}

                                                <div
                                                    style={{
                                                        background:
                                                            "#f8fafc",
                                                        padding:
                                                            "7px",
                                                        borderRadius:
                                                            "7px",
                                                    }}
                                                >

                                                    <div
                                                        style={{
                                                            fontSize:
                                                                "8px",
                                                            color:
                                                                "#64748b",
                                                        }}
                                                    >
                                                        Spectral
                                                    </div>

                                                    <strong
                                                        style={{
                                                            fontSize:
                                                                "12px",
                                                            color:
                                                                "#0f172a",
                                                        }}
                                                    >
                                                        {(
                                                            monitoringData.spectral_change *
                                                            100
                                                        ).toFixed(
                                                            1
                                                        )}
                                                        %
                                                    </strong>

                                                </div>

                                                {/* AI ANOMALY */}

                                                <div
                                                    style={{
                                                        background:
                                                            "#f8fafc",
                                                        padding:
                                                            "7px",
                                                        borderRadius:
                                                            "7px",
                                                    }}
                                                >

                                                    <div
                                                        style={{
                                                            fontSize:
                                                                "8px",
                                                            color:
                                                                "#64748b",
                                                        }}
                                                    >
                                                        AI Anomaly
                                                    </div>

                                                    <strong
                                                        style={{
                                                            fontSize:
                                                                "12px",
                                                            color:
                                                                "#0f172a",
                                                        }}
                                                    >
                                                        {(
                                                            monitoringData.ai_anomaly *
                                                            100
                                                        ).toFixed(
                                                            1
                                                        )}
                                                        %
                                                    </strong>

                                                </div>

                                                {/* COMBINED */}

                                                <div
                                                    style={{
                                                        background:
                                                            "#f8fafc",
                                                        padding:
                                                            "7px",
                                                        borderRadius:
                                                            "7px",
                                                    }}
                                                >

                                                    <div
                                                        style={{
                                                            fontSize:
                                                                "8px",
                                                            color:
                                                                "#64748b",
                                                        }}
                                                    >
                                                        Combined
                                                    </div>

                                                    <strong
                                                        style={{
                                                            fontSize:
                                                                "12px",
                                                            color:
                                                                "#0f172a",
                                                        }}
                                                    >
                                                        {(
                                                            monitoringData.combined_change *
                                                            100
                                                        ).toFixed(
                                                            1
                                                        )}
                                                        %
                                                    </strong>

                                                </div>

                                            </div>

                                            {/* RECOMMENDATION */}

                                            <div
                                                style={{
                                                    marginTop:
                                                        "8px",
                                                    padding:
                                                        "8px",
                                                    borderRadius:
                                                        "8px",
                                                    background:
                                                        "#f8fafc",
                                                    fontSize:
                                                        "10px",
                                                    lineHeight:
                                                        "1.5",
                                                    color:
                                                        "#475569",
                                                }}
                                            >
                                                {
                                                    monitoringData.recommendation
                                                }
                                            </div>

                                        </div>

                                    )}

                                    {/* MONITORING UNAVAILABLE */}

                                    {!monitoringData &&
                                        terrainData && (

                                            <div
                                                style={{
                                                    marginTop:
                                                        "12px",
                                                    padding:
                                                        "9px",
                                                    borderRadius:
                                                        "8px",
                                                    background:
                                                        "#f8fafc",
                                                    fontSize:
                                                        "10px",
                                                    color:
                                                        "#64748b",
                                                }}
                                            >
                                                🛰️ Satellite monitoring
                                                unavailable for this
                                                location.
                                            </div>

                                        )}

                                </div>

                            </Popup>

                        </Marker>

                    )}

                </MapContainer>

                {/* =================================================
                   MAP FOOTER
                ================================================= */}

                <div className="pointer-events-none absolute bottom-4 right-0 z-[1000]">

                    <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">

                        {/* DATA SOURCES */}

                        <div className="hidden rounded-xl border border-white/10 bg-slate-950/85 px-7 py-3 shadow-xl backdrop-blur-xl sm:block">

                            <div className="flex items-center gap-3">

                                <span className="text-[9px] uppercase tracking-widest text-slate-500">
                                    Data Sources
                                </span>

                                <span className="h-1 w-1 rounded-full bg-slate-600" />

                                <span className="text-[10px] text-slate-300">
                                    DEM
                                </span>

                                <span className="h-1 w-1 rounded-full bg-slate-600" />

                                <span className="text-[10px] text-slate-300">
                                    Satellite
                                </span>

                                <span className="h-1 w-1 rounded-full bg-slate-600" />

                                <span className="text-[10px] text-cyan-300">
                                    ML
                                </span>

                            </div>

                        </div>

                    </div>

                </div>

                {/* =================================================
                   INTELLIGENCE LEGEND
                ================================================= */}

                <div className="absolute bottom-20 right-4 z-[1000] hidden w-64 overflow-hidden rounded-2xl border border-white/10 bg-slate-950/90 shadow-2xl backdrop-blur-xl md:block">

                    {/* HEADER */}

                    <div className="border-b border-white/10 px-4 py-3">

                        <div className="flex items-center justify-between">

                            <p className="text-[10px] font-bold uppercase tracking-[0.15em] text-slate-300">
                                Intelligence Layers
                            </p>

                            <span className="text-[10px] text-slate-600">
                                MAP
                            </span>

                        </div>

                    </div>

                    {/* AI ANOMALY */}

                    <div className="px-4 py-3">

                        <p className="mb-2 text-[9px] font-semibold uppercase tracking-wider text-slate-500">
                            AI Change Anomaly
                        </p>

                        <div className="space-y-2">

                            <div className="flex items-center gap-3">

                                <div className="h-2.5 w-5 rounded-sm bg-slate-500" />

                                <span className="text-[10px] text-slate-400">
                                    Low anomaly
                                </span>

                            </div>

                            <div className="flex items-center gap-3">

                                <div className="h-2.5 w-5 rounded-sm bg-yellow-400" />

                                <span className="text-[10px] text-slate-400">
                                    Moderate anomaly
                                </span>

                            </div>

                            <div className="flex items-center gap-3">

                                <div className="h-2.5 w-5 rounded-sm bg-red-500" />

                                <span className="text-[10px] text-slate-400">
                                    High anomaly
                                </span>

                            </div>

                        </div>

                    </div>

                    {/* SATELLITE */}

                    <div className="border-t border-white/10 px-4 py-3">

                        <p className="mb-2 text-[9px] font-semibold uppercase tracking-wider text-slate-500">
                            Satellite Change
                        </p>

                        <div className="space-y-2">

                            <div className="flex items-center gap-3">

                                <div className="h-2.5 w-5 rounded-sm bg-slate-500" />

                                <span className="text-[10px] text-slate-400">
                                    Lower change
                                </span>

                            </div>

                            <div className="flex items-center gap-3">

                                <div className="h-2.5 w-5 rounded-sm bg-yellow-400" />

                                <span className="text-[10px] text-slate-400">
                                    Higher change
                                </span>

                            </div>

                        </div>

                    </div>

                    {/* DEM */}

                    <div className="border-t border-white/10 px-4 py-3">

                        <div className="flex items-center gap-3">

                            <div className="h-3 w-5 rounded-sm border-2 border-cyan-400" />

                            <span className="text-[10px] text-slate-400">
                                DEM analysis coverage
                            </span>

                        </div>

                    </div>

                    {/* DISCLAIMER */}

                    <div className="border-t border-white/10 px-4 py-3">

                        <p className="text-[9px] leading-relaxed text-slate-600">
                            AI anomaly indicates unusual
                            surface change and does not
                            represent confirmed landslide
                            detection.
                        </p>

                    </div>

                </div>

            </div>

        </div>
    );
}