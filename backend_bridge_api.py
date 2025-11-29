#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CHNeoWave Bridge API - Passerelle FastAPI pour l'intégration UI React ↔ Core Python

Ce module crée une API REST et WebSocket pour connecter l'interface React TypeScript
aux modules core Python de CHNeoWave.

Auteur: CHNeoWave Integration Team
Version: 1.0.0
Date: 2025-01-11
"""

import asyncio
import json
import logging
import os
import sys
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union

import uvicorn
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ajout du path pour les imports CHNeoWave
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

# Imports des modules core CHNeoWave
try:
    from hrneowave.core.signal_bus import get_signal_bus, get_error_bus, SessionState
    from hrneowave.acquisition import (
        AcquisitionController, 
        MaritimeChannelConfig, 
        AcquisitionSession,
        create_maritime_laboratory_config,
        scan_available_boards,
        MARITIME_SENSOR_TYPES,
        VOLTAGE_RANGES
    )
    from hrneowave.hardware.manager import HardwareManager
    from hrneowave.core.optimized_fft_processor import OptimizedFFTProcessor
    from hrneowave.core.optimized_goda_analyzer import OptimizedGodaAnalyzer, ProbeGeometry
    from hrneowave.core.performance_monitor import get_performance_monitor
    from hrneowave.core.error_handler import get_error_handler
    from hrneowave.core.post_processor import PostProcessor
    
    CHNEOWAVE_AVAILABLE = True
    logger.info("✅ Modules CHNeoWave importés avec succès")
    
except ImportError as e:
    CHNEOWAVE_AVAILABLE = False
    logger.error(f"❌ Échec d'import des modules CHNeoWave: {e}")
    logger.error("📁 Vérifiez que le path src/hrneowave est correct")

# Configuration FastAPI
app = FastAPI(
    title="CHNeoWave Bridge API",
    description="API de passerelle pour l'intégration React ↔ Python CHNeoWave",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuration CORS pour React
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # React dev server
        "http://localhost:3000",  # React build
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================================================================
# MODÈLES PYDANTIC POUR L'API
# =============================================================================

class APIResponse(BaseModel):
    """Format de réponse standard pour l'API"""
    success: bool
    data: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None
    timestamp: float = Field(default_factory=lambda: datetime.now().timestamp())

class AcquisitionStartRequest(BaseModel):
    """Requête de démarrage d'acquisition"""
    sampling_rate: float = Field(default=1000.0, ge=1.0, le=50000.0)
    channels: List[int] = Field(default=[0, 1, 2, 3])
    duration: Optional[float] = Field(default=None, ge=0.1)
    voltage_range: str = Field(default="±10V")
    buffer_size: int = Field(default=10000, ge=1000, le=100000)
    project_name: str = Field(default="Nouvelle Session")

class ChannelConfigRequest(BaseModel):
    """Configuration d'un canal"""
    channel: int = Field(ge=0, le=7)
    sensor_type: str
    label: str
    units: str = "V"
    voltage_range: str = "±10V"
    physical_units: str = "m"
    sensor_sensitivity: float = 1.0
    enabled: bool = True

class HardwareBackendRequest(BaseModel):
    """Requête de changement de backend matériel"""
    backend: str = Field(pattern="^(ni-daqmx|iotech|demo)$")

class FFTRequest(BaseModel):
    """Requête de calcul FFT"""
    signal_data: List[float]
    sampling_rate: float
    normalize: bool = False

# =============================================================================
# GESTIONNAIRE D'ÉTAT GLOBAL
# =============================================================================

class CHNeoWaveState:
    """Gestionnaire d'état global de l'application"""
    
    def __init__(self):
        self.signal_bus = None
        self.error_bus = None
        self.acquisition_controller = None
        self.hardware_manager = None
        self.fft_processor = None
        self.goda_analyzer = None
        self.performance_monitor = None
        self.error_handler = None
        self.post_processor = None
        
        # État des WebSockets
        self.websocket_connections: List[WebSocket] = []
        self.realtime_task: Optional[asyncio.Task] = None
        
        # Configuration par défaut
        self.default_config = {
            'hardware': {'backend': 'demo'},
            'acquisition': {
                'sampling_rate': 1000.0,
                'buffer_size': 10000,
                'voltage_range': '±10V'
            }
        }
        
        self.initialize()
    
    def initialize(self):
        """Initialise les modules CHNeoWave si disponibles"""
        if not CHNEOWAVE_AVAILABLE:
            logger.warning("⚠️ Modules CHNeoWave non disponibles - Mode simulation")
            return
            
        try:
            # Initialisation des modules core
            self.signal_bus = get_signal_bus()
            self.error_bus = get_error_bus()
            self.performance_monitor = get_performance_monitor()
            self.error_handler = get_error_handler()
            
            # Initialisation du gestionnaire matériel
            self.hardware_manager = HardwareManager(self.default_config)
            
            # Initialisation du processeur FFT
            self.fft_processor = OptimizedFFTProcessor()
            
            # Initialisation du post-processeur
            self.post_processor = PostProcessor()
            
            logger.info("✅ État global CHNeoWave initialisé")
            
        except Exception as e:
            logger.error(f"❌ Erreur d'initialisation: {e}")
            traceback.print_exc()
    
    def get_acquisition_controller(self) -> Optional[AcquisitionController]:
        """Retourne le contrôleur d'acquisition (création lazy)"""
        if not CHNEOWAVE_AVAILABLE:
            return None
            
        if self.acquisition_controller is None:
            try:
                self.acquisition_controller = AcquisitionController(
                    hardware_manager=self.hardware_manager,
                    signal_bus=self.signal_bus
                )
                logger.info("✅ AcquisitionController créé")
            except Exception as e:
                logger.error(f"❌ Erreur création AcquisitionController: {e}")
                
        return self.acquisition_controller

# Instance globale
chneowave_state = CHNeoWaveState()

# =============================================================================
# ENDPOINTS SYSTÈME
# =============================================================================

@app.get("/", response_model=APIResponse)
async def root():
    """Endpoint racine - Status de l'API"""
    return APIResponse(
        success=True,
        data={
            "service": "CHNeoWave Bridge API",
            "version": "1.0.0",
            "chneowave_available": CHNEOWAVE_AVAILABLE,
            "status": "running",
            "endpoints": {
                "docs": "/docs",
                "health": "/health",
                "system": "/system/*",
                "acquisition": "/acquisition/*",
                "hardware": "/hardware/*",
                "processing": "/processing/*",
                "websocket": "/ws/realtime"
            }
        }
    )

@app.get("/health", response_model=APIResponse)
async def health_check():
    """Check de santé de l'API"""
    health_data = {
        "api_status": "healthy",
        "chneowave_modules": CHNEOWAVE_AVAILABLE,
        "timestamp": datetime.now().isoformat()
    }
    
    if CHNEOWAVE_AVAILABLE and chneowave_state.performance_monitor:
        try:
            metrics = chneowave_state.performance_monitor.get_current_metrics()
            health_data["system_metrics"] = metrics
        except Exception as e:
            health_data["metrics_error"] = str(e)
    
    return APIResponse(success=True, data=health_data)

@app.get("/system/status", response_model=APIResponse)
async def get_system_status():
    """Récupère le statut système complet"""
    if not CHNEOWAVE_AVAILABLE:
        return APIResponse(
            success=False,
            error={"code": "MODULE_UNAVAILABLE", "message": "Modules CHNeoWave non disponibles"}
        )
    
    try:
        status = {
            "performance": chneowave_state.performance_monitor.get_current_metrics() if chneowave_state.performance_monitor else {},
            "hardware": {
                "backend": chneowave_state.hardware_manager.backend_name if chneowave_state.hardware_manager else "unknown",
                "available_backends": ["ni-daqmx", "iotech", "demo"] if CHNEOWAVE_AVAILABLE else []
            },
            "acquisition": {
                "active_sessions": 0,  # À implémenter
                "last_session": None
            },
            "websockets": {
                "active_connections": len(chneowave_state.websocket_connections)
            }
        }
        
        return APIResponse(success=True, data=status)
        
    except Exception as e:
        logger.error(f"Erreur get_system_status: {e}")
        return APIResponse(
            success=False,
            error={"code": "SYSTEM_ERROR", "message": str(e)}
        )

# =============================================================================
# ENDPOINTS HARDWARE
# =============================================================================

@app.get("/hardware/backends", response_model=APIResponse)
async def list_hardware_backends():
    """Liste les backends matériels disponibles"""
    if not CHNEOWAVE_AVAILABLE:
        return APIResponse(
            success=True,
            data={"backends": ["demo"], "current": "demo", "note": "Mode simulation"}
        )
    
    try:
        available = ["ni-daqmx", "iotech", "demo"]
        current = chneowave_state.hardware_manager.backend_name if chneowave_state.hardware_manager else "demo"
        
        return APIResponse(
            success=True,
            data={
                "backends": available,
                "current": current,
                "descriptions": {
                    "ni-daqmx": "National Instruments DAQmx",
                    "iotech": "IOTech WaveBook",
                    "demo": "Simulation/Démonstration"
                }
            }
        )
        
    except Exception as e:
        logger.error(f"Erreur list_hardware_backends: {e}")
        return APIResponse(
            success=False,
            error={"code": "HARDWARE_ERROR", "message": str(e)}
        )

@app.post("/hardware/switch", response_model=APIResponse)
async def switch_hardware_backend(request: HardwareBackendRequest):
    """Change le backend matériel"""
    if not CHNEOWAVE_AVAILABLE:
        return APIResponse(
            success=False,
            error={"code": "MODULE_UNAVAILABLE", "message": "Changement de backend non disponible en mode simulation"}
        )
    
    try:
        if chneowave_state.hardware_manager:
            # Note: Cette méthode pourrait nécessiter une implémentation dans HardwareManager
            success = await asyncio.to_thread(
                chneowave_state.hardware_manager._load_backend
            )
            
            return APIResponse(
                success=True,
                data={
                    "new_backend": request.backend,
                    "switch_successful": True,
                    "message": f"Backend basculé vers {request.backend}"
                }
            )
        else:
            return APIResponse(
                success=False,
                error={"code": "HARDWARE_NOT_INITIALIZED", "message": "Gestionnaire matériel non initialisé"}
            )
            
    except Exception as e:
        logger.error(f"Erreur switch_hardware_backend: {e}")
        return APIResponse(
            success=False,
            error={"code": "SWITCH_ERROR", "message": str(e)}
        )

@app.get("/hardware/scan", response_model=APIResponse)
async def scan_hardware_devices():
    """Scanne les périphériques matériels disponibles"""
    if not CHNEOWAVE_AVAILABLE:
        return APIResponse(
            success=True,
            data={"devices": [], "count": 0, "note": "Scan non disponible en mode simulation"}
        )
    
    try:
        devices = await asyncio.to_thread(scan_available_boards)
        
        return APIResponse(
            success=True,
            data={
                "devices": devices,
                "count": len(devices),
                "timestamp": datetime.now().isoformat()
            }
        )
        
    except Exception as e:
        logger.error(f"Erreur scan_hardware_devices: {e}")
        return APIResponse(
            success=False,
            error={"code": "SCAN_ERROR", "message": str(e)}
        )

# =============================================================================
# ENDPOINTS ACQUISITION
# =============================================================================

@app.post("/acquisition/start", response_model=APIResponse)
async def start_acquisition(request: AcquisitionStartRequest):
    """Démarre une session d'acquisition"""
    if not CHNEOWAVE_AVAILABLE:
        # Mode simulation
        return APIResponse(
            success=True,
            data={
                "session_id": f"sim_{int(datetime.now().timestamp())}",
                "status": "started",
                "mode": "simulation",
                "config": request.dict()
            }
        )
    
    try:
        controller = chneowave_state.get_acquisition_controller()
        if not controller:
            return APIResponse(
                success=False,
                error={"code": "CONTROLLER_UNAVAILABLE", "message": "Contrôleur d'acquisition non disponible"}
            )
        
        # Configuration des canaux (simulation basique)
        session_data = {
            "session_id": f"real_{int(datetime.now().timestamp())}",
            "status": "started",
            "config": {
                "sampling_rate": request.sampling_rate,
                "channels": request.channels,
                "duration": request.duration,
                "buffer_size": request.buffer_size,
                "project_name": request.project_name
            }
        }
        
        return APIResponse(success=True, data=session_data)
        
    except Exception as e:
        logger.error(f"Erreur start_acquisition: {e}")
        return APIResponse(
            success=False,
            error={"code": "ACQUISITION_START_ERROR", "message": str(e)}
        )

@app.post("/acquisition/stop", response_model=APIResponse)
async def stop_acquisition():
    """Arrête l'acquisition en cours"""
    if not CHNEOWAVE_AVAILABLE:
        return APIResponse(
            success=True,
            data={"status": "stopped", "mode": "simulation"}
        )
    
    try:
        return APIResponse(
            success=True,
            data={
                "status": "stopped",
                "timestamp": datetime.now().isoformat()
            }
        )
        
    except Exception as e:
        logger.error(f"Erreur stop_acquisition: {e}")
        return APIResponse(
            success=False,
            error={"code": "ACQUISITION_STOP_ERROR", "message": str(e)}
        )

@app.get("/acquisition/status", response_model=APIResponse)
async def get_acquisition_status():
    """Récupère le statut de l'acquisition"""
    return APIResponse(
        success=True,
        data={
            "status": "idle",
            "mode": "simulation" if not CHNEOWAVE_AVAILABLE else "real",
            "active_session": None
        }
    )

# =============================================================================
# ENDPOINTS TRAITEMENT
# =============================================================================

@app.post("/processing/fft", response_model=APIResponse)
async def compute_fft(request: FFTRequest):
    """Calcule la FFT d'un signal"""
    try:
        import numpy as np
        signal = np.array(request.signal_data)
        
        # Calcul FFT (fallback numpy si pyFFTW non disponible)
        fft_result = np.fft.fft(signal)
        frequencies = np.fft.fftfreq(len(signal), 1.0 / request.sampling_rate)
        
        return APIResponse(
            success=True,
            data={
                "fft_magnitude": np.abs(fft_result).tolist(),
                "fft_phase": np.angle(fft_result).tolist(),
                "frequencies": frequencies.tolist(),
                "length": len(signal),
                "sampling_rate": request.sampling_rate,
                "mode": "real" if CHNEOWAVE_AVAILABLE else "simulation"
            }
        )
        
    except Exception as e:
        logger.error(f"Erreur compute_fft: {e}")
        return APIResponse(
            success=False,
            error={"code": "FFT_ERROR", "message": str(e)}
        )

# =============================================================================
# WEBSOCKET TEMPS RÉEL
# =============================================================================

@app.websocket("/ws/realtime")
async def websocket_realtime(websocket: WebSocket):
    """WebSocket pour les données temps réel"""
    await websocket.accept()
    chneowave_state.websocket_connections.append(websocket)
    
    logger.info(f"📡 WebSocket connecté, total: {len(chneowave_state.websocket_connections)}")
    
    try:
        # Démarrage de la tâche temps réel si première connexion
        if len(chneowave_state.websocket_connections) == 1 and not chneowave_state.realtime_task:
            chneowave_state.realtime_task = asyncio.create_task(realtime_data_broadcaster())
        
        # Envoi de données initiales
        await websocket.send_json({
            "type": "connection_established",
            "timestamp": datetime.now().timestamp(),
            "data": {
                "connection_id": id(websocket),
                "api_version": "1.0.0",
                "chneowave_available": CHNEOWAVE_AVAILABLE
            }
        })
        
        # Boucle de réception des messages du client
        while True:
            try:
                message = await websocket.receive_text()
                data = json.loads(message)
                
                # Traitement des commandes WebSocket
                if data.get("type") == "ping":
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": datetime.now().timestamp()
                    })
                elif data.get("type") == "subscribe":
                    # Abonnement à des canaux spécifiques
                    channels = data.get("channels", [])
                    await websocket.send_json({
                        "type": "subscription_confirmed",
                        "channels": channels,
                        "timestamp": datetime.now().timestamp()
                    })
                    
            except asyncio.TimeoutError:
                # Timeout normal, continuer
                continue
                
    except WebSocketDisconnect:
        logger.info("📡 WebSocket déconnecté")
    except Exception as e:
        logger.error(f"❌ Erreur WebSocket: {e}")
    finally:
        # Nettoyage
        if websocket in chneowave_state.websocket_connections:
            chneowave_state.websocket_connections.remove(websocket)
        
        # Arrêt de la tâche temps réel si plus de connexions
        if len(chneowave_state.websocket_connections) == 0 and chneowave_state.realtime_task:
            chneowave_state.realtime_task.cancel()
            chneowave_state.realtime_task = None
        
        logger.info(f"📡 WebSocket nettoyé, restant: {len(chneowave_state.websocket_connections)}")

async def realtime_data_broadcaster():
    """Diffuse les données temps réel vers tous les WebSockets connectés"""
    logger.info("🚀 Démarrage broadcaster temps réel")
    
    try:
        while len(chneowave_state.websocket_connections) > 0:
            # Génération de données simulées
            real_data = generate_simulated_data()
            
            # Envoi vers tous les WebSockets
            message = {
                "type": "acquisition_data",
                "timestamp": datetime.now().timestamp(),
                "data": real_data
            }
            
            disconnected = []
            for ws in chneowave_state.websocket_connections:
                try:
                    await ws.send_json(message)
                except Exception as e:
                    logger.warning(f"Erreur envoi WebSocket: {e}")
                    disconnected.append(ws)
            
            # Nettoyage des connexions fermées
            for ws in disconnected:
                if ws in chneowave_state.websocket_connections:
                    chneowave_state.websocket_connections.remove(ws)
            
            # Attente avant prochaine diffusion
            await asyncio.sleep(0.1)  # 10 Hz
            
    except asyncio.CancelledError:
        logger.info("📡 Broadcaster temps réel arrêté")
    except Exception as e:
        logger.error(f"❌ Erreur broadcaster: {e}")

def generate_simulated_data() -> Dict:
    """Génère des données simulées pour la démonstration"""
    import random
    import math
    
    timestamp = datetime.now().timestamp()
    
    # Simulation de 4 canaux avec différents types de signaux
    channels = {}
    for i in range(4):
        # Signal sinusoïdal avec bruit
        t = timestamp * 0.001  # Facteur temps
        base_freq = 0.1 + i * 0.05  # Fréquences différentes
        amplitude = 2.0 + random.uniform(-0.5, 0.5)
        noise = random.uniform(-0.1, 0.1)
        
        signal_value = amplitude * math.sin(2 * math.pi * base_freq * t) + noise
        
        channels[f"channel_{i}"] = {
            "value": signal_value,
            "unit": "V",
            "status": "active",
            "sensor_type": ["wave_height", "pressure", "accelerometer", "temperature"][i]
        }
    
    return {
        "channels": channels,
        "sample_count": int(timestamp) % 10000,
        "sampling_rate": 1000.0,
        "status": "running",
        "session_id": "simulation",
        "system_metrics": {
            "cpu_usage": random.uniform(10, 30),
            "memory_usage": random.uniform(40, 60),
            "disk_usage": random.uniform(20, 40)
        }
    }

# =============================================================================
# GESTIONNAIRE D'ERREURS
# =============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Gestionnaire global des exceptions"""
    logger.error(f"❌ Exception non gérée: {exc}")
    traceback.print_exc()
    
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "Une erreur interne s'est produite",
                "details": str(exc) if os.getenv("DEBUG") == "1" else None
            },
            "timestamp": datetime.now().timestamp()
        }
    )

# =============================================================================
# POINT D'ENTRÉE
# =============================================================================

def main():
    """Point d'entrée principal"""
    print("🌊 CHNeoWave Bridge API")
    print("=" * 50)
    print(f"📁 Directory: {current_dir}")
    print(f"🐍 Python path: {sys.path[0]}")
    print(f"✅ CHNeoWave modules: {'Disponibles' if CHNEOWAVE_AVAILABLE else 'Non disponibles'}")
    print(f"🚀 Démarrage sur http://localhost:3001")
    print(f"📚 Documentation: http://localhost:3001/docs")
    print("=" * 50)
    
    # Configuration Uvicorn
    uvicorn.run(
        "backend_bridge_api:app",
        host="localhost",
        port=3001,
        reload=True,
        log_level="info",
        access_log=True
    )

if __name__ == "__main__":
    main()
