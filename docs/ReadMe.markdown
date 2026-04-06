# E-lerno (Sprachlernen App) - Benutzer- und Startanleitung

Willkommen bei **E-lerno**, einer modernen Full-Stack-Sprachlernanwendung auf Django-Basis. Diese Anleitung führt Sie durch den Prozess der Installation, Konfiguration und den ersten Start der Anwendung.

## 🛠 Voraussetzungen

Um E-lerno lokal zu betreiben, benötigen Sie:
- **Python 3.12.3**
- **pip** (Python Package Installer)
- Eine aktive Internetverbindung (für den Download der Abhängigkeiten)

## ⚙️ Installation & Setup (Lokal)

Folgen Sie diesen Schritten, um die Anwendung auf Ihrem System einzurichten:

### 1. Projekt vorbereiten
Stellen Sie sicher, dass Sie sich im Stammverzeichnis des Projekts befinden:
```bash
git clone https://github.com/Group-Projects-FIAE/sprach-lernen-app.git
cd sprach-lernen-app
```

### 2. Virtuelle Umgebung erstellen (Empfohlen)
Erstellen und aktivieren Sie eine virtuelle Umgebung, um Abhängigkeiten sauber zu trennen:
```bash
python -m venv venv

# Aktivieren (Linux/macOS):
source venv/bin/activate

# Aktivieren (Windows):
venv\Scripts\activate
```

### 3. Abhängigkeiten installieren
Installieren Sie alle notwendigen Python-Pakete:
```bash
pip install -r requirements.txt
```

### 4. Datenbank-Migrationen durchführen
Initialisieren Sie die SQLite-Datenbank und erstellen Sie alle Tabellen:
```bash
python manage.py migrate
```

### 5. Lokalen Admin-Account erstellen
Um auf die Administrationsoberfläche zuzugreifen, müssen Sie einen Superuser erstellen:
```bash
python manage.py createsuperuser
```
*Folgen Sie den Anweisungen im Terminal (Name, E-Mail, Passwort).*

## 📥 Import der Vokabeldaten (WICHTIG)

Die Anwendung startet ohne Standard-Inhalte. Um die Kuratierten Vokabellisten für die verschiedenen Niveaustufen zu laden, führen Sie nacheinander folgende Befehle aus (Die JSON-Dateien befinden sich im Root-Verzeichnis):

```bash
python manage.py import_vocab A1.json
python manage.py import_vocab A2.json
python manage.py import_vocab B1.json
```
*Hinweis: Dies füllt die Datenbank mit System-Listen, die die Grundlage für die Nutzererfahrung bilden.*

## Starten der Anwendung

Starten Sie den integrierten Django-Entwicklungsserver:
```bash
python manage.py runserver
```

Sie können die Anwendung nun im Browser aufrufen unter: [http://127.0.0.1:8000](http://127.0.0.1:8000)

## 🐞 Troubleshooting

- Falls "command not found": prüfen Sie, ob die virtuelle Umgebung aktiviert ist
- Falls Port belegt: python manage.py runserver 8001
- Falls Module fehlen: pip install -r requirements.txt erneut ausführen
  
## Konfiguration

### Environment-Variablen (Optional)
Standardmäßig nutzt die Anwendung eine lokale SQLite-Datenbank (`db.sqlite3`). Für eine produktive Umgebung sollten die entsprechenden Django-Settings in `settings.py` angepasst werden.

### Administration
Unter [http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin) können Sie sich mit dem zuvor erstellten Admin-Account anmelden, um Nutzer zu verwalten oder neue Vokabellisten einzusehen.

---
