=====================================================================
                        DAQami(tm) Version 4.2.1 Software ReadMe
                          Measurement Computing Corporation
======================================================================

1. Einführung
2. Installation
3. Erste Schritte
4. Neue Funktionen
5. Support und Kontakt
6. Bekannte Probleme
7. Gelöste Probleme


===============
1. Einführung
===============
DAQami ist eine Data Acquisition Companion Software "out-of-the-box " zur 
Erfassung, Visualisierung und Speicherung von analogen, digitalen und
Zähler-Messdaten, sowie zur Signalgenerierung und -ausgabe mit den
unterstützten Messgeräten von Measurement Computing. 

Sie konfigurieren die Geräte und Kanäle als Datenquellen, starten die
Erfassung und verfolgen die Messdaten auf einer beliebigen Kombination 
aus Numerischen Anzeigen, Linienschreibern und Oszilloskopen. Messdaten
der ausgewählten Kanäle können in TDMS-Dateien für eine spätere Analyse
gespeichert und in .csv -Dateien exportiert werden. Sie können ebenso
die Einstellungen zu Gerät, Kanal, Erfassungrate, Trigger und Anzeigen
speichern.


=======================
2. Installation
=======================
WICHTIG: Installieren Sie DAQami vor dem Anschluss eines unterstützten
MCC Messgerätes.

Die Installation von DAQami enthält die automatische
Installationsdatei DAQami.exe. 


=======================
3. Erste Schritte
=======================
Nach der Installation von DAQami kann das Gerät verbunden werden
und die Treiber werden geladen. Sind die Treiber geladen, kann
DAQami gestartet werden. 


========================
4. Neue Funktionen
========================
Version 4.2.1
* Problem beseitigt mit dem Auto Export von aufeinanderfolgenden kurzen Erfassungen 
* Problem beseitigt mit dem Erfassen über einen kurzen Zeitraum (weniger als eine Stunde) und bei niedrigen Erfassungsraten
  (10 S/s - 1000 S/s)
* Speicherproblem gelöst bei lang laufenden Erfassungen innerhalb von Linienschreiber und Oszilloskop 
* Geschwindigkeit verbessert beim Schreiben von TDMS-Dateien


Version 4.2.0
* Unterstützt die Geräte der USB-1808 Serie, inklusive synchronem 
  I/O-Betrieb (composite)
* Neue Optionen zur Spezifizierung des Dezimalformats, der  
  Trennzeichen, sowie das Setzen von Werten in Anführungszeichen
  beim Export in eine .csv.-Datei
* Maximale Länge des Kanalnamens erhöht von 10 auf 25 Zeichen
* Spachunterstützung für Deutsch und Chinesisch

Version 4.1.0
* Sprachunterstützung für Deutsch und Chinesisch
* Probleme mit der Lokalisierung beim Abspeichern im TDMS-Format behoben 

Version 4.0.0
* Speichert eine theoretisch unbegrenzte Zahl von Messwerten pro Kanal
* Unterstützt mehrere Geräte
* Anzeige-Einstellungen in eine vorhandene Datendatei speichern
* Anzeige von digitalen Bits als LEDs auf einer Numerischen Anzeige
* Unterstützt das TDMS-Dateiformat

Version 3.0.1
* Sprachunterstützung Deutsch
* Behebt Problem 584557

Version 3.0
* Ausgabe von analogen, digitalen und Counter-Signalen
* Kabelbrucherkennung für Thermoelemente
* Analoges Hardware-Triggern
* Kanäle können auf einer Anzeige umgruppiert werden
* Ein oder mehrere Cursor können während der Erfassung hinzugefügt werden
* Numerische Anzeige zeigt Minimum, Maximum und Mittelwerte
* 30-Tage Testlizenz; Messdatenspeicherung und -export wird nach 30 Tagen 
  ohne Volllizenz deaktiviert


Version 2.1 
* Unterstützt gemischte Signale (hardware- und softwaregetaktet) in derselben Anzeige.
* Verbesserter Zeitstempel für die erfassten Messdaten.
* Sprachunterstützung Chinesisch


=======================================
5. Support und Kontakt 
=======================================
Kontaktieren Sie Measurement Computing, wenn Sie technischen Support benötigen.

Für Kunden in den USA:

Measurement Computing
10 Commerce Way
Norton, MA 02766
Phone: (508) 946-5100
www.mccdaq.com
info@mccdaq.com

Für Kunden in Europa:

Measurement Computing
Im Weilerlen 10
74321 Bietigheim-Bissingen
Deutschland
Tel.: +49 (0)7142-9531-0
www.mccdaq.de
support@mccdaq.de

Kunden außerhalb der USA und Europa sollten ihren Händler kontaktieren:

www.mccdaq.com/distributors.


=======================================
6. Bekannte Probleme
=======================================

----------------
Analoge Ausgabe
----------------

|579129|
Wenn zumindest ein hardware-getakteter analoger Ausgangskanal aktiviert ist, 
verursacht die Veränderung auf einem Schieberegler für einen anderen Kanal
einen Störimpuls auf allen weiteren (sowohl hardware- als auch software-
getakteten) Ausgabekanälen.
Es gibt gegenwärtig keinen Workaround für dieses Verhalten.

–––––––––––––
Konfiguration
––––––––––––-

|473375|
Bei einigen Geräten müssen einige Konfigurationseinstellungen mit 
InstaCal durchgeführt werden:

* E-1608, E-DIO24, E-TC, TC-32: konfigurieren Sie Verbindungscode, Alarm und manuelle 
  Netzwerkeinstellungen (IP-Adresse usw.) vor dem Start von DAQami mit InstaCal.  
  DAQami kann unabhängig von dem in DAQami eingegebenen Code mit jedem
  Gerät verbinden, dessen Verbindungscode mit InstaCal auf "0" gesetzt wurde.

* USB-TEMP, USB-TEMP-AI, USB-5203: konfigurieren Sie in InstaCal Messungen mit 
  Widerstandssensoren, Thermistoren und Halbleitersensoren vor dem Starten von DAQami.
  
 |612016|
 Die automatische Konfiguration blockiert nach dem ersten Verbinden eines USB-TC-AI.
 
 Wird ein USB-TEMP-AI nach dem Start von DAQami über die automatische Konfiguration 
 das erste Mal hinzugefügt, blockiert die Konfiguration.
 
 Workaround: Schließen Sie DAQami, trennen Sie das USB-Kabel vom USB-TEMP-AI, 
 verbinden Sie es erneut mit dem USB und starten Sie DAQami neu.

-–––––-------
Daten-Logging
–-––––-------

|405216|
DAQami prüft während der Erfassung nicht den verfügbaren Speicherplatz. 

Workaround: Prüfen Sie vor der Erfassung einer großen Anzahl von
Messwerten den verfügbaren Speicherplatz.

–––––––––––––
Ausführung
––––––––––––-

|621259|
Wenn DAQami durch den Start einer weiteren MCC-Applikation wie InstaCal, einer mit
der Universal Library erstellten Applikation oder TracerDAQ(R) angehalten wird, dann
informiert DAQami nicht darüber, dass die Erfassung angehalten worden ist.

Wenn eine dieser Anwendungen während der Erfassung gestartet und dann beendet wird,
wird die Erfassung in DAQami angehalten, es erscheint jedoch keine Fehlermeldung und 
der Status meldet weiter aktiv. 

Workaround: Speichern Sie die Konfiguration, beenden Sie DAQami und die andere Anwendung 
und starten Sie DAQami und die Erfassung erneut.

-----------------------------------
Gleichzeitige Erfassung und Ausgabe
-----------------------------------

|611365|
Wird ein Gerät zur Erfassung und ein weiteres zur Ausgabe konfiguriert,
werden Signale unterhalb von 1 kS/s verzögert ausgegeben.

Wird ein Gerät zur Erfassung und ein weiteres zur Ausgabe konfiguriert,
liegt beim Start der Erfassung kein Signal zur Ausgabe an. Für Erfassung bei 1 kS/s 
ändert sich der Ausgabewert erst nach ungefähr 15 bis 70 ms (unterscheidet sich von
Wert zu Wert). Die Ausgabe wurde konfiguriert für einen Kanal und 1 Hz Signal.

Dieses Verhalten tritt auch bei einen einzelnen Gerät auf, das gleichzeitig erfasst und Signale ausgibt. 

–––––––-
Hardware
–––––––-

|480626|
miniLAB 1008 kann nur DIO0 als Triggerkanal verwenden unabhängig
von den Einstellungen in InstaCal.

Workaround: DAQami ignoriert die Auswahl einer anderen Triggerquelle
als DIO0.

-------------------
Hardware- Trigger
-------------------

|611738|
Ein Hardware-Trigger, der zwei Geräte benutzt, unterscheidet sich gelegentlich um 25 bis 75 ms 
zwischen Geräten, die mit 1 kHz erfassen. Wird der Start-Trigger auf Flankenerkennung und der Stopp-Trigger
auf einen Wert zwischen 100 und 1000 Messwerten gesetzt, ist das Triggersignal bis zu 75 ms
versetzt bei Erfassung eines Kanals auf jedem Gerät. Dies geschieht häufig (aber nicht immer)
bei Erfassung nach Änderung des Messwertzählers für den Stopp-Trigger.

-----
Hilfe
-----

|623684|
Mit älteren Browser-Versionen können Probleme beim Betrachten der DAQami Hilfe auftreten.

Sie könnten Probleme feststellen beim Betrachten von eingebetteten Videos, Grafiken
und anderen Inhalten, falls Sie einen Browser verwenden vor Internet Explorer 8, der 
mit Windows 7 eingeführt wurde. 

Workaround: Measurement Computing empfiehlt die Installation der aktuellen Browser-Version zum
Betrachten der Hilfe.

|479449|
Aktiver Inhalt (eingebettete Videos) in der DAQami Hilfe können nicht
mit dem Internet Explorer betrachtet werden. 

Workaround: Ändern Sie die IE Sicherheitseinstellungen, um aktiven Inhalt ausführen
zu können (Optionen > Advanced) und starten Sie den Internet Explorer neu.


==========================
7. Behobene Probleme
==========================

Version 4.2.0

|636424| Gespeicherte Konfigurationsdateien für Geräte der USB-CTR und 
USB-2416 Serien können nicht geöffnet werden.

Konfigurationsdateien für Geräte der USB-CTR und USB-2416 Serien können jetzt 
in DAQami geöffnet werden.



Version 4.0.0

|381519| Sich überschneidende Cursorwerte können gelesen werden, indem 
die Anzeige vergrößert wird.

|387230| Die Performance ist verlangsamt, unmittelbar nachdem der PC aus dem
Ruhemode aktiviert wird. Suchen Sie in der Dokumentation und im Support Ihres PCs
nach Hinweisen, wie dieses Verhalten optimiert werden kann.

|401042| Die Daten auf einem Linienschreiber rollen nun in der Anzeige, sobald die
Cursor über den rechten oder linken Rand der Grafik bewegt werden. Cursor können
nicht mehr über den rechten oder linken Rand eines Oszilloskop-Anzeigebereichs bewegt werden.

|458346| Eine DAQami-Installation wird nicht fortgesetzt, ehe DAQami beendet wird.
Wenn DAQami während eines Deinstallationsvorgangs ausgeführt wird,
wird es nach dem nächsten Neustart komplett deinstalliert.

|473375| Geräte der USB-2408 und USB-2416 Serie können nun in DAQami
für single-ended oder differentielle Erfassung konfiguriert werden.

|484230| Mit der Unterstützung für mehrere Geräte in DAQami 4.0.0 erzeugt das
Hinzufügen eines Gerätes nicht automatisch eine neue Konfiguration. In dieser Konstellation
muss deshalb die Konfiguration nicht länger gespeichert werden.

|519476| USB-1608HS unterstützt jetzt Erfassungen im Modus Single-Ended mit DAQami. 

|520375| Nach Systemabsturz und Neustart starten die MCC Messgeräte jetzt eine neue Erfassung.


Version 3.0.1

|584557| DAQami wird ohne Probleme beendet, wenn Befehle zum Speichern und 
Beenden mit installiertem .NET Framework 4.6.1 ausgeführt werden.


Version 3.0

|484227| Die X-Achse positioniert während einer Erfassung richtig zu den Messdaten.

|468991| Alle Anzeigen sind mit der verstrichenen Zeit synchronisiert.

|488124| Unterstützung für Bluetooth-Kommunikation hinzugefügt.


Version 2.1

|458102| Eine Meldung erscheint, wenn versucht wird, eine Konfigurationsdatei
zu öffnen, die verschoben oder gelöscht wurde.

|463679| Der Klick auf "Aktualisieren" aktualisiert sofort die Liste der verfügbaren Geräte.

|473795| Unterstützung für softwaregetaktete Erfassung.

|487854| Ein Kanal kann mit Hilfe der <Strg>-Taste kopiert werden.

|521786| Manuelle und remote Netzwerkeinstellungen können in der
Geräteliste geändert werden.




Document Revision 5.0
