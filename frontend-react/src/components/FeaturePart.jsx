import React from "react";
import {
  ShieldCheck,
  Video,
  Flame
} from "lucide-react";

export default function FeaturePart() {

  return (
    <section
      id="features"
      className="py-16 bg-white border-y border-slate-200"
    >

      <div className="max-w-7xl mx-auto px-6 space-y-10">

        {/* TITLE */}
        <div className="text-center max-w-xl mx-auto space-y-2">


          <h3 className="text-3xl font-extrabold text-slate-900">
            Safety Features
          </h3>

        </div>


        {/* FEATURE CARDS */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">

          {/* CARD 1 */}
          <div className="p-6 rounded-2xl bg-gradient-to-br from-blue-900 to-blue-950 text-white shadow-xl space-y-3 border border-blue-800">

            <div className="w-10 h-10 rounded-xl bg-blue-700 flex items-center justify-center text-white">
              <ShieldCheck size={20} />
            </div>

            <h4 className="text-base font-bold">
              3-Point PPE Verification
            </h4>

            <p className="text-blue-100 text-xs leading-relaxed">
              Simultaneous spatial matching for hard hats,
              safety vests, and reinforced boots per worker.
            </p>

          </div>


          {/* CARD 2 */}
          <div className="p-6 rounded-2xl bg-gradient-to-br from-blue-900 to-blue-950 text-white shadow-xl space-y-3 border border-blue-800">

            <div className="w-10 h-10 rounded-xl bg-blue-700 flex items-center justify-center text-white">
              <Video size={20} />
            </div>

            <h4 className="text-base font-bold">
              Tri-Input Inspection Modes
            </h4>

            <p className="text-blue-100 text-xs leading-relaxed">
              Dedicated pipelines for single-image audits,
              live CCTV camera streams, and batch recorded video files.
            </p>

          </div>


          {/* CARD 3 */}
          <div className="p-6 rounded-2xl bg-gradient-to-br from-blue-900 to-blue-950 text-white shadow-xl space-y-3 border border-blue-800">

            <div className="w-10 h-10 rounded-xl bg-blue-700 flex items-center justify-center text-white">
              <Flame size={20} />
            </div>

            <h4 className="text-base font-bold">
              Hazard & Siren Alarm
            </h4>

            <p className="text-blue-100 text-xs leading-relaxed">
              Active fire and smoke recognition with audio
              sirens and visual emergency alerts.
            </p>

          </div>

        </div>

      </div>

    </section>
  );
}