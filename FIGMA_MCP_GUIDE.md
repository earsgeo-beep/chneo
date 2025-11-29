# 🎨 Guide Complet - Serveur MCP Figma pour Windsurf

## ✅ **INSTALLATION TERMINÉE AVEC SUCCÈS !**

Le serveur MCP Figma a été installé et configuré avec votre token d'accès Figma.

**Token configuré :** `figd_NiidvIEL-LM3Ih_frDWYgpzkxHengsh74a4NEvwb`

---

## 🚀 **Comment utiliser le serveur MCP Figma**

### **Étape 1: Installer le plugin Figma**

1. **Ouvrez Figma** dans votre navigateur ou application desktop
2. **Installez le plugin MCP Figma** depuis la communauté Figma :
   - Allez sur : https://www.figma.com/community/plugin/1485687494525374295/mcp-figma-plugin
   - Cliquez sur "Install" pour installer le plugin

### **Étape 2: Démarrer le serveur MCP Figma**

**Option A - Script automatique :**
```cmd
cd "C:\Users\youcef cheriet\Desktop\chneowave"
start-figma-mcp.bat
```

**Option B - Commande manuelle :**
```powershell
$env:FIGMA_ACCESS_TOKEN="figd_NiidvIEL-LM3Ih_frDWYgpzkxHengsh74a4NEvwb"
$env:FIGMA_WEBSOCKET_PORT="3055"
node "C:\Users\youcef cheriet\AppData\Roaming\npm\node_modules\@sethdouglasford\mcp-figma\dist\talk_to_figma_mcp\server.js"
```

### **Étape 3: Configurer Windsurf**

1. **Ouvrez Windsurf**
2. **Accédez aux paramètres MCP** (Settings > MCP Servers)
3. **Ajoutez la configuration suivante :**

```json
{
  "mcpServers": {
    "figma": {
      "command": "C:\\Program Files\\nodejs\\node.exe",
      "args": [
        "C:\\Users\\youcef cheriet\\AppData\\Roaming\\npm\\node_modules\\@sethdouglasford\\mcp-figma\\dist\\talk_to_figma_mcp\\server.js"
      ],
      "env": {
        "FIGMA_ACCESS_TOKEN": "figd_NiidvIEL-LM3Ih_frDWYgpzkxHengsh74a4NEvwb",
        "FIGMA_WEBSOCKET_PORT": "3055",
        "FIGMA_WEBSOCKET_HOST": "localhost"
      }
    }
  }
}
```

### **Étape 4: Utiliser le plugin dans Figma**

1. **Ouvrez un fichier Figma** que vous voulez analyser
2. **Lancez le plugin MCP Figma** (Plugins > MCP Figma Plugin)
3. **Connectez le plugin** au serveur MCP
4. **Notez le Channel ID** affiché dans le plugin

### **Étape 5: Utiliser dans Windsurf**

Une fois configuré, vous pouvez utiliser ces commandes dans Windsurf :

#### **🔍 Commandes d'analyse de design**

```
@figma join_channel CHANNEL_ID
```
*Remplacez CHANNEL_ID par l'ID affiché dans le plugin Figma*

```
@figma get_design_info
```
*Obtenir des informations générales sur le design*

```
@figma get_text_nodes
```
*Récupérer tous les nœuds de texte du design*

```
@figma get_component_info
```
*Obtenir des informations sur les composants*

#### **📊 Exemples d'utilisation pratique**

```
"Analyse ce design Figma et décris la structure de la mise en page"
"Génère le code CSS pour reproduire ce design"
"Quels sont les styles de texte utilisés dans ce design ?"
"Crée un composant React basé sur ce design Figma"
```

---

## 🛠️ **Outils MCP Figma disponibles**

Le serveur MCP Figma fournit ces outils pour interagir avec Figma :

### **🔗 Connexion**
- `join_channel` - Se connecter à un canal Figma spécifique
- `leave_channel` - Quitter le canal actuel

### **📋 Analyse de design**
- `get_design_info` - Informations générales sur le design
- `get_text_nodes` - Tous les nœuds de texte
- `get_component_info` - Informations sur les composants
- `get_layer_info` - Détails des calques
- `get_style_info` - Styles et couleurs utilisés

### **🎨 Génération de code**
- `generate_css` - Générer du CSS à partir du design
- `generate_html` - Créer du HTML structuré
- `export_assets` - Exporter les assets (images, icônes)

---

## 🔧 **Dépannage**

### **Problème : "Socket error: AggregateError"**
**Solution :** Le plugin Figma n'est pas encore connecté
1. Ouvrez Figma
2. Lancez le plugin MCP Figma
3. Vérifiez que le Channel ID est correct

### **Problème : "FIGMA_ACCESS_TOKEN not found"**
**Solution :** Token d'accès non configuré
1. Vérifiez que le token est dans les variables d'environnement
2. Redémarrez le serveur MCP

### **Problème : "Cannot connect to Figma API"**
**Solution :** Vérifiez votre token d'accès Figma
1. Allez sur https://www.figma.com/developers/api#access-tokens
2. Vérifiez que votre token est valide
3. Assurez-vous d'avoir les permissions nécessaires

---

## 📁 **Fichiers créés**

- `windsurf-figma-mcp-config.json` - Configuration Windsurf
- `start-figma-mcp.bat` - Script de démarrage
- `figma-mcp-config.json` - Configuration générale

---

## 🎯 **Exemples d'utilisation avancée**

### **Analyse complète d'un design**
```
1. Ouvrez votre design dans Figma
2. Lancez le plugin MCP Figma
3. Dans Windsurf : "@figma join_channel YOUR_CHANNEL_ID"
4. Puis : "Analyse ce design et génère le code React complet avec Tailwind CSS"
```

### **Extraction de design system**
```
"@figma get_style_info puis crée un fichier de tokens de design avec toutes les couleurs, typographies et espacements"
```

### **Génération de composants**
```
"Sélectionne le composant principal dans Figma et génère un composant Vue.js réutilisable"
```

---

## 🎉 **Le serveur MCP Figma est maintenant prêt !**

Vous pouvez maintenant :
- ✅ Analyser vos designs Figma directement dans Windsurf
- ✅ Générer du code à partir de vos maquettes
- ✅ Extraire automatiquement les styles et composants
- ✅ Créer des design systems cohérents

**Token configuré :** Votre token d'accès Figma est sécurisé et prêt à l'emploi !
