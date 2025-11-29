
🌊 CHNeoWave Integration Test Report
============================================================

📅 Date: 2025-08-14 15:12:08
📊 Tests: 9 total, 0 passed, 9 failed
✅ Success Rate: 0.0%

Detailed Results:
💥 API Health Check: ERROR (4.012s)
   Error: HTTPConnectionPool(host='localhost', port=3001): Max retries exceeded with url: /health (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x000001904E907770>: Failed to establish a new connection: [WinError 10061] Aucune connexion n’a pu être établie car l’ordinateur cible l’a expressément refusée'))
❌ UI Connectivity: FAIL (4.014s)
💥 CORS Configuration: ERROR (4.009s)
   Error: HTTPConnectionPool(host='localhost', port=3001): Max retries exceeded with url: /health (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x000001904E9F4050>: Failed to establish a new connection: [WinError 10061] Aucune connexion n’a pu être établie car l’ordinateur cible l’a expressément refusée'))
💥 Hardware Backends: ERROR (4.007s)
   Error: HTTPConnectionPool(host='localhost', port=3001): Max retries exceeded with url: /hardware/backends (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x000001904E8EBBB0>: Failed to establish a new connection: [WinError 10061] Aucune connexion n’a pu être établie car l’ordinateur cible l’a expressément refusée'))
💥 Hardware Scan: ERROR (4.018s)
   Error: HTTPConnectionPool(host='localhost', port=3001): Max retries exceeded with url: /hardware/scan (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x000001904E8EB490>: Failed to establish a new connection: [WinError 10061] Aucune connexion n’a pu être établie car l’ordinateur cible l’a expressément refusée'))
💥 System Status: ERROR (4.008s)
   Error: HTTPConnectionPool(host='localhost', port=3001): Max retries exceeded with url: /system/status (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x000001904E996690>: Failed to establish a new connection: [WinError 10061] Aucune connexion n’a pu être établie car l’ordinateur cible l’a expressément refusée'))
💥 Acquisition Status: ERROR (4.008s)
   Error: HTTPConnectionPool(host='localhost', port=3001): Max retries exceeded with url: /acquisition/status (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x000001904E991040>: Failed to establish a new connection: [WinError 10061] Aucune connexion n’a pu être établie car l’ordinateur cible l’a expressément refusée'))
💥 Acquisition Start/Stop: ERROR (4.02s)
   Error: HTTPConnectionPool(host='localhost', port=3001): Max retries exceeded with url: /acquisition/start (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x000001904E992140>: Failed to establish a new connection: [WinError 10061] Aucune connexion n’a pu être établie car l’ordinateur cible l’a expressément refusée'))
💥 FFT Processing: ERROR (4.013s)
   Error: HTTPConnectionPool(host='localhost', port=3001): Max retries exceeded with url: /processing/fft (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x000001904E992360>: Failed to establish a new connection: [WinError 10061] Aucune connexion n’a pu être établie car l’ordinateur cible l’a expressément refusée'))

🎯 Integration Status: ISSUES DETECTED

📋 Next Steps:
⚠️ 9 test(s) en échec
🔧 Vérifier la configuration des serveurs
📡 Vérifier les ports 3001 et 5173
🐛 Consulter les logs pour plus de détails