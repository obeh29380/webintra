import json

from django.core.management.base import BaseCommand

from front.models import WorkStatus


def register(filename):
    with open(filename, 'r') as f:
        r = json.load(f)

        for i in r:

            b = WorkStatus(
                name=i['name'],
                name_selection=i['name_selection'],
                use=i['use'],
                holiday=i['holiday'],
                memo=i['memo']
            )
            try:
                b.save()
            except Exception as e:
                raise e
            else:
                print(f'WorkStatus registered data={i}')


class Command(BaseCommand):

    def handle(self, *args, **options):
        register(options['file_name'])

    def add_arguments(self, parser):
        parser.add_argument('file_name', help='ファイル名', type=str)
