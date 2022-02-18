import argparse
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Import file at command line'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', nargs='+', type=argparse.FileType('r'))
        file = options['csv_file']
        content = file.read().decode('utf-8')
        csv_data = csv.DictReader(content.splitlines())

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Successfully uploaded file'))