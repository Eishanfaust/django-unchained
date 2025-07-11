from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib.gis.db import models as gis_models
from django.contrib.gis.geos import LineString, Point
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date


class CustomUserManager(BaseUserManager):
    def get_by_natural_key(self, username):
        return self.get(username=username)

    def users_with_birthday_today(self):
        """Get all users with birthday today"""
        today = timezone.now().date()
        return self.filter(birthday__month=today.month, birthday__day=today.day)

    def users_within_radius(self, point, radius_km=10):
        """Get users within specified radius from a point"""
        radius_m = radius_km * 1000  # Convert km to meters
        return self.filter(
            home_address__distance_lte=(point, radius_m)
        ).exclude(home_address__isnull=True)

    def create_user(self, username, email=None, password=None, **extra_fields):
        if not username:
            raise ValueError('The Username field must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(username, email, password, **extra_fields)


class CustomUser(AbstractUser):
    # Basic fields
    country = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    areas_of_interest = models.JSONField(default=list, blank=True)
    documents = models.FileField(
        upload_to='user_documents/',
        blank=True,
        null=True,
        help_text='Upload PDF or image files only'
    )
    birthday = models.DateField(blank=True, null=True)
    
    # GIS fields
    home_address = gis_models.PointField(null=True, blank=True, srid=4326)
    office_address = gis_models.PointField(null=True, blank=True, srid=4326)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = CustomUserManager()
    
    def __str__(self):
        return self.username
    
    @property
    def age(self):
        """Calculate user's age"""
        if self.birthday:
            today = date.today()
            return today.year - self.birthday.year - (
                (today.month, today.day) < (self.birthday.month, self.birthday.day)
            )
        return None
    
    @property
    def full_name(self):
        """Get user's full name"""
        return f"{self.first_name} {self.last_name}".strip() or self.username
    
    @property
    def home_to_office_distance(self):
        """Calculate distance from home to office in km"""
        if self.home_address and self.office_address:
            return self.home_address.distance(self.office_address) * 111.319  # Convert degrees to km
        return None
    
    @property
    def has_complete_address(self):
        """Check if user has both home and office addresses"""
        return bool(self.home_address and self.office_address)
    
    def clean(self):
        """Validate model data"""
        super().clean()
        if self.birthday and self.birthday > date.today():
            raise ValidationError("Birthday cannot be in the future")
        if self.documents:
            # Add file validation if needed
            pass
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        
        # Create or update UserRoute if both addresses exist
        if self.has_complete_address:
            route, created = UserRoute.objects.get_or_create(user=self)
            route.save()  # This will trigger the route calculation


class UserRoute(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='route'
    )
    route = gis_models.LineStringField(geography=True, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        """Auto-generate route line when saving"""
        if self.user.home_address and self.user.office_address:
            self.route = LineString(
                (self.user.home_address.x, self.user.home_address.y),
                (self.user.office_address.x, self.user.office_address.y)
            )
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Route for {self.user.username}"
    
    @property
    def distance_km(self):
        """Get route distance in kilometers"""
        if self.route:
            return self.route.length * 111.319  # Convert degrees to km
        return None
    
    def to_geojson(self):
        """Convert route to GeoJSON format"""
        if self.route:
            return {
                "type": "Feature",
                "properties": {
                    "user": self.user.username,
                    "distance_km": self.distance_km,
                    "created_at": self.created_at.isoformat(),
                },
                "geometry": {
                    "type": "LineString",
                    "coordinates": list(self.route.coords)
                }
            }
        return None