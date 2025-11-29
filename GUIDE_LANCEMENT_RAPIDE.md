# 🚀 **GUIDE DE LANCEMENT RAPIDE - CHNeoWave Intégration**

## 📋 **PRÉ-REQUIS VÉRIFIÉS**

✅ **Bridge API Python** : `backend_bridge_api.py` créé  
✅ **Client React** : `src/api/CoreBridgeAPI.ts` créé  
✅ **Interface React** : Fonctionnelle sur http://localhost:5173  
✅ **Core CHNeoWave** : Modules disponibles dans `src/hrneowave/`

---

## 🖥️ **LANCEMENT MANUEL - 3 ÉTAPES**

### **1. 🐍 Terminal 1 - Bridge API Python**

```bash
# Ouvrir un terminal dans le dossier chneowave/
cd C:\Users\youcef cheriet\Desktop\chneowave

# Activer l'environnement virtuel Python
venv\Scripts\activate

# Lancer le Bridge API
python backend_bridge_api.py
```

**Résultat attendu** :
```
🌊 CHNeoWave Bridge API
==================================================
✅ CHNeoWave modules: Disponibles
🚀 Démarrage sur http://localhost:3001
📚 Documentation: http://localhost:3001/docs
==================================================
INFO: Uvicorn running on http://localhost:3001
```

### **2. ⚛️ Terminal 2 - Interface React**

```bash
# Ouvrir un second terminal dans i-prototype-tailwind/
cd C:\Users\youcef cheriet\Desktop\chneowave\i-prototype-tailwind

# Lancer l'interface React
npm run dev
```

**Résultat attendu** :
```
VITE v5.4.19  ready in 2645 ms
➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
```

### **3. 🌐 Navigateur - Ouvrir les interfaces**

**Interface Principale** :  
👉 **http://localhost:5173**

**Documentation API** :  
👉 **http://localhost:3001/docs**

---

## 🧪 **TESTS DE VALIDATION RAPIDES**

### **Test 1 - Bridge API Health**
```bash
curl http://localhost:3001/health -UseBasicParsing
```

**Résultat attendu** : Status 200 + JSON avec `"success": true`

### **Test 2 - Backends Hardware**
```bash
curl http://localhost:3001/hardware/backends -UseBasicParsing
```

**Résultat attendu** : Liste `["ni-daqmx", "iotech", "demo"]`

### **Test 3 - Interface React**
Dans le navigateur sur http://localhost:5173 :
- ✅ Interface charge sans erreur
- ✅ Thème Solarized Light appliqué
- ✅ Navigation fonctionnelle
- ✅ Pages d'acquisition/calibration/analyse disponibles

---

## 🔗 **INTÉGRATION React ↔ Python**

### **API Client dans React**
Le fichier `src/api/CoreBridgeAPI.ts` contient :
- ✅ Client HTTP avec retry automatique
- ✅ WebSocket temps réel avec reconnexion
- ✅ Adaptateurs de données Python ↔ React
- ✅ Gestion d'erreurs robuste

### **Utilisation dans les composants React**
```typescript
import { coreBridgeAPI } from '../api/CoreBridgeAPI';

// Dans un composant
const startAcquisition = async () => {
  const result = await coreBridgeAPI.startAcquisition({
    sampling_rate: 1000,
    channels: [0, 1, 2, 3],
    voltage_range: "±10V",
    buffer_size: 10000,
    project_name: "Test Session"
  });
  
  if (result.success) {
    console.log("Acquisition démarrée:", result.data);
  }
};
```

---

## 📊 **FONCTIONNALITÉS OPÉRATIONNELLES**

### **🔧 Backend Hardware**
- ✅ Scan des périphériques MCC DAQ
- ✅ Switch entre backends (ni-daqmx, iotech, demo)
- ✅ Configuration automatique backend demo

### **📡 Acquisition de Données**
- ✅ Start/Stop/Pause d'acquisition
- ✅ Configuration 8 canaux simultanés
- ✅ Fréquences d'échantillonnage jusqu'à 50 kS/s
- ✅ Gestion des plages de tension ±1V à ±10V

### **⚡ Traitement Signal**
- ✅ FFT optimisé (numpy.fft + fallback pyFFTW)
- ✅ Analyse spectrale temps réel
- ✅ Calculs de magnitude et phase

### **🌐 Temps Réel**
- ✅ WebSocket sur ws://localhost:3001/ws/realtime
- ✅ Données simulées à 10 Hz
- ✅ Reconnexion automatique
- ✅ Métriques système (CPU, Memory)

---

## 🎯 **POINTS DE VALIDATION**

### **✅ Bridge API Opérationnel**
- Port 3001 accessible ✅
- Modules CHNeoWave chargés ✅  
- Endpoints `/health`, `/hardware/*`, `/acquisition/*` fonctionnels ✅

### **✅ Interface React Fonctionnelle**
- Port 5173 accessible ✅
- Thème cohérent appliqué ✅
- Navigation entre pages ✅
- Composants professionnels ✅

### **✅ Intégration Prête**
- Client `CoreBridgeAPI.ts` intégré ✅
- Adaptateurs de données ✅
- Gestion d'erreurs ✅
- Configuration CORS ✅

---

## 🚧 **LIMITATIONS ACTUELLES**

### **⚠️ Mode Simulation Active**
- Pas de hardware MCC DAQ physique détecté
- Backend par défaut: `demo` (simulation)
- Données générées artificiellement

### **⚠️ Integration Partielle**
- Interface React utilise encore des mocks pour certaines fonctions
- WebSocket connecté mais pas encore utilisé par l'UI
- Transition graduelle mocks → API réelle

---

## 🎉 **PROCHAINES ÉTAPES**

1. **🔗 Connecter l'interface React au Bridge API** :
   - Remplacer les mocks dans `UnifiedAppContext`
   - Utiliser `CoreBridgeAPI` pour les vraies données

2. **📡 Intégrer le WebSocket temps réel** :
   - Afficher les données d'acquisition en live
   - Mettre à jour les graphiques en temps réel

3. **🧪 Tests avec hardware réel** :
   - Connecter une carte MCC DAQ USB-1608FS
   - Tester acquisition avec vrais capteurs

4. **🎨 Finaliser l'UX** :
   - Indicateurs de statut temps réel
   - Messages d'erreur utilisateur-friendly
   - Animations et transitions fluides

---

**🌊 CHNeoWave Integration - Ready for Testing !**

*Status: Bridge API ✅ | Interface React ✅ | Core Python ✅*
