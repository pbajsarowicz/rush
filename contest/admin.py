from django.contrib import admin

from .models import RushUser


class PersonAdmin(admin.ModelAdmin):
    list_filter = ('is_active',)


class RushUserAdmin(admin.ModelAdmin):
    """What RushUserAdmin can do and how RushUser is displayed."""

    def confirm(modeladmin, request, queryset):
    	"""RushUserAdmin can confirm RushUser."""
        queryset.update(status='Yes')

    def cancel(modeladmin, request, queryset):
    	"""RushUserAdmin can cancel RushUser."""
        queryset.update(status='No')

    exclude = (
        'password', 'date_joined', 'last_login', 'status', 'is_superuser',
        'is_staff', 'is_active',
    )
    list_display = ('first_name', 'last_name')
    readonly_fields = ('last_login', 'date_joined')
    actions = [confirm, cancel]
admin.site.register(RushUser, RushUserAdmin)
