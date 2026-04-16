import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/layout/Layout';
import Dashboard from './pages/Dashboard';
import CVReview from './pages/CVReview';
import DownloadCVs from './pages/DownloadCVs';
import Chat from './pages/Chat';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Chat />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="cv-review" element={<CVReview />} />
          <Route path="download" element={<DownloadCVs />} />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;
