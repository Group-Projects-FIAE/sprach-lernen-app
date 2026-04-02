# Handout: E-lerno - Webbasierten Sprachlernplattform

---

## Übersicht
**E-lerno** ist ein umfassendes Software-Produkt zur Unterstützung beim Sprachenlernen (Englisch & Deutsch). Die Anwendung basiert auf dem modernen Python-Webframework **Django** und bietet eine nahtlose Integration von Benutzerverwaltung, Inhaltsverwaltung und Lernfortschrittskontrolle.

## 🛠 Technischer Stack
- **Backend**: Django 6.0 (Python) - Einsatz von Class-Based Views (CBV) für maximale Wiederverwendbarkeit und modulare Struktur.
- **Frontend**: Bootstrap 5.3 (CSS) & Vanilla JavaScript - Responsive Design für Desktop und Mobile.
- **Datenbank**: SQLite3 für lokale Persistenz und schnelle Performance.
- **Authentifizierung**: Django Allauth für sichere Registrierung und Profilverwaltung.
- **Besonderes**: Integriertes Datenimport-System (`import_vocab`) für automatisierte Befüllung der Lerninhalte aus JSON-Strukturen.

## Kernfunktionen (Must-Haves)
- **Personalisierung**: Individuelle Profile mit Foto-Upload, Namensverwaltung und flexiblen Tageszielen.
- **Struktur**: Kategorisierung aller Vokabeln nach europäischen Referenzrahmen-Niveaus (A1, A2, B1).
- **Lernmodi**: 
    - **Select-Mode**: Interaktive Multiple-Choice-Erkennung.
    - **Input-Mode**: Aktives Schreiben zur Festigung des Gelernten.
- **Effizienz**: Automatisierte Vokabellisten vom System sowie die Möglichkeit, eigene Lernlisten zu erstellen.
- **Motivation**: Echtzeit-Statistiken über den Lernfortschritt, Punkte-System für Lernerfolge und visuelles Feedback.
- **Lernalgorithmus**: Umgesetzter **Spaced-Repetition-Ansatz** (Leitner-System) – Worte gelten nach 5-facher richtiger Beantwortung als gelernt und werden periodisch zur Wiederholung markiert.

## Zukunftsausblick (Nice-to-Haves)
- Erweiterung um soziale Komponenten wie Lern-Gruppen und Einladungen.
- Integration von KI-Dialogen zur Anwendung des gelernten Wortschatzes in Gesprächen.
- Strukturierte Grammatikübungen für alle Niveaustufen.

---

- **Entwickler**: Anastasiia, Tania, Humar.
- **Abgabedatum**: 06.04.2026
- **GitHub Repository**: https://github.com/Group-Projects-FIAE/sprach-lernen-app
