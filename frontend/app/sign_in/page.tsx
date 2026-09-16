"use client";

import Link from "next/link";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { signInWithEmailAndPassword, signInWithPopup, GoogleAuthProvider } from "firebase/auth";
import { auth } from "@/app/lib/firebase";
import { motion, AnimatePresence } from "framer-motion";
import {
  ArrowLeft,
  ArrowRight,
  Lock,
  Mail,
  Mountain,
  ShieldCheck,
} from "lucide-react";

export default function SignInPage() {
  const router = useRouter();
  const googleProvider = new GoogleAuthProvider()

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSignIn = async (e: React.FormEvent) => {
    e.preventDefault();

    setError("");

    if (!email.trim()) {
      setError("Please enter your email.");
      return;
    }

    if (!password) {
      setError("Please enter your password.");
      return;
    }

    try {
      setLoading(true);

      // Authenticate user with Firebase
      await signInWithEmailAndPassword(
        auth,
        email,
        password
      );

      // Authentication successful → Dashboard
      router.push("/dashboard");
    } catch (err: any) {
      console.error("Sign in error:", err);

      if (
        err.code === "auth/invalid-credential" ||
        err.code === "auth/user-not-found" ||
        err.code === "auth/wrong-password"
      ) {
        setError("Invalid email or password.");
      } else if (err.code === "auth/too-many-requests") {
        setError(
          "Too many failed attempts. Please try again later."
        );
      } else if (err.code === "auth/invalid-email") {
        setError("Please enter a valid email address.");
      } else {
        setError("Unable to sign in. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  };
  const handleGoogleSignIn = async () => {
    try {
      setError("");
      setLoading(true);

      await signInWithPopup(auth, googleProvider);

      router.push("/dashboard");
    } catch (err: any) {
      console.error("Google sign in error:", err);

      if (err.code === "auth/popup-closed-by-user") {
        setError("Google sign-in was cancelled.");
      } else if (err.code === "auth/popup-blocked") {
        setError("Please allow popups to sign in with Google.");
      } else {
        setError("Unable to sign in with Google. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  };

  const fieldVariants = {
    hidden: { opacity: 0, y: 16 },
    visible: (i: number) => ({
      opacity: 1,
      y: 0,
      transition: { delay: 0.08 * i, duration: 0.5, ease: "easeOut" as const, },
    }),
  };

  return (
    <main className="relative min-h-screen overflow-hidden bg-[#020617] text-slate-100">
      {/* Background */}
      <div className="pointer-events-none absolute inset-0">
        <motion.div
          className="absolute left-[-180px] top-[-180px] h-[500px] w-[500px] rounded-full bg-cyan-500/10 blur-[120px]"
          animate={{
            x: [0, 40, 0],
            y: [0, 30, 0],
            scale: [1, 1.1, 1],
          }}
          transition={{ duration: 10, repeat: Infinity, ease: "easeInOut" }}
        />
        <motion.div
          className="absolute bottom-[-200px] right-[-150px] h-[500px] w-[500px] rounded-full bg-blue-600/10 blur-[120px]"
          animate={{
            x: [0, -40, 0],
            y: [0, -30, 0],
            scale: [1, 1.15, 1],
          }}
          transition={{ duration: 12, repeat: Infinity, ease: "easeInOut" }}
        />

        <motion.div
          className="absolute inset-0 opacity-[0.035]"
          style={{
            backgroundImage:
              "linear-gradient(rgba(34,211,238,.7) 1px, transparent 1px), linear-gradient(90deg, rgba(34,211,238,.7) 1px, transparent 1px)",
            backgroundSize: "50px 50px",
          }}
          animate={{ backgroundPosition: ["0px 0px", "50px 50px"] }}
          transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
        />

        {/* Floating particles for extra polish */}
        {[...Array(6)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute h-1 w-1 rounded-full bg-cyan-400/40"
            style={{
              left: `${15 + i * 15}%`,
              top: `${20 + (i % 3) * 25}%`,
            }}
            animate={{
              y: [0, -20, 0],
              opacity: [0.2, 0.6, 0.2],
            }}
            transition={{
              duration: 4 + i,
              repeat: Infinity,
              ease: "easeInOut",
              delay: i * 0.5,
            }}
          />
        ))}
      </div>

      {/* Back */}
      <motion.div
        initial={{ opacity: 0, x: -10 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.5 }}
      >
        <Link
          href="/"
          className="absolute left-6 top-6 z-20 flex items-center gap-2 text-sm text-slate-500 transition hover:text-cyan-300"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to website
        </Link>
      </motion.div>

      <div className="relative z-10 flex min-h-screen items-center justify-center px-6 py-16">
        <div className="w-full max-w-md">

          {/* Logo */}
          <motion.div
            className="mb-8 text-center"
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, ease: "easeOut" }}
          >
            <motion.div
              className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl border border-cyan-400/20 bg-cyan-400/10 shadow-[0_0_40px_rgba(34,211,238,.12)]"
              animate={{
                boxShadow: [
                  "0 0 20px rgba(34,211,238,0.08)",
                  "0 0 40px rgba(34,211,238,0.28)",
                  "0 0 20px rgba(34,211,238,0.08)",
                ],
                rotate: [0, -3, 3, 0],
              }}
              transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
            >
              <Mountain className="h-7 w-7 text-cyan-300" />
            </motion.div>

            <div className="mt-5 text-sm font-bold tracking-[0.2em] text-white">
              TERRAIN INTELLIGENCE
            </div>

            <p className="mt-2 text-sm text-slate-500">
              Access your geospatial intelligence workspace
            </p>
          </motion.div>

          {/* Card */}
          <motion.div
            className="rounded-[2rem] border border-white/10 bg-slate-950/70 p-7 shadow-2xl backdrop-blur-xl sm:p-8"
            initial={{ opacity: 0, y: 24, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            transition={{ duration: 0.6, ease: "easeOut", delay: 0.1 }}
          >

            <motion.div
              className="mb-7"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.2, duration: 0.5 }}
            >
              <h1 className="text-2xl font-semibold text-white">
                Welcome back
              </h1>

              <p className="mt-2 text-sm text-slate-500">
                Sign in to continue to Terrain Intelligence.
              </p>
            </motion.div>

            <form onSubmit={handleSignIn} className="space-y-5">

              {/* Email */}
              <motion.div
                custom={0}
                variants={fieldVariants}
                initial="hidden"
                animate="visible"
              >
                <label className="mb-2 block text-xs font-semibold uppercase tracking-[0.15em] text-slate-400">
                  Email
                </label>

                <div className="relative">
                  <Mail className="absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-600" />

                  <motion.input
                    type="email"
                    placeholder="you@example.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    whileFocus={{
                      scale: 1.01,
                      boxShadow: "0 0 0 3px rgba(34,211,238,0.15)",
                    }}
                    transition={{ duration: 0.2 }}
                    className="w-full rounded-xl border border-white/10 bg-white/[0.035] py-3.5 pl-11 pr-4 text-sm text-white outline-none transition placeholder:text-slate-600 focus:border-cyan-400/40 focus:bg-cyan-400/[0.03]"
                  />
                </div>
              </motion.div>

              {/* Password */}
              <motion.div
                custom={1}
                variants={fieldVariants}
                initial="hidden"
                animate="visible"
              >
                <div className="mb-2 flex items-center justify-between">
                  <label className="text-xs font-semibold uppercase tracking-[0.15em] text-slate-400">
                    Password
                  </label>

                  <motion.button
                    type="button"
                    whileHover={{ x: 2 }}
                    className="text-xs text-cyan-400 transition hover:text-cyan-300"
                  >
                    Forgot password?
                  </motion.button>
                </div>

                <div className="relative">
                  <Lock className="absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-600" />

                  <motion.input
                    type="password"
                    placeholder="••••••••"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    whileFocus={{
                      scale: 1.01,
                      boxShadow: "0 0 0 3px rgba(34,211,238,0.15)",
                    }}
                    transition={{ duration: 0.2 }}
                    className="w-full rounded-xl border border-white/10 bg-white/[0.035] py-3.5 pl-11 pr-4 text-sm text-white outline-none transition placeholder:text-slate-600 focus:border-cyan-400/40 focus:bg-cyan-400/[0.03]"
                  />
                </div>
              </motion.div>

              {/* Error */}
              <AnimatePresence>
                {error && (
                  <motion.div
                    initial={{ opacity: 0, y: -8, height: 0 }}
                    animate={{ opacity: 1, y: 0, height: "auto" }}
                    exit={{ opacity: 0, y: -8, height: 0 }}
                    transition={{ duration: 0.25 }}
                    className="overflow-hidden"
                  >
                    <motion.div
                      animate={{ x: [0, -6, 6, -4, 4, 0] }}
                      transition={{ duration: 0.4 }}
                      className="rounded-xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-300"
                    >
                      {error}
                    </motion.div>
                  </motion.div>
                )}
              </AnimatePresence>

              {/* Submit */}
              <motion.button
                type="submit"
                disabled={loading}
                custom={2}
                variants={fieldVariants}
                initial="hidden"
                animate="visible"
                whileHover={{
                  scale: 1.02,
                  boxShadow: "0 0 35px rgba(34,211,238,.25)",
                }}
                whileTap={{ scale: 0.98 }}
                className="group relative flex w-full items-center justify-center gap-2 overflow-hidden rounded-xl bg-gradient-to-r from-cyan-400 to-blue-500 py-3.5 text-sm font-bold text-slate-950 transition disabled:cursor-not-allowed disabled:opacity-60"
              >
                <motion.span
                  className="pointer-events-none absolute inset-0 -translate-x-full bg-gradient-to-r from-transparent via-white/40 to-transparent"
                  animate={{ translateX: ["-100%", "200%"] }}
                  transition={{ duration: 2.5, repeat: Infinity, ease: "easeInOut" }}
                />

                {loading ? (
                  <motion.span className="relative flex items-center gap-2">
                    <motion.span
                      className="h-4 w-4 rounded-full border-2 border-slate-950/30 border-t-slate-950"
                      animate={{ rotate: 360 }}
                      transition={{ duration: 0.7, repeat: Infinity, ease: "linear" }}
                    />
                    Signing in...
                  </motion.span>
                ) : (
                  <span className="relative flex items-center gap-2">
                    Sign In
                    <ArrowRight className="h-4 w-4 transition group-hover:translate-x-1" />
                  </span>
                )}
              </motion.button>
            </form>

            {/* Divider */}
            <motion.div
              className="my-6 flex items-center gap-3"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.45, duration: 0.5 }}
            >
              <div className="h-px flex-1 bg-white/[0.07]" />
              <span className="text-xs text-slate-600">OR</span>
              <div className="h-px flex-1 bg-white/[0.07]" />
            </motion.div>

            {/* Google */}
            <motion.button
              onClick={handleGoogleSignIn}

              type="button"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5, duration: 0.5 }}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="flex w-full items-center justify-center gap-3 rounded-xl border border-white/10 bg-white/[0.025] py-3.5 text-sm font-semibold text-slate-300 transition hover:border-white/20 hover:bg-white/[0.05]"
            >
              <span className="flex h-5 w-5 items-center justify-center rounded-full bg-white text-xs font-bold text-slate-900">
                G
              </span>

              Continue with Google
            </motion.button>


            {/* Signup */}
            <motion.p
              className="mt-7 text-center text-sm text-slate-500"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.55, duration: 0.5 }}
            >
              Don't have an account?{" "}

              <Link
                href="/sign_up"
                className="font-semibold text-cyan-400 transition hover:text-cyan-300"
              >
                Create one
              </Link>
            </motion.p>
          </motion.div>

          {/* Security */}
          <motion.div
            className="mt-6 flex items-center justify-center gap-2 text-xs text-slate-600"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.65, duration: 0.5 }}
          >
            <motion.span
              animate={{ opacity: [1, 0.4, 1] }}
              transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
            >
              <ShieldCheck className="h-4 w-4" />
            </motion.span>
            Secure authentication powered by Firebase
          </motion.div>

        </div>
      </div>
    </main>
  );
}