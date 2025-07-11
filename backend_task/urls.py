from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from orbit.views import home

urlpatterns = [
    path('', home, name='home'),  # Homepage
    path('admin/', admin.site.urls),
    path('api/', include('orbit.urls', namespace='orbit')),  # Orbit app APIs
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # JWT obtain
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # JWT refresh
]
