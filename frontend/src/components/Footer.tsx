import React from "react";
import Link from "next/link";
import { Shield, Sparkles, Building2, MapPin } from "lucide-react";

export function Footer() {
  return (
    <footer className="bg-forest-950 text-surface-300 border-t border-forest-900/60 pt-16 pb-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-10 pb-12 border-b border-forest-900/80">
          {/* Brand info */}
          <div className="md:col-span-1 space-y-4">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-forest-600 flex items-center justify-center text-white font-display font-bold">
                S
              </div>
              <span className="font-display font-bold text-2xl text-white tracking-tight">
                Socievo
              </span>
            </div>
            <p className="text-sm text-surface-400 leading-relaxed">
              India&apos;s premier group-buying and local home services platform engineered for gated apartment societies.
            </p>
            <div className="flex items-center gap-2 text-xs text-forest-300">
              <MapPin className="w-3.5 h-3.5 text-ochre-400" />
              <span>Bengaluru • Mumbai • Pune • NCR • Hyderabad</span>
            </div>
          </div>

          {/* Popular Services */}
          <div>
            <h4 className="font-display font-semibold text-white text-sm uppercase tracking-wider mb-4">
              Society Deals
            </h4>
            <ul className="space-y-2.5 text-sm">
              <li><Link href="/services/ac-service" className="hover:text-white transition-colors">AC Deep Cleaning & Gas</Link></li>
              <li><Link href="/services/ro-water" className="hover:text-white transition-colors">RO Water Purifier Service</Link></li>
              <li><Link href="/services/deep-cleaning" className="hover:text-white transition-colors">Full Home Deep Cleaning</Link></li>
              <li><Link href="/services/pest-control" className="hover:text-white transition-colors">Herbal Pest Control</Link></li>
              <li><Link href="/services/car-wash" className="hover:text-white transition-colors">Apartment Car Detailing</Link></li>
            </ul>
          </div>

          {/* For Communities & Vendors */}
          <div>
            <h4 className="font-display font-semibold text-white text-sm uppercase tracking-wider mb-4">
              Stakeholders
            </h4>
            <ul className="space-y-2.5 text-sm">
              <li><Link href="/for-societies" className="hover:text-white transition-colors">For Society RWAs & Admins</Link></li>
              <li><Link href="/for-vendors" className="hover:text-white transition-colors">Vendor Verification & Onboarding</Link></li>
              <li><Link href="/pricing-engine" className="hover:text-white transition-colors">How Tiered Pricing Works</Link></li>
              <li><Link href="/privacy" className="hover:text-white transition-colors">Resident Privacy Standards</Link></li>
            </ul>
          </div>

          {/* Trust and Compliance */}
          <div className="space-y-3">
            <h4 className="font-display font-semibold text-white text-sm uppercase tracking-wider mb-4">
              Platform Integrity
            </h4>
            <div className="p-3.5 rounded-xl bg-forest-900/60 border border-forest-800/60 space-y-2">
              <div className="flex items-center gap-2 text-forest-300 text-xs font-semibold">
                <Shield className="w-4 h-4 text-ochre-400" />
                <span>Verified Vendors Only</span>
              </div>
              <p className="text-xs text-surface-400 leading-normal">
                Every service vendor undergoes stringent background checks, GST verification, and skill audit.
              </p>
            </div>
          </div>
        </div>

        {/* Bottom copyright and legal */}
        <div className="pt-8 flex flex-col sm:flex-row items-center justify-between text-xs text-surface-400 gap-4">
          <p>© {new Date().getFullYear()} Socievo Technologies Private Limited. All rights reserved.</p>
          <div className="flex items-center gap-6">
            <Link href="/terms" className="hover:text-white transition-colors">Terms of Service</Link>
            <Link href="/privacy" className="hover:text-white transition-colors">Privacy Policy</Link>
            <Link href="/security" className="hover:text-white transition-colors">Security & Trust</Link>
          </div>
        </div>
      </div>
    </footer>
  );
}
