from rest_framework import permissions

class IsGovOfficial(permissions.BasePermission):
    """Allow access only to RURA/RRA officials."""
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            request.user.role == 'GOV'
        )

class IsSectorAgent(permissions.BasePermission):
    """Agents can only see data for their specific sector."""
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            request.user.role == 'AGENT'
        )

class IsOwnerOrReadOnly(permissions.BasePermission):
    """Object-level permission: Users can only edit their own profile."""
    def has_object_permission(self, request, view, obj):
        # Allow any safe method (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return True
        # Write permissions only to the owner
        return obj == request.user