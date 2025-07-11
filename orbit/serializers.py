# orbit/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point

User = get_user_model()

class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    home_address = serializers.SerializerMethodField()
    office_address = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'password', 'country', 'bio', 'phone_number',
            'areas_of_interest', 'birthday', 'user_documents',
            'home_address', 'office_address'
        ]
        read_only_fields = ['id']

    def get_home_address(self, obj):
        if obj.home_address:
            return {'latitude': obj.home_address.y, 'longitude': obj.home_address.x}
        return None

    def get_office_address(self, obj):
        if obj.office_address:
            return {'latitude': obj.office_address.y, 'longitude': obj.office_address.x}
        return None

    def to_internal_value(self, data):
        home = data.get('home_address')
        office = data.get('office_address')
        if home:
            data['home_address'] = Point(home['longitude'], home['latitude'])
        if office:
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
