import React, { useEffect, useRef, useState } from 'react';
import { Camera, CameraOff, AlertTriangle, Flame, CloudFog, Activity, Mail } from 'lucide-react';
import { playSiren } from '../utils/audio';

const blank={total_workers:0,compliant:0,violations:0,hazards:0,fire:false,smoke:false,compliance_pct:'0%',fps:0,latency_ms:0,events:[]};

export default function LiveDetection(){
 const videoRef=useRef(null), canvasRef=useRef(null), streamRef=useRef(null), timerRef=useRef(null), busy=useRef(false);
 const [running,setRunning]=useState(false),[stats,setStats]=useState(blank),[image,setImage]=useState(null),[error,setError]=useState('');
 const [emailNote,setEmailNote]=useState('Email alerts are enabled for detected violations and hazards when SMTP is configured.');

 const stop=()=>{
   clearInterval(timerRef.current);
   timerRef.current=null;
   if(streamRef.current) streamRef.current.getTracks().forEach(t=>t.stop());
   streamRef.current=null;
   if(videoRef.current) videoRef.current.srcObject=null;
   busy.current=false;
   setRunning(false);
   setImage(null);
   setStats(blank);
 };

 const sendFrame=async()=>{
   if(!videoRef.current||!canvasRef.current||busy.current||videoRef.current.readyState<2)return;
   busy.current=true;
   const v=videoRef.current,c=canvasRef.current;
   const scale=Math.min(1,960/v.videoWidth);
   c.width=Math.round(v.videoWidth*scale); c.height=Math.round(v.videoHeight*scale);
   c.getContext('2d').drawImage(v,0,0,c.width,c.height);
   await new Promise(resolve=>c.toBlob(async blob=>{
     try{
       if(!blob) return;
       const body=new FormData(); body.append('file',blob,'live.jpg');
       const res=await fetch('/api/detect/live',{method:'POST',body});
       const data=await res.json();
       if(res.ok){
         setStats({...data.stats,latency_ms:data.stats.processing_ms});
         setImage(data.image);
         if(data.stats.hazards) playSiren();
         if(data.stats.violations || data.stats.hazards){
           setEmailNote('Detection found. Evidence image is being recorded and an email alert is queued when SMTP is configured.');
         }
       }
     }catch(e){}
     finally{busy.current=false;resolve();}
   },'image/jpeg',.78));
 };

 const start=async()=>{
   try{
     setError('');
     if(!navigator.mediaDevices?.getUserMedia){setError('This browser does not support camera access.');return;}
     const stream=await navigator.mediaDevices.getUserMedia({video:{width:{ideal:960},height:{ideal:540},facingMode:'environment'},audio:false});
     streamRef.current=stream;
     videoRef.current.srcObject=stream;
     await videoRef.current.play();
     setRunning(true);
     clearInterval(timerRef.current);
     timerRef.current=setInterval(sendFrame,140);
   }catch(e){setError('Camera unavailable. Allow browser camera permission and try again.');}
 };

 useEffect(()=>()=>stop(),[]);

 return <div className="w-full max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8 space-y-5 flex-1">
   <div><p className="text-[10px] font-black uppercase tracking-[.2em] text-blue-600">Browser camera + AI analysis</p><h1 className="text-2xl sm:text-3xl font-black">Live Detection</h1><p className="mt-1 text-sm text-slate-500">Start Camera opens the browser camera. Frames are continuously captured and analyzed by both the PPE and Fire/Smoke models until Stop is pressed.</p></div>
   {error&&<div className="rounded-xl bg-rose-50 border border-rose-200 p-3 text-sm font-semibold text-rose-700">{error}</div>}
   {stats.hazards>0&&<div className="rounded-xl bg-rose-600 text-white p-3 font-black flex items-center gap-2 animate-pulse"><AlertTriangle size={17}/> {stats.fire?'FIRE DETECTED — CRITICAL':'SMOKE DETECTED — HIGH PRIORITY'}</div>}

   <div className="grid grid-cols-1 xl:grid-cols-2 gap-5">
     <section className="rounded-2xl border bg-white p-3 shadow-sm">
       <div className="flex items-center justify-between mb-3"><h2 className="font-black">Camera Feed</h2><span className={`rounded-full px-3 py-1 text-[10px] font-black ${running?'bg-emerald-100 text-emerald-700':'bg-slate-100 text-slate-500'}`}>{running?'CAMERA ON':'CAMERA OFF'}</span></div>
       <div className="relative aspect-video rounded-xl bg-slate-950 overflow-hidden flex items-center justify-center">
         <video ref={videoRef} muted playsInline className="w-full h-full object-contain"/>
         {!running&&<div className="absolute inset-0 flex items-center justify-center text-slate-400 text-sm font-bold">Press Start Camera</div>}
         <div className="absolute left-3 top-3 rounded-full bg-black/70 px-3 py-1 text-[10px] font-black text-white">{running?'CAPTURING + ANALYZING':'STOPPED'}</div>
       </div>
       <canvas ref={canvasRef} className="hidden"/>
       <div className="flex gap-2 mt-3">
         <button onClick={start} disabled={running} className="inline-flex items-center gap-2 rounded-xl bg-blue-600 px-4 py-2.5 text-xs font-black text-white disabled:bg-slate-300"><Camera size={15}/> Start Camera</button>
         <button onClick={stop} disabled={!running} className="inline-flex items-center gap-2 rounded-xl border px-4 py-2.5 text-xs font-black disabled:opacity-40"><CameraOff size={15}/> Stop</button>
       </div>
     </section>

     <section className="rounded-2xl border bg-white p-3 shadow-sm">
       <div className="flex items-center justify-between mb-3"><h2 className="font-black">AI Detection Result</h2><span className="text-[10px] font-black text-slate-500">LIVE FRAME</span></div>
       <div className="relative aspect-video rounded-xl bg-slate-950 overflow-hidden flex items-center justify-center">
         {image?<img src={image} alt="Live annotated detection" className="w-full h-full object-contain"/>:<p className="text-slate-400 text-sm font-bold">Detection result will appear here</p>}
       </div>
     </section>
   </div>

   <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-6 gap-3">{[["FPS",stats.fps||0],["Latency",`${stats.latency_ms||0} ms`],["Workers",stats.total_workers||0],["Compliant",stats.compliant||0],["Violations",stats.violations||0],["Hazards",stats.hazards||0]].map(([k,v])=><div key={k} className="rounded-2xl border bg-white p-4 shadow-sm"><p className="text-[11px] text-slate-500">{k}</p><p className="mt-1 text-xl font-black">{v}</p></div>)}</div>

   <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
     <div className="rounded-2xl bg-slate-950 p-5 text-white space-y-3"><h2 className="font-black">Hazard monitor</h2><p className="flex justify-between text-sm"><span className="flex gap-2"><Flame size={16}/> Fire</span><b className={stats.fire?'text-rose-400':'text-emerald-400'}>{stats.fire?'YES':'NO'}</b></p><p className="flex justify-between text-sm"><span className="flex gap-2"><CloudFog size={16}/> Smoke</span><b className={stats.smoke?'text-amber-400':'text-emerald-400'}>{stats.smoke?'YES':'NO'}</b></p><p className="flex justify-between text-sm"><span className="flex gap-2"><Activity size={16}/> Compliance</span><b>{stats.compliance_pct}</b></p></div>
     <div className="rounded-2xl border bg-white p-5 shadow-sm"><h2 className="font-black flex items-center gap-2"><Mail size={17}/> Email alerts</h2><p className="mt-2 text-sm text-slate-500">{emailNote}</p><p className="mt-2 text-xs text-slate-400">Alerts are debounced to avoid sending an email for every video frame of the same ongoing event.</p></div>
   </div>
 </div>
}
