from django.contrib import admin

from apps.core.utils import generate_unique_key
from apps.users.models import User


@admin.register(User)
class UserModelAdmin(admin.ModelAdmin):
    add_fieldsets = (
        (None, {
            'description': (
                "Enter the new user's name and email address and click save."
                " The user will be emailed a link allowing them to login to"
                " the site and set their password."
            ),
            'fields': ('email', 'name'),
        }),

    )
    list_display = [
        'id',
        'is_active',
        'name',
        'role',
        'email'
    ]

    search_fields = [
        'username',
        'name',
        'email'
    ]
    exclude = [
        'username',
        'last_login',
        'is_superuser',
        'groups',
        'user_permissions',
        'is_staff',
        'is_active',
        'password',
    ]

    def save_model(self, request, obj, form, change):
        if obj.user_register is True and obj.is_active is False and obj.check_account is True:
            obj.is_active = True

            super().save_model(request, obj, form, change)
        else:
            obj.is_active = False
            obj.email_confirmation_token = generate_unique_key(obj.email)

            super().save_model(request, obj, form, change)
