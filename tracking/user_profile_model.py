from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    """
    Extended user profile model to store additional user information.
    This works with Django's built-in User model and MongoDB via djongo.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # You can add more fields as needed:
    # address = models.CharField(max_length=255, blank=True, null=True)
    # date_of_birth = models.DateField(blank=True, null=True)
    # profile_picture = models.ImageField(upload_to='profile_pics', blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"

# Signal to create a user profile when a new user is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        instance.profile.save()
    except UserProfile.DoesNotExist:
        UserProfile.objects.create(user=instance)