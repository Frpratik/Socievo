import React from "react";
import Link from "next/link";
import { Users, ShieldCheck, Tag, ArrowRight } from "lucide-react";

export function Navbar() {
  return (
    <header className="sticky top-0 z-50 bg-white/95 backdrop-blur-md border-b border-surface-300">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16 sm:h-20">
          {/* Brand Logo */}
          <Link href="/" className="flex items-center gap-2.5 group">
            <div className="w-10 h-10 rounded-xl bg-forest-900 flex items-center justify-center text-white font-display font-bold text-xl shadow-card group-hover:bg-forest-800 transition-colors">
              S
            </div>
            <div>
              <span className="font-display font-bold text-2xl text-forest-900 tracking-tight">
                Socievo
              </span>
              <span className="hidden sm:inline-block ml-2 text-xs font-semibold px-2 py-0.5 rounded-full bg-forest-100 text-forest-800 border border-forest-200">
                Society Group-Buying
              </span>
            </div>
          </Link>

          {/* Navigation Links */}
          <nav className="hidden md:flex items-center gap-8 text-sm font-medium text-charcoal-800">
            <Link href="/deals" className="hover:text-forest-800 transition-colors flex items-center gap-1.5">
              <Tag className="w-4 h-4 text-ochre-600" />
              Active Deals
            </Link>
            <Link href="/services" className="hover:text-forest-800 transition-colors">
              Services Catalog
            </Link>
            <Link href="/how-it-works" className="hover:text-forest-800 transition-colors">
              How It Works
            </Link>
            <Link href="/for-vendors" className="hover:text-forest-800 transition-colors flex items-center gap-1.5 text-charcoal-800/80">
              <ShieldCheck className="w-4 h-4 text-forest-700" />
              Partner as Vendor
            </Link>
          </nav>

          {/* Action CTAs */}
          <div className="flex items-center gap-3">
            <Link
              href="/login"
              className="px-4 py-2 text-sm font-medium text-forest-900 hover:text-forest-700 hover:bg-forest-50 rounded-lg transition-colors"
            >
              Log In
            </Link>
            <Link
              href="/register"
              className="inline-flex items-center gap-1.5 px-4 py-2 text-sm font-semibold text-white bg-forest-900 hover:bg-forest-800 rounded-lg shadow-subtle hover:shadow-card transition-all"
            >
              <span>Join Society</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      </div>
    </header>
  );
}
