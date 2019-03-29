from django.utils.html import format_html

from .models import Library

import django_tables2 as tables


class LibraryTable(tables.Table):
    edit_button = tables.Column(empty_values=(), verbose_name='', attrs={'td': {'style': 'width:95px;text-align: center;'}})
    delete_button = tables.Column(empty_values=(), verbose_name='', attrs={'td': {'style': 'width:95px;text-align: center;'}})

    class Meta:
        attrs = {
            'class': 'table table-bordered table-hover',
            'id': 'libraryTable'
        }
        model = Library
        fields = (
            'key', 'value'
        )

    def render_edit_button(self, record):
        return format_html('<button class="btn btn-fee text-light btn-sm" style="width:80px;">EDIT</button>')

    def render_delete_button(self, record):
        return format_html('<button class="btn btn-danger btn-sm" style="width:80px;">DELETE</button>')


