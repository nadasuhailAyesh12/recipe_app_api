import time 

from django .core.management.base import BaseCommand
from django.db.utils import OperationalError
from psycopg2 import OperationalError as psycopg2opError


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write("waiting for database...")
        db_up = False
        while not db_up:
            try:
                self.check(databases=['default'])
                db_up = True
            except (OperationalError, psycopg2opError):
                self.stdout.write('Database unavailable,waiting 1 second...')
                time.sleep(1)
        self.stdout.write(self.style.SUCCESS('Database available'))
