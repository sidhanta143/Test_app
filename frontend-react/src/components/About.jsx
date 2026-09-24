
import React from "react";
import { ShieldCheck, Eye, AlertTriangle, Brain } from "lucide-react";

const About = () => {
  return (
    <section id="about" className="bg-slate-50 py-20 px-6">

      <div className="max-w-7xl mx-auto">

        {/* HEADING */}
        <div className="text-center max-w-3xl mx-auto mb-14">

          <p className="text-blue-600 font-medium text-sm mb-3">
            ABOUT OUR SYSTEM
          </p>

          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-semibold text-slate-900 mb-5">
            Making Workplace Safe and 
            <span className="text-blue-700"> Smart</span>
          </h2>

          <p className="text-slate-600 leading-relaxed">
            Our AI-powered safety monitoring system uses computer vision
            to automatically detect safety gear compliance and identify
            potential hazards in workplace environments.
          </p>

        </div>


        {/* CONTENT */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">

          {/* LEFT */}
          <div>

            <h3 className="text-2xl font-semibold text-slate-900 mb-5">
              AI-Powered Safety Monitoring
            </h3>

            <p className="text-slate-600 leading-relaxed mb-5">
              Traditional workplace safety inspections can be time-consuming
              and depend heavily on manual monitoring. Our system provides
              an automated approach by analyzing images and video feeds
              using a trained YOLOv8 object detection model.
            </p>

            <p className="text-slate-600 leading-relaxed mb-6">
              The system can identify workers and check whether required
              protective equipment such as helmets, safety vests, boots,
              gloves, and goggles are being used properly.
            </p>

            <div className="flex items-center gap-3">
              <div className="p-3 bg-blue-100 rounded-xl">
                <ShieldCheck className="text-blue-600" size={25} />
              </div>

              <div>
                <h4 className="font-semibold text-slate-900">
                  Safer Workplaces
                </h4>

                <p className="text-sm text-slate-500">
                  Faster detection of safety violations and hazards.
                </p>
              </div>
            </div>

          </div>


          {/* RIGHT - FEATURES */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">

            <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">

              <div className="w-11 h-11 flex items-center justify-center bg-blue-100 rounded-xl mb-4">
                <Eye className="text-blue-600" size={22} />
              </div>

              <h4 className="text-lg font-semibold text-slate-900 mb-2">
                Real-Time Detection
              </h4>

              <p className="text-sm text-slate-600 leading-relaxed">
                Monitor workplace environments and detect PPE violations
                from video feeds.
              </p>

            </div>


            <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">

              <div className="w-11 h-11 flex items-center justify-center bg-red-100 rounded-xl mb-4">
                <AlertTriangle className="text-red-500" size={22} />
              </div>

              <h4 className="text-lg font-semibold text-slate-900 mb-2">
                Hazard Alerts
              </h4>

              <p className="text-sm text-slate-600 leading-relaxed">
                Identify safety violations and potential hazardous
                situations quickly.
              </p>

            </div>


            <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">

              <div className="w-11 h-11 flex items-center justify-center bg-green-100 rounded-xl mb-4">
                <ShieldCheck className="text-green-600" size={22} />
              </div>

              <h4 className="text-lg font-semibold text-slate-900 mb-2">
                PPE Compliance
              </h4>

              <p className="text-sm text-slate-600 leading-relaxed">
                Check helmets, vests, boots, gloves, and goggles
                automatically.
              </p>

            </div>


            <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">

              <div className="w-11 h-11 flex items-center justify-center bg-purple-100 rounded-xl mb-4">
                <Brain className="text-purple-600" size={22} />
              </div>

              <h4 className="text-lg font-semibold text-slate-900 mb-2">
                AI-Based Analysis
              </h4>

              <p className="text-sm text-slate-600 leading-relaxed">
                Uses computer vision and YOLOv8 to analyze workplace
                safety conditions.
              </p>

            </div>

          </div>

        </div>

      </div>

    </section>
  );
};

export default About;

