from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserSettings

class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'username', 'display_name', 'is_premium', 'is_active')
    search_fields = ('email', 'username')
    ordering = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('username', 'display_name', 'avatar', 'bio', 'native_language', 'timezone')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_premium')}),
        ('Important dates', {'fields': ('last_login', 'created_at', 'updated_at')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    readonly_fields = ('created_at', 'updated_at')

admin.site.register(User, UserAdmin)
admin.site.register(UserSettings)