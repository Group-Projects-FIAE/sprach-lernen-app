import json
import os
from vocab.models import Language, LanguageLevel, VocabularyList, Word

class VocabPopulator:
    """
    A utility class to handle importing vocabulary and potentially other 
    learning resources into the database.
    """

    def __init__(self, stdout=None, stderr=None):
        self.stdout = stdout
        self.stderr = stderr

    def log(self, message, style='info'):
        if self.stdout:
            if style == 'success':
                self.stdout.write(f"SUCCESS: {message}")
            elif style == 'warning':
                self.stdout.write(f"WARNING: {message}")
            else:
                self.stdout.write(message)
        else:
            print(f"[{style.upper()}] {message}")

    def error(self, message):
        if self.stderr:
            self.stderr.write(message)
        else:
            print(f"[ERROR] {message}")

    def import_from_json(self, json_file_path):
        """
        Imports vocabulary from a JSON file.
        Supports two formats:
        1. Simple format: { "words": [ { "word": "...", ... } ] }
        2. Open CEFR format: { "levels": { "A1": { "vocabulary": [ { "lemma": "...", ... } ] } } }
        """
        if not os.path.exists(json_file_path):
            self.error(f"File not found: {json_file_path}")
            return False

        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            self.error(f"Failed to parse JSON: {e}")
            return False

        # Ensure German language exists (Default for this project)
        german, _ = Language.objects.get_or_create(name="German")

        imported_count = 0
        updated_count = 0

        # Check format
        if 'levels' in data:
            # Handle Open CEFR format
            self.log("Detected Open CEFR format.", style='info')
            for level_code, level_data in data['levels'].items():
                vocab_list_name = f'System List {level_code}'
                
                # Get or create Level
                level_obj, _ = LanguageLevel.objects.get_or_create(
                    code=level_code,
                    defaults={'description': f'Language Level {level_code}'}
                )

                # Get or create Vocabulary List
                vocab_list, _ = VocabularyList.objects.get_or_create(
                    name=vocab_list_name,
                    level=level_obj,
                    language=german,
                    is_system=True
                )

                vocabulary = level_data.get('vocabulary', [])
                for item in vocabulary:
                    word_text = item.get('lemma')
                    pos = item.get('pos')
                    example = item.get('example_usage')
                    
                    # Extract translation (assuming English for now, taking first sense)
                    translations = item.get('translations', {})
                    en_translations = translations.get('en', [])
                    translation_text = en_translations[0].get('text') if en_translations else ""
                    
                    # details/metadata
                    details = {
                        'id': item.get('id'),
                        'gender': item.get('gender'),
                        'pos': pos
                    }

                    # Create or update Word
                    word_obj, created = Word.objects.update_or_create(
                        word=word_text,
                        vocab_list=vocab_list,
                        defaults={
                            'translation': translation_text,
                            'word_type': pos,
                            'example': example,
                            'metadata': details
                        }
                    )

                    if created:
                        imported_count += 1
                        self.log(f"Imported: {word_text}", style='success')
                    else:
                        updated_count += 1
                        self.log(f"Updated: {word_text}", style='warning')

        else:
            # Handle original simple format
            self.log("Detected simple format.", style='info')
            words_data = data.get('words', [])
            
            for entry in words_data:
                word_text = entry.get('word')
                translation = entry.get('translation')
                details = entry.get('details', {})
                level_code = details.get('level', 'A1')
                word_type = details.get('type')
                example = entry.get('example')
                example_translation = entry.get('example_translation')

                # Get or create Level
                level, _ = LanguageLevel.objects.get_or_create(
                    code=level_code,
                    defaults={'description': f'Language Level {level_code}'}
                )

                # Get or create Vocabulary List for this level
                vocab_list, _ = VocabularyList.objects.get_or_create(
                    name=f'System List {level_code}',
                    level=level,
                    language=german,
                    is_system=True
                )

                # Create or update Word
                word_obj, created = Word.objects.update_or_create(
                    word=word_text,
                    vocab_list=vocab_list,
                    defaults={
                        'translation': translation,
                        'word_type': word_type,
                        'example': example,
                        'example_translation': example_translation,
                        'metadata': details
                    }
                )

                if created:
                    imported_count += 1
                    self.log(f"Imported: {word_text}", style='success')
                else:
                    updated_count += 1
                    self.log(f"Updated: {word_text}", style='warning')

        self.log(f"Import process completed. (New: {imported_count}, Updated: {updated_count})", style='info')
        return True

    def import_grammar(self, data):
        """Placeholder for future imports for learning grammar"""
        self.log("Grammar import logic not yet implemented.", style='warning')

    def import_stories(self, data):
        """Placeholder for future imports for reading excecises"""
        self.log("Story import logic not yet implemented.", style='warning')
