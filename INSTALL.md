# Guide d'Installation CHNeoWave v1.0.0

## Prérequis Système

### Configuration Minimale
- **OS**: Windows 10/11 (64-bit)
- **RAM**: 4 GB minimum, 8 GB recommandé
- **Espace disque**: 500 MB pour l'installation
- **Python**: 3.8+ (pour installation depuis les sources)

### Configuration Recommandée
- **OS**: Windows 11 (64-bit)
- **RAM**: 16 GB ou plus
- **Espace disque**: 2 GB (données + logs)
- **Processeur**: Intel i5/AMD Ryzen 5 ou supérieur
- **Résolution**: 1920x1080 minimum

## Installation Rapide (Exécutable)

### Option 1: Exécutable Standalone

1. **Téléchargement**
   ```
   Téléchargez chneowave.exe depuis la release v1.0.0
   ```

2. **Installation**
   ```
   # Créez un répertoire dédié
   mkdir C:\CHNeoWave
   
   # Copiez l'exécutable
   copy chneowave.exe C:\CHNeoWave\
   ```

3. **Premier lancement**
   ```
   cd C:\CHNeoWave
   chneowave.exe --simulate --fs 32 --channels 8
   ```

### Option 2: Installation avec Configuration

1. **Structure recommandée**
   ```
   C:\CHNeoWave\
   ├── chneowave.exe
   ├── config\
   │   ├── app_config.yaml
   │   └── sensors.yaml
   ├── data\
   └── logs\
   ```

2. **Fichiers de configuration**
   - Copiez les fichiers de configuration depuis `config/examples/`
   - Adaptez selon votre matériel

## Installation Développeur (Sources)

### Prérequis
```bash
# Python 3.8+
python --version

# Git
git --version
```

### Installation

1. **Clonage du repository**
   ```bash
   git clone https://github.com/votre-org/chneowave.git
   cd chneowave
   ```

2. **Environnement virtuel**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Installation des dépendances**
   ```bash
   pip install -e .
   ```

4. **Installation des dépendances de développement**
   ```bash
   pip install -e ".[dev]"
   ```

5. **Vérification**
   ```bash
   python -m pytest tests/
   chneowave --version
   ```

## Configuration Initiale

### 1. Configuration de Base

Créez `config/app_config.yaml`:
```yaml
app:
  name: "CHNeoWave"
  version: "1.0.0"
  debug: false
  
acquisition:
  default_fs: 1000
  buffer_size: 8192
  max_channels: 16
  
analysis:
  fft_window: "hann"
  overlap: 0.5
  nfft: 2048
  
ui:
  theme: "default"
  auto_save: true
  save_interval: 300
```

### 2. Configuration Capteurs

Créez `config/sensors.yaml`:
```yaml
sensors:
  - name: "WG1"
    type: "wave_gauge"
    channel: 0
    calibration: 1.0
    units: "m"
    
  - name: "WG2"
    type: "wave_gauge"
    channel: 1
    calibration: 1.0
    units: "m"
```

### 3. Répertoires de Données

```bash
# Créez les répertoires nécessaires
mkdir data\raw
mkdir data\processed
mkdir data\exports
mkdir logs
```

## Vérification de l'Installation

### Tests de Base

1. **Test de démarrage**
   ```bash
   chneowave --version
   # Sortie attendue: CHNeoWave v1.0.0
   ```

2. **Test simulation**
   ```bash
   chneowave --simulate --fs 32 --channels 4 --duration 10
   ```

3. **Test interface graphique**
   ```bash
   chneowave
   # L'interface doit s'ouvrir sans erreur
   ```

### Diagnostic Automatique

```bash
# Exécutez le diagnostic intégré
chneowave --diagnose
```

Cette commande vérifie:
- Configuration système
- Dépendances Python
- Fichiers de configuration
- Permissions d'écriture
- Matériel d'acquisition (si connecté)

## Résolution de Problèmes

### Problèmes Courants

#### 1. Erreur "Module not found"
```bash
# Réinstallez les dépendances
pip install --force-reinstall -e .
```

#### 2. Erreur d'acquisition
```bash
# Vérifiez les permissions
# Exécutez en tant qu'administrateur si nécessaire
```

#### 3. Interface ne s'affiche pas
```bash
# Vérifiez les pilotes graphiques
# Testez avec --no-gui
chneowave --no-gui --simulate
```

### Logs de Diagnostic

Les logs sont disponibles dans:
- `logs/chneowave.log` (logs généraux)
- `logs/acquisition.log` (logs d'acquisition)
- `logs/analysis.log` (logs d'analyse)

### Support

- **Documentation**: `docs/_build/html/index.html`
- **Guide technique**: `docs/_build/html/technical_guide.html`
- **Issues**: GitHub Issues
- **Email**: support@chneowave.org

## Mise à Jour

### Exécutable
1. Sauvegardez vos configurations
2. Téléchargez la nouvelle version
3. Remplacez l'exécutable
4. Restaurez vos configurations

### Sources
```bash
git pull origin main
pip install -e . --upgrade
```

## Désinstallation

### Exécutable
```bash
# Supprimez le répertoire d'installation
rmdir /s C:\CHNeoWave
```

### Sources
```bash
# Désactivez l'environnement virtuel
deactivate

# Supprimez le répertoire
rmdir /s chneowave
```

---

**CHNeoWave v1.0.0** - Logiciel d'acquisition et d'analyse de données maritimes

Pour plus d'informations, consultez la documentation complète dans `docs/`.