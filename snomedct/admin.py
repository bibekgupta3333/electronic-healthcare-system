from django.contrib import admin
from import_export import fields as imFields, resources
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget
from .models import SnomedConcept, SnomedDescendant, ReadCode


# Register your models here.
class SnomedConceptResource(resources.ModelResource):
    count = 1

    class Meta:
        model = SnomedConcept
        fields = ('external_id', 'created_at', 'updated_at', 'file_path', 'fsn_description', 'external_fsn_description_id', 'id',)
        widgets = {
            'created_at': {'format': '%Y-%m-%dT%H:%M:%SZ'},
            'updated_at': {'format': '%Y-%m-%dT%H:%M:%SZ'},
        }

    def before_import(self, dataset, using_transactions, dry_run, **kwargs):
        SnomedConcept.objects.all().delete()

    def after_import_row(self, row, row_result, **kwargs):
        self.count = self.count + 1
        print("SnomedConcept Imported:", self.count)


class SnomedConceptAdmin(ImportExportModelAdmin):
    resource_class = SnomedConceptResource


class SnomedConceptWidget(ForeignKeyWidget):
    def clean(self, value, row):
        return self.model.objects.get_or_create(external_id=value)[0]


class SnomedDescendantResource(resources.ModelResource):
    count = 1

    class Meta:
        model = SnomedDescendant
        fields = ('external_id', 'descendant_external_id', 'id',)

    def before_import(self, dataset, using_transactions, dry_run, **kwargs):
        SnomedDescendant.objects.all().delete()

    def after_import_row(self, row, row_result, **kwargs):
        self.count = self.count + 1
        print("SnomedDescendant Imported:", self.count)


class ReadCodeResource(resources.ModelResource):
    count = 1

    class Meta:
        model = ReadCode
        fields = ('ext_read_code', 'created_at', 'updated_at', 'file_path', 'concept_id', 'id',)
        widgets = {
            'created_at': {'format': '%Y-%m-%dT%H:%M:%SZ'},
            'updated_at': {'format': '%Y-%m-%dT%H:%M:%SZ'},
        }

    def before_import(self, dataset, using_transactions, dry_run, **kwargs):
        ReadCode.objects.all().delete()

    def after_import_row(self, row, row_result, **kwargs):
        self.count = self.count + 1
        print("ReadCode Imported:", self.count)


# admin.site.register(SnomedConcept, SnomedConceptAdmin)
