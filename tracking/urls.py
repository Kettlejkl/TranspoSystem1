from django.urls import path
from django.views.generic import RedirectView
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Main homepage route
    path('', views.main_homepage, name='main_homepage'),

    # Redirect '/home/' to '/'
    path('home/', RedirectView.as_view(url='/', permanent=True), name='home'),

    # Other pages
    path('map/', views.map_view, name='map'),  # Map page route
    path('login/', views.login_view, name='login'),  # Custom login page
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('accounts/login/', views.login_view),  # Fallback for Django default redirects
    path('register/', views.register_view, name='register'),  # Registration page
    path('about/', views.about_view, name='about_us'),  # About Us page route
    path('feedback/', views.feedback_view, name='feedback'),
    path('wallet/', views.wallet_view, name='wallet'),  # Wallet page

    # Existing API endpoints
    path('api/vehicle-data/', views.get_vehicle_data, name='get_vehicle_data'),
    path('api/vehicles/', views.vehicles_api, name='vehicles_api'),

    # Wallet API endpoints
    path('api/update-balance/', views.update_balance, name='update_balance'),

    # ✅ Make sure these two views exist in views.py
    path('api/wallet/update/', views.update_wallet, name='update_wallet'),  # New standardized endpoint
    path('api/wallet/submit/', views.submit_wallet, name='submit_wallet'),  # New endpoint for saving wallet info

    #AI Integration
    path('support/', views.support_chat_view, name='support_chat'),

    # Social auth error handler
    path('social-login-error/', views.social_login_error, name='social_login_error')
]
