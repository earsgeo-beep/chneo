# 🔗 MATRICE D'ALIGNEMENT UI ↔ CORE CHNeoWave

## 📊 **VUE D'ENSEMBLE DE L'INTÉGRATION**

### **État Actuel**: Interface React Mock + Modules Core Python Complets
### **Objectif**: Intégration 100% locale, 0% mock en production

---

## 🎯 **MATRICE ACTION UI → CONTRAT API → FONCTION CORE**

### **🔴 MODULE ACQUISITION**

| Action UI | Endpoint Actuel | Status | Module Core | Fonction Réelle | Format I/O | Priorité |
|-----------|-----------------|---------|-------------|-----------------|------------|----------|
| `startAcquisition()` | `/acquisition/start` | **MOCK** | `hrneowave.acquisition` | `start_session()` | Config → Status | **P0** |
| `stopAcquisition()` | `/acquisition/stop` | **MOCK** | `hrneowave.acquisition` | `stop_session()` | Void → Status | **P0** |
| `pauseAcquisition()` | `/acquisition/pause` | **MOCK** | `hrneowave.acquisition` | `pause_session()` | Void → Status | **P0** |
| `getRealtimeData()` | WebSocket `/ws` | **MOCK** | `hrneowave.core.signal_bus` | `get_signal_bus()` | Stream | **P0** |
| `setSamplingRate()` | `/acquisition/config` | **MOCK** | `hrneowave.hardware.manager` | `configure_sampling()` | Rate → Bool | **P1** |

**🔍 Points d'entrée identifiés**:
- `src/hrneowave/core/signal_bus.py` - Bus principal de données
- `src/hrneowave/hardware/manager.py` - Gestionnaire matériel
- `src/hrneowave/acquisition/__init__.py` - Module acquisition

---

### **⚙️ MODULE CALIBRATION**

| Action UI | Endpoint Actuel | Status | Module Core | Fonction Réelle | Format I/O | Priorité |
|-----------|-----------------|---------|-------------|-----------------|------------|----------|
| `startCalibration()` | `/calibration/start` | **MOCK** | `hrneowave.core` | À identifier | SondeId → Status | **P1** |
| `addCalibrationPoint()` | `/calibration/point` | **MOCK** | `hrneowave.core` | À identifier | Point → Result | **P1** |
| `calculateCalibration()` | `/calibration/calculate` | **MOCK** | `hrneowave.core` | À identifier | Data → Coeffs | **P1** |

**❗ GAPS IDENTIFIÉS**: Module calibration non encore localisé dans `core/`

---

### **📈 MODULE TRAITEMENT/FFT**

| Action UI | Endpoint Actuel | Status | Module Core | Fonction Réelle | Format I/O | Priorité |
|-----------|-----------------|---------|-------------|-----------------|------------|----------|
| Spectres FFT temps réel | Simulé dans UI | **MOCK** | `hrneowave.core.optimized_fft_processor` | `process_fft()` | Samples → Spectrum | **P0** |
| Analyse Goda | Simulé dans UI | **MOCK** | `hrneowave.core.optimized_goda_analyzer` | `analyze()` | Waves → Metrics | **P1** |
| Statistiques H1/3, Tp | Calculé côté UI | **MOCK** | `hrneowave.core.post_processor` | `calculate_statistics()` | Data → Stats | **P1** |

**✅ Points d'entrée confirmés**:
- `src/hrneowave/core/optimized_fft_processor.py` - FFT optimisées
- `src/hrneowave/core/optimized_goda_analyzer.py` - Analyse des vagues

---

### **💾 MODULE EXPORT**

| Action UI | Endpoint Actuel | Status | Module Core | Fonction Réelle | Format I/O | Priorité |
|-----------|-----------------|---------|-------------|-----------------|------------|----------|
| Export CSV | `/export/csv` | **MOCK** | `hrneowave.core` | À identifier | Session → File | **P2** |
| Export MATLAB | `/export/matlab` | **MOCK** | `hrneowave.core` | À identifier | Session → .mat | **P2** |
| Génération Rapport | `/reports/generate` | **MOCK** | `hrneowave.core` | À identifier | Session → PDF | **P2** |

---

### **🔧 MODULE CONFIGURATION**

| Action UI | Endpoint Actuel | Status | Module Core | Fonction Réelle | Format I/O | Priorité |
|-----------|-----------------|---------|-------------|-----------------|------------|----------|
| `changeBackend()` | `/system/backend` | **MOCK** | `hrneowave.hardware.manager` | `switch_backend()` | Type → Status | **P1** |
| `testConnection()` | `/system/test` | **MOCK** | `hrneowave.hardware.manager` | `test_hardware()` | Channels → Results | **P1** |
| `getSystemStatus()` | `/system/status` | **MOCK** | `hrneowave.core.performance_monitor` | `get_metrics()` | Void → Status | **P2** |

**✅ Points d'entrée confirmés**:
- `src/hrneowave/hardware/manager.py` - Gestionnaire matériel
- `src/hrneowave/core/performance_monitor.py` - Monitoring système

---

## 🎭 **IDENTIFICATION DES MOCKS À REMPLACER**

### **🔍 Mocks dans l'Interface UI**

| Fichier | Ligne | Type Mock | Remplacé par |
|---------|--------|-----------|--------------|
| `UnifiedAppContext.tsx` | 400-500 | Simulated sensors data | SignalBus bridge |
| `ProfessionalAcquisitionPage.tsx` | 98-117 | Fallback simulation | Real-time bridge |
| `NewAcquisitionPage.tsx` | 75-110 | Wave data simulation | Core acquisition |
| `ModernAcquisitionPage.tsx` | 69-77 | Static metrics | Core calculations |
| `MinimalistDashboard.tsx` | 66-77 | CPU/Memory simulation | Performance monitor |

### **🔍 Mocks dans l'API Layer**

| Fichier | Fonction | Status | Action |
|---------|----------|---------|---------|
| `CHNeoWaveAPI.ts` | Tous les endpoints | **MOCK** | Remplacer par Python bridge |
| `RealtimeBridge.ts` | WebSocket simulation | **MOCK** | Connecter au SignalBus |

---

## 🏗️ **ARCHITECTURE D'INTÉGRATION PROPOSÉE**

```
┌─────────────────────────┐
│     React Frontend      │
│   (i-prototype-tailwind)│
├─────────────────────────┤
│    Integration Layer    │
│  ┌─────────────────────┐│
│  │  Python Bridge API  ││  ← À créer
│  │  (FastAPI/Flask)    ││
│  └─────────────────────┘│
├─────────────────────────┤
│     Backend Core        │
│  ┌─────────────────────┐│
│  │  SignalBus          ││  ✅ Existe
│  │  FFT Processor      ││  ✅ Existe
│  │  Hardware Manager   ││  ✅ Existe
│  │  Performance Monitor││  ✅ Existe
│  └─────────────────────┘│
└─────────────────────────┘
```

---

## 📋 **CONTRATS API À NORMALISER**

### **Format Standard de Réponse**
```typescript
interface APIResponse<T> {
  success: boolean;
  data?: T;
  error?: {
    code: string;
    message: string;
    details?: any;
  };
  timestamp: number;
  version: string;
}
```

### **Format SignalBus Bridge**
```typescript
interface RealtimeData {
  acquisition: {
    timestamp: number;
    channel_data: { [channel: string]: number[] };
    sample_count: number;
    status: 'idle' | 'running' | 'paused' | 'stopped' | 'error';
    sampling_rate: number;
    duration_elapsed: number;
  };
  processing: {
    fft_results: any[];
    goda_metrics: any;
    statistics: any;
  };
  system: {
    cpu_usage: number;
    memory_usage: number;
    hardware_status: any;
  };
}
```

---

## 🎯 **PRIORISATION DES MODULES**

### **Phase 1 (P0) - Flux Critique**
1. **Acquisition** → Connecter SignalBus
2. **FFT Temps Réel** → Intégrer OptimizedFFTProcessor

### **Phase 2 (P1) - Fonctionnalités Core**
3. **Calibration** → Identifier/créer module
4. **Configuration Hardware** → HardwareManager

### **Phase 3 (P2) - Fonctionnalités Avancées**
5. **Export** → Modules d'export
6. **Monitoring** → PerformanceMonitor

---

## ⚠️ **GAPS ET ACTIONS REQUISES**

| Gap Identifié | Impact | Action | Assigné |
|---------------|---------|---------|---------|
| Module Calibration manquant | Bloquant P1 | Créer ou localiser module | TBD |
| Module Export manquant | Bloquant P2 | Créer ou localiser module | TBD |
| Python Bridge API manquant | Bloquant P0 | Créer FastAPI/Flask server | TBD |
| WebSocket Real-time manquant | Bloquant P0 | Implémenter WebSocket bridge | TBD |

---

## 📊 **MÉTRIQUES DE SUCCÈS**

- **0 mock** actif en mode production
- **100% des endpoints** connectés au core
- **Latence** < 100ms pour données temps réel
- **0 dépendance** réseau externe
- **Tests E2E** passants sur tous les flux

---

*Document généré le: $(date)*
*Version: 1.0.0*
*Statut: DRAFT - Phase 1 en cours*