from django.contrib import admin
from .models import User, AuditLog

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    # This makes the log look professional in the dashboard
    list_display = ('timestamp', 'user', 'action', 'ip_address')
    list_filter = ('action', 'timestamp')
    readonly_fields = ('timestamp', 'user', 'action', 'ip_address', 'details')

    # Security: Don't allow anyone to edit logs manually!
    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False

# Also register your User model if it isn't already
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_verified', 'role')