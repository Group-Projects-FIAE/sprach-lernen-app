# Projektbeschreibung: E-lerno

## Projektname
**E-lerno** – Eine moderne Webbasierten Sprachlernplattform.

## Kurzbeschreibung
E-lerno ist eine Full-Stack-Webanwendung, die auf dem Django-Framework basiert. Das Ziel der Anwendung ist es, Nutzer beim Erlernen von Vokabeln und der Verbesserung ihrer Sprachkenntnisse (Deutsch und Englisch) zu unterstützen. Dies geschieht durch einen strukturierten Ansatz, der sich an den europäischen Referenzrahmen für Sprachen (A1, A2, B1) orientiert.

## Projektziel
Die Anwendung bietet eine strukturierte Umgebung für Lernende, um ihren Wortschatz systematisch zu erweitern. Durch integrierte Fortschrittskontrolle, verschiedene Übungsmodi und eine automatisierte Datenverwaltung wird der Lernprozess effizient gestaltet.

---

## Funktionalitäten (Must-Haves) - Umgesetzt

### 1. Benutzerverwaltung & Profile
- **Registrierung & Login**: Sicherer Zugriff über Django Allauth.
- **Profilmanagement**: Nutzer können ihren Namen ändern, das Passwort verwalten und ein individuelles Profilbild hochladen.
- **Tagesziele**: Definition einer täglichen Wortanzahl, die direkt im Dashboard visualisiert wird.

### 2. Sprachniveaus & Struktur
- **Niveauauswahl**: Alle Inhalte sind nach Niveaus (A1, A2, B1) gefiltert.
- **System-Listen**: Vordefinierte Vokabellisten werden vom System bereitgestellt (automatischer Datenimport).

### 3. Interaktive Übungsmodi
- **Eingabe-Modus (Write)**: Vokabeln müssen aktiv getippt werden.
- **Auswahl-Modus (Select)**: Multiple-Choice-Verfahren zur Erkennung.
- **Flexibilität**: Nutzer können wählen, ob sie eine Standardliste oder eine eigene Liste üben möchten.

### 4. Fortschritt & Statistik
- **Lernfortschritt**: Speicherung der Trefferquote für jedes Wort.
- **Spaced Repetition**: Ein Wort gilt nach 5 richtigen Antworten als "gelernt" und wird erst nach einer Woche wieder zur Wiederholung vorgeschlagen.
- **Echtzeit-Statistiken**: Anzeige von gelernten Worten und anstehenden Wiederholungen im Dashboard.
- **Punkte-System**: Nutzer erhalten Punkte für erfolgreich gelernte Worte.
- **Feedback**: Positives visuelles Feedback nach Meilensteinen (z.B. 10 gelernte Worte).

### 5. Listenverwaltung
- **Eigene Listen**: Nutzer können aus System-Vorschlägen eigene Listen zusammenstellen und speichern.
- **Aktive Listen**: Verwaltung von Listen, die sich aktuell im Lernprozess befinden.

---

## Zukünftige Erweiterungen (Nice-to-Haves) - Vision

- **Soziales Lernen**: Erstellung von Gruppen, um gemeinsam Listen zu lernen und Einladungen an andere Nutzer.
- **Erweiterte Grammatik**: Strukturierte Grammatikübungen für verschiedene Niveaus.
- **KI-Integration**: Dialogsystem mit künstlicher Intelligenz, das bereits gelernte Vokabeln in Gesprächen abfragt.
- **Lektionssteuerung**: Blockierung von Lektionen basierend auf dem aktuellen Sprachniveau des Nutzers.
- **Erweitertes Admin-Dashboard**: Feinpräzise Steuerung von Nutzergruppen und Inhaltsfreigaben.

---

## Technische Eckpunkte
- **Framework**: Django (Python) mit Class-Based Views (CBVs) für saubere Modularität.
- **Frontend**: Responsive Design mit Bootstrap 5.3 und Vanilla JavaScript.
- **Datenhaltung**: SQLite3 (lokal) mit automatisiertem JSON-Import-System.
- **Logik**: Spaced Repetition Algorithmus zur Optimierung des Langzeitgedächtnisses.
