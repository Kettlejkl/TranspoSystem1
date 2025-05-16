from django.shortcuts import redirect, render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.db.models import Sum
import json
from decimal import Decimal
import random
import openai

from tracking.utils import analyze_toxicity


from .models import Feedback, Transaction, WalletTransaction, UserProfile
from .forms import FeedbackForm  # Create this form if not done
from .models import Feedback




# View function for the main homepage
def main_homepage(request):
    """View for the main homepage."""
    return render(request, 'tracking/MainHomepage.html')


# View function for the map page
def map_view(request):
    """View for the map page with vehicle tracking functionality."""
    return render(request, 'tracking/map.html')


# View function for about page
def about_view(request):
    """View for the about us page."""
    return render(request, 'tracking/about-us.html')


def feedback_view(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            message = form.cleaned_data['message']

            # Analyze toxicity score
            toxicity_score = analyze_toxicity(message)
            print("Toxicity score:", toxicity_score)  # Debug output

            # Threshold to block toxic feedback
            if toxicity_score >= 0.7:
                messages.error(request, "Your message contains inappropriate language and cannot be submitted.")
                return render(request, 'tracking/feedback.html', {
                    'form': form,
                    'all_feedbacks': Feedback.objects.all().order_by('-id'),
                })

            # Save only if feedback is not toxic
            form.save()
            messages.success(request, "Thank you for your feedback!")
            return redirect('feedback')
    else:
        form = FeedbackForm()

    # Show all feedbacks in GET request or if form is invalid
    all_feedbacks = Feedback.objects.all().order_by('-id')
    return render(request, 'tracking/feedback.html', {
        'form': form,
        'all_feedbacks': all_feedbacks,
    })

# API endpoint to get vehicle data - used by both API paths
def vehicles_api(request):
    """API view that returns vehicle data including routes and info for Manila jeepneys."""
    vehicles = [
        {
            'id': 1,
            'plateNumber': f"{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}{random.randint(100, 999)}",
            'driverName': f"{random.choice(['Juan', 'Pedro', 'Ricardo', 'Manuel', 'Carlo', 'Eduardo'])} {random.choice(['Santos', 'Reyes', 'Cruz', 'Garcia', 'Mendoza', 'Dela Cruz'])}",
            'capacity': random.randint(16, 22),
            'routeName': 'Pasig-Quiapo',
            'routeColor': '#FF0000', # Red color for Pasig-Quiapo route
            'route': [
                {'lat': 14.569391, 'lng': 121.081547},
                {'lat': 14.567177, 'lng': 121.080232},
                {'lat': 14.566141, 'lng': 121.077492},
                {'lat': 14.566124, 'lng': 121.076063},
                {'lat': 14.566170, 'lng': 121.073506},
                {'lat': 14.566295, 'lng': 121.070878},
                {'lat': 14.565953, 'lng': 121.070183},
                {'lat': 14.563603, 'lng': 121.069252},
                {'lat': 14.562798, 'lng': 121.067493},
                {'lat': 14.563317, 'lng': 121.065379},
                {'lat': 14.567330, 'lng': 121.065935},
                {'lat': 14.570228, 'lng': 121.066436},
                {'lat': 14.576790, 'lng': 121.058694},
                {'lat': 14.587210, 'lng': 121.046462},
                {'lat': 14.588027, 'lng': 121.044851},
                {'lat': 14.589162, 'lng': 121.041724},
                {'lat': 14.589473, 'lng': 121.037087},
                {'lat': 14.589463, 'lng': 121.035330},
                {'lat': 14.590018, 'lng': 121.034726},
                {'lat': 14.590780, 'lng': 121.033214},
                {'lat': 14.591870, 'lng': 121.030752},
                {'lat': 14.593059, 'lng': 121.028474},
                {'lat': 14.594645, 'lng': 121.024300},
                {'lat': 14.596130, 'lng': 121.020436},
                {'lat': 14.595902, 'lng': 121.019916},
                {'lat': 14.597661, 'lng': 121.017623},
                {'lat': 14.597339, 'lng': 121.015964},
                {'lat': 14.597574, 'lng': 121.015540},
                {'lat': 14.600601, 'lng': 121.013482},
                {'lat': 14.602424, 'lng': 121.011635},
                {'lat': 14.601235, 'lng': 121.000645},
                {'lat': 14.601080, 'lng': 120.997996},
                {'lat': 14.600483, 'lng': 120.996119},
                {'lat': 14.601229, 'lng': 120.994140},
                {'lat': 14.601585, 'lng': 120.992512},
                {'lat': 14.600524, 'lng': 120.991123},
                {'lat': 14.597343, 'lng': 120.989440},
                {'lat': 14.596441, 'lng': 120.989538},
                {'lat': 14.594352, 'lng': 120.988239},
                {'lat': 14.592472, 'lng': 120.987129},
                {'lat': 14.593764, 'lng': 120.985286},
                # Quiapo Church (End point) - approach properly
                {'lat': 14.596382, 'lng':120.983288},
                {'lat': 14.5977, 'lng': 120.9831}
            ]
        },
        {
            'id': 2,
            'plateNumber': f"{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}{random.randint(100, 999)}",
            'driverName': f"{random.choice(['Juan', 'Pedro', 'Ricardo', 'Manuel', 'Carlo', 'Eduardo'])} {random.choice(['Santos', 'Reyes', 'Cruz', 'Garcia', 'Mendoza', 'Dela Cruz'])}",
            'capacity': random.randint(16, 22),
            'routeName': 'Punta-Quiapo',
            'routeColor': '#0000FF', # Blue color for Punta-Quiapo route
            'route': [
                # Punta Sta. Ana (Starting point)
                {'lat': 14.585802, 'lng': 121.011084},
                {'lat': 14.586383, 'lng': 121.012381},
                {'lat': 14.587023, 'lng': 121.013234},
                {'lat': 14.587238, 'lng': 121.013948},
                {'lat': 14.587128, 'lng': 121.014309},
                {'lat': 14.587356, 'lng': 121.014725},
                {'lat': 14.587697, 'lng': 121.015830},
                {'lat': 14.587558, 'lng': 121.016139},
                {'lat': 14.587546, 'lng': 121.017678},
                {'lat': 14.587567, 'lng': 121.019645},
                {'lat': 14.587504, 'lng': 121.020328},
                {'lat': 14.587323, 'lng': 121.020776},
                {'lat': 14.589021, 'lng': 121.022425},
                {'lat': 14.590180, 'lng': 121.023781},
                {'lat': 14.591805, 'lng': 121.025858},
                {'lat': 14.593698, 'lng': 121.026965},
                {'lat': 14.594645, 'lng': 121.024300},
                {'lat': 14.596130, 'lng': 121.020436},
                {'lat': 14.595902, 'lng': 121.019916},
                {'lat': 14.597661, 'lng': 121.017623},
                {'lat': 14.597339, 'lng': 121.015964},
                {'lat': 14.597574, 'lng': 121.015540},
                {'lat': 14.600601, 'lng': 121.013482},
                {'lat': 14.602424, 'lng': 121.011635},
                {'lat': 14.601235, 'lng': 121.000645},
                {'lat': 14.601080, 'lng': 120.997996},
                {'lat': 14.600483, 'lng': 120.996119},
                {'lat': 14.601229, 'lng': 120.994140},
                {'lat': 14.601585, 'lng': 120.992512},
                # More detailed route through San Miguel
                {'lat': 14.600458, 'lng': 120.991087},
                {'lat': 14.600566, 'lng': 120.991205},
                {'lat': 14.599144, 'lng': 120.990271},
                {'lat': 14.599352, 'lng': 120.989687},
                {'lat': 14.599284, 'lng': 120.989306},
                {'lat': 14.599486, 'lng': 120.988810},
                {'lat': 14.599042, 'lng': 120.987940},
                {'lat': 14.598231, 'lng': 120.985832},
                # Quiapo Church (End point)
                {'lat': 14.597868, 'lng': 120.984886},
                {'lat': 14.597895960834517,'lng': 120.98467323114842}
            ]
        },
        {
            'id': 3,
            'plateNumber': f"{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}{random.randint(100, 999)}",
            'driverName': f"{random.choice(['Juan', 'Pedro', 'Ricardo', 'Manuel', 'Carlo', 'Eduardo'])} {random.choice(['Santos', 'Reyes', 'Cruz', 'Garcia', 'Mendoza', 'Dela Cruz'])}",
            'capacity': random.randint(16, 22),
            'routeName': 'San Miguel-Quiapo',
            'routeColor': '#008000', # Green color for San Miguel-Quiapo route
            'route': [
                # San Miguel, Manila (Starting point near Malacañang)
                {'lat': 14.590385, 'lng': 120.983128},
                {'lat': 14.590409, 'lng': 120.985416},
                {'lat': 14.590142, 'lng': 120.985772},
                {'lat': 14.590691, 'lng': 120.986234},
                {'lat': 14.591794, 'lng': 120.986802},
                {'lat': 14.592992, 'lng': 120.987468},
                # More detailed route through San Miguel
                {'lat': 14.594251, 'lng': 120.988238},
                {'lat': 14.595572, 'lng': 120.989006},
                {'lat': 14.596496, 'lng': 120.989563},
                {'lat': 14.597784, 'lng': 120.989574},
                {'lat': 14.599092, 'lng': 120.990347},
                {'lat': 14.599352, 'lng': 120.989687},
                {'lat': 14.599284, 'lng': 120.989306},
                {'lat': 14.599486, 'lng': 120.988810},
                {'lat': 14.599042, 'lng': 120.987940},
                {'lat': 14.598231, 'lng': 120.985832},
                # Quiapo Church (End point)
                {'lat': 14.597868, 'lng': 120.984886},
                {'lat': 14.597895960834517,'lng': 120.98467323114842}
            ]
        }
    ]
    return JsonResponse(vehicles, safe=False)


# Maintain compatibility with existing code
get_vehicle_data = vehicles_api


@login_required
def wallet_view(request):
    # Get the user's profile or create if it doesn't exist
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    # Get recent transactions
    transactions = Transaction.objects.filter(user=request.user).order_by('-timestamp')[:5]
    
    context = {
        'user_profile': user_profile,
        'transactions': transactions,
    }
    
    return render(request, 'tracking/wallet.html', context)


@login_required
@csrf_exempt
def update_balance(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            action = data.get('action')
            amount = float(data.get('amount', 0))
            
            # Get the user profile
            user_profile = UserProfile.objects.get(user=request.user)
            
            # Update balance based on action
            if action == 'deposit':
                new_balance = user_profile.deposit(amount)
                return JsonResponse({
                    'success': True,
                    'balance': float(new_balance),
                    'message': f'Successfully deposited ${amount:.2f}'
                })
            elif action == 'withdraw':
                try:
                    new_balance = user_profile.withdraw(amount)
                    return JsonResponse({
                        'success': True,
                        'balance': float(new_balance),
                        'message': f'Successfully withdrew ${amount:.2f}'
                    })
                except ValueError as e:
                    return JsonResponse({
                        'success': False,
                        'message': str(e)
                    })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Invalid action'
                })
                
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
        
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

@login_required
@csrf_exempt
def update_wallet(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            amount = float(data.get('amount', 0))

            user_profile = UserProfile.objects.get(user=request.user)

            # Example logic: simply add amount to balance
            new_balance = user_profile.deposit(amount)
            return JsonResponse({
                'success': True,
                'balance': float(new_balance),
                'message': f'Wallet updated with ${amount:.2f}'
            })
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

@login_required
@csrf_exempt
def submit_wallet(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            # Assuming wallet submission includes some fields, e.g., 'payment_method' or 'notes'
            payment_method = data.get('payment_method', '')
            notes = data.get('notes', '')

            user_profile = UserProfile.objects.get(user=request.user)

            # Implement your wallet submission logic here
            # e.g., create a Transaction record
            Transaction.objects.create(
                user=request.user,
                amount=0,  # or any relevant amount
                type='submission',
                notes=notes,
                payment_method=payment_method,
            )

            return JsonResponse({'success': True, 'message': 'Wallet submission successful'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

# Process fare payment from the map interface
@login_required
@require_POST
def pay_fare(request):
    """API endpoint to process fare payments."""
    try:
        data = json.loads(request.body)
        amount = Decimal(data.get('amount', 0))
        vehicle_id = data.get('vehicle_id', '')
        
        # Create a payment transaction record
        transaction = WalletTransaction.objects.create(
            user=request.user,
            amount=amount,
            transaction_type='PAYMENT',
            recipient_name=f'JeepneySystem-Vehicle-{vehicle_id}',
            recipient_contact='',
            recipient_email=''
        )
        
        # Calculate new balance
        deposits = WalletTransaction.objects.filter(
            user=request.user, 
            transaction_type='DEPOSIT'
        ).aggregate(sum=Sum('amount'))['sum'] or 0
        
        withdrawals = WalletTransaction.objects.filter(
            user=request.user, 
            transaction_type__in=['WITHDRAWAL', 'PAYMENT']
        ).aggregate(sum=Sum('amount'))['sum'] or 0
        
        balance = deposits - withdrawals
        
        return JsonResponse({
            'success': True,
            'balance': float(balance),
            'message': 'Fare payment successful'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


def register_view(request):
    """View for the registration page."""
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return render(request, 'tracking/register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return render(request, 'tracking/register.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return render(request, 'tracking/register.html')

        user = User.objects.create_user(username=username, email=email, password=password1)
        messages.success(request, "Account created successfully! Please log in.")
        return redirect('login')

    return render(request, 'tracking/register.html')


def login_view(request):
    """View for the login page."""
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('main_homepage')
        else:
            messages.error(request, "Invalid username or password.")
            return render(request, 'tracking/login.html')
    
    return render(request, 'tracking/login.html')

# ✅ AI SUPPORT PAGE VIEW
@csrf_exempt
def support_chat_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_message = data.get('message')

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful AI support assistant for a public transport app."},
                    {"role": "user", "content": user_message}
                ]
            )
            answer = response.choices[0].message.content.strip()
            return JsonResponse({"success": True, "response": answer})

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return render(request, 'tracking/support_chat.html')