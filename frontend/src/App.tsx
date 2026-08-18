import { BrowserRouter, Routes, Route } from 'react-router-dom';
import PublicLayout from './components/public/PublicLayout';
import LandingPage from './features/landing/LandingPage';
import { SinaqPortal } from './features/sinaq/SinaqPortal';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<PublicLayout><LandingPage /></PublicLayout>} />
        <Route path="/sinaq" element={<SinaqPortal />} />
        <Route path="*" element={<PublicLayout><LandingPage /></PublicLayout>} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
