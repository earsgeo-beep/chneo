import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AppLayout } from '@/components/layout/AppLayout';

// Pages
import { Dashboard } from '@/pages/Dashboard';
import { LiveAcquisitionPage } from '@/pages/acquisition/LiveAcquisitionPage';
import { SpectralAnalysisPage } from '@/pages/analysis/SpectralAnalysisPage';
import { GodaAnalysisPage } from '@/pages/analysis/GodaAnalysisPage';
import { ReflectionAnalysisPage } from '@/pages/analysis/ReflectionAnalysisPage';
import { CalibrationPage } from '@/pages/CalibrationPage';
import { ExportPage } from '@/pages/ExportPage';

export default function App() {
    return (
        <BrowserRouter>
            <Routes>
                <Route element={<AppLayout />}>
                    <Route path="/" element={<Dashboard />} />
                    <Route path="/acquisition/live" element={<LiveAcquisitionPage />} />
                    <Route path="/acquisition/config" element={<LiveAcquisitionPage />} />
                    <Route path="/acquisition/sessions" element={<ExportPage />} /> {/* Fallback to export for sessions */}
                    <Route path="/analysis/spectral" element={<SpectralAnalysisPage />} />
                    <Route path="/analysis/goda" element={<GodaAnalysisPage />} />
                    <Route path="/analysis/reflection" element={<ReflectionAnalysisPage />} />
                    <Route path="/calibration" element={<CalibrationPage />} />
                    <Route path="/export" element={<ExportPage />} />
                </Route>
            </Routes>
        </BrowserRouter>
    );
}
