from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, generics
from .models import CustomUser
from .serializers import CustomUserSerializer
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.shortcuts import render

# public access
class CustomUserList(generics.ListAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.AllowAny]

#auth for ddetail and update
class CustomUserDetail(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        user = get_object_or_404(CustomUser, pk=pk)
        serializer = CustomUserSerializer(user)
        return Response(serializer.data)

    def patch(self, request, pk):
        #only allow user to edit own account
        if request.user.pk != pk:
            return Response({'detail': 'You do not have permission to edit this user.'}, status=status.HTTP_403_FORBIDDEN)
        user = get_object_or_404(CustomUser, pk=pk)
        serializer = CustomUserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        if request.user.pk != pk:
            return Response({'detail': 'You do not have permission to delete this user.'}, status=status.HTTP_403_FORBIDDEN)
        user = get_object_or_404(CustomUser, pk=pk)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

#api for signup
class CustomUserCreate(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
from django.http import HttpResponse


def home(request):
    return render(request, 'home.html')

def user_dashboard(request):
    return render(request, 'user-dashboard.html')