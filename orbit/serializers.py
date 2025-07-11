from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point
from .models import UserRoute

User = get_user_model()

class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    home_address = serializers.SerializerMethodField()
    office_address = serializers.SerializerMethodField()
    age = serializers.ReadOnlyField()
    full_name = serializers.ReadOnlyField()
    home_to_office_distance = serializers.ReadOnlyField()
    has_complete_address = serializers.ReadOnlyField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'password',
            'country', 'bio', 'phone_number', 'areas_of_interest', 'birthday',
            'documents', 'home_address', 'office_address', 'created_at',
            'updated_at', 'age', 'full_name', 'home_to_office_distance',
            'has_complete_address'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True},
        }

    def get_home_address(self, obj):
        if obj.home_address:
            return {
                'latitude': obj.home_address.y,
                'longitude': obj.home_address.x
            }
        return None

    def get_office_address(self, obj):
        if obj.office_address:
            return {
                'latitude': obj.office_address.y,
                'longitude': obj.office_address.x
            }
        return None

    def to_internal_value(self, data):
        # Handle home address
        if 'home_address' in data and data['home_address']:
            home = data['home_address']
            if isinstance(home, dict) and 'latitude' in home and 'longitude' in home:
                data['home_address'] = Point(home['longitude'], home['latitude'])
        
        # Handle office address
        if 'office_address' in data and data['office_address']:
            office = data['office_address']
            if isinstance(office, dict) and 'latitude' in office and 'longitude' in office:
                data['office_address'] = Point(office['longitude'], office['latitude'])
        
        return super().to_internal_value(data)

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance

class UserRouteSerializer(GeoFeatureModelSerializer):
    user = serializers.StringRelatedField()
    distance_km = serializers.ReadOnlyField()
    
    class Meta:
        model = UserRoute
        geo_field = 'route'
        fields = ['user', 'distance_km', 'created_at', 'updated_at']