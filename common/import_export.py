from import_export.admin import ExportMixin, ImportExportModelAdmin
from django.http import HttpResponse
from django.utils import timezone
import csv


class CustomImportExport(ImportExportModelAdmin):
    """
    Subclass of ImportExportModelAdmin with import/export functionality.
    """

    def get_export_queryset(self, request):
        list_display = self.get_list_display(request)
        list_display_links = self.get_list_display_links(request, list_display)
        list_filter = self.get_list_filter(request)
        search_fields = self.get_search_fields(request)
        if self.get_actions(request):
            list_display = ['action_checkbox'] + list(list_display)

        ChangeList = self.get_changelist(request)
        changelist_kwargs = {
            'request': request,
            'model': self.model,
            'list_display': list_display,
            'list_display_links': list_display_links,
            'list_filter': list_filter,
            'date_hierarchy': self.date_hierarchy,
            'search_fields': search_fields,
            'list_select_related': self.list_select_related,
            'list_per_page': self.list_per_page,
            'list_max_show_all': self.list_max_show_all,
            'list_editable': self.list_editable,
            'model_admin': self,
            'sortable_by': self.sortable_by,
        }
        cl = ChangeList(**changelist_kwargs)

        return cl.get_queryset(request)

    def export_status_report_as_csv(self, request, queryset):
        field_names = ['id', 'medi_ref', 'gp_practice']
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=instruction-status-report:{date}.csv'.format(
            date=timezone.now())
        writer = csv.writer(response)
        writer.writerow(['ID', 'MediRef', 'Surgery', 'Status'])
        for obj in reversed(queryset):
            export_row = [getattr(obj, field) for field in field_names]
            export_row.append(obj.get_status_display())
            row = writer.writerow(export_row)

        return response

    export_status_report_as_csv.short_description = "Export status report"

    def export_payment_as_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=payment-report:{date}.csv'.format(date=timezone.now())
        writer = csv.writer(response)
        writer.writerow(['Sort Code', 'Account number', 'GP Surgery', 'Amount', 'VAT', 'Reference'])
        for obj in (queryset):
            gp_practice = obj.gp_practice
            export_row = [
                gp_practice.payment_bank_sort_code,
                gp_practice.payment_bank_account_number,
                gp_practice.name,
                obj.gp_earns,
                '',
                'Dummy reference'
            ]
            row = writer.writerow(export_row)
        return response

    export_payment_as_csv.short_description = "Export payment report"
