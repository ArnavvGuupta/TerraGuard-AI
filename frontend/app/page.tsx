"use client";

import Link from "next/link";
import { useEffect } from "react";
import {
  ArrowRight,
  Brain,
  Mountain,
  Satellite,
  ShieldAlert,
  Sparkles,
  Database,
  Map,
  Activity,
  ChevronRight,
} from "lucide-react";




const features = [
  {
    icon: Mountain,
    title: "DEM Terrain Analysis",
    description:
      "Analyze elevation, slope and aspect to understand the physical characteristics of mountainous terrain.",
  },
  {
    icon: Satellite,
    title: "Geospatial Intelligence",
    description:
      "Combine satellite and terrain data to identify environmental patterns and areas requiring attention.",
  },
  {
    icon: Brain,
    title: "AI Risk Analysis",
    description:
      "Machine-learning models transform terrain and environmental features into actionable risk intelligence.",
  },
  {
    icon: Sparkles,
    title: "AI Risk Assistant",
    description:
      "Ask questions about terrain conditions and receive contextual explanations and recommendations.",
  },
];

const workflow = [
  {
    number: "01",
    title: "Collect",
    description: "DEM, satellite and geospatial data",
    icon: Database,
  },
  {
    number: "02",
    title: "Analyze",
    description: "Extract terrain and environmental features",
    icon: Activity,
  },
  {
    number: "03",
    title: "Predict",
    description: "Estimate terrain susceptibility with AI/ML",
    icon: Brain,
  },
  {
    number: "04",
    title: "Understand",
    description: "Turn complex analysis into clear insights",
    icon: ShieldAlert,
  },
];

export default function HomePage() {
    useEffect(() => {
    const handleSmoothScroll = (e: MouseEvent) => {
      const target = e.currentTarget as HTMLAnchorElement;
      const href = target.getAttribute("href");

      if (!href?.startsWith("#")) return;

      const element = document.querySelector(href);

      if (element) {
        e.preventDefault();

        element.scrollIntoView({
          behavior: "smooth",
          block: "start",
        });

        // Update URL without causing another jump
        window.history.pushState(null, "", href);
      }
    };

    const links = document.querySelectorAll<HTMLAnchorElement>(
      'a[href^="#"]'
    );

    links.forEach((link) => {
      link.addEventListener("click", handleSmoothScroll);
    });

    return () => {
      links.forEach((link) => {
        link.removeEventListener("click", handleSmoothScroll);
      });
    };
  }, []);
  return (
    <main className="min-h-screen overflow-hidden bg-[#020617] text-slate-100">
      {/* Background */}
      <div className="pointer-events-none fixed inset-0 -z-0">
        <div className="absolute left-[-180px] top-[-180px] h-[500px] w-[500px] rounded-full bg-cyan-500/10 blur-[120px]" />
        <div className="absolute right-[-200px] top-[30%] h-[500px] w-[500px] rounded-full bg-blue-600/10 blur-[120px]" />
        <div className="absolute bottom-[-250px] left-[35%] h-[500px] w-[500px] rounded-full bg-indigo-600/10 blur-[120px]" />

        <div
          className="absolute inset-0 opacity-[0.035]"
          style={{
            backgroundImage:
              "linear-gradient(rgba(34,211,238,.7) 1px, transparent 1px), linear-gradient(90deg, rgba(34,211,238,.7) 1px, transparent 1px)",
            backgroundSize: "50px 50px",
          }}
        />
      </div>

      {/* Navbar */}
      <nav className="relative z-20 mx-auto flex max-w-7xl items-center justify-between px-6 py-6 lg:px-8">
        <Link href="/" className="group flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl border border-cyan-400/20 bg-cyan-400/10 shadow-[0_0_30px_rgba(34,211,238,0.12)]">
            <Mountain className="h-5 w-5 text-cyan-300" />
          </div>

          <div>
            <div className="text-sm font-bold tracking-[0.18em] text-white">
              TERRAIN
            </div>
            <div className="text-[10px] font-medium tracking-[0.3em] text-cyan-400">
              INTELLIGENCE
            </div>
          </div>
        </Link>

        <div className="hidden items-center gap-8 md:flex">
          <a
            href="#capabilities"
            className="text-sm text-slate-400 transition hover:text-cyan-300"
          >
            Capabilities
          </a>

          <a
            href="#workflow"
            className="text-sm text-slate-400 transition hover:text-cyan-300"
          >
            How it works
          </a>

          <a
            href="#technology"
            className="text-sm text-slate-400 transition hover:text-cyan-300"
          >
            Technology
          </a>
        </div>

        <div className="flex items-center gap-3">
          <Link
            href="/sign_in"
            className="hidden rounded-xl px-4 py-2.5 text-sm font-medium text-slate-300 transition hover:bg-white/5 hover:text-white sm:block"
          >
            Sign in
          </Link>

          <Link
            href="/sign_in"
            className="group flex items-center gap-2 rounded-xl border border-cyan-400/30 bg-cyan-400/10 px-4 py-2.5 text-sm font-semibold text-cyan-200 transition hover:border-cyan-300/50 hover:bg-cyan-400/20"
          >
            Explore Platform
            <ArrowRight className="h-4 w-4 transition group-hover:translate-x-1" />
          </Link>
        </div>
      </nav>

      {/* Hero */}
      <section className="relative z-10 mx-auto max-w-7xl px-6 pb-24 pt-16 lg:px-8 lg:pb-32 lg:pt-24">
        <div className="grid items-center gap-16 lg:grid-cols-[1.05fr_.95fr]">
          {/* Hero copy */}
          <div>
            <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-cyan-400/20 bg-cyan-400/[0.07] px-3 py-1.5 text-xs font-medium uppercase tracking-[0.18em] text-cyan-300">
              <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-cyan-300" />
              AI-powered geospatial intelligence
            </div>

            <h1 className="max-w-4xl text-5xl font-semibold leading-[1.05] tracking-tight text-white sm:text-6xl lg:text-7xl">
              Understand terrain.
              <span className="block bg-gradient-to-r from-cyan-300 via-sky-400 to-blue-500 bg-clip-text text-transparent">
                Detect risk.
              </span>
            </h1>

            <p className="mt-7 max-w-2xl text-lg leading-8 text-slate-400 sm:text-xl">
              Transform terrain, satellite and environmental data into
              intelligent insights for understanding landslide susceptibility
              across mountainous regions.
            </p>

            <div className="mt-9 flex flex-col gap-3 sm:flex-row">
              <Link
                href="/sign_in"
                className="group flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-cyan-400 to-blue-500 px-6 py-3.5 text-sm font-bold text-slate-950 shadow-[0_0_40px_rgba(34,211,238,0.15)] transition hover:scale-[1.02] hover:shadow-[0_0_50px_rgba(34,211,238,0.25)]"
              >
                Launch Terrain Intelligence
                <ArrowRight className="h-4 w-4 transition group-hover:translate-x-1" />
              </Link>

              <a
                href="#capabilities"
                className="flex items-center justify-center gap-2 rounded-xl border border-white/10 bg-white/[0.03] px-6 py-3.5 text-sm font-semibold text-slate-200 backdrop-blur-xl transition hover:border-cyan-400/20 hover:bg-white/[0.06]"
              >
                Explore capabilities
                <ChevronRight className="h-4 w-4" />
              </a>
            </div>

            <div className="mt-10 flex flex-wrap gap-x-7 gap-y-3 text-xs uppercase tracking-[0.18em] text-slate-500">
              <span>DEM Analysis</span>
              <span>•</span>
              <span>Satellite Data</span>
              <span>•</span>
              <span>AI / ML</span>
            </div>
          </div>

          {/* Hero visual */}
          <div className="relative">
            <div className="absolute -inset-6 rounded-[2rem] bg-cyan-400/5 blur-3xl" />

            <div className="relative overflow-hidden rounded-[2rem] border border-white/10 bg-slate-950/70 shadow-2xl backdrop-blur-xl">
              {/* Fake map preview */}
              <div
                className="relative h-[420px] overflow-hidden"
                style={{
                  background:
                    "radial-gradient(circle at 35% 35%, rgba(34,211,238,.18), transparent 22%), radial-gradient(circle at 70% 65%, rgba(59,130,246,.20), transparent 25%), linear-gradient(135deg,#07111f,#020617)",
                }}
              >
                <div
                  className="absolute inset-0 opacity-30"
                  style={{
                    backgroundImage:
                      "linear-gradient(rgba(148,163,184,.18) 1px, transparent 1px), linear-gradient(90deg, rgba(148,163,184,.18) 1px, transparent 1px)",
                    backgroundSize: "42px 42px",
                  }}
                />

                {/* Terrain-like contours */}
                <div className="absolute left-[8%] top-[12%] h-[75%] w-[80%] rotate-[-12deg] rounded-[45%] border border-cyan-400/20" />
                <div className="absolute left-[17%] top-[19%] h-[60%] w-[65%] rotate-[-12deg] rounded-[45%] border border-cyan-400/20" />
                <div className="absolute left-[27%] top-[27%] h-[45%] w-[45%] rotate-[-12deg] rounded-[45%] border border-cyan-400/20" />

                {/* Risk zones */}
                <div className="absolute left-[24%] top-[27%] h-28 w-36 rounded-full bg-red-500/15 blur-2xl" />
                <div className="absolute right-[18%] top-[46%] h-24 w-32 rounded-full bg-yellow-400/10 blur-2xl" />

                {/* Map marker */}
                <div className="absolute left-[34%] top-[38%]">
                  <div className="absolute -inset-3 animate-ping rounded-full bg-red-400/20" />
                  <div className="relative h-4 w-4 rounded-full border-2 border-white bg-red-500 shadow-[0_0_20px_rgba(239,68,68,.8)]" />
                </div>

                {/* Status */}
                <div className="absolute left-5 top-5 rounded-xl border border-white/10 bg-slate-950/80 px-4 py-3 backdrop-blur-xl">
                  <div className="flex items-center gap-2">
                    <span className="h-2 w-2 animate-pulse rounded-full bg-emerald-400" />
                    <span className="text-[10px] font-semibold uppercase tracking-[0.2em] text-emerald-300">
                      Intelligence active
                    </span>
                  </div>
                  <div className="mt-1 text-xs text-slate-500">
                    Himalayan terrain monitoring
                  </div>
                </div>

                {/* Bottom card */}
                <div className="absolute bottom-5 left-5 right-5 rounded-xl border border-white/10 bg-slate-950/85 p-4 backdrop-blur-xl">
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="text-[10px] uppercase tracking-[0.2em] text-slate-500">
                        Terrain assessment
                      </div>
                      <div className="mt-1 text-lg font-semibold text-white">
                        Multi-factor risk intelligence
                      </div>
                    </div>

                    <Map className="h-6 w-6 text-cyan-300" />
                  </div>

                  <div className="mt-4 grid grid-cols-3 gap-2">
                    <div className="rounded-lg bg-white/[0.04] p-2">
                      <div className="text-[9px] uppercase text-slate-500">
                        Elevation
                      </div>
                      <div className="mt-1 text-sm text-slate-200">DEM</div>
                    </div>

                    <div className="rounded-lg bg-white/[0.04] p-2">
                      <div className="text-[9px] uppercase text-slate-500">
                        Terrain
                      </div>
                      <div className="mt-1 text-sm text-slate-200">Slope</div>
                    </div>

                    <div className="rounded-lg bg-white/[0.04] p-2">
                      <div className="text-[9px] uppercase text-slate-500">
                        Intelligence
                      </div>
                      <div className="mt-1 text-sm text-slate-200">AI / ML</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Workflow */}
      <section
        id="workflow"
        className="relative z-10 border-y border-white/[0.06] bg-white/[0.015]"
      >
        <div className="mx-auto max-w-7xl px-6 py-20 lg:px-8">
          <div className="mb-12 max-w-2xl">
            <div className="text-xs font-semibold uppercase tracking-[0.25em] text-cyan-400">
              From data to intelligence
            </div>

            <h2 className="mt-4 text-3xl font-semibold tracking-tight text-white sm:text-4xl">
              A complete geospatial intelligence pipeline.
            </h2>
          </div>

          <div className="grid gap-4 md:grid-cols-4">
            {workflow.map((item) => {
              const Icon = item.icon;

              return (
                <div
                  key={item.number}
                  className="group rounded-2xl border border-white/[0.07] bg-slate-950/50 p-6 transition duration-300 hover:-translate-y-1 hover:border-cyan-400/20 hover:bg-cyan-400/[0.03]"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-semibold tracking-[0.2em] text-cyan-400">
                      {item.number}
                    </span>

                    <Icon className="h-5 w-5 text-slate-600 transition group-hover:text-cyan-300" />
                  </div>

                  <h3 className="mt-7 text-lg font-semibold text-white">
                    {item.title}
                  </h3>

                  <p className="mt-2 text-sm leading-6 text-slate-500">
                    {item.description}
                  </p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Capabilities */}
      <section
        id="capabilities"
        className="relative z-10 mx-auto max-w-7xl px-6 py-24 lg:px-8"
      >
        <div className="mx-auto max-w-2xl text-center">
          <div className="text-xs font-semibold uppercase tracking-[0.25em] text-cyan-400">
            Platform capabilities
          </div>

          <h2 className="mt-4 text-3xl font-semibold tracking-tight text-white sm:text-4xl">
            Built for terrain intelligence.
          </h2>

          <p className="mt-5 text-slate-400">
            Bring multiple geospatial signals together and turn them into
            understandable, decision-ready information.
          </p>
        </div>

        <div className="mt-14 grid gap-5 md:grid-cols-2">
          {features.map((feature) => {
            const Icon = feature.icon;

            return (
              <div
                key={feature.title}
                className="group rounded-2xl border border-white/[0.07] bg-white/[0.025] p-7 backdrop-blur-xl transition duration-300 hover:-translate-y-1 hover:border-cyan-400/20 hover:bg-cyan-400/[0.035]"
              >
                <div className="flex h-11 w-11 items-center justify-center rounded-xl border border-cyan-400/15 bg-cyan-400/[0.07]">
                  <Icon className="h-5 w-5 text-cyan-300" />
                </div>

                <h3 className="mt-6 text-xl font-semibold text-white">
                  {feature.title}
                </h3>

                <p className="mt-3 max-w-xl text-sm leading-7 text-slate-400">
                  {feature.description}
                </p>

                <div className="mt-6 flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.18em] text-cyan-400 opacity-0 transition group-hover:opacity-100">
                  Explore capability
                  <ArrowRight className="h-3.5 w-3.5" />
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {/* Problem / Solution */}
      <section className="relative z-10 border-y border-white/[0.06] bg-white/[0.015]">
        <div className="mx-auto grid max-w-7xl gap-14 px-6 py-24 lg:grid-cols-2 lg:px-8">
          <div>
            <div className="text-xs font-semibold uppercase tracking-[0.25em] text-slate-500">
              The challenge
            </div>

            <h2 className="mt-4 text-3xl font-semibold tracking-tight text-white">
              Mountain environments are complex.
            </h2>

            <p className="mt-6 leading-8 text-slate-400">
              Steep terrain, changing environmental conditions and limited
              ground-level monitoring make it difficult to understand where
              terrain may be more susceptible to landslides.
            </p>
          </div>

          <div className="rounded-2xl border border-cyan-400/10 bg-cyan-400/[0.025] p-7">
            <div className="flex items-center gap-3">
              <div className="h-2 w-2 rounded-full bg-cyan-300" />
              <span className="text-xs font-semibold uppercase tracking-[0.2em] text-cyan-300">
                Our approach
              </span>
            </div>

            <p className="mt-5 text-xl leading-8 text-slate-200">
              Combine geospatial data, terrain analysis and machine learning
              to create a clearer picture of terrain susceptibility.
            </p>

            <div className="mt-7 grid gap-3 sm:grid-cols-2">
              {[
                "Terrain-derived features",
                "Satellite observations",
                "Machine learning",
                "AI explanations",
              ].map((item) => (
                <div
                  key={item}
                  className="rounded-xl border border-white/[0.06] bg-black/20 px-4 py-3 text-sm text-slate-300"
                >
                  {item}
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Technology */}
      <section
        id="technology"
        className="relative z-10 mx-auto max-w-7xl px-6 py-24 lg:px-8"
      >
        <div className="grid items-center gap-12 lg:grid-cols-[.8fr_1.2fr]">
          <div>
            <div className="text-xs font-semibold uppercase tracking-[0.25em] text-cyan-400">
              Technology
            </div>

            <h2 className="mt-4 text-3xl font-semibold tracking-tight text-white sm:text-4xl">
              Modern tools. Geospatial intelligence.
            </h2>

            <p className="mt-5 leading-7 text-slate-400">
              A full-stack architecture connecting geospatial processing,
              machine learning, APIs and an interactive intelligence
              interface.
            </p>
          </div>

          <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
            {[
              "Next.js",
              "TypeScript",
              "FastAPI",
              "Python",
              "XGBoost",
              "Raster Processing",
              "DEM Data",
              "Satellite Data",
              "AI Assistant",
            ].map((tech) => (
              <div
                key={tech}
                className="rounded-xl border border-white/[0.07] bg-white/[0.025] px-4 py-5 text-center text-sm font-medium text-slate-300 transition hover:border-cyan-400/20 hover:text-cyan-300"
              >
                {tech}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="relative z-10 mx-auto max-w-5xl px-6 pb-24 text-center lg:px-8">
        <div className="relative overflow-hidden rounded-[2rem] border border-cyan-400/15 bg-gradient-to-br from-cyan-400/[0.08] via-blue-500/[0.05] to-transparent px-6 py-16 sm:px-12">
          <div className="absolute left-1/2 top-0 h-40 w-80 -translate-x-1/2 rounded-full bg-cyan-400/10 blur-[80px]" />

          <div className="relative">
            <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl border border-cyan-400/20 bg-cyan-400/10">
              <Mountain className="h-6 w-6 text-cyan-300" />
            </div>

            <h2 className="mt-7 text-3xl font-semibold text-white sm:text-4xl">
              Explore the terrain.
              <span className="block text-cyan-300">
                Understand the risk.
              </span>
            </h2>

            <p className="mx-auto mt-5 max-w-xl text-slate-400">
              Enter the Terrain Intelligence platform and explore
              data-driven terrain analysis.
            </p>

            <Link
              href="/sign_in"
              className="group mx-auto mt-8 flex w-fit items-center gap-2 rounded-xl bg-white px-6 py-3.5 text-sm font-bold text-slate-950 transition hover:scale-[1.02]"
            >
              Launch Platform
              <ArrowRight className="h-4 w-4 transition group-hover:translate-x-1" />
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative z-10 border-t border-white/[0.06]">
        <div className="mx-auto flex max-w-7xl flex-col gap-4 px-6 py-8 text-xs text-slate-500 sm:flex-row sm:items-center sm:justify-between lg:px-8">
          <div className="flex items-center gap-2">
            <Mountain className="h-4 w-4 text-cyan-400" />
            <span>Terrain Intelligence</span>
          </div>

          <div>
            AI-powered geospatial intelligence for mountainous terrain
          </div>
        </div>
      </footer>
    </main>
  );
}