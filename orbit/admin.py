from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, UserRoute

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'is_staff', 'is_superuser']
    fieldsets = UserAdmin.fieldsets + (
        ("Additional Info", {
            "fields": (
                'country',
                'bio',
                'phone_number',
                'areas_of_interest',
                'documents',
                'birthday',
                'home_location',
                'office_location',
            )
        }),
    )

@admin.register(UserRoute)
class UserRouteAdmin(admin.ModelAdmin):
    list_display = ['user']
