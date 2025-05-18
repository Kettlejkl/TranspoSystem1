from django.shortcuts import render, redirect
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
from allauth.socialaccount.models import SocialAccount
from bson import Decimal128


from tracking.utils import analyze_toxicity


from .models import Feedback, Transaction, WalletTransaction, UserProfile
from .forms import FeedbackForm  # Create this form if not done
from .models import Feedback
import requests 
OPENROUTER_API_KEY = "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"



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
                {'lat': 14.593220, 'lng': 120.985961},
                {'lat': 14.593764, 'lng': 120.985286},
                # Quiapo Church (End point) - approach properly
                {'lat': 14.595491, 'lng': 120.983855},
                {'lat': 14.596193, 'lng': 120.983388},
                {'lat': 14.596559, 'lng': 120.983790},
                {'lat': 14.597585, 'lng': 120.983960},
                {'lat': 14.598770, 'lng': 120.984233},
                {'lat': 14.600661, 'lng': 120.984607},
                {'lat': 14.601765, 'lng': 120.984859},
                {'lat': 14.601912, 'lng': 120.984939},
                {'lat': 14.602855, 'lng': 120.985122},
                {'lat': 14.602962, 'lng': 120.985264},
                {'lat': 14.602639, 'lng': 120.985992},
                {'lat': 14.602136, 'lng': 120.987127},
                {'lat': 14.601395, 'lng': 120.988701},
                {'lat': 14.600408, 'lng': 120.990780},
                {'lat': 14.600410, 'lng': 120.991115},
                {'lat': 14.600911, 'lng': 120.991521},
                {'lat': 14.601585, 'lng': 120.992512},
                {'lat': 14.601229, 'lng': 120.994140},
                {'lat': 14.600483, 'lng': 120.996119},
                {'lat': 14.601080, 'lng': 120.997996},
                {'lat': 14.601235, 'lng': 121.000645},
                {'lat': 14.602424, 'lng': 121.011635},
                {'lat': 14.600601, 'lng': 121.013482},
                {'lat': 14.597574, 'lng': 121.015540},
                {'lat': 14.597339, 'lng': 121.015964},
                {'lat': 14.597661, 'lng': 121.017623},
                {'lat': 14.595902, 'lng': 121.019916},
                {'lat': 14.596130, 'lng': 121.020436},
                {'lat': 14.594645, 'lng': 121.024300},
                {'lat': 14.593059, 'lng': 121.028474},
                {'lat': 14.591870, 'lng': 121.030752},
                {'lat': 14.590780, 'lng': 121.033214},
                {'lat': 14.590018, 'lng': 121.034726},
                {'lat': 14.589463, 'lng': 121.035330},
                {'lat': 14.589473, 'lng': 121.037087},
                {'lat': 14.589162, 'lng': 121.041724},
                {'lat': 14.588027, 'lng': 121.044851},
                {'lat': 14.587210, 'lng': 121.046462},
                {'lat': 14.576790, 'lng': 121.058694},
                {'lat': 14.570228, 'lng': 121.066436},
                {'lat': 14.567330, 'lng': 121.065935},
                {'lat': 14.563317, 'lng': 121.065379},
                {'lat': 14.562798, 'lng': 121.067493},
                {'lat': 14.563603, 'lng': 121.069252},
                {'lat': 14.565953, 'lng': 121.070183},
                {'lat': 14.566295, 'lng': 121.070878},
                {'lat': 14.566170, 'lng': 121.073506},
                {'lat': 14.566124, 'lng': 121.076063},
                {'lat': 14.566141, 'lng': 121.077492},
                {'lat': 14.567177, 'lng': 121.080232},
                {'lat': 14.569391, 'lng': 121.081547},
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
                {'lat': 14.601585, 'lng': 120.992512},
                # More detailed route through San Miguel
                {'lat': 14.600566, 'lng': 120.991205},
                {'lat': 14.599144, 'lng': 120.990271},
                {'lat': 14.599352, 'lng': 120.989687},
                {'lat': 14.599284, 'lng': 120.989306},
                {'lat': 14.599486, 'lng': 120.988810},
                {'lat': 14.599042, 'lng': 120.987940},
                {'lat': 14.598231, 'lng': 120.985832},
                # Quiapo Church (End point)
                {'lat': 14.597868, 'lng': 120.984886},
                {'lat': 14.597926103624483,'lng': 120.98450142628147},
                {'lat': 14.597340, 'lng':  120.984402},
                {'lat': 14.597126, 'lng':  120.985642},
                {'lat': 14.596776, 'lng':  120.987770},
                {'lat': 14.596536, 'lng':  120.989226},
                {'lat': 14.596504, 'lng':  120.989598},
                {'lat': 14.596930, 'lng':  120.989615},
                {'lat': 14.597660, 'lng':  120.989557},
                {'lat': 14.599092, 'lng':  120.990274},
                {'lat': 14.600074, 'lng':  120.990779},
                {'lat': 14.600566, 'lng': 120.991205},
                {'lat': 14.601585, 'lng': 120.992512},
                {'lat': 14.600483, 'lng': 120.996119},
                {'lat': 14.601080, 'lng': 120.997996},
                {'lat': 14.601235, 'lng': 121.000645},
                {'lat': 14.602424, 'lng': 121.011635},
                {'lat': 14.600601, 'lng': 121.013482},
                {'lat': 14.597574, 'lng': 121.015540},
                {'lat': 14.597339, 'lng': 121.015964},
                {'lat': 14.597661, 'lng': 121.017623},
                {'lat': 14.595902, 'lng': 121.019916},
                {'lat': 14.596130, 'lng': 121.020436},
                {'lat': 14.594645, 'lng': 121.024300},
                {'lat': 14.593698, 'lng': 121.026965},
                {'lat': 14.591805, 'lng': 121.025858},
                {'lat': 14.590180, 'lng': 121.023781},
                {'lat': 14.589021, 'lng': 121.022425},
                {'lat': 14.587323, 'lng': 121.020776},
                {'lat': 14.587504, 'lng': 121.020328},
                {'lat': 14.587567, 'lng': 121.019645},
                {'lat': 14.587546, 'lng': 121.017678},
                {'lat': 14.587558, 'lng': 121.016139},
                {'lat': 14.587697, 'lng': 121.015830},
                {'lat': 14.587356, 'lng': 121.014725},
                {'lat': 14.587128, 'lng': 121.014309},
                {'lat': 14.587238, 'lng': 121.013948},
                {'lat': 14.587023, 'lng': 121.013234},
                {'lat': 14.586383, 'lng': 121.012381},
                {'lat': 14.585802, 'lng': 121.011084}
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
                {'lat': 14.599092, 'lng': 120.990347},
                {'lat': 14.597784, 'lng': 120.989574},
                {'lat': 14.596496, 'lng': 120.989563},
                {'lat': 14.595572, 'lng': 120.989006},
                {'lat': 14.594251, 'lng': 120.988238},
                {'lat': 14.592992, 'lng': 120.987468},
                {'lat': 14.591794, 'lng': 120.986802},
                {'lat': 14.590691, 'lng': 120.986234},
                {'lat': 14.590142, 'lng': 120.985772},
                {'lat': 14.590409, 'lng': 120.985416},
                {'lat': 14.590385, 'lng': 120.983128}
            ]
        }
    ]
    return JsonResponse(vehicles, safe=False)


# Maintain compatibility with existing code
get_vehicle_data = vehicles_api


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
@require_POST
def update_wallet(request):
    try:
        data = json.loads(request.body)
        amount = Decimal(str(data.get('amount', '0')))
        action = data.get('action', '').lower()

        user_profile = UserProfile.objects.get(user=request.user)

        # Convert balance if stored as Decimal128
        if isinstance(user_profile.balance, Decimal128):
            user_profile.balance = user_profile.balance.to_decimal()
        elif isinstance(user_profile.balance, str):
            user_profile.balance = Decimal(user_profile.balance)

        if amount <= 0:
            return JsonResponse({'success': False, 'message': 'Amount must be positive'})

        if action == 'deposit':
            new_balance = user_profile.deposit(amount)
        elif action == 'withdraw':
            if amount > user_profile.balance:
                return JsonResponse({'success': False, 'message': 'Insufficient balance'})
            new_balance = user_profile.withdraw(amount)
        else:
            return JsonResponse({'success': False, 'message': 'Invalid action'})

        return JsonResponse({
            'success': True,
            'balance': float(new_balance),
            'message': f'{action.capitalize()} of ${amount:.2f} successful'
        })

    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

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
    """View for the login page with OAuth options."""
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Redirect to next parameter if available, otherwise to main homepage
            next_url = request.POST.get('next', 'main_homepage')
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password.")
            return render(request, 'tracking/login.html')
    
    return render(request, 'tracking/login.html')

@login_required
def profile_view(request):
    """View for user profile with social account information."""
    # Check if user has connected social accounts
    social_accounts = SocialAccount.objects.filter(user=request.user)
    
    # Get user's Google account if connected
    google_account = social_accounts.filter(provider='google').first()
    github_account = social_accounts.filter(provider='github').first()
    
    context = {
        'user': request.user,
        'google_account': google_account,
        'github_account': github_account,
    }
    
    return render(request, 'tracking/profile.html', context)

# Custom handler for social login failures
def social_login_error(request):
    """Handle social login errors."""
    messages.error(
        request, 
        "There was an error during social authentication. Please try again or use traditional login."
    )
    return redirect('login')

def social_login_error(request):
    """Handle social login errors."""
    messages.error(
        request, 
        "There was an error during social authentication. Please try again or use traditional login."
    )
    return redirect('login')

@login_required
def main_homepage(request):
    """Main homepage view after login."""
    # Your implementation here
    return render(request, 'tracking/mainhomepage.html')

# ✅ AI SUPPORT PAGE VIEW
@csrf_exempt
def support_chat_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_message = data.get('message')

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://yourdomain.com/",  # Required by OpenRouter
            "X-Title": "Smart Transport Assistant"     # Optional: title shown on OpenRouter dashboard
        }

        body = {
            "model": "openai/gpt-3.5-turbo",  # You can change this to another model like anthropic/claude-3-opus if supported
            "messages": [
                {"role": "system", "content": "You are a helpful AI support assistant for a public transport app."},
                {"role": "user", "content": user_message}
            ]
        }

        try:
            response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=body)
            response_data = response.json()

            if "choices" in response_data:
                answer = response_data["choices"][0]["message"]["content"].strip()
                return JsonResponse({"success": True, "response": answer})
            else:
                return JsonResponse({"success": False, "error": response_data.get("error", "Unknown error")})

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return render(request, 'tracking/support_chat.html')