from django.conf import settings

def google_maps_api_key(request):
    """
    Context processor to add the Google Maps API key to the context
    """
    return {
        'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY,
    }