from django.contrib import admin

# Register your models here.
from apps.property.models import Agency, Salutarium, Paper


@admin.register(Agency)
class AgencyModelAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'code',
        'name',
        'treasurer_name',
        'contact'
    ]

    search_fields = [
        'name'
    ]


@admin.register(Salutarium)
class SalutariumModelAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'agency',
        'name',
        'treasurer_name',
        'contact'
    ]

    search_fields = [
        'name'
    ]


@admin.register(Paper)
class PaperModelAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'registerer',
        'patient',
        'file'
    ]

    search_fields = [
        'registerer'
    ]
