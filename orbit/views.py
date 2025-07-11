# orbit/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse

from .models import CustomUser, UserRoute
from .serializers import CustomUserSerializer, UserRouteSerializer

# User CRUD Views
class CustomUserListView(generics.ListAPIView):
    """Public API to list all users"""
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [AllowAny]

class CustomUserCreateView(generics.CreateAPIView):
    """Public API for user signup"""
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [AllowAny]

class CustomUserDetailView(APIView):
    """Authenticated API for user detail, update, delete"""
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        return get_object_or_404(CustomUser, pk=pk)

    def get(self, request, pk):
        user = self.get_object(pk)
        serializer = CustomUserSerializer(user)
        return Response(serializer.data)

    def patch(self, request, pk):
        # Only allow user to edit their own account
        if request.user.pk != pk:
            return Response(
                {'detail': 'You do not have permission to edit this user.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        user = self.get_object(pk)
        serializer = CustomUserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        if request.user.pk != pk:
            return Response(
                {'detail': 'You do not have permission to delete this user.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        user = self.get_object(pk)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# GeoJSON API for user routes
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_route_geojson(request, user_id):
    """Get user's route as GeoJSON"""
    try:
        user = CustomUser.objects.get(pk=user_id)
        route = UserRoute.objects.filter(user=user).first()
        
        if not route or not route.route:
            return Response(
                {'error': 'No route found for this user'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        geojson = route.to_geojson()
        return Response(geojson)
    
    except CustomUser.DoesNotExist:
        return Response(
            {'error': 'User not found'},
            status=status.HTTP_404_NOT_FOUND
        )

# Nearby users API
@api_view(['GET'])
@permission_classes([AllowAny])
def users_nearby(request):
    """Get users within 10km radius of given coordinates"""
    try:
        lat = float(request.GET.get('lat'))
        lng = float(request.GET.get('lng'))
        radius_km = float(request.GET.get('radius', 10))
    except (TypeError, ValueError):
        return Response(
            {'error': 'Invalid or missing lat/lng parameters'},
            status=status.HTTP_400_BAD_REQUEST
        )

    user_location = Point(lng, lat, srid=4326)
    
    # Get users within radius
    nearby_users = CustomUser.objects.users_within_radius(user_location, radius_km)
    nearby_users = nearby_users.annotate(
        distance=Distance('home_address', user_location)
    ).order_by('distance')

    serializer = CustomUserSerializer(nearby_users, many=True)
    return Response({
        'count': nearby_users.count(),
        'radius_km': radius_km,
        'center': {'latitude': lat, 'longitude': lng},
        'users': serializer.data
    })

# Template views
def home(request):
    """Home page view"""
    return render(request, 'home.html')

def user_dashboard(request):
    """User dashboard view"""
    return render(request, 'user_dashboard.html')

