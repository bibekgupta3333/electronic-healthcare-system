from import_export.admin import ExportMixin, ImportExportModelAdmin


class CustomExport(ExportMixin):

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


class CustomImportExport(ImportExportModelAdmin, CustomExport):
    """
    Subclass of ImportExportModelAdmin with import/export functionality.
    """
