from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, UserRoute

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin, admin.ModelAdmin):
    list_display = [
        'username', 'email', 'first_name', 'last_name', 'country',
        'age', 'has_complete_address', 'is_staff', 'is_superuser'
    ]
    list_filter = UserAdmin.list_filter + ('country', 'birthday', 'created_at')
    search_fields = ['username', 'email', 'first_name', 'last_name', 'country']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Personal Information', {
            'fields': ('country', 'bio', 'phone_number', 'areas_of_interest', 'birthday')
        }),
        ('Documents', {
            'fields': ('documents',)
        }),
        ('Location Information', {
            'fields': ('home_address', 'office_address')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']

@admin.register(UserRoute)
class UserRouteAdmin(admin.ModelAdmin):
    list_display = ['user', 'distance_km', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['distance_km', 'created_at', 'updated_at']
