import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/layout/Layout';
import Dashboard from './pages/Dashboard';
import Nodos from './pages/Nodos';
import Metricas from './pages/Metricas';

function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/nodos" element={<Nodos />} />
          <Route path="/metricas" element={<Metricas />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}

export default App;