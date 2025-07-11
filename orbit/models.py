from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.gis.db import models as gis_models
from django.contrib.gis.geos import LineString
from django.conf import settings

# --- Extended CustomUser model ---
class CustomUser(AbstractUser):
    country = models.CharField(max_length=100)
    bio = models.TextField(blank=True)
    phone_number = models.CharField(max_length=20)
    areas_of_interest = models.JSONField(default=list, blank=True)
    documents = models.FileField(upload_to='documents/', blank=True, null=True)
    birthday = models.DateField(blank=True, null=True)
    home_location = gis_models.PointField(null=True, blank=True, srid=4326)
    office_location = gis_models.PointField(null=True, blank=True, srid=4326)


    def __str__(self):
        return self.username

# --- UserRoute model: Line from home to office ---
class UserRoute(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    route = gis_models.LineStringField(geography=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.user.home_location and self.user.office_location:
            self.route = LineString(
                (self.user.home_location.x, self.user.home_location.y),
                (self.user.office_location.x, self.user.office_location.y)
            )
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Route for {self.user.username}"
