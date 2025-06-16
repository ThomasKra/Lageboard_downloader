# coding=utf8
# the above tag defines encoding for this document and is for Python 2.x compatibility
# Downloader und Installer

import re
import requests
import os
import tarfile
import shutil
import subprocess
import glob
from pathlib import Path

from dotenv import dotenv_values, load_dotenv

load_dotenv('.env')

repository = 'Lageboard'
githubUser = 'ThomasKra'
githubPersonalAccessToken = os.getenv('GITHUB_PERSONAL_ACCESS_TOKEN')
if githubPersonalAccessToken is None:
  print('GITHUB_PERSONAL_ACCESS_TOKEN muss im .env angegeben werden!')
  exit(2)
headersList = {
    "Accept": "*/*",
    "Authorization": f"Bearer {githubPersonalAccessToken}",
    "X-GitHub-Api-Version": "2022-11-28"

}
targetFolder = os.getenv('TARGET_FOLDER', 'LageBoard')
tempFolder = 'temp'
configsFolder = 'configs'

basePath = os.getcwd()  # Holt das aktuelle Arbeitsverzeichnis


def run_artisan_command(command: str):
  """
  Führt einen PHP Artisan-Befehl aus und gibt die Ausgabe zurück.

  :param command: Der PHP Artisan-Befehl, der ausgeführt werden soll.
  :return: Die Ausgabe des Befehls.
  """
  full_command = [php_bin, "artisan"] + command.split()
  try:
    result = subprocess.run(
        full_command, 
        capture_output=True, 
        text=True, 
        check=True,
        cwd=targetFolder)
    return result.stdout
  except subprocess.CalledProcessError as e:
    print(f"Fehler beim Ausführen des Befehls: {e}")
    print(f"Rückgabecode: {e.returncode}")
    print(f"Ausgabe: {e.stdout}")
    print(f"Fehlerausgabe: {e.stderr}")
    return None


def get_app_url():
    """
    Liest den Wert der Variablen APP_URL aus einer spezifischen .env Datei, ohne die Umgebungsvariablen zu verändern.

    :return: Der Wert der APP_URL Variable, oder None wenn sie nicht gefunden wurde.
    """
    env_vars = dotenv_values(
        os.path.join(configsFolder, '.env'))  # Liest die .env Datei als Dictionary ein
    app_url = env_vars.get('APP_URL')  # Extrahiert den APP_URL Wert
    return app_url


def extract_tar_gz(archive_path: str, destination_directory: str):
    """
    Extracts a .tar.gz archive into a specified destination directory.

    :param archive_path: The path to the .tar.gz archive.
    :param destination_directory: The directory where the archive should be extracted.
    """
    try:
        with tarfile.open(archive_path, "r:gz") as tar:
            tar.extractall(path=destination_directory)
        print(
            f"The archive '{archive_path}' was successfully extracted to '{destination_directory}'.")
    except Exception as e:
        print(f"An error occurred while extracting the archive: {e}")



def getDownloadsList():
    reqUrl = f"https://api.github.com/repos/{githubUser}/{repository}/releases"

    return requests.request("GET", reqUrl, headers=headersList)

def downloadArtifact(filename: str, reqUrl: str):
    open(filename, 'wb').write(requests.request(
            "GET", reqUrl, headers=headersList |{"Accept": "application/octet-stream",
}).content)
        
def delete_tar_gz_files_in_basepath():
    """
    Löscht alle *.tar.gz-Dateien im Basis Verzeichnis.
    """
    # Verwende glob, um alle .tar.gz Dateien im Verzeichnis zu finden
    pattern = str(Path(basePath) / "*.tar.gz")
    tar_gz_files = glob.glob(pattern)
    
    # Lösche jede gefundene Datei
    for file_path in tar_gz_files:
        try:
            Path(file_path).unlink()
            print(f"Gelöscht: {file_path}")
        except Exception as e:
            print(f"Fehler beim Löschen von {file_path}: {e}")


try:
    downloadsList = getDownloadsList().json()
except:
    print('Exception occurred')
    exit(code=-1)

# Latest:
latest = downloadsList[0].get('assets')[0]
filename = latest.get('name')
created_on = latest.get('created_at')
link = latest.get('url')

print(f'File: {filename} Created on: {created_on}: {link}')

delete_tar_gz_files_in_basepath()
print('Downloading it now')
downloadArtifact(filename, link)
print('Downloading finished')

print("Deleting old installation")
shutil.rmtree(targetFolder,True)

extract_tar_gz(filename, targetFolder)

if not os.path.isdir(os.path.abspath(configsFolder)):
    print('\"configs\"-Verzeichnis muss existieren!')
    exit(2)

if not os.path.isfile(os.path.join(configsFolder, '.env')):
    print('.env Datei muss im \"configs\"-Verzeichnis existieren!')
    exit(2)
if not os.path.isfile(os.path.join(configsFolder, 'user_seed.json')):
    print('user_seed.json Datei muss im \"configs\"-Verzeichnis existieren!')
    exit(2)

[shutil.copy2(
  os.path.join(configsFolder, item),
  os.path.join(targetFolder, item))
 for item in ['.env', 'user_seed.json']]

print('Kopieren der Konfigurationsdaten erfolgreich')

app_url= dotenv_values(os.path.join(configsFolder, '.env')).get('APP_URL')

app_url_regex= r"(http[s]?):\/\/(\S*)"
matches= re.findall(app_url_regex, app_url)

if len(matches) != 1:
    print('Probleme beim Evaluieren der APP_URL aus dem .env')
    exit(2)

(app_url_protocol, app_url_domain)= matches[0]

print(
    f'App URL Protocol: {app_url_protocol}, App URL domain: {app_url_domain}')


# Routes anpassen

def replace_localhost_url_in_build_assets():
    """
    Ersetzt die URL in den Build Assets (Ziggy Routes) durch die URL im .env file.
    """

    pattern= r"http(:[\/\\]*)localhost"
    replacement= rf"{app_url_protocol}\1{app_url_domain}"

    directory= os.path.join(targetFolder, 'public/build/assets')
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(('.js', '.map')):
                filepath= os.path.join(root, file)
                try:
                    # Dateiinhalt lesen
                    with open(filepath, 'r') as file:
                        content= file.read()

                    # Regex-Substitution durchführen
                    modified_content= re.sub(pattern, replacement, content)
                    if (modified_content != content):
                        # Geänderten Inhalt zurück in die Datei schreiben
                        with open(filepath, 'w') as file:
                            file.write(modified_content)

                        print(
                            f"Die Datei '{filepath}' wurde erfolgreich geändert.")
                except Exception as e:
                    print(f"Fehler beim Ändern der Datei: {e}")


replace_localhost_url_in_build_assets()


# Aritsan-Commands für die Installations / Update

php_bin= os.getenv('PHP_BIN', 'php')

antwort = input(
        f"Soll eine frische Migration durchlaufen werden? (ja/nein): ").strip().lower()
migrateFresh = (antwort == 'ja')

artisan_commands = ['optimize']

if migrateFresh:
  artisan_commands.insert(0, 'migrate:fresh')
  artisan_commands.append('app:init')
  artisan_commands.append('app:user-import')
else:
  artisan_commands.insert(0, 'migrate')

for cmd in artisan_commands:
  run_artisan_command(cmd)