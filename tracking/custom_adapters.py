# tracking/custom_adapters.py

from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialAccount
from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse

class CustomAccountAdapter(DefaultAccountAdapter):
    """
    Custom adapter for django-allauth to handle compatibility with Djongo (MongoDB)
    """
    def pre_login(self, request, user, **kwargs):
        """
        Override the pre_login method to handle the verified email check in a MongoDB-compatible way
        """
        email = kwargs.get('email', None)
        signup = kwargs.get('signup', False)
        
        # Custom verification check that works with MongoDB by using explicit values
        if email and signup:
            # Use explicit value checks for verified field (1, True) to be MongoDB compatible
            has_verified = EmailAddress.objects.filter(
                Q(user=user) & (Q(verified=1) | Q(verified=True))
            ).exists()
            # You can do something with has_verified if needed
        
        # Continue with the regular flow
        return super().pre_login(request, user, **kwargs)

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Custom social account adapter for django-allauth to handle compatibility with Djongo (MongoDB)
    """
    def pre_social_login(self, request, sociallogin):
        """
        Override pre_social_login to handle verification checks in a MongoDB-compatible way
        and prevent duplicate social account errors
        """
        # Check if this social account already exists
        if not sociallogin.is_existing:
            try:
                # Try to get the existing social account
                social_account = SocialAccount.objects.get(
                    provider=sociallogin.account.provider,
                    uid=sociallogin.account.uid
                )
                # If we get here, a social account exists but is not connected to the current flow
                # Connect the user to the social account
                sociallogin.user = social_account.user
                sociallogin.is_existing = True
                
                # If user is authenticated, we can skip the rest
                if request.user.is_authenticated:
                    return

                # Log the user in directly instead of going through signup
                # This prevents the duplicate key error
                from django.contrib.auth import login
                login(request, social_account.user, backend='django.contrib.auth.backends.ModelBackend')
                
                # Redirect to a success page or home
                # Note: returning a redirect will short-circuit the normal flow
                return redirect('/')  # Change this to your desired redirect path
                
            except SocialAccount.DoesNotExist:
                # This is a new social account, continue with the signup process
                pass
        
        # Handle email verification as in your original code
        if sociallogin.is_existing:
            if sociallogin.account.provider == 'google' or sociallogin.account.provider == 'github':
                # Most social providers verify emails, so we can trust the email is verified
                for email_address in sociallogin.email_addresses:
                    try:
                        # Find if the email already exists in our system
                        existing_email = EmailAddress.objects.get(email=email_address.email)
                        # Set it as verified (using integer for MongoDB compatibility)
                        existing_email.verified = 1
                        existing_email.save()
                    except EmailAddress.DoesNotExist:
                        # Email doesn't exist in our system yet, it will be created during the signup process
                        pass
        
        # Continue with the regular flow
        return super().pre_social_login(request, sociallogin)