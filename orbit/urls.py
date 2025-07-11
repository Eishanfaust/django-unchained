from django.urls import path
from .views import CustomUserList, CustomUserDetail, CustomUserCreate, user_dashboard, home

app_name = 'orbit'

urlpatterns = [
    path('', home, name='home'),  # optional if homepage handled here
    path('users/', CustomUserList.as_view(), name='user-list'),
    path('users/<int:pk>/', CustomUserDetail.as_view(), name='user-detail'),
    path('signup/', CustomUserCreate.as_view(), name='user-create'),
    path('dashboard/', user_dashboard, name='user-dashboard'),
]
