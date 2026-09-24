import React from "react";

export default function WorkingPart() {

  const steps = [
    {
      title: "Input Ingestion",
      description:
        "Frame extraction and decoding from image, video, or webcam."
    },
    {
      title: "YOLOv8 Inference",
      description:
        "Feature classification for workers, gear items, and smoke/fire."
    },
    {
      title: "Spatial Containment",
      description:
        "Zone intersection logic testing boots, vests, and helmet bounds."
    },
    {
      title: "Instant Alerting",
      description:
        "Dynamic dispatching of UI alerts, sirens, and audit metrics."
    }
  ];

  return (
    <section
      id="how-it-works"
      className="py-16 max-w-7xl mx-auto px-6 space-y-10"
    >

      {/* TITLE */}
      <div className="text-center max-w-xl mx-auto space-y-2">


        <h3 className="text-3xl font-extrabold text-slate-900">
          How It Works
        </h3>

      </div>


      {/* STEPS */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">

        {steps.map((step, index) => (

          <div
            key={step.title}
            className="p-5 rounded-2xl bg-white border border-slate-200 shadow-sm space-y-2"
          >

            {/* NUMBER */}
            <div className="w-8 h-8 rounded-lg bg-blue-100 text-blue-700 font-black flex items-center justify-center text-xs">
              {index + 1}
            </div>

            {/* TITLE */}
            <h4 className="font-bold text-slate-900 text-sm">
              {step.title}
            </h4>

            {/* DESCRIPTION */}
            <p className="text-slate-600 text-xs leading-relaxed">
              {step.description}
            </p>

          </div>

        ))}

      </div>

    </section>
  );
}