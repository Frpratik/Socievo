"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { 
  Users, 
  Sparkles, 
  Clock, 
  ShieldCheck, 
  ArrowRight, 
  TrendingDown, 
  CheckCircle2, 
  Building,
  Activity,
  Layers,
  Wrench,
  Percent
} from "lucide-react";
import { fetchHealthStatus, HealthResponse } from "@/lib/api";

export default function HomePage() {
  const [backendHealth, setBackendHealth] = useState<HealthResponse | null>(null);
  const [loadingHealth, setLoadingHealth] = useState(true);

  useEffect(() => {
    fetchHealthStatus()
      .then((data) => {
        setBackendHealth(data);
        setLoadingHealth(false);
      })
      .catch(() => setLoadingHealth(false));
  }, []);

  return (
    <div className="space-y-16 pb-20">
      {/* Backend Status Bar */}
      <div className="bg-forest-950 text-surface-200 text-xs py-2 px-4 border-b border-forest-900">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="flex h-2 w-2 relative">
              <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${backendHealth?.status === 'healthy' ? 'bg-emerald-400' : 'bg-amber-400'}`}></span>
              <span className={`relative inline-flex rounded-full h-2 w-2 ${backendHealth?.status === 'healthy' ? 'bg-emerald-500' : 'bg-amber-500'}`}></span>
            </span>
            <span className="font-medium">
              Backend Status:{" "}
              {loadingHealth
                ? "Connecting to FastAPI..."
                : backendHealth
                ? `Online (${backendHealth.app_name} v${backendHealth.version} [${backendHealth.environment}])`
                : "Standby (Local mock API available)"}
            </span>
          </div>
          <div className="hidden sm:flex items-center gap-4 text-surface-400">
            <span>FastAPI • PostgreSQL • Redis • Next.js 14</span>
          </div>
        </div>
      </div>

      {/* Hero Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-6 sm:pt-12">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
          {/* Left Text */}
          <div className="lg:col-span-7 space-y-6">
            <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-forest-100 border border-forest-200 text-forest-900 text-xs font-semibold">
              <Sparkles className="w-3.5 h-3.5 text-ochre-600" />
              <span>Smarter Group-Buying for Residential Societies</span>
            </div>

            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold text-charcoal-900 leading-[1.12]">
              Book home services with neighbours.{" "}
              <span className="text-forest-800 underline decoration-ochre-400 decoration-wavy decoration-2">
                Unlock up to 50% off.
              </span>
            </h1>

            <p className="text-lg sm:text-xl text-charcoal-800/80 leading-relaxed max-w-2xl">
              Socievo aggregates service demand within your apartment society. Vendors save on multiple trips; your community secures verified professionals at unbeatable volume rates.
            </p>

            <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-4 pt-2">
              <Link
                href="/register"
                className="inline-flex justify-center items-center gap-2 px-6 py-3.5 rounded-xl bg-forest-900 hover:bg-forest-800 text-white font-semibold text-base shadow-card transition-all"
              >
                <span>Find Your Society Deals</span>
                <ArrowRight className="w-4 h-4" />
              </Link>
              <Link
                href="/deals"
                className="inline-flex justify-center items-center gap-2 px-6 py-3.5 rounded-xl bg-white hover:bg-surface-200 text-forest-900 font-semibold text-base border border-surface-300 shadow-subtle transition-all"
              >
                <span>Explore Live Deals</span>
              </Link>
            </div>

            {/* Micro Trust Indicators */}
            <div className="grid grid-cols-3 gap-4 pt-6 border-t border-surface-300/80 max-w-lg">
              <div>
                <p className="text-2xl font-bold font-display text-forest-900">40-50%</p>
                <p className="text-xs text-charcoal-800/70">Average Group Savings</p>
              </div>
              <div>
                <p className="text-2xl font-bold font-display text-forest-900">100%</p>
                <p className="text-xs text-charcoal-800/70">Verified & Insured Pros</p>
              </div>
              <div>
                <p className="text-2xl font-bold font-display text-forest-900">Zero</p>
                <p className="text-xs text-charcoal-800/70">Risk Pre-Authorization</p>
              </div>
            </div>
          </div>

          {/* Right Live Deal Card Preview */}
          <div className="lg:col-span-5">
            <div className="bg-white rounded-2xl border border-surface-300 shadow-elevated p-6 sm:p-7 relative overflow-hidden">
              <div className="absolute top-0 right-0 bg-ochre-600 text-white text-[11px] font-bold uppercase tracking-wider px-3 py-1 rounded-bl-xl flex items-center gap-1">
                <Clock className="w-3 h-3" />
                <span>28 Hours Left</span>
              </div>

              {/* Society Badge */}
              <div className="flex items-center gap-2 text-xs font-semibold text-forest-800 mb-2">
                <Building className="w-4 h-4 text-forest-700" />
                <span>Prestige Falcon City, Tower 3 & 4</span>
              </div>

              <h3 className="text-xl font-bold text-charcoal-900 mb-1">
                Master Split AC Jet Servicing & Coil Clean
              </h3>
              <p className="text-xs text-charcoal-800/70 mb-5">
                Provided by UrbanCool Climate Care (GST Verified Partner)
              </p>

              {/* Dynamic Price Display */}
              <div className="bg-forest-50/80 rounded-xl p-4 border border-forest-200/60 mb-5">
                <div className="flex items-baseline justify-between mb-1">
                  <div>
                    <span className="text-xs font-medium text-charcoal-800/70 uppercase tracking-wider">Current Tier Price</span>
                    <div className="flex items-baseline gap-2">
                      <span className="text-3xl font-extrabold font-display text-forest-900">₹600</span>
                      <span className="text-sm text-charcoal-800/50 line-through">₹999</span>
                    </div>
                  </div>
                  <div className="text-right">
                    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 font-bold text-xs">
                      <TrendingDown className="w-3.5 h-3.5" />
                      40% OFF
                    </span>
                    <p className="text-[11px] text-forest-700 font-medium mt-1">₹500 at 20 units</p>
                  </div>
                </div>

                {/* Progress bar to next tier */}
                <div className="space-y-1.5 mt-3 pt-3 border-t border-forest-200/50">
                  <div className="flex justify-between text-xs font-medium text-forest-900">
                    <span>14 Homes Committed</span>
                    <span className="text-ochre-700 font-bold">6 more for ₹500 Tier!</span>
                  </div>
                  <div className="w-full bg-forest-200/60 h-2.5 rounded-full overflow-hidden">
                    <div className="bg-forest-700 h-2.5 rounded-full transition-all duration-500" style={{ width: "70%" }}></div>
                  </div>
                </div>
              </div>

              {/* Tier breakdown preview */}
              <div className="space-y-2 mb-6">
                <p className="text-xs font-semibold text-charcoal-800 uppercase tracking-wider">
                  Transparent Volume Tiers
                </p>
                <div className="grid grid-cols-4 gap-1.5 text-center text-xs">
                  <div className="p-2 rounded-lg bg-surface-200 text-charcoal-800/70">
                    <span className="block font-bold">1–4</span>
                    <span className="text-[11px]">₹800</span>
                  </div>
                  <div className="p-2 rounded-lg bg-surface-200 text-charcoal-800/70">
                    <span className="block font-bold">5–9</span>
                    <span className="text-[11px]">₹700</span>
                  </div>
                  <div className="p-2 rounded-lg bg-forest-100 border border-forest-300 text-forest-900 font-bold">
                    <span className="block">10–19</span>
                    <span className="text-[11px]">₹600 ✓</span>
                  </div>
                  <div className="p-2 rounded-lg bg-ochre-50 border border-ochre-200 text-ochre-800 font-bold">
                    <span className="block">20+</span>
                    <span className="text-[11px]">₹500 ★</span>
                  </div>
                </div>
              </div>

              {/* Commit CTA */}
              <Link
                href="/deals/ac-jet-clean-pfc"
                className="w-full py-3 px-4 rounded-xl bg-forest-900 hover:bg-forest-800 text-white font-semibold text-sm flex items-center justify-center gap-2 shadow-subtle transition-all"
              >
                <span>Join Deal with Flat Number</span>
                <ArrowRight className="w-4 h-4" />
              </Link>
              <p className="text-center text-[11px] text-charcoal-800/60 mt-2">
                Uniform Final-Tier Pricing: If 20 homes join, everyone pays ₹500!
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Popular Categories Grid */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-8">
        <div className="flex flex-col sm:flex-row sm:items-end justify-between mb-8 gap-4">
          <div>
            <h2 className="text-2xl sm:text-3xl font-bold text-charcoal-900">
              Essential Residential Services
            </h2>
            <p className="text-sm text-charcoal-800/70 mt-1">
              Pre-negotiated rate cards tailored for multi-family apartment communities.
            </p>
          </div>
          <Link href="/services" className="text-sm font-semibold text-forest-800 hover:text-forest-900 flex items-center gap-1">
            <span>View All Services</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {[
            {
              title: "AC Servicing & Gas",
              desc: "Deep foam jet cleaning, refrigerant check, filter sanitation.",
              badge: "Up to 50% Off",
              icon: Sparkles,
            },
            {
              title: "RO & Water Purifiers",
              desc: "Membrane replacement, TDS balance, sediment filter change.",
              badge: "Up to 35% Off",
              icon: ShieldCheck,
            },
            {
              title: "Deep Home Cleaning",
              desc: "Kitchen degreasing, bathroom scrubbing, floor buffing.",
              badge: "Up to 40% Off",
              icon: Layers,
            },
            {
              title: "Herbal Pest Control",
              desc: "Cockroach gel baiting, termite barrier, bed bug treatment.",
              badge: "Up to 45% Off",
              icon: Wrench,
            },
          ].map((cat, idx) => (
            <div
              key={idx}
              className="p-6 rounded-2xl bg-white border border-surface-300 shadow-subtle hover:shadow-card hover:border-forest-200 transition-all group"
            >
              <div className="w-12 h-12 rounded-xl bg-forest-100 flex items-center justify-center text-forest-800 mb-4 group-hover:bg-forest-900 group-hover:text-white transition-colors">
                <cat.icon className="w-6 h-6" />
              </div>
              <span className="inline-block px-2.5 py-0.5 rounded-full bg-ochre-100 text-ochre-800 font-semibold text-xs mb-2">
                {cat.badge}
              </span>
              <h3 className="font-bold text-lg text-charcoal-900 mb-1">{cat.title}</h3>
              <p className="text-xs text-charcoal-800/70 leading-relaxed mb-4">{cat.desc}</p>
              <span className="text-xs font-semibold text-forest-800 flex items-center gap-1 group-hover:gap-1.5 transition-all">
                <span>Browse Society Deals</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </span>
            </div>
          ))}
        </div>
      </section>

      {/* How It Works Section */}
      <section className="bg-white border-y border-surface-300 py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-12">
            <h2 className="text-3xl font-bold text-charcoal-900">How Socievo Works</h2>
            <p className="text-sm text-charcoal-800/70 mt-2">
              Transforming individual home chores into collective community savings in three simple steps.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="p-6 rounded-2xl bg-surface-100 border border-surface-300/80">
              <div className="w-10 h-10 rounded-xl bg-forest-900 text-white font-bold flex items-center justify-center mb-4">
                1
              </div>
              <h4 className="font-bold text-lg text-charcoal-900 mb-2">Deal Opens for Your Society</h4>
              <p className="text-xs text-charcoal-800/70 leading-relaxed">
                Your society admin or vetted vendor launches a group campaign with explicit tier pricing (e.g. ₹800 $\to$ ₹500).
              </p>
            </div>

            <div className="p-6 rounded-2xl bg-surface-100 border border-surface-300/80">
              <div className="w-10 h-10 rounded-xl bg-forest-900 text-white font-bold flex items-center justify-center mb-4">
                2
              </div>
              <h4 className="font-bold text-lg text-charcoal-900 mb-2">Neighbours Join & Price Drops</h4>
              <p className="text-xs text-charcoal-800/70 leading-relaxed">
                Residents commit their unit numbers and desired slots. As participation grows, the price drops for everyone.
              </p>
            </div>

            <div className="p-6 rounded-2xl bg-surface-100 border border-surface-300/80">
              <div className="w-10 h-10 rounded-xl bg-forest-900 text-white font-bold flex items-center justify-center mb-4">
                3
              </div>
              <h4 className="font-bold text-lg text-charcoal-900 mb-2">Vendor Executes in One Visit</h4>
              <p className="text-xs text-charcoal-800/70 leading-relaxed">
                Vendor dispatches dedicated technicians on the scheduled day, servicing all units efficiently with verified proof.
              </p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
