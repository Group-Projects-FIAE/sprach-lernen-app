# E-lerno (Sprachlernen App)

E-lerno is a modern, full-stack language learning application built with Django. It provides a structured approach to learning vocabulary and completing lessons categorized by language levels (A1, A2, B1).

## Key Features

- **Personalized Dashboard**: Track your daily progress and manage your active vocabulary lists.
- **Level-Based Learning**: Content organized into standardized language levels (A1, A2, B1).
- **Comprehensive Vocabulary**: 
    - Word translations, types (noun, verb, etc.), and examples.
    - Progress tracking with review intervals.
    - Systematic data import support.
- **Interactive Lessons**: Structured lessons linked to specific vocabulary lists.
- **User Profiles**: Customizable profiles with support for profile pictures and daily learning targets.
- **Secure Authentication**: Robust authentication system using Django Allauth.

## 🛠 Tech Stack

- **Backend**: Django 6.0 (Python)
- **Frontend**: Bootstrap 5.3, Vanilla JavaScript, CSS
- **Database**: SQLite3
- **Authentication**: Django Allauth
- **Image Processing**: Pillow

## ⚙️ Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Group-Projects-FIAE/sprach-lernen-app.git
   cd sprach-lernen-app
   ```

2. **Set up a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**:
   ```bash
   python manage.py migrate
   ```

5. **Import initial vocabulary data** (Curated lists):
   ```bash
   python manage.py import_vocab A1.json
   python manage.py import_vocab A2.json
   python manage.py import_vocab B1.json
   ```
   *Note: `german_words.json` is provided for testing purposes only.*

6. **Start the development server**:
   ```bash
   python manage.py runserver
   ```

## 📂 Project Structure

- `vocab/`: Manages vocabulary lists, words, and user progress.
- `lessons/`: Handles structured learning modules.
- `users/`: Custom user profiles and authentication logic.
- `templates/`: Centralized storage for HTML templates and static assets.
- `media/`: Storage for user-uploaded profile pictures.

## 📄 Documentation

For more detailed information on data population, refer to the [Vocabulary Data Import Guide](DATA_IMPORT_GUIDE.md).
