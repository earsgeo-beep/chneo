# 🔧 Solutions pour les erreurs MCP Windsurf

## 🚨 Problèmes identifiés

### Erreur 1: `uvx` executable non trouvé
```
Error: failed to create mcp stdio client: failed to start stdio transport: failed to start command: exec: "uvx": executable file not found in %PATH%
```

### Erreur 2: Répertoire chneowave manquant
```
Error: ENOENT: no such file or directory, stat 'C:\Users\youcef cheriet\AppData\Local\Programs\Windsurf\chneowave'
```

---

## ✅ **Solution 1: Installer et configurer UV/UVX**

### Option A: Installation via pip (Recommandée)
```powershell
# Dans votre environnement virtuel CHNeoWave
cd "C:\Users\youcef cheriet\Desktop\chneowave"
.\venv\Scripts\activate
pip install uv

# Ajouter uv au PATH global
$uvPath = "C:\Users\youcef cheriet\Desktop\chneowave\venv\Scripts"
$currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($currentPath -notlike "*$uvPath*") {
    [Environment]::SetEnvironmentVariable("Path", "$currentPath;$uvPath", "User")
}
```

### Option B: Installation via PowerShell (Alternative)
```powershell
# Installation directe d'UV
irm https://astral.sh/uv/install.ps1 | iex

# Redémarrer PowerShell après installation
```

### Option C: Créer un alias uvx
```powershell
# Créer un script uvx.bat dans le PATH
$uvxScript = @"
@echo off
uv run %*
"@
$uvxScript | Out-File -FilePath "C:\Windows\System32\uvx.bat" -Encoding ASCII
```

---

## ✅ **Solution 2: Configurer le répertoire Windsurf**

### Méthode 1: Lien symbolique (Nécessite droits admin)
```powershell
# Exécuter PowerShell en tant qu'administrateur
New-Item -ItemType SymbolicLink -Path "C:\Users\youcef cheriet\AppData\Local\Programs\Windsurf\chneowave" -Target "C:\Users\youcef cheriet\Desktop\chneowave" -Force
```

### Méthode 2: Junction (Alternative sans admin)
```powershell
# Créer une junction (ne nécessite pas de droits admin)
cmd /c mklink /J "C:\Users\youcef cheriet\AppData\Local\Programs\Windsurf\chneowave" "C:\Users\youcef cheriet\Desktop\chneowave"
```

### Méthode 3: Configuration MCP alternative
Modifier la configuration MCP pour pointer vers le bon répertoire :

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "C:\\Users\\youcef cheriet\\Desktop\\chneowave"],
      "env": {}
    }
  }
}
```

---

## ✅ **Solution 3: Script de résolution automatique**

Créer un script PowerShell pour automatiser la résolution :

```powershell
# fix_mcp_issues.ps1
Write-Host "🔧 Résolution des problèmes MCP Windsurf..." -ForegroundColor Green

# 1. Installer UV si nécessaire
try {
    uv --version | Out-Null
    Write-Host "✅ UV déjà installé" -ForegroundColor Green
} catch {
    Write-Host "📦 Installation d'UV..." -ForegroundColor Yellow
    irm https://astral.sh/uv/install.ps1 | iex
}

# 2. Créer le répertoire Windsurf
$windsurfPath = "C:\Users\youcef cheriet\AppData\Local\Programs\Windsurf\chneowave"
$projectPath = "C:\Users\youcef cheriet\Desktop\chneowave"

if (!(Test-Path $windsurfPath)) {
    Write-Host "📁 Création du lien vers le projet..." -ForegroundColor Yellow
    try {
        # Essayer junction d'abord
        cmd /c mklink /J "$windsurfPath" "$projectPath" 2>$null
        Write-Host "✅ Junction créée avec succès" -ForegroundColor Green
    } catch {
        # Fallback: copie des fichiers essentiels
        Write-Host "📋 Copie des fichiers essentiels..." -ForegroundColor Yellow
        New-Item -ItemType Directory -Path $windsurfPath -Force
        Copy-Item -Path "$projectPath\*.py" -Destination $windsurfPath -Force
        Copy-Item -Path "$projectPath\*.md" -Destination $windsurfPath -Force
        Copy-Item -Path "$projectPath\*.txt" -Destination $windsurfPath -Force
        Copy-Item -Path "$projectPath\*.toml" -Destination $windsurfPath -Force
        Copy-Item -Path "$projectPath\src" -Destination $windsurfPath -Recurse -Force -ErrorAction SilentlyContinue
    }
}

Write-Host "🎉 Problèmes MCP résolus !" -ForegroundColor Green
Write-Host "Redémarrez Windsurf pour appliquer les changements." -ForegroundColor Cyan
```

---

## ✅ **Solution 4: Configuration Windsurf MCP**

Modifier le fichier de configuration Windsurf (généralement dans `%APPDATA%\Windsurf\User\settings.json`) :

```json
{
  "mcp.servers": {
    "filesystem": {
      "command": "C:\\Users\\youcef cheriet\\Desktop\\chneowave\\venv\\Scripts\\python.exe",
      "args": ["-m", "mcp_server_filesystem", "C:\\Users\\youcef cheriet\\Desktop\\chneowave"],
      "env": {}
    }
  }
}
```

---

## 🚀 **Instructions d'application**

### Étape 1: Choisir une solution
- **Pour uvx**: Utilisez la Solution 1, Option A (recommandée)
- **Pour le répertoire**: Utilisez la Solution 2, Méthode 2 (junction)

### Étape 2: Exécuter les commandes
```powershell
# Solution complète en une fois
cd "C:\Users\youcef cheriet\Desktop\chneowave"

# Installer UV dans l'environnement virtuel
.\venv\Scripts\activate
pip install uv

# Créer junction vers Windsurf
cmd /c mklink /J "C:\Users\youcef cheriet\AppData\Local\Programs\Windsurf\chneowave" "C:\Users\youcef cheriet\Desktop\chneowave"

# Ajouter UV au PATH
$uvPath = "C:\Users\youcef cheriet\Desktop\chneowave\venv\Scripts"
$env:PATH += ";$uvPath"
```

### Étape 3: Redémarrer Windsurf
Fermez et rouvrez Windsurf pour que les changements prennent effet.

---

## 🔍 **Vérification**

Après application des solutions, vérifiez :

```powershell
# Vérifier UV
uv --version

# Vérifier le répertoire
Test-Path "C:\Users\youcef cheriet\AppData\Local\Programs\Windsurf\chneowave"

# Vérifier les fichiers
Get-ChildItem "C:\Users\youcef cheriet\AppData\Local\Programs\Windsurf\chneowave"
```

---

## 📞 **Support**

Si les problèmes persistent :
1. Redémarrez votre système
2. Vérifiez les permissions de fichiers
3. Exécutez PowerShell en tant qu'administrateur
4. Consultez les logs Windsurf pour plus de détails

**🎯 Ces solutions devraient résoudre complètement vos erreurs MCP !**
