from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True)
    bio = models.TextField(blank=True)
    avatar_initials = models.CharField(max_length=3, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.avatar_initials:
            name = self.user.get_full_name() or self.user.username
            parts = name.split()
            self.avatar_initials = ''.join(p[0].upper() for p in parts[:2])
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username}'s profile"
