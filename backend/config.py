import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key')
    
    # Base de datos
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_NAME = os.getenv('DB_NAME', 'ClusterMonitor')
    DB_PORT = int(os.getenv('DB_PORT', 3306))
    
    # Para MySQL local
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Para SQLITE (opcional, más fácil)
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///cluster.db'
    
    # Configuración de sockets
    SOCKET_HOST = os.getenv('SOCKET_HOST', '0.0.0.0')
    SOCKET_PORT = int(os.getenv('SOCKET_PORT', 9999))
    MAX_CLIENTS = int(os.getenv('MAX_CLIENTS', 9))
    
    REPORT_TIMEOUT = int(os.getenv('REPORT_TIMEOUT', 30))
    NODE_TIMEOUT = int(os.getenv('NODE_TIMEOUT', 300))

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}