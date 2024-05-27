from django.contrib import admin  # noqa
from core import models
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _


class UserAdmin(BaseUserAdmin):
    ordering = ['id']
    list_display = ['email', 'name']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal Info'), {'fields': ('name',)}),
        (_('Permissions'),
         {'fields': ('is_staff', 'is_superuser', 'is_active')}),
        (_('Important dates'), {'fields': ('last_login',)})
    )
    readonly_fields = ['last_login']
    add_fieldsets = (
     (None, {
        'classes': ('wide',),
        'fields': (
            'email',
            'password1',
            'password2',
            'name',
            'is_staff',
            'is_superuser',
            'is_active',
        ),
     }),
     )


admin.site.register(models.User, UserAdmin)
