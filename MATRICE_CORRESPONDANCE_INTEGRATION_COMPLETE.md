# 🔗 **MATRICE D'ALIGNEMENT UI ↔ CORE CHNeoWave (VERSION COMPLÈTE)**

## 📊 **ARCHITECTURE DÉCOUVERTE**

### **Séparation des Responsabilités**:
- **Interface UI**: `chneowave/i-prototype-tailwind/` (React/TypeScript)
- **Core Application**: `chneowave/src/hrneowave/` (Python/PySide6)

---

## 🎯 **MODULES CORE IDENTIFIÉS**

### **🏗️ ARCHITECTURE PRINCIPALE**

| Module | Chemin | Responsabilité | Status |
|--------|--------|----------------|---------|
| **GUI Controller** | `hrneowave/gui/controllers/main_controller.py` | Orchestration workflow 5 étapes | ✅ **COMPLET** |
| **MainWindow** | `hrneowave/gui/main_window.py` | Fenêtre principale Qt | ✅ **COMPLET** |
| **ViewManager** | `hrneowave/gui/view_manager.py` | Gestion des vues | ✅ **COMPLET** |
| **SignalBus** | `hrneowave/core/signal_bus.py` | Bus de signaux unifié | ✅ **COMPLET** |

### **📡 MODULES D'ACQUISITION**

| Fonction UI | Module Core | Classe/Fonction | API Endpoint à créer |
|-------------|-------------|-----------------|----------------------|
| `startAcquisition()` | `hrneowave.acquisition.acquisition_controller` | `AcquisitionController.start_session()` | `POST /acquisition/start` |
| `stopAcquisition()` | `hrneowave.acquisition.acquisition_controller` | `AcquisitionController.stop_session()` | `POST /acquisition/stop` |
| `pauseAcquisition()` | `hrneowave.acquisition.acquisition_controller` | `AcquisitionController.pause_session()` | `POST /acquisition/pause` |
| Données temps réel | `hrneowave.core.signal_bus` | `SignalBus.get_signal_bus()` | `WebSocket /ws/realtime` |
| Configuration canaux | `hrneowave.acquisition.acquisition_controller` | `MaritimeChannelConfig` | `PUT /acquisition/config` |

**🔍 Points d'entrée identifiés**:
```python
# Contrôleur principal
from hrneowave.acquisition import AcquisitionController, MaritimeChannelConfig, AcquisitionSession

# Configuration maritime prédéfinie
from hrneowave.acquisition import create_maritime_laboratory_config, MARITIME_SENSOR_TYPES

# Hardware MCC DAQ USB-1608FS
from hrneowave.acquisition import MCCDAQ_USB1608FS, scan_available_boards
```

### **⚡ MODULES DE TRAITEMENT SIGNAL**

| Fonction UI | Module Core | Classe/Fonction | Performance |
|-------------|-------------|-----------------|-------------|
| FFT temps réel | `hrneowave.core.optimized_fft_processor` | `OptimizedFFTProcessor.compute_fft()` | **+80%** avec pyFFTW |
| Spectres de puissance | `hrneowave.core.optimized_fft_processor` | `compute_power_spectrum()` | Cache FFTW |
| Analyse Goda | `hrneowave.core.optimized_goda_analyzer` | `OptimizedGodaAnalyzer.analyze()` | **+1000%** avec cache |
| Séparation d'ondes | `hrneowave.core.optimized_goda_analyzer` | `separate_wave_components()` | SVD optimisé |
| Post-traitement | `hrneowave.core.post_processor` | `PostProcessor` | Signaux Qt |

**🔍 Points d'entrée identifiés**:
```python
# FFT optimisé
from hrneowave.core.optimized_fft_processor import OptimizedFFTProcessor

# Analyse Goda optimisée
from hrneowave.core.optimized_goda_analyzer import OptimizedGodaAnalyzer, ProbeGeometry

# Post-traitement
from hrneowave.core.post_processor import PostProcessor
```

### **🔧 MODULES HARDWARE**

| Fonction UI | Module Core | Classe/Fonction | Backends supportés |
|-------------|-------------|-----------------|-------------------|
| `changeBackend()` | `hrneowave.hardware.manager` | `HardwareManager.switch_backend()` | ni-daqmx, iotech, demo |
| `testConnection()` | `hrneowave.hardware.manager` | `HardwareManager.test_hardware()` | Auto-détection |
| `getSystemStatus()` | `hrneowave.hardware.manager` | `HardwareManager.get_status()` | Monitoring live |

**🔍 Backends disponibles**:
```python
from hrneowave.hardware.backends.ni_daqmx import NIDaqmxBackend
from hrneowave.hardware.backends.iotech import IOTechBackend  
from hrneowave.hardware.backends.demo import DemoBackend
```

### **📊 MODULES DE MONITORING**

| Fonction UI | Module Core | Classe/Fonction | Métriques |
|-------------|-------------|-----------------|-----------|
| Métriques système | `hrneowave.core.performance_monitor` | `get_performance_monitor()` | CPU, Memory, Disk |
| Alertes | `hrneowave.core.performance_monitor` | `Alert, AlertLevel` | INFO, WARNING, ERROR, CRITICAL |
| Gestion erreurs | `hrneowave.core.error_handler` | `get_error_handler()` | ErrorCategory, ErrorContext |

### **⚙️ MODULES DE CONFIGURATION**

| Fonction UI | Module Core | Classe/Fonction | Configurations |
|-------------|-------------|-----------------|----------------|
| Config acquisition | `hrneowave.core.config_manager` | `AcquisitionConfig` | Sampling, triggers, buffers |
| Config analyse | `hrneowave.core.config_manager` | `AnalysisConfig` | FFT, Goda, méthodes |
| Config calibration | `hrneowave.core.config_manager` | `CalibrationConfig` | Coefficients, validation |
| Métadonnées | `hrneowave.core.metadata_manager` | `ExperimentType, WaveType` | Types d'expérience |

---

## 🌐 **PLAN D'INTÉGRATION PYTHON BRIDGE API**

### **1. Création du Bridge FastAPI**

**📁 Fichier**: `chneowave/backend_bridge_api.py`

```python
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import uvicorn

# Imports Core CHNeoWave
from hrneowave.core.signal_bus import get_signal_bus
from hrneowave.acquisition import AcquisitionController
from hrneowave.hardware.manager import HardwareManager
from hrneowave.core.optimized_fft_processor import OptimizedFFTProcessor
from hrneowave.core.performance_monitor import get_performance_monitor

app = FastAPI(title="CHNeoWave Bridge API", version="1.0.0")

# Configuration CORS pour React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instances globales
signal_bus = get_signal_bus()
acquisition_controller = None
hardware_manager = None
fft_processor = OptimizedFFTProcessor()
performance_monitor = get_performance_monitor()
```

### **2. Endpoints REST API**

| Endpoint | Méthode | Fonction Core | Description |
|----------|---------|---------------|-------------|
| `/acquisition/start` | POST | `AcquisitionController.start_session()` | Démarrer acquisition |
| `/acquisition/stop` | POST | `AcquisitionController.stop_session()` | Arrêter acquisition |
| `/acquisition/status` | GET | `AcquisitionController.get_status()` | État acquisition |
| `/hardware/backends` | GET | `HardwareManager.list_backends()` | Backends disponibles |
| `/hardware/switch` | POST | `HardwareManager.switch_backend()` | Changer backend |
| `/system/status` | GET | `performance_monitor.get_metrics()` | Métriques système |
| `/processing/fft` | POST | `fft_processor.compute_fft()` | Calcul FFT |

### **3. WebSocket Temps Réel**

```python
@app.websocket("/ws/realtime")
async def websocket_realtime(websocket: WebSocket):
    await websocket.accept()
    
    # Connexion au SignalBus
    def signal_handler(data):
        asyncio.create_task(websocket.send_json({
            "type": "acquisition_data",
            "data": data
        }))
    
    signal_bus.connect("data_acquired", signal_handler)
    
    try:
        while True:
            await websocket.receive_text()
    except:
        signal_bus.disconnect("data_acquired", signal_handler)
        await websocket.close()
```

---

## 🎯 **PRIORISATION PHASES D'INTÉGRATION**

### **🔴 Phase 1 (P0) - Flux Critique**
1. **SignalBus Bridge** → Remplacer `RealtimeBridge.ts` mock
2. **Acquisition Controller** → Connecter start/stop/pause réels
3. **WebSocket Temps Réel** → Streaming de données réelles

### **🟡 Phase 2 (P1) - Fonctionnalités Core**  
4. **Hardware Manager** → Backend switching ni-daqmx/iotech/demo
5. **FFT Processor** → Calculs spectraux réels optimisés
6. **Performance Monitor** → Métriques système réelles

### **🟢 Phase 3 (P2) - Modules Avancés**
7. **Goda Analyzer** → Analyse avancée des vagues
8. **Post Processor** → Export et rapports
9. **Calibration** → Gestion coefficients et validation

---

## 📋 **CONTRATS D'INTÉGRATION DÉTAILLÉS**

### **Format Standard Request/Response**

```typescript
// Request format
interface AcquisitionStartRequest {
  sampling_rate: number;
  channels: number[];
  duration: number;
  voltage_range: string;
  buffer_size: number;
}

// Response format  
interface APIResponse<T> {
  success: boolean;
  data?: T;
  error?: {
    code: string;
    message: string;
    details?: any;
  };
  timestamp: number;
}

// WebSocket realtime format
interface RealtimeData {
  type: 'acquisition_data' | 'system_status' | 'error';
  timestamp: number;
  data: {
    channel_data: { [channel: string]: number[] };
    sample_count: number;
    status: 'running' | 'paused' | 'stopped';
    fft_results?: any[];
    system_metrics?: any;
  };
}
```

---

## 🛠️ **ADAPTATEURS DE DONNÉES**

### **Conversion Core Python ↔ UI React**

```typescript
// Adaptateur pour AcquisitionSession Python → UISessionData React
export const adaptAcquisitionSession = (pythonSession: any): UISessionData => {
  return {
    id: pythonSession.session_id,
    name: pythonSession.project_name,
    startTime: new Date(pythonSession.start_time),
    endTime: pythonSession.end_time ? new Date(pythonSession.end_time) : null,
    samplingRate: pythonSession.sampling_rate,
    totalSamples: pythonSession.total_samples,
    channels: pythonSession.channels.map(adaptMaritimeChannelConfig),
    metadata: pythonSession.metadata
  };
};

// Adaptateur pour MaritimeChannelConfig Python → UISensorData React  
export const adaptMaritimeChannelConfig = (pythonChannel: any): UISensorData => {
  return {
    id: pythonChannel.channel.toString(),
    name: pythonChannel.label,
    type: pythonChannel.sensor_type,
    isActive: pythonChannel.enabled,
    channel: pythonChannel.channel,
    unit: pythonChannel.physical_units,
    sensitivity: pythonChannel.sensor_sensitivity,
    lastValue: 0, // À remplir par données temps réel
    status: pythonChannel.enabled ? 'active' : 'inactive'
  };
};
```

---

## ⚡ **COMMANDES DE LANCEMENT**

### **1. Démarrer le Bridge API**
```bash
cd chneowave/
python -m uvicorn backend_bridge_api:app --host localhost --port 3001 --reload
```

### **2. Démarrer l'Interface React**
```bash
cd chneowave/i-prototype-tailwind/
npm run dev
# Interface sur http://localhost:5173
# API Bridge sur http://localhost:3001
```

### **3. Configuration Variables d'Environnement**
```bash
# Dans i-prototype-tailwind/.env
VITE_API_URL=http://localhost:3001
VITE_WS_URL=ws://localhost:3001
VITE_BACKEND_TYPE=local
```

---

## 📊 **MÉTRIQUES DE SUCCÈS**

- ✅ **0 mock** actif en mode production
- ✅ **100% endpoints** connectés au core Python
- ✅ **Latence < 50ms** pour WebSocket temps réel  
- ✅ **0 dépendance** réseau externe
- ✅ **Integration tests** passants sur tous les flux
- ✅ **Performance +80%** FFT avec pyFFTW
- ✅ **Performance +1000%** Goda avec cache

---

## 🎭 **RÉSUMÉ DES CAPACITÉS DÉCOUVERTES**

### **Modules Prêts à l'Intégration** ✅
- **Acquisition MCC DAQ**: `hrneowave.acquisition` - Complet
- **SignalBus**: `hrneowave.core.signal_bus` - Complet  
- **FFT Optimisé**: `hrneowave.core.optimized_fft_processor` - Complet
- **Goda Analyzer**: `hrneowave.core.optimized_goda_analyzer` - Complet
- **Hardware Manager**: `hrneowave.hardware.manager` - Complet
- **Performance Monitor**: `hrneowave.core.performance_monitor` - Complet

### **Architecture Robuste** 💪
- **Workflow 5 étapes** orchestré
- **Backends multiples** (ni-daqmx, iotech, demo)
- **Configuration maritime** prédéfinie  
- **Validation matérielle** automatique
- **Cache intelligent** pour performances
- **Gestion erreurs** centralisée

### **Prêt pour Production** 🚀
Le core CHNeoWave est **complet et production-ready**. L'intégration consiste principalement à créer le **bridge API Python** et adapter les **contrats de données** entre React et Python.

---

*Document généré le: $(date)*  
*Version: 2.0.0 - ARCHITECTURE COMPLÈTE*  
*Statut: READY FOR INTEGRATION - Core Python identifié*
