from django.core.management.base import BaseCommand
from sprachlernen.utils.vocab_populator import VocabPopulator

class Command(BaseCommand):
    help = 'Import vocabulary from a JSON file'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='Path to the JSON file')

    def handle(self, *args, **options):
        populator = VocabPopulator(stdout=self.stdout, stderr=self.stderr)
        populator.import_from_json(options['json_file'])
