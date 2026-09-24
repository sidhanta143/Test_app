import React from "react";
import {
  ArrowRight,
  ShieldCheck,
  AlertTriangle,
  Camera,
  Activity
} from "lucide-react";

import video from "../assets/annotated_video-2.mp4";

export default function Header({ onOpenModal }) {
  return (
    <section
      id="home"
      className="max-w-7xl mx-auto px-6 py-16 lg:py-24"
    >
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">

        {/* ================= LEFT : VIDEO ================= */}
        <div className="order-2 lg:order-1">

          <div className="rounded-3xl border border-blue-900/20 bg-gradient-to-br from-blue-900 to-blue-950 text-white shadow-2xl p-5">

            {/* Video */}
            <div className="relative overflow-hidden rounded-2xl bg-black">

              <video
                src={video}
                controls
                autoPlay
                muted
                loop
                playsInline
                className="w-full aspect-video object-cover"
              >
                Your browser does not support video playback.
              </video>



            </div>


            {/* VIDEO STATS */}
            <div className="grid grid-cols-2 gap-3 mt-5">

              <div className="p-4 rounded-xl bg-blue-900/60 border border-blue-800">

                <div className="flex items-center gap-2 text-blue-200 text-xs">
                  <ShieldCheck size={15} />
                  Model Accuracy
                </div>

                <div className="text-xl font-black text-white mt-1">
                  99.2%
                </div>

              </div>


              <div className="p-4 rounded-xl bg-blue-900/60 border border-blue-800">

                <div className="flex items-center gap-2 text-blue-200 text-xs">
                  <Activity size={15} />
                  Detection Speed
                </div>

                <div className="text-xl font-black text-blue-300 mt-1">
                  38 FPS
                </div>

              </div>

            </div>

          </div>

        </div>


        {/* ================= RIGHT : CONTENT ================= */}
        <div className="order-1 lg:order-2 space-y-7">




          {/* MAIN TITLE */}
          <div>

            <h1 className="text-4xl sm:text-4xl lg:text-6xl font-black  ">

              Smart Safety

              <br />

              <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-700 to-indigo-600">
                Detection Demo
              </span>

            </h1>

          </div>


          {/* DESCRIPTION */}
          <p className="text-slate-600 text-base lg:text-lg leading-relaxed max-w-xl">

            An AI-powered computer vision system that automatically
            monitors industrial environments and verifies worker
            safety equipment in real time.

          </p>


          {/* PPE ITEMS */}
          <div className="grid grid-cols-2 gap-3 max-w-md">

            <div className="flex items-center gap-3 p-3 rounded-xl bg-white border border-slate-200 shadow-sm">

              <div className="w-9 h-9 rounded-lg bg-blue-100 text-blue-700 flex items-center justify-center">
                <ShieldCheck size={18} />
              </div>

              <div>
                <div className="text-sm font-bold text-slate-900">
                  Helmet
                </div>

                <div className="text-xs text-slate-500">
                  Detection
                </div>
              </div>

            </div>


            <div className="flex items-center gap-3 p-3 rounded-xl bg-white border border-slate-200 shadow-sm">
<div>
                <div className="text-sm font-bold text-slate-900">
                  Safety Vest
                </div>

                <div className="text-xs text-slate-500">
                  Detection
                </div>
              </div>

            </div>





          </div>


          {/* BUTTONS */}



          {/* TECHNOLOGY */}

        </div>

      </div>
    </section>
  );
}