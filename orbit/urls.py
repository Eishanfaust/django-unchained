from django.urls import path
from .views import CustomUserList, CustomUserDetail, CustomUserCreate

app_name = 'orbit'

urlpatterns = [
    path('users/', CustomUserList.as_view(), name='user-list'),
    path('users/<int:pk>/', CustomUserDetail.as_view(), name='user-detail'),
    path('signup/', CustomUserCreate.as_view(), name='user-create'),
]
