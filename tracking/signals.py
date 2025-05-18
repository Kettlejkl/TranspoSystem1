# tracking/signals.py - Full code for handling OAuth user creation

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from allauth.socialaccount.models import SocialAccount
from django.utils.text import slugify
import uuid

@receiver(post_save, sender=SocialAccount)
def create_username_for_social_user(sender, instance, created, **kwargs):
    """
    Create a username for users who sign up via social auth.
    This is useful when ACCOUNT_USERNAME_REQUIRED = False but you still want
    users to have a username.
    """
    if created:
        user = instance.user
        
        # Skip if user already has a non-empty username
        if user.username and not user.username.startswith('user_'):
            return
            
        if instance.provider == 'google':
            # Get data from Google account
            extra_data = instance.extra_data
            name = extra_data.get('name', '')
            
            if name:
                # Create username from name
                base_username = slugify(name)
                username = base_username
                
                # Check if username exists
                counter = 1
                while User.objects.filter(username=username).exclude(id=user.id).exists():
                    username = f"{base_username}{counter}"
                    counter += 1
                    
                user.username = username
                user.save()
                
        elif instance.provider == 'github':
            # Get data from GitHub account
            extra_data = instance.extra_data
            login = extra_data.get('login', '')
            
            if login:
                # Use GitHub username if available
                username = login
                
                # Check if username exists
                counter = 1
                base_username = username
                while User.objects.filter(username=username).exclude(id=user.id).exists():
                    username = f"{base_username}{counter}"
                    counter += 1
                    
                user.username = username
                user.save()
                
        # If no username was set, use a random one
        if not user.username or user.username.startswith('user_'):
            user.username = f"user_{uuid.uuid4().hex[:10]}"
            user.save()