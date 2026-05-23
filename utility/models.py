from django.db import models

# Create your models here.

class SiteSettings(models.Model):
    siteName = models.CharField(max_length=100)
    siteFavIconLink = models.CharField(max_length=100)
    siteLink = models.CharField(max_length=100)
    uUid = models.CharField(max_length=10)
    def __str__(self):
        return self.siteName

class AdminUser(models.Model):
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=40)
    def __str__(self):
        return self.username


class Otp(models.Model):
    PURPOSE_CHOICES = [
        ("signup", "Signup"),
        ("login", "Login"),
        ("password_reset", "Password Reset"),
    ]

    email = models.EmailField()
    otp_code = models.CharField(max_length=6)
    purpose = models.CharField(
        max_length=20,
        choices=PURPOSE_CHOICES
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "otp_table"

    def __str__(self):
        return f"{self.email} - {self.purpose}"


