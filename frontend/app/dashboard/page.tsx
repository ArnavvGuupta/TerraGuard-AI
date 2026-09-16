"use client";

import dynamic from "next/dynamic";
import { useEffect, useState } from "react";

const TerrainMap = dynamic(
    () => import("../../components/TerrainMap"),
    {
        ssr: false,
    }
);
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

type ChatMessage = {
    role: "user" | "assistant";
    content: string;
};

type SelectedLocation = {
    latitude: number;
    longitude: number;
};

/* =========================================================
   MAIN PAGE
========================================================= */

export default function Home() {
    const [terrain, setTerrain] =
        useState<TerrainData | null>(null);

    const [loading, setLoading] =
        useState(false);

    const [error, setError] =
        useState<string | null>(null);

    const [selectedLocation, setSelectedLocation] =
        useState<SelectedLocation | null>(null);

    const [chatMessage, setChatMessage] =
        useState("");

    const [chatLoading, setChatLoading] =
        useState(false);

    const [chatMessages, setChatMessages] =
        useState<ChatMessage[]>([
            {
                role: "assistant",
                content:
                    "Hello! I'm your AI Risk Assistant. Select a location on the map and I can explain its terrain susceptibility, risk factors, and satellite monitoring signals.",
            },
        ]);

    /* =====================================================
       READ SELECTED LOCATION
    ===================================================== */

    useEffect(() => {
        const updateLocation = () => {
            const saved =
                localStorage.getItem(
                    "selectedTerrainLocation"
                );

            if (!saved) return;

            try {
                const location =
                    JSON.parse(saved);

                if (
                    typeof location.latitude ===
                        "number" &&
                    typeof location.longitude ===
                        "number"
                ) {
                    setSelectedLocation(
                        location
                    );
                }
            } catch {
                console.error(
                    "Invalid saved terrain location"
                );
            }
        };

        updateLocation();

        const interval =
            setInterval(
                updateLocation,
                500
            );

        return () =>
            clearInterval(interval);
    }, []);

    /* =====================================================
       CHAT
    ===================================================== */

    async function sendChatMessage(
        customMessage?: string
    ) {
        const message =
            customMessage ??
            chatMessage.trim();

        if (!message || !selectedLocation)
            return;

        const userMessage: ChatMessage = {
            role: "user",
            content: message,
        };

        const updatedMessages = [
            ...chatMessages,
            userMessage,
        ];

        setChatMessages(
            updatedMessages
        );

        setChatMessage("");
        setChatLoading(true);

        try {
            const response =
                await fetch(
                    "http://127.0.0.1:8000/chat",
                    {
                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json",
                        },

                        body: JSON.stringify({
                            message,
                            latitude:
                                selectedLocation.latitude,
                            longitude:
                                selectedLocation.longitude,
                            history:
                                updatedMessages,
                        }),
                    }
                );

            const data =
                await response.json();

            if (!response.ok) {
                throw new Error(
                    data.detail ||
                        "Chat request failed"
                );
            }

            setChatMessages(
                (prev) => [
                    ...prev,
                    {
                        role: "assistant",
                        content:
                            data.answer ||
                            "I couldn't generate an answer.",
                    },
                ]
            );
        } catch (err) {
            console.error(err);

            setChatMessages(
                (prev) => [
                    ...prev,
                    {
                        role: "assistant",
                        content:
                            "I couldn't connect to the AI backend. Please make sure FastAPI is running on port 8000.",
                    },
                ]
            );
        } finally {
            setChatLoading(false);
        }
    }

    /* =====================================================
       QUICK QUESTIONS
    ===================================================== */

    function askQuickQuestion(
        question: string
    ) {
        sendChatMessage(question);
    }

    /* =====================================================
       RISK STYLING
    ===================================================== */

    function getRiskStyle(
        level: string
    ) {
        switch (
            level?.toUpperCase()
        ) {
            case "HIGH":
                return {
                    text: "text-red-400",
                    border:
                        "border-red-500/30",
                    bg:
                        "bg-red-500/10",
                    glow:
                        "shadow-[0_0_35px_rgba(239,68,68,0.12)]",
                    icon: "🔴",
                };

            case "MEDIUM":
                return {
                    text: "text-yellow-400",
                    border:
                        "border-yellow-500/30",
                    bg:
                        "bg-yellow-500/10",
                    glow:
                        "shadow-[0_0_35px_rgba(250,204,21,0.10)]",
                    icon: "🟡",
                };

            default:
                return {
                    text: "text-emerald-400",
                    border:
                        "border-emerald-500/30",
                    bg:
                        "bg-emerald-500/10",
                    glow:
                        "shadow-[0_0_35px_rgba(52,211,153,0.10)]",
                    icon: "🟢",
                };
        }
    }

    /* =====================================================
       RISK STYLE
    ===================================================== */

    const riskStyle = terrain
        ? getRiskStyle(
              terrain.risk_level
          )
        : null;

    /* =====================================================
       PAGE
    ===================================================== */

    return (
        <main className="relative min-h-screen overflow-hidden bg-[#020617] text-white">

            {/* =================================================
               BACKGROUND ATMOSPHERE
            ================================================= */}

            <div className="pointer-events-none fixed inset-0">

                <div className="absolute left-[-15%] top-[-10%] h-[550px] w-[550px] rounded-full bg-cyan-500/[0.07] blur-[140px]" />

                <div className="absolute right-[-15%] top-[20%] h-[500px] w-[500px] rounded-full bg-blue-600/[0.06] blur-[150px]" />

                <div className="absolute bottom-[-20%] left-[30%] h-[500px] w-[500px] rounded-full bg-indigo-600/[0.05] blur-[160px]" />

                <div
                    className="absolute inset-0 opacity-[0.035]"
                    style={{
                        backgroundImage:
                            "linear-gradient(rgba(34,211,238,0.7) 1px, transparent 1px), linear-gradient(90deg, rgba(34,211,238,0.7) 1px, transparent 1px)",
                        backgroundSize:
                            "50px 50px",
                    }}
                />

            </div>

            <div className="relative z-10 mx-auto max-w-[1700px] px-4 py-6 sm:px-6 lg:px-8">

                {/* =================================================
                   TOP STATUS BAR
                ================================================= */}

                <div className="mb-6 flex flex-col gap-3 rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-3 backdrop-blur-xl md:flex-row md:items-center md:justify-between">

                    <div className="flex items-center gap-3">

                        <div className="h-2 w-2 animate-pulse rounded-full bg-emerald-400 shadow-[0_0_12px_rgba(52,211,153,0.9)]" />

                        <span className="text-[10px] font-semibold uppercase tracking-[0.2em] text-slate-400">
                            Geospatial Intelligence Network
                        </span>

                        <span className="hidden text-slate-700 sm:block">
                            /
                        </span>

                        <span className="hidden text-[10px] uppercase tracking-widest text-cyan-400 sm:block">
                            Sikkim Monitoring Region
                        </span>

                    </div>

                    <div className="flex items-center gap-5 text-[10px] uppercase tracking-widest">

                        <span className="text-slate-500">
                            DEM
                            <span className="ml-1 text-emerald-400">
                                ONLINE
                            </span>
                        </span>

                        <span className="text-slate-500">
                            SATELLITE
                            <span className="ml-1 text-emerald-400">
                                ONLINE
                            </span>
                        </span>

                        <span className="text-slate-500">
                            AI
                            <span className="ml-1 text-cyan-400">
                                READY
                            </span>
                        </span>

                    </div>

                </div>

                {/* =================================================
                   HERO HEADER
                ================================================= */}

                <section className="mb-8">

                    <div className="flex flex-col justify-between gap-8 lg:flex-row lg:items-end">

                        <div className="max-w-4xl">

                            <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-cyan-400/20 bg-cyan-400/[0.06] px-3 py-1.5">

                                <span className="text-sm">
                                    🛰️
                                </span>

                                <span className="text-[10px] font-bold uppercase tracking-[0.18em] text-cyan-300">
                                    ISRO Geospatial Terrain Analysis
                                </span>

                            </div>

                            <h1 className="text-4xl font-black tracking-tight sm:text-5xl lg:text-6xl">

                                Himalayan Terrain

                                <span className="block bg-gradient-to-r from-cyan-300 via-blue-400 to-indigo-400 bg-clip-text text-transparent">
                                    Intelligence Platform
                                </span>

                            </h1>

                            <p className="mt-5 max-w-3xl text-sm leading-7 text-slate-400 sm:text-base">

                                Explore terrain characteristics,
                                visualize multi-source geospatial
                                intelligence, and estimate terrain
                                susceptibility to landslide hazards
                                using DEM-derived analysis and
                                AI-assisted monitoring.

                            </p>

                        </div>

                        {/* SYSTEM CARD */}

                        <div className="hidden min-w-[280px] rounded-2xl border border-white/10 bg-white/[0.025] p-4 shadow-2xl backdrop-blur-xl xl:block">

                            <div className="mb-4 flex items-center justify-between">

                                <span className="text-[9px] font-bold uppercase tracking-[0.2em] text-slate-500">
                                    SYSTEM STATUS
                                </span>

                                <span className="rounded-full border border-emerald-400/20 bg-emerald-400/10 px-2 py-1 text-[9px] font-bold text-emerald-400">
                                    OPERATIONAL
                                </span>

                            </div>

                            <div className="space-y-3">

                                <div className="flex items-center justify-between">

                                    <span className="text-xs text-slate-400">
                                        Terrain Engine
                                    </span>

                                    <span className="text-xs font-semibold text-emerald-400">
                                        ● Ready
                                    </span>

                                </div>

                                <div className="flex items-center justify-between">

                                    <span className="text-xs text-slate-400">
                                        Satellite Monitor
                                    </span>

                                    <span className="text-xs font-semibold text-emerald-400">
                                        ● Ready
                                    </span>

                                </div>

                                <div className="flex items-center justify-between">

                                    <span className="text-xs text-slate-400">
                                        AI Risk Assistant
                                    </span>

                                    <span className="text-xs font-semibold text-cyan-400">
                                        ● Online
                                    </span>

                                </div>

                            </div>

                        </div>

                    </div>

                </section>

                {/* =================================================
                   MAIN WORKSPACE
                ================================================= */}

                <section className="grid grid-cols-1 gap-6 lg:grid-cols-[minmax(0,1fr)_390px]">

                    {/* =================================================
                       LEFT — MAP
                    ================================================= */}

                    <div className="min-w-0">

                        <div className="overflow-hidden rounded-3xl border border-white/10 bg-slate-950/70 shadow-2xl backdrop-blur-xl">

                            {/* MAP HEADER */}

                            <div className="border-b border-white/10 px-5 py-4 sm:px-6">

                                <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">

                                    <div className="flex items-center gap-3">

                                        <div className="flex h-10 w-10 items-center justify-center rounded-xl border border-cyan-400/20 bg-cyan-400/10">
                                            🌐
                                        </div>

                                        <div>

                                            <div className="flex items-center gap-2">

                                                <h2 className="font-bold tracking-wide">
                                                    Interactive Terrain Intelligence
                                                </h2>

                                                <span className="hidden rounded-full bg-cyan-400/10 px-2 py-0.5 text-[8px] font-bold uppercase tracking-widest text-cyan-400 sm:block">
                                                    LIVE MAP
                                                </span>

                                            </div>

                                            <p className="mt-1 text-xs text-slate-500">
                                                Select a location to run terrain and satellite analysis
                                            </p>

                                        </div>

                                    </div>

                                    {loading && (

                                        <div className="flex items-center gap-2 rounded-full border border-cyan-400/20 bg-cyan-400/5 px-3 py-2">

                                            <div className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-cyan-400 border-t-transparent" />

                                            <span className="text-[10px] font-semibold uppercase tracking-widest text-cyan-300">
                                                Processing
                                            </span>

                                        </div>

                                    )}

                                </div>

                            </div>

                            {/* MAP */}

                            <TerrainMap
                                onTerrainData={
                                    setTerrain
                                }
                                onLoading={
                                    setLoading
                                }
                                onError={
                                    setError
                                }
                            />

                        </div>

                        {/* ERROR */}

                        {error && (

                            <div className="mt-5 rounded-2xl border border-red-500/20 bg-red-500/10 p-5">

                                <div className="flex gap-3">

                                    <span className="text-xl">
                                        ⚠️
                                    </span>

                                    <div>

                                        <p className="font-semibold text-red-300">
                                            Analysis Error
                                        </p>

                                        <p className="mt-1 text-sm text-red-300/70">
                                            {error}
                                        </p>

                                    </div>

                                </div>

                            </div>

                        )}

                        {/* EMPTY STATE */}

                        {!terrain &&
                            !loading &&
                            !error && (

                                <div className="mt-5 rounded-2xl border border-white/10 bg-white/[0.025] p-5">

                                    <div className="flex items-center gap-4">

                                        <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-cyan-400/10 text-xl">
                                            🎯
                                        </div>

                                        <div>

                                            <p className="font-semibold text-white">
                                                Ready for terrain analysis
                                            </p>

                                            <p className="mt-1 text-sm text-slate-500">
                                                Click anywhere inside the mapped region to retrieve elevation, slope, aspect, and susceptibility information.
                                            </p>

                                        </div>

                                    </div>

                                </div>

                            )}

                    </div>

                    {/* =================================================
                       RIGHT — AI ASSISTANT
                    ================================================= */}

                    <aside className="min-w-0">

                        <div className="sticky top-6 flex h-[650px] flex-col overflow-hidden rounded-3xl border border-cyan-400/10 bg-slate-950/85 shadow-[0_0_50px_rgba(8,145,178,0.08)] backdrop-blur-xl">

                            {/* CHAT HEADER */}

                            <div className="border-b border-white/10 p-5">

                                <div className="flex items-start justify-between">

                                    <div className="flex gap-3">

                                        <div className="flex h-11 w-11 items-center justify-center rounded-xl border border-cyan-400/20 bg-cyan-400/10 text-xl">
                                            🤖
                                        </div>

                                        <div>

                                            <h2 className="font-bold">
                                                AI Risk Assistant
                                            </h2>

                                            <p className="mt-1 text-[11px] text-slate-500">
                                                Geospatial reasoning engine
                                            </p>

                                        </div>

                                    </div>

                                    <div className="flex items-center gap-1.5 rounded-full border border-emerald-400/20 bg-emerald-400/5 px-2.5 py-1">

                                        <div className="h-1.5 w-1.5 animate-pulse rounded-full bg-emerald-400" />

                                        <span className="text-[8px] font-bold uppercase tracking-widest text-emerald-400">
                                            Online
                                        </span>

                                    </div>

                                </div>

                                {/* LOCATION */}

                                <div className="mt-5">

                                    {selectedLocation ? (

                                        <div className="rounded-2xl border border-cyan-400/20 bg-gradient-to-br from-cyan-400/[0.08] to-blue-500/[0.04] p-4">

                                            <div className="flex items-center justify-between">

                                                <span className="text-[9px] font-bold uppercase tracking-[0.16em] text-slate-500">
                                                    ACTIVE LOCATION
                                                </span>

                                                <span className="text-[10px] text-cyan-400">
                                                    ● ANALYZED
                                                </span>

                                            </div>

                                            <p className="mt-2 font-mono text-sm font-semibold text-cyan-300">

                                                {selectedLocation.latitude.toFixed(
                                                    5
                                                )}

                                                <span className="mx-2 text-slate-600">
                                                    /
                                                </span>

                                                {selectedLocation.longitude.toFixed(
                                                    5
                                                )}

                                            </p>

                                        </div>

                                    ) : (

                                        <div className="rounded-2xl border border-white/10 bg-white/[0.025] p-4">

                                            <div className="flex items-center gap-3">

                                                <span className="text-lg">
                                                    📍
                                                </span>

                                                <div>

                                                    <p className="text-sm font-medium text-slate-300">
                                                        No location selected
                                                    </p>

                                                    <p className="mt-1 text-[10px] text-slate-600">
                                                        Select a point on the map to activate AI analysis.
                                                    </p>

                                                </div>

                                            </div>

                                        </div>

                                    )}

                                </div>

                            </div>

                            {/* QUICK QUESTIONS */}

                            {selectedLocation && (

                                <div className="border-b border-white/10 p-4">

                                    <div className="mb-2 flex items-center justify-between">

                                        <span className="text-[9px] font-bold uppercase tracking-[0.16em] text-slate-600">
                                            QUICK ANALYSIS
                                        </span>

                                        <span className="text-[9px] text-cyan-500">
                                            AI
                                        </span>

                                    </div>

                                    <div className="grid grid-cols-3 gap-2">

                                        <button
                                            onClick={() =>
                                                askQuickQuestion(
                                                    "Explain the risk at this location in simple terms."
                                                )
                                            }
                                            className="rounded-xl border border-white/10 bg-white/[0.03] px-2 py-2.5 text-[10px] font-medium text-slate-400 transition hover:-translate-y-0.5 hover:border-cyan-400/30 hover:bg-cyan-400/[0.05] hover:text-cyan-300"
                                        >
                                            Explain risk
                                        </button>

                                        <button
                                            onClick={() =>
                                                askQuickQuestion(
                                                    "What factors are contributing to the landslide risk at this location?"
                                                )
                                            }
                                            className="rounded-xl border border-white/10 bg-white/[0.03] px-2 py-2.5 text-[10px] font-medium text-slate-400 transition hover:-translate-y-0.5 hover:border-cyan-400/30 hover:bg-cyan-400/[0.05] hover:text-cyan-300"
                                        >
                                            Risk factors
                                        </button>

                                        <button
                                            onClick={() =>
                                                askQuickQuestion(
                                                    "What should be monitored at this location?"
                                                )
                                            }
                                            className="rounded-xl border border-white/10 bg-white/[0.03] px-2 py-2.5 text-[10px] font-medium text-slate-400 transition hover:-translate-y-0.5 hover:border-cyan-400/30 hover:bg-cyan-400/[0.05] hover:text-cyan-300"
                                        >
                                            Monitor
                                        </button>

                                    </div>

                                </div>

                            )}

                            {/* MESSAGES */}

                            <div className="flex-1 space-y-4 overflow-y-auto p-4">

                                {chatMessages.map(
                                    (
                                        message,
                                        index
                                    ) => (

                                        <div
                                            key={
                                                index
                                            }
                                            className={`flex ${
                                                message.role ===
                                                "user"
                                                    ? "justify-end"
                                                    : "justify-start"
                                            }`}
                                        >

                                            {message.role ===
                                                "assistant" && (

                                                <div className="mr-2 mt-1 flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-cyan-400/10 text-xs">
                                                    🤖
                                                </div>

                                            )}

                                            <div
                                                className={`max-w-[88%] rounded-2xl px-3.5 py-3 text-xs leading-6 ${
                                                    message.role ===
                                                    "user"
                                                        ? "rounded-br-md bg-gradient-to-r from-cyan-600 to-blue-600 text-white shadow-lg shadow-cyan-900/20"
                                                        : "rounded-bl-md border border-white/10 bg-white/[0.04] text-slate-300"
                                                }`}
                                            >
                                                {
                                                    message.content
                                                }
                                            </div>

                                        </div>

                                    )
                                )}

                                {chatLoading && (

                                    <div className="flex items-center gap-2">

                                        <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-cyan-400/10 text-xs">
                                            🤖
                                        </div>

                                        <div className="rounded-2xl rounded-bl-md border border-white/10 bg-white/[0.04] px-4 py-3">

                                            <div className="flex gap-1">

                                                <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-cyan-400 [animation-delay:-0.3s]" />

                                                <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-cyan-400 [animation-delay:-0.15s]" />

                                                <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-cyan-400" />

                                            </div>

                                        </div>

                                    </div>

                                )}

                            </div>

                            {/* CHAT INPUT */}

                            <div className="border-t border-white/10 bg-black/10 p-4">

                                <div className="flex gap-2">

                                    <input
                                        type="text"
                                        value={
                                            chatMessage
                                        }
                                        onChange={(
                                            e
                                        ) =>
                                            setChatMessage(
                                                e.target
                                                    .value
                                            )
                                        }
                                        onKeyDown={(
                                            e
                                        ) => {
                                            if (
                                                e.key ===
                                                    "Enter" &&
                                                !e.shiftKey
                                            ) {
                                                e.preventDefault();

                                                sendChatMessage();
                                            }
                                        }}
                                        placeholder={
                                            selectedLocation
                                                ? "Ask about this location..."
                                                : "Select a map location first..."
                                        }
                                        disabled={
                                            !selectedLocation ||
                                            chatLoading
                                        }
                                        className="min-w-0 flex-1 rounded-xl border border-white/10 bg-white/[0.04] px-3 py-3 text-xs text-white outline-none transition placeholder:text-slate-600 focus:border-cyan-400/40 focus:bg-white/[0.06] disabled:cursor-not-allowed disabled:opacity-40"
                                    />

                                    <button
                                        onClick={() =>
                                            sendChatMessage()
                                        }
                                        disabled={
                                            !selectedLocation ||
                                            !chatMessage.trim() ||
                                            chatLoading
                                        }
                                        className="rounded-xl bg-gradient-to-r from-cyan-600 to-blue-600 px-4 text-xs font-bold text-white shadow-lg shadow-cyan-900/20 transition hover:-translate-y-0.5 hover:from-cyan-500 hover:to-blue-500 disabled:cursor-not-allowed disabled:opacity-30"
                                    >
                                        {chatLoading
                                            ? "..."
                                            : "Send"}
                                    </button>

                                </div>

                                <p className="mt-2 text-center text-[9px] leading-relaxed text-slate-700">
                                    AI-generated analysis is an estimate and does not replace professional geological assessment.
                                </p>

                            </div>

                        </div>

                    </aside>

                </section>

                {/* =================================================
                   RESULTS
                ================================================= */}

                       {/* =====================================================
           METHODOLOGY
        ================================================= */}


        {/* =========================================================
           TERRAIN INDICATOR — EXPLAINABLE AI / METHODOLOGY
        ========================================================= */}

        <section className="relative mt-8 overflow-hidden rounded-[2rem] border border-white/10 bg-slate-950/70 p-6 shadow-2xl backdrop-blur-xl sm:p-8">

            {/* Ambient glows */}
            <div className="pointer-events-none absolute -right-32 -top-32 h-72 w-72 rounded-full bg-cyan-500/[0.06] blur-[100px]" />
            <div className="pointer-events-none absolute -bottom-32 -left-32 h-72 w-72 rounded-full bg-blue-500/[0.06] blur-[100px]" />

            {/* Subtle grid */}
            <div
                className="pointer-events-none absolute inset-0 opacity-[0.025]"
                style={{
                    backgroundImage:
                        "linear-gradient(rgba(34,211,238,.8) 1px, transparent 1px), linear-gradient(90deg, rgba(34,211,238,.8) 1px, transparent 1px)",
                    backgroundSize: "40px 40px",
                }}
            />

            <div className="relative z-10">

                {/* =====================================================
                   HEADER
                ====================================================== */}

                <div className="flex flex-col gap-5 md:flex-row md:items-start md:justify-between">

                    <div className="flex gap-4">

                        {/* Animated icon */}
                        <div className="group relative flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl border border-cyan-400/20 bg-cyan-400/[0.08] shadow-[0_0_30px_rgba(34,211,238,0.06)]">

                            <div className="absolute inset-0 rounded-2xl bg-cyan-400/10 blur-lg transition-all duration-500 group-hover:bg-cyan-400/20" />

                            <span className="relative text-xl transition-transform duration-500 group-hover:scale-110">
                                🧠
                            </span>

                        </div>

                        <div>

                            <div className="flex flex-wrap items-center gap-2">

                                <h3 className="text-lg font-bold tracking-tight text-white">
                                    How the Terrain Indicator Works
                                </h3>

                                <span className="rounded-full border border-cyan-400/20 bg-cyan-400/[0.06] px-2 py-0.5 text-[8px] font-bold uppercase tracking-[0.2em] text-cyan-400">
                                    Explainable
                                </span>

                            </div>

                            <p className="mt-2 max-w-2xl text-xs leading-5 text-slate-500">
                                A transparent terrain susceptibility model that combines
                                elevation and slope characteristics derived from
                                Digital Elevation Model (DEM) data.
                            </p>

                        </div>

                    </div>

                    {/* Method badge */}
                    <div className="flex shrink-0 items-center gap-2 rounded-full border border-white/10 bg-white/[0.025] px-3 py-2">

                        <span className="relative flex h-2 w-2">
                            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-cyan-400 opacity-50" />
                            <span className="relative inline-flex h-2 w-2 rounded-full bg-cyan-400" />
                        </span>

                        <span className="text-[9px] font-bold uppercase tracking-[0.18em] text-slate-400">
                            Rule-Based Model
                        </span>

                    </div>

                </div>


                {/* =====================================================
                   SCORE FLOW
                ====================================================== */}

                <div className="mt-7 rounded-2xl border border-white/5 bg-black/20 p-5">

                    <div className="mb-4 flex items-center justify-between">

                        <div>
                            <p className="text-[9px] font-bold uppercase tracking-[0.2em] text-cyan-500">
                                Analysis Pipeline
                            </p>

                            <p className="mt-1 text-xs text-slate-600">
                                Terrain characteristics → weighted score → risk class
                            </p>
                        </div>

                        <span className="hidden text-[9px] font-semibold text-slate-700 sm:block">
                            DEM PROCESSING
                        </span>

                    </div>

                    <div className="grid gap-3 md:grid-cols-3">

                        {/* Step 1 */}
                        <div className="group relative overflow-hidden rounded-xl border border-white/5 bg-white/[0.025] p-4 transition-all duration-300 hover:-translate-y-1 hover:border-cyan-400/20 hover:bg-cyan-400/[0.03]">

                            <div className="flex items-center gap-3">

                                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-cyan-400/10 text-xs font-black text-cyan-400">
                                    01
                                </div>

                                <div>
                                    <p className="text-xs font-bold text-slate-300">
                                        Extract Terrain
                                    </p>

                                    <p className="mt-0.5 text-[10px] text-slate-600">
                                        DEM → slope + elevation
                                    </p>
                                </div>

                            </div>

                        </div>

                        {/* Step 2 */}
                        <div className="group relative overflow-hidden rounded-xl border border-white/5 bg-white/[0.025] p-4 transition-all duration-300 hover:-translate-y-1 hover:border-blue-400/20 hover:bg-blue-400/[0.03]">

                            <div className="flex items-center gap-3">

                                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-400/10 text-xs font-black text-blue-400">
                                    02
                                </div>

                                <div>
                                    <p className="text-xs font-bold text-slate-300">
                                        Calculate Score
                                    </p>

                                    <p className="mt-0.5 text-[10px] text-slate-600">
                                        Apply terrain weights
                                    </p>
                                </div>

                            </div>

                        </div>

                        {/* Step 3 */}
                        <div className="group relative overflow-hidden rounded-xl border border-white/5 bg-white/[0.025] p-4 transition-all duration-300 hover:-translate-y-1 hover:border-emerald-400/20 hover:bg-emerald-400/[0.03]">

                            <div className="flex items-center gap-3">

                                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-emerald-400/10 text-xs font-black text-emerald-400">
                                    03
                                </div>

                                <div>
                                    <p className="text-xs font-bold text-slate-300">
                                        Classify Risk
                                    </p>

                                    <p className="mt-0.5 text-[10px] text-slate-600">
                                        Low → Medium → High
                                    </p>
                                </div>

                            </div>

                        </div>

                    </div>

                </div>


                {/* =====================================================
                   CONTRIBUTION CARDS
                ====================================================== */}

                <div className="mt-5 grid gap-5 md:grid-cols-2">

                    {/* =================================================
                       SLOPE
                    ================================================== */}

                    <div className="group relative overflow-hidden rounded-2xl border border-white/5 bg-white/[0.025] p-5 transition-all duration-500 hover:-translate-y-1 hover:border-orange-400/20 hover:shadow-[0_15px_50px_rgba(251,146,60,0.05)]">

                        <div className="absolute left-0 top-0 h-px w-full bg-gradient-to-r from-transparent via-orange-400/40 to-transparent opacity-0 transition-opacity duration-500 group-hover:opacity-100" />

                        <div className="flex items-center justify-between">

                            <div className="flex items-center gap-3">

                                <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-orange-400/10 text-sm">
                                    ⛰️
                                </div>

                                <div>
                                    <p className="font-semibold text-slate-200">
                                        Slope Contribution
                                    </p>

                                    <p className="text-[9px] uppercase tracking-widest text-slate-700">
                                        Terrain gradient
                                    </p>
                                </div>

                            </div>

                            <span className="rounded-full border border-orange-400/10 bg-orange-400/[0.05] px-2.5 py-1 text-[9px] font-bold text-orange-400">
                                DEM
                            </span>

                        </div>

                        <div className="mt-5 space-y-3">

                            <div>
                                <div className="mb-1.5 flex justify-between text-[11px]">
                                    <span className="text-slate-500">
                                        ≥ 45°
                                    </span>
                                    <span className="font-bold text-red-400">
                                        +60
                                    </span>
                                </div>

                                <div className="h-1 overflow-hidden rounded-full bg-white/5">
                                    <div className="h-full w-full rounded-full bg-red-400/70 transition-all duration-700 group-hover:w-[100%]" />
                                </div>
                            </div>

                            <div>
                                <div className="mb-1.5 flex justify-between text-[11px]">
                                    <span className="text-slate-500">
                                        30° – 44.9°
                                    </span>
                                    <span className="font-bold text-red-400">
                                        +45
                                    </span>
                                </div>

                                <div className="h-1 overflow-hidden rounded-full bg-white/5">
                                    <div className="h-full w-3/4 rounded-full bg-red-400/60" />
                                </div>
                            </div>

                            <div>
                                <div className="mb-1.5 flex justify-between text-[11px]">
                                    <span className="text-slate-500">
                                        20° – 29.9°
                                    </span>
                                    <span className="font-bold text-yellow-400">
                                        +30
                                    </span>
                                </div>

                                <div className="h-1 overflow-hidden rounded-full bg-white/5">
                                    <div className="h-full w-1/2 rounded-full bg-yellow-400/60" />
                                </div>
                            </div>

                            <div>
                                <div className="mb-1.5 flex justify-between text-[11px]">
                                    <span className="text-slate-500">
                                        10° – 19.9°
                                    </span>
                                    <span className="font-bold text-yellow-400">
                                        +15
                                    </span>
                                </div>

                                <div className="h-1 overflow-hidden rounded-full bg-white/5">
                                    <div className="h-full w-1/4 rounded-full bg-yellow-400/50" />
                                </div>
                            </div>

                            <div>
                                <div className="mb-1.5 flex justify-between text-[11px]">
                                    <span className="text-slate-500">
                                        &lt; 10°
                                    </span>
                                    <span className="font-bold text-emerald-400">
                                        +0
                                    </span>
                                </div>

                                <div className="h-1 overflow-hidden rounded-full bg-white/5">
                                    <div className="h-full w-[4%] rounded-full bg-emerald-400/60" />
                                </div>
                            </div>

                        </div>

                    </div>


                    {/* =================================================
                       ELEVATION
                    ================================================== */}

                    <div className="group relative overflow-hidden rounded-2xl border border-white/5 bg-white/[0.025] p-5 transition-all duration-500 hover:-translate-y-1 hover:border-blue-400/20 hover:shadow-[0_15px_50px_rgba(59,130,246,0.05)]">

                        <div className="absolute left-0 top-0 h-px w-full bg-gradient-to-r from-transparent via-blue-400/40 to-transparent opacity-0 transition-opacity duration-500 group-hover:opacity-100" />

                        <div className="flex items-center justify-between">

                            <div className="flex items-center gap-3">

                                <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-blue-400/10 text-sm">
                                    🏔️
                                </div>

                                <div>
                                    <p className="font-semibold text-slate-200">
                                        Elevation Contribution
                                    </p>

                                    <p className="text-[9px] uppercase tracking-widest text-slate-700">
                                        Terrain altitude
                                    </p>
                                </div>

                            </div>

                            <span className="rounded-full border border-blue-400/10 bg-blue-400/[0.05] px-2.5 py-1 text-[9px] font-bold text-blue-400">
                                DEM
                            </span>

                        </div>

                        <div className="mt-5 space-y-3">

                            <div>
                                <div className="mb-1.5 flex justify-between text-[11px]">
                                    <span className="text-slate-500">
                                        ≥ 5000 m
                                    </span>
                                    <span className="font-bold text-red-400">
                                        +40
                                    </span>
                                </div>

                                <div className="h-1 overflow-hidden rounded-full bg-white/5">
                                    <div className="h-full w-full rounded-full bg-red-400/70" />
                                </div>
                            </div>

                            <div>
                                <div className="mb-1.5 flex justify-between text-[11px]">
                                    <span className="text-slate-500">
                                        3500 – 4999 m
                                    </span>
                                    <span className="font-bold text-red-400">
                                        +30
                                    </span>
                                </div>

                                <div className="h-1 overflow-hidden rounded-full bg-white/5">
                                    <div className="h-full w-3/4 rounded-full bg-red-400/60" />
                                </div>
                            </div>

                            <div>
                                <div className="mb-1.5 flex justify-between text-[11px]">
                                    <span className="text-slate-500">
                                        2000 – 3499 m
                                    </span>
                                    <span className="font-bold text-yellow-400">
                                        +20
                                    </span>
                                </div>

                                <div className="h-1 overflow-hidden rounded-full bg-white/5">
                                    <div className="h-full w-1/2 rounded-full bg-yellow-400/60" />
                                </div>
                            </div>

                            <div>
                                <div className="mb-1.5 flex justify-between text-[11px]">
                                    <span className="text-slate-500">
                                        1000 – 1999 m
                                    </span>
                                    <span className="font-bold text-yellow-400">
                                        +10
                                    </span>
                                </div>

                                <div className="h-1 overflow-hidden rounded-full bg-white/5">
                                    <div className="h-full w-1/4 rounded-full bg-yellow-400/50" />
                                </div>
                            </div>

                            <div>
                                <div className="mb-1.5 flex justify-between text-[11px]">
                                    <span className="text-slate-500">
                                        &lt; 1000 m
                                    </span>
                                    <span className="font-bold text-emerald-400">
                                        +0
                                    </span>
                                </div>

                                <div className="h-1 overflow-hidden rounded-full bg-white/5">
                                    <div className="h-full w-[4%] rounded-full bg-emerald-400/60" />
                                </div>
                            </div>

                        </div>

                    </div>

                </div>


                {/* =====================================================
                   RISK CLASSIFICATION
                ====================================================== */}

                <div className="mt-5 rounded-2xl border border-white/5 bg-black/20 p-5">

                    <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">

                        <div>

                            <p className="text-[9px] font-bold uppercase tracking-[0.2em] text-slate-500">
                                Risk Classification
                            </p>

                            <p className="mt-1 text-xs text-slate-700">
                                Combined terrain score determines the final category
                            </p>

                        </div>

                        <div className="text-[9px] font-semibold text-slate-700">
                            SCORE RANGE: 0 — 100
                        </div>

                    </div>

                    <div className="mt-5 grid gap-3 sm:grid-cols-3">

                        {/* LOW */}
                        <div className="group relative overflow-hidden rounded-xl border border-emerald-400/10 bg-emerald-400/[0.025] p-4 transition-all duration-300 hover:-translate-y-1 hover:border-emerald-400/30 hover:bg-emerald-400/[0.05]">

                            <div className="absolute right-3 top-3 h-2 w-2 rounded-full bg-emerald-400/60 shadow-[0_0_12px_rgba(52,211,153,.4)]" />

                            <p className="text-xs font-black tracking-wider text-emerald-400">
                                LOW
                            </p>

                            <p className="mt-1 text-[10px] text-slate-600">
                                Score below 40
                            </p>

                            <div className="mt-4 h-1 overflow-hidden rounded-full bg-white/5">
                                <div className="h-full w-[35%] rounded-full bg-emerald-400/70" />
                            </div>

                        </div>


                        {/* MEDIUM */}
                        <div className="group relative overflow-hidden rounded-xl border border-yellow-400/10 bg-yellow-400/[0.025] p-4 transition-all duration-300 hover:-translate-y-1 hover:border-yellow-400/30 hover:bg-yellow-400/[0.05]">

                            <div className="absolute right-3 top-3 h-2 w-2 rounded-full bg-yellow-400/60 shadow-[0_0_12px_rgba(250,204,21,.4)]" />

                            <p className="text-xs font-black tracking-wider text-yellow-400">
                                MEDIUM
                            </p>

                            <p className="mt-1 text-[10px] text-slate-600">
                                Score 40–69
                            </p>

                            <div className="mt-4 h-1 overflow-hidden rounded-full bg-white/5">
                                <div className="h-full w-[60%] rounded-full bg-yellow-400/70" />
                            </div>

                        </div>


                        {/* HIGH */}
                        <div className="group relative overflow-hidden rounded-xl border border-red-400/10 bg-red-400/[0.025] p-4 transition-all duration-300 hover:-translate-y-1 hover:border-red-400/30 hover:bg-red-400/[0.05]">

                            <div className="absolute right-3 top-3 h-2 w-2 rounded-full bg-red-400/70 shadow-[0_0_12px_rgba(248,113,113,.5)] animate-pulse" />

                            <p className="text-xs font-black tracking-wider text-red-400">
                                HIGH
                            </p>

                            <p className="mt-1 text-[10px] text-slate-600">
                                Score 70–100
                            </p>

                            <div className="mt-4 h-1 overflow-hidden rounded-full bg-white/5">
                                <div className="h-full w-[90%] rounded-full bg-red-400/70" />
                            </div>

                        </div>

                    </div>

                </div>


                {/* =====================================================
                   EXPLAINABILITY NOTE
                ====================================================== */}

                <div className="mt-5 flex gap-3 rounded-xl border border-cyan-400/10 bg-cyan-400/[0.025] p-4">

                    <div className="mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-cyan-400/10 text-xs">
                        💡
                    </div>

                    <div>

                        <p className="text-[10px] font-bold uppercase tracking-[0.15em] text-cyan-500">
                            Why this matters
                        </p>

                        <p className="mt-1 text-[10px] leading-5 text-slate-600">
                            Each risk score is traceable to measurable terrain
                            characteristics. This makes the indicator easier to
                            interpret, audit, and communicate than a completely
                            opaque prediction.
                        </p>

                    </div>

                </div>


                {/* =====================================================
                   DISCLAIMER
                ====================================================== */}

                <div className="mt-5 flex gap-2 text-[9px] leading-5 text-slate-700">

                    <span className="shrink-0 text-slate-600">
                        ⚠
                    </span>

                    <p>
                        This terrain-based susceptibility indicator is intended for
                        exploratory geospatial analysis. It should not be interpreted
                        as a confirmed landslide prediction or a replacement for
                        professional geological assessment.
                    </p>

                </div>

            </div>

        </section>

            </div>

        </main>
    );
}