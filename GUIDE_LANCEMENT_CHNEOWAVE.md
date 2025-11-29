# 🚀 Guide de Lancement CHNeoWave

## Points d'Entrée Principaux

CHNeoWave dispose de plusieurs points d'entrée selon vos besoins :

### 1. 🎯 **POINT D'ENTRÉE PRINCIPAL RECOMMANDÉ**

#### **Version Corrigée et Fonctionnelle (RECOMMANDÉE)**
```bash
python lancer_chneowave_corrige.py
```
✅ **Interface complète avec tous les modules**  
✅ **Navigation entre toutes les vues**  
✅ **Thème maritime appliqué**  
✅ **Gestion d'erreurs robuste**  

---

### 2. 📋 **Points d'Entrée Alternatifs**

#### **A. Version Standard (main.py)**
```bash
python main.py
```
- Interface principale corrigée
- Avec gestion des thèmes
- Logging détaillé

#### **B. Interface en Ligne de Commande**
```bash
# Lancer l'interface graphique via CLI
python -m hrneowave --gui

# Ou directement
python src/hrneowave/cli.py --gui
```

#### **C. Module Python**
```bash
# Depuis le répertoire racine
python -m hrneowave
```

---

## 🏗️ **Architecture des Modules CHNeoWave**

### **Modules Principaux Intégrés**

#### 🖥️ **Interface Utilisateur (GUI)**
- **MainWindow** : Fenêtre principale
- **ViewManager** : Gestionnaire de navigation
- **ThemeManager** : Gestion des thèmes maritimes

#### 📊 **Vues Fonctionnelles**
1. **WelcomeView** : Page d'accueil et sélection de projet
2. **DashboardView** : Tableau de bord maritime
3. **AcquisitionView** : Acquisition de données en temps réel
4. **CalibrationView** : Calibration des capteurs
5. **AnalysisView** : Analyse des données de houle
6. **ReportsView** : Génération de rapports

#### ⚙️ **Modules Techniques**
- **Core** : Moteur de calcul et algorithmes
- **Hardware** : Interface avec les capteurs
- **Data** : Gestion des données et formats
- **Utils** : Utilitaires et helpers
- **Config** : Configuration système

---

## 🚀 **Commandes de Lancement Complètes**

### **1. Lancement Rapide (RECOMMANDÉ)**
```bash
cd c:\Users\LEM\Desktop\chneowave
python lancer_chneowave_corrige.py
```

### **2. Lancement avec Validation**
```bash
# Validation préalable
python validation_chneowave.py

# Puis lancement
python lancer_chneowave_corrige.py
```

### **3. Lancement avec Diagnostic**
```bash
# Si problème d'affichage
python diagnostic_chneowave_affichage.py
```

### **4. Tests d'Interface**
```bash
# Test interface directe
python test_interface_directe.py

# Test final sans erreur
python test_final_sans_erreur.py
```

---

## 🔧 **Configuration et Modules**

### **Modules Automatiquement Chargés**
Lors du lancement, CHNeoWave charge automatiquement :

1. **Système Qt** (PySide6)
2. **Gestionnaire de thèmes maritimes**
3. **Toutes les vues fonctionnelles**
4. **Système de navigation**
5. **Gestion des événements**
6. **Configuration par défaut**

### **Vérification des Modules**
```bash
# Vérifier que tous les modules sont disponibles
python -c "from src.hrneowave.gui.main_window import MainWindow; print('✅ Tous les modules OK')"
```

---

## 🎯 **Utilisation Recommandée**

### **Pour Utilisation Normale**
```bash
python lancer_chneowave_corrige.py
```

### **Pour Développement**
```bash
python main.py
```

### **Pour Tests**
```bash
python test_interface_finale.py
```

---

## 🔍 **Résolution de Problèmes**

### **Si l'interface ne s'affiche pas :**
```bash
# 1. Test Qt basique
python test_qt_minimal.py

# 2. Diagnostic complet
python diagnostic_chneowave_affichage.py

# 3. Version corrigée
python lancer_chneowave_corrige.py
```

### **Si erreurs d'import :**
```bash
# Vérifier les dépendances
pip install -r requirements.txt

# Test d'import
python -c "import PySide6; print('✅ PySide6 OK')"
```

---

## 📋 **Résumé des Commandes**

| Commande | Usage | Statut |
|----------|-------|--------|
| `python lancer_chneowave_corrige.py` | **Production** | ✅ **RECOMMANDÉ** |
| `python main.py` | Développement | ✅ Fonctionnel |
| `python -m hrneowave --gui` | CLI | ✅ Fonctionnel |
| `python validation_chneowave.py` | Test | ✅ Validation |
| `python diagnostic_chneowave_affichage.py` | Debug | 🔧 Diagnostic |

---

## 🎉 **Interface Complète**

Une fois lancé, CHNeoWave offre :

- 🏠 **Interface d'accueil** avec sélection de projet
- 📊 **Tableau de bord maritime** temps réel
- 📡 **Module d'acquisition** de données
- ⚙️ **Calibration** des capteurs
- 📈 **Analyse** des données de houle
- 📄 **Génération de rapports** automatisée
- 🎨 **Thème maritime** professionnel
- 🧭 **Navigation fluide** entre modules

---

**🚀 Pour commencer immédiatement :**
```bash
python lancer_chneowave_corrige.py
```

**L'interface CHNeoWave s'ouvrira avec tous les modules intégrés et fonctionnels !**