from django.contrib import admin
from django.utils.translation import gettext as _
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from core import models


class UserAdmin(BaseUserAdmin):
    ordering = ['id']
    list_display = ['email', 'name']
    fieldsets = (
        (None, {"fields": ('email', 'password')}),
        (_('Personal Info'), {'fields': ('name',)}),
        (
            _('Permissions'),
            {'fields': ('is_active', 'is_staff', 'is_superuser',)}
        ),
        (_('Important dates'), {'fields': ('last_login',)})
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )


admin.site.register(models.User, UserAdmin)
admin.site.register(models.Tag)
