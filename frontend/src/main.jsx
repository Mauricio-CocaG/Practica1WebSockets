import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

// Opción 1: Usar fuente del sistema (recomendado para evitar errores)
import './index.css';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);