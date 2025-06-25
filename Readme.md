# Einsatzleitsoftware Downloader Installer

Dieses Repository enthält ein Python-Skript `run.py`, das verwendet wird, um die Einsatzleitsoftware herunterzuladen und zu installieren.

## Voraussetzungen

Stellen Sie sicher, dass die folgenden Voraussetzungen erfüllt sind, bevor Sie das Skript ausführen:

- Python 3.7 oder höher ist installiert.

## Verwendung

1. Klonen Sie dieses Repository:
  ```bash
  git clone https://github.com/ThomasKra/Lageboard_downloader.git
  cd Lageboard_downloader
  ```

2. Erstellen Sie eine virtuelle Umgebung und aktivieren Sie diese:
  ```bash
  python -m venv venv
  source venv/bin/activate  # Für Windows: venv\Scripts\activate
  ```

3. Installieren Sie die Abhängigkeiten:
  ```bash
  pip install -r requirements.txt
  ```
4. Erstellen der notwendigen Dateien
  Erstelle eine .env Datei (z.B. durch Kopieren der .env_example) und trage den GITHUB_PERSONAL_ACCESS_TOKEN ein

  Im Unterordner configs/ muss die .env für die Laravel-Installation hinterlegt sein, sowie die user_seed.json die für die Initialisierung verwendet werden soll. Beispieldateien sind im Repository vorhanden. Die Dateien müssen an die Installation angepasst werden.

5. Führen Sie das Skript aus:
  ```bash
  python run.py
  ```
  Es wird automatisch die aktuellste Version heruntergeladen, installiert und ggf. eine frische Migration durchgeführt.

6. Bereite die Instanz vor:
  Wenn du die Instanz zum ersten Mal nutzt musst du einen Schlüssel für die Verschlüsselung erzeugen:
  ```
  php artisan key:generate
  ```


## Fehlerbehebung

- **Fehlende Abhängigkeiten**: Stellen Sie sicher, dass alle Abhängigkeiten aus `requirements.txt` installiert sind.
- **Python-Version**: Überprüfen Sie, ob die richtige Python-Version verwendet wird.
- **Virtuelle Umgebung**: Vergewissern Sie sich, dass die virtuelle Umgebung korrekt aktiviert wurde.
- **Fehlende Dateien**: Vergewissern Sie sich, dass die benötigten Konfigurationsdateien vorhanden sind.
