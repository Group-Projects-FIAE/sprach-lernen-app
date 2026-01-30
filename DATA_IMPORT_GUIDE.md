# Vocabulary Data Import Guide

This document explains how to populate the database with vocabulary using the centralized `VocabPopulator` utility.

## 1. Centralized Utility: `VocabPopulator`
A dedicated folder for all data-related helpers:
`sprachlernen/utils/vocab_populator.py`

This script is designed to be reusable and extendable. In the future, you can add methods here for importing grammar exercises, short stories, or other learning materials.

## 2. Step-by-Step Data Population

### Option A: Using the Django Management Command (Recommended)
This is the easiest way to run the import from your terminal.

1.  **Open your terminal** in the project root.
2.  **Activate your virtual environment**:
    ```bash
    source venv/bin/activate
    ```
3.  **Run the import command**:
    ```bash
    python manage.py import_vocab german_words.json
    ```

### Option B: Checking current counts
To quickly see how many words are in your database without opening PyCharm's database tool:
```bash
python manage.py shell -c "from vocab.models import Word; print(f'Total words: {Word.objects.count()}')"
```

## 3. How to check data in PyCharm (Table View)

PyCharm has an integrated Database tool that lets you view your SQLite tables like an Excel spreadsheet.

1.  **Open the "Database" Tool Window**: Usually found on the right-hand side of PyCharm. If not there, go to `View -> Tool Windows -> Database`.
2.  **Add your SQLite database**:
    *   Click the **+** (New) button.
    *   Select `Data Source -> SQLite`.
    *   In the "File" field, browse and select the `db.sqlite3` file located in your project root.
    *   *Note: If PyCharm asks to download drivers, click the "Download missing driver files" link.*
3.  **Browse the Tables**:
    *   Expand `db.sqlite3` -> `main` -> `tables`.
    *   Find the table named `vocab_word` (this is where the vocabulary is stored).
    *   **Double-click** the table to open it in a grid view.
4.  **Refresh Data**: If you run an import while the table is open, click the **Refresh** icon (blue circular arrows) in the database toolbar to see the new rows.
