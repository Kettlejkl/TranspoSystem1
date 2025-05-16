from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
from django.utils import timezone

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    sender_number = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)  # set once on creation
    updated_at = models.DateTimeField(auto_now=True)      # updated on each save
    
    # deposit and withdraw methods ...
    def deposit(self, amount):
        # Convert both values to Python's Decimal to ensure compatibility
        amount = Decimal(str(amount))  # convert to Decimal safely
        current_balance = Decimal(str(self.balance))  # ensure balance is also Decimal type
        
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
            
        self.balance = current_balance + amount
        self.save()
        return self.balance
    
    def withdraw(self, amount):
        # Convert both values to Python's Decimal to ensure compatibility
        amount = Decimal(str(amount))
        current_balance = Decimal(str(self.balance))
        
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        if amount > current_balance:
            raise ValueError("Insufficient balance")
            
        self.balance = current_balance - amount
        self.save()
        return self.balance  # Fixed typo here (was balancepuy)

class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('deposit', 'Deposit'),
        ('withdraw', 'Withdraw'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    action = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    sender_number = models.CharField(max_length=20)
    timestamp = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.action} of ${self.amount} by {self.user.username}"
        
class Vehicle(models.Model):
    plate_number = models.CharField(max_length=10)
    driver_name = models.CharField(max_length=100)
    capacity = models.IntegerField()
    
    def __str__(self):
        return f"{self.plate_number} - {self.driver_name}"
        
class RoutePoint(models.Model):
    vehicle = models.ForeignKey(Vehicle, related_name='route_points', on_delete=models.CASCADE)
    latitude = models.FloatField()
    longitude = models.FloatField()
    sequence = models.IntegerField()
    
    class Meta:
        ordering = ['sequence']
        
    def __str__(self):
        return f"Point {self.sequence} for {self.vehicle}"
        
class Payment(models.Model):
    user = models.ForeignKey(User, related_name='payments', on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, related_name='payments', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Payment of {self.amount} by {self.user.username}"
        
class WalletTransaction(models.Model):
    user = models.ForeignKey(User, related_name='wallet_transactions', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=20, choices=[
        ('DEPOSIT', 'Deposit'),
        ('WITHDRAWAL', 'Withdrawal'),
        ('PAYMENT', 'Payment'),
    ])
    recipient_name = models.CharField(max_length=100, blank=True, null=True)
    recipient_contact = models.CharField(max_length=100, blank=True, null=True)
    recipient_email = models.EmailField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.transaction_type} of {self.amount} by {self.user.username}"
        
class Feedback(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True)
    subject = models.CharField(max_length=200, blank=True)
    message = models.TextField()
    
    def __str__(self):
        return f"{self.name}: {self.message[:30]}"