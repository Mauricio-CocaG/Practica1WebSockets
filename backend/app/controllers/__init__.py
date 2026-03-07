# Este archivo hace que la carpeta sea un módulo Python
from .dashboard_controller import dashboard_bp
from .metrica_controller import metrica_bp
from .nodo_controller import nodo_bp

__all__ = ['dashboard_bp', 'metrica_bp', 'nodo_bp']