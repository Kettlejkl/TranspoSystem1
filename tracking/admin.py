from django.contrib import admin
from .models import Vehicle, RoutePoint, Payment, UserProfile, Transaction


class RoutePointInline(admin.TabularInline):
    model = RoutePoint
    extra = 1


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('plate_number', 'driver_name', 'capacity')
    search_fields = ('plate_number', 'driver_name')
    inlines = [RoutePointInline]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'vehicle', 'amount', 'timestamp')
    list_filter = ('timestamp', 'vehicle')
    date_hierarchy = 'timestamp'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance', 'sender_number', 'updated_at')
    search_fields = ('user__username', 'sender_number')
    list_filter = ('updated_at',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'amount', 'sender_number', 'timestamp')
    list_filter = ('action', 'timestamp')
    search_fields = ('user__username', 'sender_number')
    readonly_fields = ('timestamp',)
    date_hierarchy = 'timestamp'
