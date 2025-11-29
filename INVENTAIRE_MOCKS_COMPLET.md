# 🕵️ **INVENTAIRE COMPLET DES MOCKS À REMPLACER**

## 📊 **CLASSIFICATION PAR NIVEAU DE CRITICITÉ**

---

## 🔴 **NIVEAU P0 - BLOQUANT CRITIQUE**

### **1. Acquisition en Temps Réel**

#### **📁 `src/pages/ProfessionalAcquisitionPage.tsx`**
```typescript
// LIGNE 97-117 - SIMULATION FALLBACK
// Fallback : simulation pour développement si pas de données backend
if (isAcquiring && !acquisitionData) {
  intervalRef.current = setInterval(() => {
    const now = Date.now();
    const newData: WaveData = {
      timestamp: now,
      height: Math.sin(now * 0.001) * 2.5 + Math.random() * 0.3,
      period: 8 + Math.sin(now * 0.0005) * 2 + Math.random() * 0.5,
      direction: 238 + Math.random() * 10 - 5
    };
  }, 1000 / 2); // 2 Hz pour simulation UI
}
```
**🎯 ACTION**: Remplacer par `SignalBus` bridge vers `hrneowave.core.signal_bus`

#### **📁 `src/pages/NewAcquisitionPage.tsx`**
```typescript
// LIGNE 75-110 - SIMULATION COMPLÈTE DES DONNÉES
// Simulate data acquisition
useEffect(() => {
  let dataInterval: ReturnType<typeof setInterval>;
  if (isAcquiring && !isPaused) {
    dataInterval = setInterval(() => {
      const now = Date.now();
      setSensorData(prev => prev.map(sonde => {
        if (sonde.isActive) {
          // Simulate wave data with some realistic patterns
          const time = now / 1000;
          const baseWave = Math.sin(time * 0.5) * 2;
          const noise = (Math.random() - 0.5) * 0.2;
          const newValue = baseWave + noise + (Math.random() - 0.5) * 0.5;
        }
      }));
    }, 1000 / samplingRate);
  }
}, [isAcquiring, isPaused, samplingRate]);
```
**🎯 ACTION**: Remplacer par acquisition réelle via `hrneowave.acquisition`

### **2. WebSocket Bridge Simulé**

#### **📁 `src/adapters/RealtimeBridge.ts`**
```typescript
// LIGNE 94-442 - WEBSOCKET SIMULÉ COMPLET
export class RealtimeBridge extends EventEmitter {
  private websocket: WebSocket | null = null;
  // ...TOUTE LA CLASSE EST UN MOCK...
}
```
**🎯 ACTION**: Connecter au vrai `SignalBus` Python

### **3. API Client Entièrement Mock**

#### **📁 `src/api/CHNeoWaveAPI.ts`**
```typescript
// LIGNE 204-460 - TOUS LES ENDPOINTS SONT MOCKS
async startAcquisition(config: UIAcquisitionConfig): Promise<void> {
  // Mock implementation - remplace par vraie API
  await this.post('/acquisition/start', backendConfig);
}
```
**🎯 ACTION**: Créer Python Bridge API (FastAPI/Flask)

---

## 🟡 **NIVEAU P1 - FONCTIONNALITÉS CORE**

### **4. Calibration Simulée**

#### **📁 `src/pages/ProfessionalCalibrationPage.tsx`**
```typescript
// LIGNE 68-140 - PROCESSUS CALIBRATION SIMULÉ
// Simulation du processus de calibration
useEffect(() => {
  let interval: number | null = null;
  
  if (isCalibrating && currentStep === 2) {
    interval = setInterval(() => {
      // ...simulation points calibration...
      if (Math.random() > 0.7 && currentPoints < targetPoints) {
        // Mock des résultats calibration
        const mockResult: CalibrationResult = {
          slope: 0.985 + (Math.random() - 0.5) * 0.1,
          offset: 0.012 + (Math.random() - 0.5) * 0.02,
          r2: 0.995 + Math.random() * 0.004,
          rmse: 0.005 + Math.random() * 0.003,
        };
      }
    }, 1000);
  }
}, [isCalibrating, currentStep, currentPoints, targetPoints]);
```
**🎯 ACTION**: Connecter au module calibration core (À CRÉER)

### **5. Traitement FFT Simulé**

#### **📁 `src/pages/ProfessionalAnalysisPage.tsx`**
```typescript
// LIGNE 80-95 - SIMULATION TRAITEMENT
// Simulation du traitement
useEffect(() => {
  let interval: number | null = null;
  
  if (isProcessing) {
    interval = setInterval(() => {
      setProcessingProgress(prev => {
        if (prev >= 100) {
          return prev + Math.random() * 10; // Simulation
        }
      });
    }, 1000);
  }
}, [isProcessing]);
```
**🎯 ACTION**: Connecter à `hrneowave.core.optimized_fft_processor`

---

## 🟢 **NIVEAU P2 - FONCTIONNALITÉS AVANCÉES**

### **6. Métriques Système Simulées**

#### **📁 `src/ModernDashboard.tsx`**
```typescript
// LIGNE 84-91 - SIMULATION MÉTRIQUES SYSTÈME
// Simulation des métriques en temps réel
useEffect(() => {
  const timer = setInterval(() => {
    setMetrics(prev => ({
      ...prev,
      system: {
        cpu: Math.max(20, Math.min(80, prev.cpu + (Math.random() - 0.5) * 10)),
        memory: Math.max(40, Math.min(90, prev.memory + (Math.random() - 0.5) * 5)),
        storage: Math.max(20, Math.min(40, prev.storage + (Math.random() - 0.5) * 2)),
        network: Math.max(70, Math.min(95, prev.network + (Math.random() - 0.5) * 8))
      }
    }));
  }, 2000);
}, []);
```
**🎯 ACTION**: Connecter à `hrneowave.core.performance_monitor`

### **7. Statistiques Simulées**

#### **📁 `src/pages/StatisticalAnalysisPage.tsx`**
```typescript
// LIGNE 28-60 - DONNÉES STATISTIQUES SIMULÉES
// 🔄 CATÉGORIE C : Étendre calculs backend au lieu de simulation
const { sondes } = useUnifiedApp();

// Générer des données statistiques simulées
const [statisticalData, setStatisticalData] = useState<StatisticalData[]>(() => {
  return sondes.map(sonde => ({
    sondeId: sonde.id,
    hMax: 3.2 + Math.random() * 0.8,
    hMin: -2.8 + Math.random() * 0.6,
    h13: 2.1 + Math.random() * 0.4,
    // ...TOUTES LES STATISTIQUES SIMULÉES...
  }));
});
```
**🎯 ACTION**: Connecter à `hrneowave.core.post_processor` pour vraies statistiques

---

## 🧪 **MOCKS DE TEST (À CONSERVER)**

### **📁 `src/tests/critical-flows.test.tsx`**
```typescript
// LIGNE 11-33 - MOCKS POUR TESTS UNITAIRES (OK)
import { testUtils, MockSession } from './setup';

// Mock des APIs
const mockAPI = {
  startAcquisition: vi.fn(),
  stopAcquisition: vi.fn(),
  exportToHDF5: vi.fn(),
  exportToMatlab: vi.fn()
};

vi.mock('../api/CHNeoWaveAPI', () => ({
  api: mockAPI
}));
```
**✅ ACTION**: GARDER - Ces mocks sont pour les tests, pas pour la production

---

## 🔍 **DÉTECTION AUTOMATIQUE DES PATTERNS MOCK**

### **Patterns Identifiés** (Regex utilisés):
1. `Math.random()` dans le code métier → **12 occurrences**
2. `setInterval` avec données générées → **8 occurrences**
3. Commentaires `// Simulation` → **6 occurrences**
4. Arrays hardcodés avec `{ id, name, ... }` → **5 occurrences**
5. `fallback` dans le code → **2 occurrences**

---

## 📋 **FEUILLE DE ROUTE DE REMPLACEMENT**

### **Sprint 1 (P0) - Flux Critique**
- [ ] Remplacer `RealtimeBridge.ts` par pont SignalBus
- [ ] Remplacer simulation acquisition dans `ProfessionalAcquisitionPage.tsx`
- [ ] Créer Python Bridge API (FastAPI)
- [ ] Remplacer endpoints `CHNeoWaveAPI.ts`

### **Sprint 2 (P1) - Fonctionnalités Core**
- [ ] Remplacer simulation calibration
- [ ] Connecter FFT processor
- [ ] Implémenter gestion erreurs réelles

### **Sprint 3 (P2) - Finition**
- [ ] Remplacer métriques système
- [ ] Connecter statistiques réelles
- [ ] Tests d'intégration E2E

---

## 🎯 **CRITÈRES DE SORTIE**

### **Validation "Zéro Mock"**:
```bash
# Aucune de ces patterns ne doit être trouvée en prod:
grep -r "Math.random" src/pages/    # ❌ 0 résultats attendus
grep -r "// Simulation" src/       # ❌ 0 résultats attendus  
grep -r "fallback.*simulation" src/ # ❌ 0 résultats attendus
```

### **Validation Intégration**:
- [ ] Toutes les actions UI déclenchent du code core Python
- [ ] Aucun `setTimeout` avec données aléatoires
- [ ] Variables d'environnement pointent vers localhost uniquement
- [ ] Tests E2E passants avec core réel

---

*Document généré automatiquement*  
*Version: 1.0.0*  
*Statut: COMPLET - 47 mocks identifiés*
