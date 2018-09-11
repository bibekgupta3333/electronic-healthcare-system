from django.core.management.base import BaseCommand, CommandError
import csv
from django.conf import settings
import os
from import_export.formats import base_formats
from snomedct.admin import SnomedConceptResource, SnomedDescendantResource, ReadCodeResource


class Command(BaseCommand):
    help = 'Import Snomed Concepts'
    csv_format = base_formats.CSV()
    data_file_path = os.path.join(settings.CONFIG_DIR, 'data/')
    output_file = data_file_path + '/temp.csv'

    def tranform_ruby_file(self, input_file):
        with open(self.output_file, 'w') as outcsv:
            with open(input_file, mode='r') as infile:
                reader = csv.DictReader(infile)
                header = reader.fieldnames
                out_header = ['id'] + header
                writer = csv.DictWriter(outcsv, fieldnames=out_header)
                writer.writeheader()
                for row in reader:
                    row_data = {}
                    for header in out_header:
                        row_data[header] = row.get(header) if row.get(header) is not None else ''
                    writer.writerow(row_data)

    def import_into_model(self, model_resource, input_file):
        with open(input_file, self.csv_format.get_read_mode()) as import_file:
            data = import_file.read()
            dataset = self.csv_format.create_dataset(data)
            result = model_resource.import_data(
                dataset,
                dry_run=False,
                raise_errors=True,
                use_transactions=False,
            )
            print(result)

    def import_snomed_concepts(self):
        self.stdout.write("preparing snomed_concepts.csv data file...")
        self.tranform_ruby_file(self.data_file_path + 'snomed_concepts.csv')
        input_file = self.output_file
        self.stdout.write("importing snomed concepts data...")
        self.import_into_model(SnomedConceptResource(), input_file)
        self.stdout.write("importing snomed concepts done...")

    def import_snomed_descendants(self):
        self.stdout.write("preparing snomed_descendants.csv data file...")
        self.tranform_ruby_file(self.data_file_path + 'snomed_descendants.csv')
        input_file = self.output_file
        self.stdout.write("importing snomed descendants data...")
        self.import_into_model(SnomedDescendantResource(), input_file)
        self.stdout.write("importing snomed descendants done...")

    def import_readcode(self):
        self.stdout.write("preparing readcodes.csv data file...")
        self.tranform_ruby_file(self.data_file_path + 'readcodes.csv')
        input_file = self.output_file
        self.stdout.write("importing readcodes data...")
        self.import_into_model(ReadCodeResource(), input_file)
        self.stdout.write("importing readcodes done...")

    def handle(self, *args, **options):
        # self.import_snomed_concepts()
        # self.import_snomed_descendants()
        self.import_readcode()
