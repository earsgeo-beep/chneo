<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# Prompt clé en main pour générer un main.py unique (matériel réel, 100% local, UI+API+Core)

Copier-coller ce prompt à l’agent pour qu’il crée un fichier main.py à la racine du projet qui lance:

- le backend FastAPI relié aux vrais modules core CHNeoWave (aucun mode demo),
- l’UI React en local,
- l’ouverture automatique du navigateur,
- avec healthcheck et arrêts propres.

-------------------------------------
PROMPT À DONNER À L’AGENT
-------------------------------------
Objectif:
Créer un fichier main.py unique à la racine du repo CHNeoWave qui lance toute la pile en local (offline), en mode matériel réel uniquement (aucun simulateur/demo), pour tester l’interface React avec le core Python connecté aux drivers/SDK réels.

Contexte:

- Backend: FastAPI + WebSocket, app exposée dans backend_bridge_api.py sous la variable app = FastAPI(...).
- Core Python: modules réels (AcquisitionController, HardwareManager, FFTProcessor, SignalBus, etc.) déjà intégrés au bridge (pas de mocks).
- UI: React/Vite, servie en dev sur le port 5173, code dans le dossier frontend/ (variable VITE_API_URL pointant vers http://127.0.0.1:3001).
- WebSocket: flux temps réel depuis l’API backend (10Hz typiquement).
- Offline total: tout doit tourner sur localhost, sans aucune ressource externe (CDN, télémétrie, etc.).

Exigences techniques:

1) main.py doit:
    - Lancer le backend uvicorn sur 127.0.0.1:3001, sans reload, et en “mode réel” strict.
    - Attendre que le healthcheck GET /health réponde OK, sinon réessayer (timeout global 30s).
    - Lancer l’UI React:
        - Si un build prod existe (frontend/dist), servir ce build localement avec un petit serveur Python (http.server) sur 127.0.0.1:5173.
        - Sinon, lancer npm run dev dans frontend/ (avec vérification préalable de node_modules et npm install si absent).
    - Ouvrir automatiquement le navigateur par défaut sur http://127.0.0.1:5173.
    - Afficher des logs lisibles (préfixes [API], [UI], [HEALTH], [MAIN]).
    - Gérer l’arrêt propre: Ctrl+C stoppe UI puis API; tuer les sous‑process proprement.
2) Mode matériel réel seulement:
    - Forcer une variable d’environnement côté backend indiquant le mode réel, ex: BACKEND_MODE=real.
    - Désactiver explicitement toute initialisation “demo/simulateur”.
    - Si un matériel requis est absent, retourner une erreur claire côté /health, mais ne jamais basculer en mode faux flux.
3) Robustesse:
    - Avant de lancer l’UI, valider que l’API répond à /health et détecte les backends matériels disponibles (ex: ni-daqmx, iotech).
    - Timeout raisonnables et messages d’erreur utiles si API ne démarre pas.
    - Si le port 3001 ou 5173 est occupé, proposer les ports alternatifs 3002/5174 automatiquement et adapter VITE_API_URL à la volée (pour le mode dev), ou pour le build statique, afficher un message pour relancer avec un port libre.
4) Offline strict:
    - Host = 127.0.0.1 pour API et UI.
    - Aucun téléchargement CDN: si UI en mode dev dépend de CDN, documenter comment empêcher tout appel sortant.
    - main.py ne doit déclencher aucune requête extérieure.
5) Compatibilité:
    - Fonctionne sous Windows, macOS, Linux.
    - Détecter npm vs pnpm vs yarn si nécessaire; privilégier npm par défaut.
6) Healthcheck:
    - Endpoint: GET http://127.0.0.1:{BACKEND_PORT}/health
    - Attendre “status: ok” et “hardware_backends” contenant les drivers réels détectés.
    - Logger l’état détecté, sinon échouer avec message explicite.

Structure attendue du code:

- Fonctions utilitaires: find_free_port, wait_for_health, run_subprocess_with_logs.
- Thread pour l’API (uvicorn.run), subprocess pour l’UI (ou http.server pour dossier dist).
- Gestion signaux/KeyboardInterrupt et arrêt propre.

Variables/chemins:

- backend module: backend_bridge_api:app (adapter si l’app est ailleurs).
- dossier frontend: ./frontend
- port API par défaut: 3001; port UI par défaut: 5173.

Snippet de départ imposé (à adapter/compléter):
"""
import os, time, threading, subprocess, sys, socket, webbrowser
import uvicorn
import requests
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

BACKEND_HOST = "127.0.0.1"
BACKEND_PORT = int(os.environ.get("CHNEO_API_PORT", "3001"))
UI_HOST = "127.0.0.1"
UI_PORT = int(os.environ.get("CHNEO_UI_PORT", "5173"))
FRONTEND_DIR = Path(__file__).parent / "frontend"
USE_BUILD_IF_AVAILABLE = True  \# servir frontend/dist si présent
OPEN_BROWSER = True

def port_in_use(host, port):
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
return s.connect_ex((host, port)) == 0

def find_free_port(host, start_port, max_tries=20):
port = start_port
for _ in range(max_tries):
if not port_in_use(host, port):
return port
port += 1
raise RuntimeError(f"Aucun port libre trouvé à partir de {start_port}")

def start_backend():
os.environ["BACKEND_MODE"] = "real"
uvicorn.run("backend_bridge_api:app",
host=BACKEND_HOST,
port=BACKEND_PORT,
reload=False,
log_level="info")

def wait_for_health(timeout=30):
start = time.time()
url = f"http://{BACKEND_HOST}:{BACKEND_PORT}/health"
last_err = None
while time.time() - start < timeout:
try:
r = requests.get(url, timeout=2)
if r.ok:
data = r.json()
if data.get("status") == "ok":
print(f"[HEALTH] OK — backends: {data.get('hardware_backends')}")
return True
else:
print(f"[HEALTH] Non-OK: {data}")
else:
print(f"[HEALTH] HTTP {r.status_code}")
except Exception as e:
last_err = e
time.sleep(1)
print(f"[HEALTH] Échec healthcheck: {last_err}")
return False

def start_ui_dev():
\# Assure l’install si node_modules absent
if not (FRONTEND_DIR / "node_modules").exists():
print("[UI] npm install…")
subprocess.run(["npm", "install"], cwd=str(FRONTEND_DIR), check=True)
env = os.environ.copy()
env["VITE_API_URL"] = f"http://{BACKEND_HOST}:{BACKEND_PORT}"
print(f"[UI] VITE_API_URL={env['VITE_API_URL']}")
return subprocess.Popen(["npm", "run", "dev"], cwd=str(FRONTEND_DIR), env=env)

class DistHandler(SimpleHTTPRequestHandler):
def translate_path(self, path):
\# Servir depuis frontend/dist
root = FRONTEND_DIR / "dist"
full = root / path.lstrip("/")
if full.is_dir():
full = full / "index.html"
if not full.exists():
full = root / "index.html"
return str(full)

def start_ui_build():
handler = DistHandler
httpd = ThreadingHTTPServer((UI_HOST, UI_PORT), handler)
print(f"[UI] build servi sur http://{UI_HOST}:{UI_PORT}")
threading.Thread(target=httpd.serve_forever, daemon=True).start()
return httpd

if __name__ == "__main__":
print("=== CHNeoWave — Lancement complet (matériel réel, offline) ===")

    # Ports libres
    if port_in_use(BACKEND_HOST, BACKEND_PORT):
        BACKEND_PORT = find_free_port(BACKEND_HOST, BACKEND_PORT)
        print(f"[MAIN] Port API occupé, nouvel API_PORT={BACKEND_PORT}")
    
    if port_in_use(UI_HOST, UI_PORT):
        UI_PORT = find_free_port(UI_HOST, UI_PORT)
        print(f"[MAIN] Port UI occupé, nouvel UI_PORT={UI_PORT}")
    
    # Backend
    api_thread = threading.Thread(target=start_backend, daemon=True)
    api_thread.start()
    
    # Healthcheck
    if not wait_for_health(timeout=30):
        print("[MAIN] Échec du démarrage API — vérifie drivers/SDK matériels et logs backend.")
        sys.exit(1)
    
    # UI: build si présent, sinon dev
    ui_proc = None
    ui_httpd = None
    if USE_BUILD_IF_AVAILABLE and (FRONTEND_DIR / "dist" / "index.html").exists():
        ui_httpd = start_ui_build()
    else:
        ui_proc = start_ui_dev()
    
    if OPEN_BROWSER:
        url = f"http://{UI_HOST}:{UI_PORT}"
        print(f"[MAIN] Ouverture navigateur: {url}")
        try:
            webbrowser.open(url)
        except Exception:
            pass
    
    # Attente et arrêt propre
    try:
        if ui_proc:
            ui_proc.wait()
        else:
            while True:
                time.sleep(1)
    except KeyboardInterrupt:
        print("\n[MAIN] Arrêt demandé. Nettoyage…")
        if ui_proc and ui_proc.poll() is None:
            ui_proc.terminate()
            try:
                ui_proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                ui_proc.kill()
        print("[MAIN] Arrêté.")
    """

Livrables attendus:

- Fichier main.py fonctionnel et testé.
- Instructions courtes dans README/GUIDE_LANCEMENT_RAPIDE.md:
    - Pré-requis drivers matériels (NI‑DAQmx, iotech, etc.).
    - Commande: python main.py
    - URL UI: http://127.0.0.1:5173
    - Vérification: /health expose status: ok et backends réels détectés; WebSocket en temps réel OK.
- Aucune référence à un mode demo/simulateur dans le code de lancement; toute indisponibilité matérielle doit être remontée en erreur, pas “simulée”.

Critères d’acceptation:

- Lancement unique par python main.py.
- API joignable en 127.0.0.1:{port}/docs et /health → status: ok + backends matériels réels listés.
- UI opérationnelle, flux acquisition/FFT réels via WebSocket.
- Fonctionne offline complet (Internet coupé), sans appels sortants.
- Arrêt propre via Ctrl+C.
-------------------------------------

Souhaites-tu que je l’adapte à l’arborescence exacte de ton repo si tu me donnes les chemins de backend_bridge_api.py et du dossier frontend ?

<div style="text-align: center">⁂</div>

[^1]: BDD-INST-2025-Enregistre-automatiquement.xlsx

[^2]: index.html

