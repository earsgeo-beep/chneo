# Guide de Déploiement - Base de Données d'Instrumentation Maritime

## Vue d'ensemble

Ce guide détaille le déploiement complet de la solution moderne de gestion d'équipements d'instrumentation maritime, comprenant :
- Base de données PostgreSQL
- API Backend FastAPI
- Interface Web moderne
- Outils d'administration

## Prérequis

### Système
- **OS** : Windows 10/11, Linux (Ubuntu 20.04+), macOS
- **RAM** : 8 GB minimum, 16 GB recommandé
- **Stockage** : 50 GB d'espace libre
- **Réseau** : Accès Internet pour l'installation des dépendances

### Logiciels
- **Python 3.9+** : [https://www.python.org/downloads/](https://www.python.org/downloads/)
- **PostgreSQL 15+** : [https://www.postgresql.org/download/](https://www.postgresql.org/download/)
- **Git** : [https://git-scm.com/downloads](https://git-scm.com/downloads/)
- **Node.js 18+** (optionnel pour le développement frontend)

## Installation

### 1. Configuration de la Base de Données

#### Installation PostgreSQL
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install postgresql postgresql-contrib

# Windows
# Télécharger et installer depuis postgresql.org

# macOS
brew install postgresql
```

#### Configuration initiale
```sql
-- Se connecter en tant que postgres
sudo -u postgres psql

-- Créer la base de données
CREATE DATABASE instrumentation_maritime;

-- Créer un utilisateur dédié
CREATE USER maritime_user WITH PASSWORD 'secure_password_2025';

-- Accorder les privilèges
GRANT ALL PRIVILEGES ON DATABASE instrumentation_maritime TO maritime_user;

-- Quitter
\q
```

#### Exécution du schéma
```bash
# Exécuter le script de création du schéma
psql -U maritime_user -d instrumentation_maritime -f database_schema.sql
```

### 2. Configuration du Backend

#### Installation des dépendances Python
```bash
# Créer un environnement virtuel
python -m venv venv

# Activer l'environnement virtuel
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

# Installer les dépendances
cd backend
pip install -r requirements.txt
```

#### Configuration des variables d'environnement
Créer un fichier `.env` dans le dossier `backend/` :
```env
# Base de données
DATABASE_URL=postgresql://maritime_user:secure_password_2025@localhost/instrumentation_maritime

# Sécurité
SECRET_KEY=your-super-secret-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=False

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080,http://127.0.0.1:5500

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/api.log
```

### 3. Démarrage des Services

#### Lancement du Backend
```bash
cd backend
python app.py

# Ou avec uvicorn
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

#### Lancement du Frontend
```bash
cd frontend

# Option 1: Serveur Python simple
python -m http.server 8080

# Option 2: Serveur Node.js (si installé)
npx serve . -p 8080

# Option 3: Live Server (VS Code extension)
# Clic droit sur index.html > "Open with Live Server"
```

### 4. Vérification de l'Installation

#### Tests de connectivité
```bash
# Test de l'API
curl http://localhost:8000/health

# Test de la base de données
psql -U maritime_user -d instrumentation_maritime -c "SELECT COUNT(*) FROM services;"
```

#### Accès à l'interface
- **Frontend** : [http://localhost:8080](http://localhost:8080)
- **API Documentation** : [http://localhost:8000/docs](http://localhost:8000/docs)
- **API Alternative** : [http://localhost:8000/redoc](http://localhost:8000/redoc)

## Configuration de Production

### 1. Sécurité

#### Base de données
```sql
-- Créer des utilisateurs avec privilèges limités
CREATE USER maritime_read WITH PASSWORD 'read_password';
CREATE USER maritime_write WITH PASSWORD 'write_password';

-- Accorder des privilèges spécifiques
GRANT SELECT ON ALL TABLES IN SCHEMA public TO maritime_read;
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO maritime_write;
```

#### Variables d'environnement de production
```env
DATABASE_URL=postgresql://maritime_user:STRONG_PASSWORD@db-server:5432/instrumentation_maritime
SECRET_KEY=GENERATE-A-STRONG-SECRET-KEY-HERE
API_DEBUG=False
ALLOWED_ORIGINS=https://yourdomain.com
LOG_LEVEL=WARNING
```

### 2. Déploiement avec Docker

#### Dockerfile pour le Backend
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Docker Compose
```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: instrumentation_maritime
      POSTGRES_USER: maritime_user
      POSTGRES_PASSWORD: secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./database_schema.sql:/docker-entrypoint-initdb.d/schema.sql
    ports:
      - "5432:5432"

  backend:
    build: .
    environment:
      DATABASE_URL: postgresql://maritime_user:secure_password@db:5432/instrumentation_maritime
    ports:
      - "8000:8000"
    depends_on:
      - db

  frontend:
    image: nginx:alpine
    volumes:
      - ./frontend:/usr/share/nginx/html
    ports:
      - "80:80"
    depends_on:
      - backend

volumes:
  postgres_data:
```

### 3. Sauvegarde et Restauration

#### Script de sauvegarde automatique
```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"
DB_NAME="instrumentation_maritime"
DB_USER="maritime_user"

# Créer le dossier de sauvegarde
mkdir -p $BACKUP_DIR

# Sauvegarde de la base de données
pg_dump -U $DB_USER -h localhost $DB_NAME > $BACKUP_DIR/backup_$DATE.sql

# Compression
gzip $BACKUP_DIR/backup_$DATE.sql

# Nettoyage des anciennes sauvegardes (garder 30 jours)
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +30 -delete

echo "Sauvegarde terminée: backup_$DATE.sql.gz"
```

#### Restauration
```bash
# Restaurer depuis une sauvegarde
gunzip backup_20250812_140000.sql.gz
psql -U maritime_user -d instrumentation_maritime < backup_20250812_140000.sql
```

## Maintenance et Monitoring

### 1. Logs et Monitoring

#### Configuration des logs
```python
# backend/logging_config.py
import logging
from logging.handlers import RotatingFileHandler

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            RotatingFileHandler('logs/api.log', maxBytes=10485760, backupCount=5),
            logging.StreamHandler()
        ]
    )
```

#### Monitoring des performances
```sql
-- Requêtes pour surveiller les performances
SELECT schemaname, tablename, n_tup_ins, n_tup_upd, n_tup_del 
FROM pg_stat_user_tables;

-- Index les plus utilisés
SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read, idx_tup_fetch 
FROM pg_stat_user_indexes 
ORDER BY idx_scan DESC;
```

### 2. Maintenance Préventive

#### Tâches quotidiennes
- Vérification des logs d'erreur
- Contrôle de l'espace disque
- Sauvegarde automatique

#### Tâches hebdomadaires
- Analyse des performances de la base de données
- Mise à jour des statistiques PostgreSQL
- Vérification des alertes métrologiques

#### Tâches mensuelles
- Mise à jour des dépendances
- Audit de sécurité
- Test de restauration des sauvegardes

## Dépannage

### Problèmes Courants

#### Erreur de connexion à la base de données
```bash
# Vérifier le statut de PostgreSQL
sudo systemctl status postgresql

# Redémarrer si nécessaire
sudo systemctl restart postgresql

# Vérifier les connexions
sudo -u postgres psql -c "SELECT * FROM pg_stat_activity;"
```

#### Problèmes de performance
```sql
-- Identifier les requêtes lentes
SELECT query, mean_time, calls, total_time 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;

-- Analyser l'utilisation des index
SELECT schemaname, tablename, attname, n_distinct, correlation 
FROM pg_stats 
WHERE schemaname = 'public';
```

#### Erreurs d'API
```bash
# Vérifier les logs de l'API
tail -f logs/api.log

# Tester la connectivité
curl -v http://localhost:8000/health

# Vérifier les processus
ps aux | grep uvicorn
```

## Support et Contact

### Documentation Technique
- **API Documentation** : `/docs` endpoint
- **Architecture** : `ARCHITECTURE.md`
- **Schéma de base** : `database_schema.sql`

### Ressources Externes
- **FastAPI** : [https://fastapi.tiangolo.com/](https://fastapi.tiangolo.com/)
- **PostgreSQL** : [https://www.postgresql.org/docs/](https://www.postgresql.org/docs/)
- **Bootstrap** : [https://getbootstrap.com/docs/](https://getbootstrap.com/docs/)

### Support Technique
Pour toute assistance technique, consulter les logs et la documentation avant de contacter le support.

---

**Version** : 1.0.0  
**Date** : 2025-08-12  
**Auteur** : Nexus AI Software Architect
