import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import DetectionModal from './components/DetectionModal';
import Home from './pages/Home';
import ImageDetection from './pages/ImageDetection';
import LiveDetection from './pages/LiveDetection';
import VideoAudit from './pages/VideoAudit';
import IncidentArchive from './pages/IncidentArchive';
import Dashboard from './pages/Dashboard';
import Analytics from "./pages/Analytics";

export default function App() {
  const [modalOpen, setModalOpen] = useState(false);

  return (
    <Router>
      <div className="bg-slate-50 text-slate-900 min-h-screen flex flex-col justify-between">
        <Navbar onOpenModal={() => setModalOpen(true)} />
        <main className="flex-1 flex flex-col">
          <Routes>
            <Route path="/" element={<Home onOpenModal={() => setModalOpen(true)} />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/image" element={<ImageDetection />} />
            <Route path="/live" element={<LiveDetection />} />
            <Route path="/video" element={<VideoAudit />} />
            <Route path="/incident-archive" element={<IncidentArchive />} />
            <Route path="/analytics" element={<Analytics />} />
          </Routes>
        </main>
        <Footer />
        <DetectionModal isOpen={modalOpen} onClose={() => setModalOpen(false)} />
      </div>
    </Router>
  );
}