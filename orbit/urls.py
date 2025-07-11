from django.urls import path
from . import views

app_name = 'orbit'

urlpatterns = [
    path('users/', views.CustomUserListView.as_view(), name='user-list'),
    path('users/create/', views.CustomUserCreateView.as_view(), name='user-create'),
    path('users/<int:pk>/', views.CustomUserDetailView.as_view(), name='user-detail'),
    
    path('users/<int:user_id>/route/', views.user_route_geojson, name='user-route-geojson'),
    
    path('users/nearby/', views.users_nearby, name='users-nearby'),
    
    path('dashboard/', views.user_dashboard, name='user-dashboard'),
]