# 🔧 Contrats Techniques et Adaptateurs - Intégration CHNeoWave

## 📋 Phase 0.2 : Documentation Contrats API et Modèles de Données

### **🏗️ ARCHITECTURE BACKEND EXISTANTE**

#### **1. Modèles de Données Core**

##### **SessionMetadata (Contrat Principal)**
```python
# src/hrneowave/core/metadata_manager.py
@dataclass
class SessionMetadata:
    # Identifiants
    session_id: str = UUID
    session_name: str = ""
    
    # Timestamps
    created_at: datetime = UTC
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Expérience
    experiment_type: ExperimentType = Enum
    experiment_description: str = ""
    test_number: Optional[str] = None
    operator: str = ""
    laboratory: str = ""
    project_name: str = ""
    
    # Configuration technique
    sensors: List[SensorMetadata] = []
    acquisition_settings: Optional[AcquisitionSettings] = None
    
    # Conditions expérimentales
    wave_conditions: Optional[WaveConditions] = None
    environmental_conditions: Optional[EnvironmentalConditions] = None
    model_geometry: Optional[ModelGeometry] = None
    
    # Données de session
    data_files: List[str] = []
    total_samples: int = 0
    file_size_bytes: int = 0
    
    # Qualité et validation
    data_quality_score: Optional[float] = None  # 0-100
    validation_status: str = "pending|validated|rejected"
    validation_notes: str = ""
```

##### **AcquisitionSettings (Configuration)**
```python
@dataclass
class AcquisitionSettings:
    sampling_rate: float = 1000.0  # Hz
    duration: float = 60.0  # secondes
    buffer_size: int = 10000
    channels: List[int] = []
    voltage_range: str = "±5V"
    trigger_mode: str = "software"
    pre_trigger_samples: int = 0
```

##### **SensorMetadata (Capteurs)**
```python
@dataclass  
class SensorMetadata:
    sensor_id: str
    sensor_type: str  # 'wave_height', 'pressure', 'accelerometer'...
    channel: int
    position: Dict[str, float]  # x, y, z
    calibration: Optional[CalibrationData] = None
    unit: str = "V"
    range_min: float = -10.0
    range_max: float = 10.0
```

#### **2. Formats d'Export Existants**

##### **HDF5 Structure (Format Principal)**
```python
# Structure HDF5 standardisée
{
    "/raw": np.ndarray,  # Données brutes (samples x channels)
    "/metadata": {
        "fs": float,  # Fréquence échantillonnage
        "n_channels": int,
        "n_samples": int, 
        "duration": float,
        "created_at": str,  # ISO format
        "software": "CHNeoWave v1.1.0",
        "channel_names": List[str],
        "sha256": str  # Hash intégrité
    },
    "/calibration": {
        "channel_00": {
            "slope": float,
            "offset": float,
            "r2": float,
            "unit": str
        }
    }
}
```

##### **JSON Export Structure**
```json
{
    "session": {
        "id": "uuid-string",
        "name": "string",
        "timestamp": "ISO-datetime",
        "operator": "string",
        "laboratory": "string"
    },
    "acquisition": {
        "sampling_rate": 1000.0,
        "duration": 60.0,
        "channels": [0, 1, 2, 3],
        "total_samples": 60000
    },
    "sensors": [
        {
            "id": "sensor_01",
            "type": "wave_height",
            "channel": 0,
            "position": {"x": 0.0, "y": 0.0, "z": 0.0},
            "calibration": {
                "slope": 0.985,
                "offset": 0.012,
                "r2": 0.9985,
                "unit": "m"
            }
        }
    ],
    "data": {
        "format": "hdf5|csv|json",
        "file_path": "path/to/data.h5",
        "checksum": "sha256-hash"
    },
    "analysis": {
        "basic_stats": {
            "channel_00": {
                "mean": 0.0,
                "std": 0.15,
                "min": -0.45,
                "max": 0.48,
                "rms": 0.15
            }
        },
        "wave_stats": {
            "Hs": 0.12,      # Hauteur significative
            "Hmax": 0.48,    # Hauteur maximale
            "H13": 0.18,     # Hauteur du tiers supérieur
            "Tm": 8.5,       # Période moyenne
            "Tp": 9.2        # Période pic
        }
    }
}
```

---

## 🔄 **ADAPTATEURS NÉCESSAIRES**

### **1. Format Data Adapter (Critique)**

#### **Backend → Frontend Adapter**
```typescript
// i-prototype-tailwind/src/adapters/DataFormatAdapter.ts
interface BackendSessionData {
  session_id: string;
  session_name: string;
  created_at: string;  // ISO datetime
  experiment_type: string;
  sensors: BackendSensorData[];
  acquisition_settings: BackendAcquisitionSettings;
  data_files: string[];
  total_samples: number;
  validation_status: 'pending' | 'validated' | 'rejected';
}

interface UISessionData {
  id: string;
  name: string;
  createdAt: Date;
  type: 'wave_generation' | 'wave_propagation' | 'ship_resistance';
  sensors: UISensorData[];
  config: UIAcquisitionConfig;
  files: string[];
  samples: number;
  status: 'pending' | 'validated' | 'rejected';
}

class DataFormatAdapter {
  static toUIFormat(backendData: BackendSessionData): UISessionData {
    return {
      id: backendData.session_id,
      name: backendData.session_name,
      createdAt: new Date(backendData.created_at),
      type: this.mapExperimentType(backendData.experiment_type),
      sensors: backendData.sensors.map(this.mapSensorToUI),
      config: this.mapAcquisitionToUI(backendData.acquisition_settings),
      files: backendData.data_files,
      samples: backendData.total_samples,
      status: backendData.validation_status
    };
  }

  static toBackendFormat(uiData: UISessionData): BackendSessionData {
    return {
      session_id: uiData.id,
      session_name: uiData.name,
      created_at: uiData.createdAt.toISOString(),
      experiment_type: this.mapExperimentTypeToBackend(uiData.type),
      sensors: uiData.sensors.map(this.mapSensorToBackend),
      acquisition_settings: this.mapAcquisitionToBackend(uiData.config),
      data_files: uiData.files,
      total_samples: uiData.samples,
      validation_status: uiData.status
    };
  }

  private static mapExperimentType(backendType: string): UIExperimentType {
    const mapping = {
      'wave_generation': 'wave_generation',
      'wave_propagation': 'wave_propagation', 
      'ship_resistance': 'ship_resistance',
      'ship_seakeeping': 'ship_seakeeping',
      'offshore_structure': 'offshore_structure',
      'coastal_engineering': 'coastal_engineering'
    };
    return mapping[backendType] || 'wave_generation';
  }
}
```

### **2. Real-time Data Bridge (Critique)**

#### **Signal Bus → React Context Bridge**
```typescript
// i-prototype-tailwind/src/adapters/RealtimeBridge.ts
import { EventEmitter } from 'events';

interface AcquisitionData {
  timestamp: number;
  channel_data: { [channel: string]: number[] };
  sample_count: number;
  status: 'running' | 'stopped' | 'error';
}

interface CalibrationUpdate {
  sensor_id: string;
  slope: number;
  offset: number;
  r2: number;
  status: 'calibrating' | 'completed' | 'failed';
}

interface SystemStatus {
  hardware_connected: boolean;
  sensors_active: number;
  acquisition_running: boolean;
  last_error: string | null;
}

class RealtimeBridge extends EventEmitter {
  private websocket: WebSocket | null = null;
  private reconnectInterval: number = 5000;
  private maxReconnectAttempts: number = 10;
  private reconnectAttempts: number = 0;

  constructor(private wsUrl: string = 'ws://localhost:8080/ws') {
    super();
    this.connect();
  }

  private connect(): void {
    try {
      this.websocket = new WebSocket(this.wsUrl);
      
      this.websocket.onopen = () => {
        console.log('Connected to CHNeoWave backend');
        this.reconnectAttempts = 0;
        this.emit('connected');
      };

      this.websocket.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          this.handleBackendMessage(message);
        } catch (error) {
          console.error('Error parsing backend message:', error);
        }
      };

      this.websocket.onclose = () => {
        console.log('Disconnected from CHNeoWave backend');
        this.emit('disconnected');
        this.attemptReconnect();
      };

      this.websocket.onerror = (error) => {
        console.error('WebSocket error:', error);
        this.emit('error', error);
      };

    } catch (error) {
      console.error('Failed to connect to backend:', error);
      this.attemptReconnect();
    }
  }

  private handleBackendMessage(message: any): void {
    switch (message.type) {
      case 'acquisition_data':
        this.emit('acquisitionData', this.adaptAcquisitionData(message.data));
        break;
      case 'calibration_update':
        this.emit('calibrationUpdate', this.adaptCalibrationUpdate(message.data));
        break;
      case 'system_status':
        this.emit('systemStatus', this.adaptSystemStatus(message.data));
        break;
      case 'error':
        this.emit('error', message.data);
        break;
    }
  }

  private adaptAcquisitionData(backendData: any): AcquisitionData {
    return {
      timestamp: Date.now(),
      channel_data: backendData.channels || {},
      sample_count: backendData.samples || 0,
      status: backendData.status || 'stopped'
    };
  }

  private adaptCalibrationUpdate(backendData: any): CalibrationUpdate {
    return {
      sensor_id: backendData.sensor_id || '',
      slope: backendData.slope || 1.0,
      offset: backendData.offset || 0.0,
      r2: backendData.r2 || 0.0,
      status: backendData.status || 'calibrating'
    };
  }

  private adaptSystemStatus(backendData: any): SystemStatus {
    return {
      hardware_connected: backendData.hardware_connected || false,
      sensors_active: backendData.sensors_active || 0,
      acquisition_running: backendData.acquisition_running || false,
      last_error: backendData.last_error || null
    };
  }

  public sendCommand(command: string, data?: any): void {
    if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
      this.websocket.send(JSON.stringify({ command, data }));
    } else {
      console.error('WebSocket not connected');
    }
  }

  public startAcquisition(config: any): void {
    this.sendCommand('start_acquisition', config);
  }

  public stopAcquisition(): void {
    this.sendCommand('stop_acquisition');
  }

  public startCalibration(sensorId: string): void {
    this.sendCommand('start_calibration', { sensor_id: sensorId });
  }

  private attemptReconnect(): void {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
      setTimeout(() => this.connect(), this.reconnectInterval);
    } else {
      console.error('Max reconnection attempts reached');
      this.emit('maxReconnectAttemptsReached');
    }
  }
}

export { RealtimeBridge, AcquisitionData, CalibrationUpdate, SystemStatus };
```

### **3. Theme Synchronization Bridge**

#### **Qt Themes ↔ CSS Variables Bridge**
```typescript
// i-prototype-tailwind/src/adapters/ThemeBridge.ts
interface QtThemeData {
  name: string;
  colors: {
    background: string;
    foreground: string;
    accent: string;
    border: string;
  };
  fonts: {
    family: string;
    size: number;
  };
}

interface CSSThemeVariables {
  '--bg-primary': string;
  '--text-primary': string;
  '--accent-primary': string;
  '--border-primary': string;
  '--font-family': string;
  '--font-size-base': string;
}

class ThemeBridge {
  private static qtToCssMapping: { [key: string]: string } = {
    'background': '--bg-primary',
    'foreground': '--text-primary',
    'accent': '--accent-primary',
    'border': '--border-primary'
  };

  static syncToQt(webTheme: string): void {
    // Envoie le thème web vers l'application Qt
    if (window.qtBridge) {
      window.qtBridge.setTheme(webTheme);
    } else {
      // Fallback: localStorage pour synchronisation différée
      localStorage.setItem('qt_theme_sync', webTheme);
    }
  }

  static syncFromQt(): string {
    // Récupère le thème depuis Qt
    if (window.qtBridge) {
      return window.qtBridge.getTheme();
    }
    // Fallback
    return localStorage.getItem('qt_theme_sync') || 'light';
  }

  static applyToWeb(qtTheme: QtThemeData): void {
    const cssVariables: CSSThemeVariables = {
      '--bg-primary': qtTheme.colors.background,
      '--text-primary': qtTheme.colors.foreground,
      '--accent-primary': qtTheme.colors.accent,
      '--border-primary': qtTheme.colors.border,
      '--font-family': qtTheme.fonts.family,
      '--font-size-base': `${qtTheme.fonts.size}px`
    };

    // Application des variables CSS
    const root = document.documentElement;
    Object.entries(cssVariables).forEach(([property, value]) => {
      root.style.setProperty(property, value);
    });

    // Déclenchement d'événement pour mise à jour React
    window.dispatchEvent(new CustomEvent('themeChanged', { 
      detail: { source: 'qt', theme: qtTheme.name } 
    }));
  }

  static webToQtTheme(cssTheme: string): QtThemeData {
    // Conversion thème web → format Qt
    const computedStyle = getComputedStyle(document.documentElement);
    
    return {
      name: cssTheme,
      colors: {
        background: computedStyle.getPropertyValue('--bg-primary').trim(),
        foreground: computedStyle.getPropertyValue('--text-primary').trim(),
        accent: computedStyle.getPropertyValue('--accent-primary').trim(),
        border: computedStyle.getPropertyValue('--border-primary').trim()
      },
      fonts: {
        family: computedStyle.getPropertyValue('--font-family').trim() || 'Inter',
        size: parseInt(computedStyle.getPropertyValue('--font-size-base')) || 14
      }
    };
  }
}

// Extension de window pour le bridge Qt
declare global {
  interface Window {
    qtBridge?: {
      setTheme(theme: string): void;
      getTheme(): string;
      onThemeChanged(callback: (theme: string) => void): void;
    };
  }
}

export { ThemeBridge, QtThemeData, CSSThemeVariables };
```

---

## 🗺️ **MAPPING DES ENDPOINTS API**

### **Backend Endpoints Identifiés**

#### **1. Acquisition Controller**
```python
# Endpoints REST à exposer
POST /api/acquisition/start
POST /api/acquisition/stop  
GET  /api/acquisition/status
GET  /api/acquisition/data/realtime
POST /api/acquisition/config
```

#### **2. Calibration Manager**
```python
POST /api/calibration/start/{sensor_id}
POST /api/calibration/point
GET  /api/calibration/status/{sensor_id}
POST /api/calibration/calculate
GET  /api/calibration/results/{sensor_id}
```

#### **3. Project Manager**
```python
GET    /api/projects
POST   /api/projects
GET    /api/projects/{id}
PUT    /api/projects/{id}
DELETE /api/projects/{id}
GET    /api/projects/{id}/sessions
```

#### **4. Export Manager**
```python
POST /api/export/hdf5
POST /api/export/csv
POST /api/export/json
GET  /api/export/status/{export_id}
GET  /api/export/download/{export_id}
```

### **Frontend API Client**
```typescript
// i-prototype-tailwind/src/api/CHNeoWaveAPI.ts
class CHNeoWaveAPI {
  private baseUrl: string = 'http://localhost:8000/api';

  // Acquisition
  async startAcquisition(config: AcquisitionConfig): Promise<void> {
    await this.post('/acquisition/start', config);
  }

  async stopAcquisition(): Promise<void> {
    await this.post('/acquisition/stop');
  }

  async getAcquisitionStatus(): Promise<AcquisitionStatus> {
    return await this.get('/acquisition/status');
  }

  // Calibration
  async startCalibration(sensorId: string): Promise<void> {
    await this.post(`/calibration/start/${sensorId}`);
  }

  async addCalibrationPoint(point: CalibrationPoint): Promise<void> {
    await this.post('/calibration/point', point);
  }

  // Projects
  async getProjects(): Promise<Project[]> {
    return await this.get('/projects');
  }

  async createProject(project: CreateProjectRequest): Promise<Project> {
    return await this.post('/projects', project);
  }

  // Export
  async exportToHDF5(sessionId: string): Promise<ExportResult> {
    return await this.post('/export/hdf5', { session_id: sessionId });
  }

  private async get(endpoint: string): Promise<any> {
    const response = await fetch(`${this.baseUrl}${endpoint}`);
    if (!response.ok) throw new Error(`API Error: ${response.statusText}`);
    return await response.json();
  }

  private async post(endpoint: string, data?: any): Promise<any> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: data ? JSON.stringify(data) : undefined
    });
    if (!response.ok) throw new Error(`API Error: ${response.statusText}`);
    return await response.json();
  }
}

export const api = new CHNeoWaveAPI();
```

---

## 📊 **SCHÉMAS DE VALIDATION**

### **JSON Schema pour SessionMetadata**
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["session_id", "created_at", "experiment_type", "metadata_version"],
  "properties": {
    "session_id": {
      "type": "string",
      "pattern": "^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
    },
    "session_name": { "type": "string", "maxLength": 255 },
    "created_at": { "type": "string", "format": "date-time" },
    "experiment_type": {
      "type": "string",
      "enum": ["wave_generation", "wave_propagation", "wave_breaking", 
               "ship_resistance", "ship_seakeeping", "offshore_structure", 
               "coastal_engineering", "free_surface_flow", "other"]
    },
    "metadata_version": { "type": "string", "pattern": "^\\d+\\.\\d+\\.\\d+$" },
    "sensors": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["sensor_id", "sensor_type", "channel"],
        "properties": {
          "sensor_id": { "type": "string" },
          "sensor_type": {
            "type": "string", 
            "enum": ["wave_height", "pressure", "accelerometer", "temperature", 
                     "flow_velocity", "force", "displacement", "strain", "generic"]
          },
          "channel": { "type": "integer", "minimum": 0, "maximum": 15 }
        }
      }
    },
    "acquisition_settings": {
      "type": "object",
      "properties": {
        "sampling_rate": { "type": "number", "minimum": 1, "maximum": 10000 },
        "duration": { "type": "number", "minimum": 0.1 },
        "voltage_range": { 
          "type": "string", 
          "enum": ["±1V", "±2V", "±5V", "±10V"] 
        }
      }
    }
  }
}
```

---

## 🎯 **LIVRABLES PHASE 0.2**

✅ **Contrats API Backend** : Endpoints REST + WebSocket documentés  
✅ **Modèles de Données** : Structures Python ↔ TypeScript mappées  
✅ **Adaptateurs Critiques** : Format, Realtime, Theme bridges créés  
✅ **Schémas de Validation** : JSON Schema pour intégrité données  
✅ **API Client Frontend** : Interface unifiée pour backend calls  

**🔄 Phase 0 Terminée - Prêt pour Phase 1 : Intégration Structurelle**
