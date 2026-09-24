import React from 'react';
import { Link } from 'react-router-dom';
import img from "../assets/ppe-logo.png"

export default function Footer() {
  return (
    <footer id="about" className="bg-gradient-to-br from-blue-950 via-slate-900 to-blue-900 text-white border-t border-slate-800 py-14 px-6 lg:px-12">
      <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-12 gap-10">
        <div className="md:col-span-5 space-y-3">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-xl bg-white text-blue-900 flex items-center justify-center font-black shadow-md">
              <img src={img} alt="" />
            </div>
            <span className="font-black text-lg tracking-wide">SafeScan<span className="text-blue-400">360</span></span>
          </div>
          <p className="text-slate-300 text-xs leading-relaxed max-w-sm">
            Automated industrial safety compliance sentinel utilizing YOLOv8 and FastAPI for real-time PPE & hazard monitoring on active work sites.
          </p>
        </div>

        <div className="md:col-span-4 space-y-2">
          <h4 className="text-xs font-bold uppercase tracking-wider text-blue-300">Project Overview</h4>
          <p className="text-xs text-slate-300 leading-relaxed">
            Engineered to detect helmets, reflective vests, and safety boots with custom containment algorithms and instant hazard warnings.
          </p>
        </div>

        <div className="md:col-span-3 space-y-2">
          <h4 className="text-xs font-bold uppercase tracking-wider text-blue-300">Navigation</h4>
          <ul className="space-y-1 text-xs text-slate-300 font-medium">
            <li><Link to="/image" className="hover:text-white transition">Image Audit</Link></li>
            <li><Link to="/live" className="hover:text-white transition">Live Camera</Link></li>
            <li><Link to="/video" className="hover:text-white transition">Video Audit</Link></li>
          </ul>
        </div>
      </div>

      <div className="max-w-7xl mx-auto mt-10 pt-5 border-t border-slate-800 flex items-center justify-between text-[11px] text-slate-400">
        <p>&copy; 2026 SafeSight AI. Certified Safety Compliance Sentinel.</p>
        <span className="text-emerald-400 font-semibold">&bull; System Operational</span>
      </div>
    </footer>
  );
}