from django.shortcuts import render, redirect
from myadmin.models import User,Feedback,Shelter,Product_form,Order_table,Pet,BoardingRequest
from myadmin.models import *
from myadmin.models import User
from django.utils.timezone import now
from django.db.models import Count,Sum
from django.utils import timezone
from django.db.models.functions import TruncMonth
import json
import jwt
import requests
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from myadmin.models import User
from myadmin.serializers import UserSerializer
from myadmin.serializers import *
from rest_framework.decorators import api_view
from django.db import connection
from rest_framework.response import Response
from django.contrib.auth.hashers import make_password, check_password
from django.db.models import Q
from django.core.paginator import Paginator
from rest_framework import status
import uuid
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import check_password
from django.core.mail import send_mail
from django.conf import settings
from .models import PasswordResetToken
from django.db import connection
from decimal import Decimal
from django.forms.models import model_to_dict
from django.db.models.functions import TruncDate
from django.http import JsonResponse
#genai.configure(api_key="AIzaSyBRpHsJc2kv8fXCDe5kbYgzlg8S75_7Bbw")
from django.http import JsonResponse
from .models import User, ChatHistory
from django.http import JsonResponse, StreamingHttpResponse
import requests
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from .models import User, ChatHistory

 #API_KEY = "AIzaSyBtvGU3CZFxeJmWvHWkcdwjRHVwaLOks7c"
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from rest_framework_simplejwt.tokens import RefreshToken
import json
import time
import os
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import ChatHistory

@csrf_exempt
def chat_with_dog_ai(request):
    if request.method != "POST":
        return JsonResponse({"error": "Use POST"}, status=405)

    try:
        data = json.loads(request.body)
        user_message = data.get("message", "").strip()
        user_id = data.get("user_id")

        if not user_message:
            return JsonResponse({"reply": "Woof! I need a message first! 🐶"})

        API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyDIcYQNyBQQi5DYNhhM4DIU1FLV-7D3nkI")

        print(f"API KEY LOADED: {API_KEY[:10]}...")

        # ✅ These are confirmed available on your account
        models_to_try = [
        "gemini-2.5-flash", 
            "gemini-2.0-flash",
            "gemini-2.0-flash-lite",
        ]

        system_prompt = """You are HappyPaws, a friendly dog expert and vet assistant.

STRICT RULES:
1. ONLY answer questions about dogs (breeds, health, food, training, grooming, behavior, vaccines, etc.)
2. If the question is NOT about dogs, reply exactly: "I'm only able to help with dog-related questions! 🐶 Please ask me something about your furry friend."
3. Keep every answer between 100-250 words. Be concise and clear.
4. Always be warm and friendly.
5. If unsure about medical issues, advise consulting a real vet.

User question: """

        ai_reply = "I'm having trouble connecting right now. Please try again! 🐶"

        for model in models_to_try:
            # ✅ v1beta works for both these models
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={API_KEY}"

            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": system_prompt + user_message}
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 350,
                }
            }

            success = False
            for attempt in range(2):
                try:
                    response = requests.post(url, json=payload, timeout=15)
                    result = response.json()

                    if response.status_code == 200:
                        ai_reply = result['candidates'][0]['content']['parts'][0]['text']
                        success = True
                        break

                    elif response.status_code in [429, 503]:
                        print(f"Rate limited, waiting...")
                        time.sleep(2 ** attempt)
                        continue

                    else:
                        error_msg = result.get('error', {}).get('message', 'Unknown')
                        print(f"Model {model} error: {error_msg}")
                        break

                except requests.exceptions.Timeout:
                    print(f"Timeout on {model}, attempt {attempt + 1}")
                    continue
                except Exception as e:
                    print(f"Exception on {model}: {e}")
                    continue

            if success:
                # ✅ Save to chat history
                if user_id:
                    try:
                        ChatHistory.objects.create(
                            user_id=user_id,
                            user_query=user_message,
                            ai_response=ai_reply
                        )
                    except Exception as e:
                        print(f"History save error: {e}")
                return JsonResponse({"reply": ai_reply})

        return JsonResponse({"reply": ai_reply})

    except Exception as e:
        print(f"Server error: {e}")
        return JsonResponse(
            {"reply": "Server error. Please try again! 🐶"},
            status=500
        )

def get_chat_history(request, user_id):
    try:
        chats = ChatHistory.objects.filter(user_id=user_id).order_by("timestamp")
        history = []
        for chat in chats:
            history.append({"role": "user", "text": chat.user_query})
            history.append({"role": "bot", "text": chat.ai_response})
        return JsonResponse({"history": history})
    except Exception as e:
        print("History Error:", e)
        return JsonResponse({"history": []})

from rest_framework import viewsets
from .serializers import (
    UserSerializer,
    FeedbackSerializer,
    ShelterSerializer,
    ProductSerializer,
    OrderSerializer,
    PetSerializer,
    PetHealthSerializer
)


import random
import string
from django.core.mail import send_mail
from rest_framework.decorators import api_view
from rest_framework.response import Response


def generate_password(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

@api_view(['POST'])
def forgot_password(request):
    email = request.data.get("email")

    if not email:
        return Response({"message": "Email required"}, status=400)

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({"message": "Email not registered"}, status=404)

    # Generate new password
    new_password = generate_password(10)

    # 🔥 Hash password manually (IMPORTANT FIX)
    user.password = make_password(new_password)
    user.save()

    # Send email
    send_mail(
        subject="Your New Password - HappyPaws",
        message=f"Your new password is:\n\n{new_password}\n\nPlease login and change it immediately.",
        from_email=settings.EMAIL_HOST_USER,  # safer than None
        recipient_list=[email],
        fail_silently=False,
    )

    return Response({"message": "New password sent to your email"}, status=200)

from django.utils import timezone
from datetime import timedelta

from django.utils import timezone
from datetime import timedelta

@api_view(['POST'])
def reset_password(request):
    token = request.data.get("token")
    new_password = request.data.get("new_password")

    if not token or not new_password:
        return Response({"message": "Token and password required"}, status=400)

    try:
        record = PasswordResetToken.objects.get(token=token)
    except PasswordResetToken.DoesNotExist:
        return Response({"message": "Invalid or expired token"}, status=400)

    # Expiry check (15 minutes)
    if timezone.now() - record.created_at > timedelta(minutes=15):
        record.delete()
        return Response({"message": "Token expired"}, status=400)

    user = record.user

    # 🔥 Hash password manually (IMPORTANT FIX)
    user.password = make_password(new_password)
    user.save()

    record.delete()

    return Response({"message": "Password reset successful"}, status=200)



from django.db.models import Q
from django.contrib.auth.hashers import check_password
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import User, Shelter
from django.views.decorators.csrf import csrf_exempt


from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password, check_password
from django.db.models import Q
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import uuid
import re


from .models import User, Shelter

GOOGLE_WEB_CLIENT_ID = "314947311521-1nndpp6so52q6i88n7qr210m4o5inui6.apps.googleusercontent.com"



# ───────────────────────────────────────────────
#  SIGNUP
# ───────────────────────────────────────────────
@api_view(['POST'])
def signup(request):
    try:
        data = request.data
        
        full_name = data.get('full_name')
        email     = data.get('email')
        contact   = data.get('contact')
        address   = data.get('address')
        username  = data.get('username')
        password  = data.get('password')
        role      = data.get('role', 'user')
        role      = role.lower().strip()

        print("full_name:", full_name)
        print("email:", email)
        print("contact:", contact)
        print("address:", address)
        print("username:", username)
        print("password:", password)
        print("role:", role)

        if role not in ['user', 'shelter', 'admin']:
            print("❌ FAILED: invalid role")
            return Response({"message": "Invalid role"}, status=400)

        if not all([full_name, email, contact, address, username, password]):
            print("❌ FAILED: missing fields")
            print("Missing:", [k for k, v in {
                'full_name': full_name,
                'email': email,
                'contact': contact,
                'address': address,
                'username': username,
                'password': password,
            }.items() if not v])
            return Response({"message": "All fields are required"}, status=400)

        if User.objects.filter(email=email).exists():
            print("❌ FAILED: email exists")
            return Response({"message": "Email already registered"}, status=400)

        if User.objects.filter(username=username).exists():
            print("❌ FAILED: username exists")
            return Response({"message": "Username already taken"}, status=400)

        if len(password) < 8:
            print("❌ FAILED: password too short")
            return Response({"message": "Password must be at least 8 characters"}, status=400)

        if not re.search(r'[A-Z]', password):
            print("❌ FAILED: no uppercase")
            return Response({"message": "Password must contain uppercase letter"}, status=400)

        if not re.search(r'[a-z]', password):
            print("❌ FAILED: no lowercase")
            return Response({"message": "Password must contain lowercase letter"}, status=400)

        if not re.search(r'[0-9]', password):
            print("❌ FAILED: no number")
            return Response({"message": "Password must contain number"}, status=400)

        if not re.search(r'[!@#$%^&*(),.?\":{}|<>]', password):
            print("❌ FAILED: no special char")
            return Response({"message": "Password must contain special character"}, status=400)

        user = User(
            full_name=full_name,
            email=email,
            contact=contact,
            address=address,
            username=username,
            password=make_password(password),
            role=role
        )
        user.save()
        print("✅ USER SAVED:", username)
        return Response({"message": "Signup successful"}, status=201)

    except Exception as e:
        print("SIGNUP ERROR:", str(e))
        return Response({"message": str(e)}, status=500)


# ───────────────────────────────────────────────
#  CHECK EMAIL
# ───────────────────────────────────────────────
@api_view(['POST'])
def check_email(request):
    email = request.data.get('email')
    exists = User.objects.filter(email=email).exists()
    return Response({"exists": exists})


# ───────────────────────────────────────────────
#  CHECK USERNAME
# ───────────────────────────────────────────────
@api_view(['POST'])
def check_username(request):
    username = request.data.get('username')
    exists = User.objects.filter(username=username).exists()
    return Response({"exists": exists})


# ───────────────────────────────────────────────
#  LOGIN
# ───────────────────────────────────────────────
@csrf_exempt
@api_view(['POST'])
def login(request):
    print("USER:", request.user)
    print("AUTH:", request.auth)

    try:
        data = request.data
        identifier = data.get('identifier')
        password = data.get('password')
        role = data.get('role')

        if role:
            role = str(role).lower().strip()

        if not identifier or not password or not role:
            return Response({"message": "All fields required"}, status=400)

        identifier = identifier.strip()

        try:
            user = User.objects.get(
                Q(username=identifier) | Q(email=identifier)
            )
        except User.DoesNotExist:
            return Response({"message": "User not found"}, status=404)

        if str(user.role).lower().strip() != role:
            return Response({
                "message": f"This account is registered as '{user.role}'. Please login as {user.role}"
            }, status=403)

        if not check_password(password, user.password):
            return Response({"message": "Invalid password"}, status=401)

        refresh = RefreshToken()
        refresh['user_id'] = user.user_id

        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        profile_completed = True
        shelter = None

        if user.role == "shelter":
            try:
                shelter = Shelter.objects.get(user=user)
                profile_completed = True
            except Shelter.DoesNotExist:
                try:
                    shelter = Shelter.objects.get(contact=user.contact)
                    shelter.user = user
                    shelter.save()
                    profile_completed = True
                except Shelter.DoesNotExist:
                    profile_completed = False

        return Response({
            "message": "Login successful",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "profile_completed": profile_completed,
            "user": {
                "id": user.user_id,
                "username": user.username,
                "full_name": user.full_name,
                "email": user.email,
                "contact": user.contact,
                "address": user.address,
                "role": user.role
            },
            "shelter_id": shelter.shelter_id if user.role == "shelter" and profile_completed else None
        }, status=200)

    except Exception as e:
        print("LOGIN ERROR:", str(e))
        return Response({"message": "Server error"}, status=500)



# ───────────────────────────────────────────────
#  GOOGLE LOGIN / SIGNUP
# ───────────────────────────────────────────────
@api_view(['POST'])
def google_auth(request):
    try:
        token = request.data.get('id_token')
        role = request.data.get('role', 'user').lower().strip()

        if not token:
            return Response({"message": "Token missing"}, status=400)

        # ✅ Verify token
        try:
            idinfo = id_token.verify_oauth2_token(
                token,
                google_requests.Request(),
                "314947311521-1nndpp6so52q6i88n7qr210m4o5inui6.apps.googleusercontent.com"
            )
        except ValueError as ve:
            print("TOKEN VERIFICATION FAILED:", str(ve))
            return Response({"message": "Invalid Google token"}, status=400)

        email = idinfo.get('email')
        name = idinfo.get('name', '')

        if not email:
            return Response({"message": "Email not found in token"}, status=400)

        print("GOOGLE AUTH - email:", email, "name:", name)

        # ✅ If user already exists, just log them in
        user = User.objects.filter(email=email).first()

        if not user:
            # ✅ Create new Google user
            random_username = email.split('@')[0] + str(uuid.uuid4())[:6]
            random_password = make_password(str(uuid.uuid4()))

            user = User(
                full_name=name,
                email=email,
                username=random_username,
                password=random_password,
                role=role,
                contact=None,
                address=None,
            )
            user.save()
            print("GOOGLE USER SAVED:", user.email)

        # ✅ Generate JWT tokens (same as normal login)
        refresh = RefreshToken()
        refresh['user_id'] = user.user_id

        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        # ✅ Handle shelter profile
        profile_completed = True
        shelter = None

        if user.role == "shelter":
            try:
                shelter = Shelter.objects.get(user=user)
                profile_completed = True
            except Shelter.DoesNotExist:
                profile_completed = False

        return Response({
            "message": "Login successful",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "profile_completed": profile_completed,
            "user": {
                "id": user.user_id,
                "username": user.username,
                "full_name": user.full_name,
                "email": user.email,
                "contact": user.contact,
                "address": user.address,
                "role": user.role,
            },
            "shelter_id": shelter.shelter_id if user.role == "shelter" and profile_completed else None,
        }, status=200)

    except Exception as e:
        print("GOOGLE AUTH ERROR:", str(e))
        return Response({"message": str(e)}, status=500)

@api_view(['POST'])
def add_pet(request):
    try:
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({"message": "User ID required"}, status=400)

        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return Response({"message": "User not found"}, status=404)

        pet_name = request.data.get('pet_name')
        breed = request.data.get('breed')
        age = request.data.get('age')
        weight = request.data.get('weight')  # ✅ get weight separately
        gender = request.data.get('gender')
        pet_image = request.FILES.get('pet_image')

        if not pet_name:
            return Response({"message": "Pet name required"}, status=400)

        pet = Pet.objects.create(
            user=user,
            pet_name=pet_name,
            breed=breed,
            age=age,
            weight=weight,   # ✅ FIXED — was wrongly set to age
            gender=gender,
            pet_image=pet_image
        )

        return Response({
            "message": "Pet added successfully",
            "pet_id": pet.pet_id
        }, status=200)

    except Exception as e:
        print("ADD PET ERROR:", e)   # ✅ always print to see in terminal
        return Response({"message": str(e)}, status=500)


@api_view(['GET'])
def get_user_pets(request, user_id):
    pets = Pet.objects.filter(user__user_id=user_id)

    pet_list = []

    for pet in pets:

        # Get related health records
        health_records = PetHealth.objects.filter(pet=pet)

        health_data = []
        for record in health_records:
            health_data.append({
                "pet_health_id": record.pet_health_id,
                "disease": record.disease,
                "allergies": record.allergies,
                "description": record.description,
                "medicine": record.medicine,
                "vaccine_name": record.vaccine_name,
                "last_vaccination": record.last_vaccination,
                "next_vaccination": record.next_vaccination,
                "reminder_status": record.reminder_status,
            })

        pet_list.append({
            "pet_id": pet.pet_id,
            "pet_name": pet.pet_name,
            "breed": pet.breed,
            "age": pet.age,
            "weight": pet.weight,
            "gender": pet.gender,
            "pet_image": request.build_absolute_uri(pet.pet_image.url) if pet.pet_image else "",
            "health_records": health_data   # ✅ IMPORTANT
        })

    return Response(pet_list)
from django.http import JsonResponse
from rest_framework.decorators import api_view
from .models import Pet, PetHealth

@api_view(['POST'])
def add_pet_health(request):
    if request.method == "POST":
        try:
            pet_id = request.POST.get("pet_id")

            if not pet_id:
                return JsonResponse(
                    {"error": "pet_id is required"},
                    status=400
                )

            # Get pet object
            pet = Pet.objects.get(pet_id=pet_id)

            # Create health record
            health = PetHealth.objects.create(
                pet=pet,
                disease=request.POST.get("disease"),
                allergies=request.POST.get("allergies"),
                medicine=request.POST.get("medicine"),
                description=request.POST.get("description"),
                vaccine_name=request.POST.get("vaccine_name"),
                last_vaccination=request.POST.get("last_vaccination"),
                next_vaccination=request.POST.get("next_vaccination"),
            )

            return JsonResponse({
                "message": "Health record added successfully",
                "health_id": health.pet_health_id  # <-- use the object’s field
            })

        except Pet.DoesNotExist:
            return JsonResponse(
                {"error": "Pet not found"},
                status=404
            )

        except Exception as e:
            return JsonResponse(
                {"error": str(e)},
                status=500
            )

    return JsonResponse(
        {"error": "Invalid request method"},
        status=400
    )

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import BoardingRequest, Shelter


def user_pets(request, user_id):

    pets = Pet.objects.filter(user_id=user_id)

    data = []

    for pet in pets:
        data.append({
            "pet_id": pet.pet_id,
            "pet_name": pet.pet_name
        })

    return JsonResponse(data, safe=False)

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from datetime import datetime
from .models import User, Pet, Shelter, BoardingRequest

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from datetime import datetime
from .models import User, Pet, Shelter, BoardingRequest

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from datetime import datetime
from .models import User, Pet, Shelter, BoardingRequest

from datetime import datetime

@api_view(['POST'])
def book_shelter(request):
    try:
        user_id = request.data.get('user_id')
        pet_id = request.data.get('pet_id')
        shelter_id = request.data.get('shelter_id')
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')

        if not all([user_id, pet_id, shelter_id, start_date, end_date]):
            return Response({"error": "All fields are required."}, status=status.HTTP_400_BAD_REQUEST)

        user = get_object_or_404(User, user_id=user_id)
        pet = get_object_or_404(Pet, pet_id=pet_id)
        shelter = get_object_or_404(Shelter, shelter_id=shelter_id)

        # ✅ Convert dates
        start_dt = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_dt = datetime.strptime(end_date, "%Y-%m-%d").date()

        start_dt = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_dt = datetime.strptime(end_date, "%Y-%m-%d").date()

        if start_dt > end_dt:
            return Response({"error": "Start date cannot be after end date."}, status=status.HTTP_400_BAD_REQUEST)

        total_days = (end_dt - start_dt).days + 1
        if total_days > 31:
            return Response({"error": "Booking cannot exceed 31 days (1 month)."}, status=status.HTTP_400_BAD_REQUEST)



        if start_dt > end_dt:
            return Response({"error": "Start date cannot be after end date."}, status=status.HTTP_400_BAD_REQUEST)

        # ✅ CALCULATE DAYS
        total_days = (end_dt - start_dt).days + 1

        # ✅ GET PRICE PER DAY FROM SHELTER
        price_per_day = shelter.price

        # ✅ CALCULATE TOTAL
        total_amount = price_per_day * total_days

        # ✅ SAVE IN DB (IMPORTANT)
        boarding_request = BoardingRequest.objects.create(
            user=user,
            pet=pet,
            shelter=shelter,
            start_date=start_dt,
            end_date=end_dt,
            boarding_status='pending',

            price_per_day=price_per_day,   # ✅ snapshot
            total_amount=total_amount      # ✅ calculated
        )

        return Response({
            "message": "Booking request sent successfully!",
            "booking_id": boarding_request.request_id,
            "total_amount": total_amount   # optional
        }, status=status.HTTP_200_OK)

    except Exception as e:
        print("Booking error:", e)
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def user_notifications(request, user_id):
    bookings = BoardingRequest.objects.filter(
        user__user_id=user_id,
        boarding_status__in=['approved', 'paid', 'pending']
    )
    data = []
    for b in bookings:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT payment_status 
                FROM shelter_payment
                WHERE request_id = %s
                LIMIT 1
            """, [b.request_id])
            result = cursor.fetchone()
        payment_status = result[0] if result else "pending"
        final_status = "paid" if payment_status == "completed" else b.boarding_status

        # ✅ NOTIFICATION TYPE
        if final_status == "paid":
            notif_type = "payment"
            message = "Payment completed successfully"
        elif final_status == "approved":
            notif_type = "approval"
            message = f"{b.shelter.shelter_name} accepted your request"
        else:
            continue  # skip pending/other

        data.append({
            "booking_id": b.request_id,
            "message": message,
            "notif_type": notif_type,   # ✅ NEW
            "status": final_status,
            "amount": float(b.total_amount) if b.total_amount else 0,
            "price_per_day": float(b.price_per_day) if b.price_per_day else 0,
            "start_date": str(b.start_date),
            "end_date": str(b.end_date),
            "shelter_name": b.shelter.shelter_name if b.shelter else "Unknown Shelter",
        })
    return Response(data)

@api_view(['POST'])
def cancel_booking(request, booking_id):
    try:
        booking = BoardingRequest.objects.get(request_id=booking_id)
        if booking.boarding_status in ['approved']:
            booking.boarding_status = 'cancelled'
            booking.save()
            return Response({"message": "Booking cancelled successfully"})
        else:
            return Response(
                {"error": "Cannot cancel this booking"},
                status=400
            )
    except BoardingRequest.DoesNotExist:
        return Response({"error": "Booking not found"}, status=404)


@api_view(['POST'])
def make_payment(request):
    try:
        data = request.data

        request_id = data.get('request_id')
        user_id = data.get('user_id')

        # 🔥 GET BOOKING DATA
        booking = BoardingRequest.objects.get(request_id=request_id)

        # 🔥 CREATE PAYMENT
        payment = ShelterPayment.objects.create(
    request_id=booking.request_id,
    user_id=booking.user.user_id,        # ✅ FIXED
    shelter_id=booking.shelter.shelter_id,  # ✅ FIXED
    amount=data.get('amount'),
    payment_mode=data.get('payment_mode'),
    payment_status=data.get('payment_status'),
    payment_date=timezone.now(),
)

        return Response({"message": "Payment successful"}, status=200)

    except BoardingRequest.DoesNotExist:
        return Response({"error": "Booking not found"}, status=400)

    except Exception as e:
        return Response({"error": str(e)}, status=500)
from .models import User, Product_form, Order_table, Order_item


@csrf_exempt
def create_order(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            print("DATA:", data)

            user_id = data.get("user_id")
            payment_id = data.get("payment_id")
            items = data.get("items", [])

            print("USER ID:", user_id)
            print("PAYMENT ID:", payment_id)
            print("ITEMS:", items)

            # VALIDATIONS
            if not user_id:
                return JsonResponse({"error": "User not logged in"}, status=400)
            if not items:
                return JsonResponse({"error": "No items provided"}, status=400)

            # CALCULATE TOTAL
            total_amount = sum(
                item["quantity"] * float(item["unit_price"])
                for item in items
            )

            # FIRST PRODUCT (required field)
            first_product = items[0]["product_id"]

            # CREATE ORDER
            order = Order_table.objects.create(
                user_id=user_id,
                product_id=first_product,
                TotalAmount=Decimal(str(total_amount)),
                order_date=timezone.now(),
                payment_status="Paid",
                payment_mode="Online",
                payment_date=timezone.now(),
                timestamp=timezone.now()
            )

            # ADD payment_id IF FIELD EXISTS
            if hasattr(order, 'payment_id'):
                order.payment_id = payment_id
                order.save()

            # CREATE ORDER ITEMS
            for item in items:
                subtotal = item["quantity"] * Decimal(str(item["unit_price"]))
                Order_item.objects.create(
                    order=order,
                    product_id=item["product_id"],
                    quantity=item["quantity"],
                    unit_price=Decimal(str(item["unit_price"])),
                    subtotal=subtotal,
                    total_amount=subtotal,
                    timestamp=timezone.now()
                )

            print("✅ Order created successfully:", order.order_id)

            return JsonResponse({
                "message": "Order created",
                "order_id": order.order_id
            }, status=201)

        except Exception as e:
            import traceback
            traceback.print_exc()
            return JsonResponse({"error": str(e)}, status=500)  # ✅ INSIDE except

    return JsonResponse({"error": "Invalid request"}, status=400)  # ✅ OUTSIDE if block


@api_view(['GET'])
def get_user_orders(request, user_id):
    orders = Order_table.objects.filter(user_id=user_id)
    if not orders.exists():
        return Response({"error": "No orders found"}, status=404)

    data = []
    for order in orders:
        items = Order_item.objects.filter(order=order)
        item_list = []
        for item in items:
            item_list.append({
                "product_name": item.product.product_name,
                "quantity": item.quantity,
                "price": str(item.unit_price)
            })
        data.append({
            "order_id": order.order_id,
            "total": str(order.TotalAmount),
            "payment_id": getattr(order, "payment_id", None),
            "items": item_list
        })
    return Response(data)


def shelter_payments(request):
    shelter_id = request.GET.get('shelter_id')

    payments = ShelterPayment.objects.filter(shelter_id=shelter_id)

    data = []

    for p in payments:
        data.append({
            "user_name": p.user.full_name,
            "pet_name": p.request.pet.pet_name,
            "amount": str(p.amount),
            "payment_mode": p.payment_mode,
            "payment_status": p.payment_status,
            "payment_date": p.payment_date,
        })

    return JsonResponse(data, safe=False)


@api_view(['GET'])
def get_shelter_profile(request, shelter_id):
    try:
        # ✅ CORRECT QUERY
        shelter = Shelter.objects.get(shelter_id=shelter_id)

        data = {
            "shelter_name": shelter.shelter_name,
            "city": shelter.city,
            "capacity": shelter.capacity,
            "available_slot_count": shelter.available_slot_count,
            "price": shelter.price,
            "contact": shelter.contact,
        }

        return Response(data)

    except Shelter.DoesNotExist:
        return Response({"error": "Shelter not found"}, status=404)


@csrf_exempt
def update_shelter_profile(request, shelter_id):
    if request.method == "PUT":
        try:
            data = json.loads(request.body)

            shelter = Shelter.objects.get(shelter_id=shelter_id)

            shelter.shelter_name = data.get('shelter_name', shelter.shelter_name)
            shelter.city = data.get('city', shelter.city)
            shelter.address1 = data.get('address1', shelter.address1)
            shelter.capacity = data.get('capacity', shelter.capacity)
            shelter.available_slot_count = data.get('available_slot_count', shelter.available_slot_count)
            shelter.price = data.get('price', shelter.price)
            shelter.contact = data.get('contact', shelter.contact)

            shelter.save()

            return JsonResponse({"message": "Profile updated successfully"})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
















        
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class FeedbackViewSet(viewsets.ModelViewSet):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer


class ShelterViewSet(viewsets.ModelViewSet):
    queryset = Shelter.objects.all()
    serializer_class = ShelterSerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product_form.objects.all()
    serializer_class = ProductSerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order_table.objects.all()
    serializer_class = OrderSerializer


class PetViewSet(viewsets.ModelViewSet):
    queryset = Pet.objects.all()
    serializer_class = PetSerializer


class PetHealthViewSet(viewsets.ModelViewSet):
    queryset = PetHealth.objects.all()
    serializer_class = PetHealthSerializer

# Create your views here.
def index(request):
    total_users = User.objects.count()
    total_shelters = Shelter.objects.count()
    total_orders = Order_table.objects.count()

    
    # 1. Customers by role
    customers_data = User.objects.values('role').annotate(count=Count('user_id'))
    roles = [entry['role'] for entry in customers_data]
    counts = [entry['count'] for entry in customers_data]

    # 2. Orders per month
    orders_by_month = (
        Order_table.objects
        .annotate(month=TruncMonth('order_date'))
        .values('month')
        .annotate(count=Count('order_id'))
        .order_by('month')
    )
    months = [entry['month'].strftime("%b %Y") for entry in orders_by_month]
    orders_count = [entry['count'] for entry in orders_by_month]

    # 3. Revenue per month
    revenue_by_month = (
        Order_table.objects
        .annotate(month=TruncMonth('order_date'))
        .values('month')
        .annotate(total_revenue=Sum('TotalAmount'))
        .order_by('month')
    )
    revenue_months = [entry['month'].strftime("%b %Y") for entry in revenue_by_month]
    revenue_data = [float(entry['total_revenue']) for entry in revenue_by_month]

    context = {
        'total_users': total_users,
        'total_shelters': total_shelters,
        'total_orders': total_orders,
        'roles': roles,
        'counts': counts,
        'months': months,
        'orders_count': orders_count,
        'revenue_months': revenue_months,
        'revenue_data': revenue_data,
    }
    return render(request, 'myadmin/index.html', context)

def demo(request):
    return render(request,'myadmin/demo.html')

def layout(request):
    return render(request,'myadmin/layout.html')

def login_screen(request):
    return render(request,'myadmin/login_screen.html')

def user(request):
    users = User.objects.all()  
    return render(request, 'myadmin/user.html', {'users': users})


def feedback(request):
    feedbacks = Feedback.objects.all()
    return render(request, 'myadmin/feedback.html', {
        'feedbacks': feedbacks
    })



@api_view(['GET'])
def shelter(request):
    query = request.GET.get('q', '').strip()
    shelters = Shelter.objects.all().order_by('-timestamp')
    if query:
        shelters = Shelter.filter(
            Q(shelter_name__icontains=query) |
            Q(city__icontains=query) |
            Q(area__icontains=query) |
            Q(pincode__icontains=query)
        )
    # make sure pincode is included in serializer response
    data = list(Shelter.values(
        'shelter_id', 'shelter_name', 'city', 'area',
        'address1', 'price', 'available_slot_count',
        'capacity', 'contact', 'pincode'
    ))
    return Response(data)

def shelter_view(request):
    query = request.GET.get('q', '')  # search input

    shelters = Shelter.objects.all()

    # 🔍 Search filter
    if query:
        shelters = shelters.filter(
            shelter_name__icontains=query
        ) | shelters.filter(
            city__icontains=query
        ) | shelters.filter(
            area__icontains=query
        ) | shelters.filter(
            pincode__icontains=query
        )

    context = {
        "shelters": shelters,
        "query": query
    }

    return render(request, "myadmin/shelter.html", context)



def product_form(request):
    products = Product_form.objects.all()
    return render(request, 'myadmin/product.html', {
        'products': products
    })

def product_form(request):
    query = request.GET.get('q', '')   

    products = Product_form.objects.all().order_by('-timestamp')

    if query:
        products = products.filter(
            Q(product_name__icontains=query) |
            Q(category__icontains=query)
        )

    paginator = Paginator(products, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'myadmin/view_product.html', {
        'page_obj': page_obj,
        'query': query
    })


def add_product(request):
    if request.method == "POST":
        product_name = request.POST.get("product_name")
        category = request.POST.get("category")
        price = request.POST.get("price")
        description = request.POST.get("description")
        age_range = request.POST.get("age_range")
        product_image = request.FILES.get("product_image")  # keep file object

        # Save product
        product = Product_form(
            product_name=product_name,
            category=category,
            price=price,
            description=description,
            age_range=age_range,
            product_image=product_image  # pass the actual file
        )
        product.save()

        return redirect('/myadmin/view_product')

    products = Product_form.objects.all()
    return render(request, "myadmin/product.html", {'products': products})


def view_product(request):
    products = Product_form.objects.all().order_by('-timestamp')

    paginator = Paginator(products, 5)  # 5 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'myadmin/view_product.html', {
        'page_obj': page_obj
    })

def order_table(request):
    orders = Order_table.objects.all()
    return render(request, 'myadmin/order_table.html', {
        'orders': orders
    })


# def view_pet(request):
#     pets = Pet.objects.prefetch_related('health_records')
#     return render(request, 'myadmin/view_pet.html', {'pets': pets})



def view_pet(request, id):
    pets = (
        Pet.objects
        .filter(user_id=id)        
        .prefetch_related('health_records')
    )
    return render(request, 'myadmin/view_pet.html', {'pets': pets})




def product_delete(request, id):
    result = Product_form.objects.get(pk=id)
    result.delete()
    return redirect('/myadmin/view_product')


def product_edit(request, id):
    result = Product_form.objects.get(pk=id)

    context = {
        'result': result
    }
    return render(request, 'myadmin/product_edit.html', context)



def product_update(request, id):
    product = Product_form.objects.get(pk=id)
    
    if request.method == 'POST':
        product.product_name = request.POST.get('product_name')
        product.category = request.POST.get('category')
        product.price = request.POST.get('price')
        product.age_range = request.POST.get('age_range')
        product.description = request.POST.get('description')

        # Handle image update
        if request.FILES.get('product_image'):
            product.product_image = request.FILES['product_image']
        
        product.save()
        return redirect('view_product')  # after update, go to product list

    # If GET request (optional)
    return render(request, 'product_edit.html', {'result': product})


def add_shelter(request):
    if request.method == "POST":
        Shelter.objects.create(
            shelter_name=request.POST.get('shelter_name'),

            address1=request.POST.get('address1'),
            address2=request.POST.get('address2'),
            landmark=request.POST.get('landmark'),
            area=request.POST.get('area'),
            city=request.POST.get('city'),
            pincode=request.POST.get('pincode'),

            price=request.POST.get('price'),
            contact=request.POST.get('contact'),
            capacity=request.POST.get('capacity'),
            available_slot_count=request.POST.get('available_slot_count'),
            timestamp=timezone.now()
        )

        return redirect('/myadmin/shelter')  # change if needed

    return render(request, 'myadmin/add_shelter.html')


def shelter_delete(request, id):
    shelter = Shelter.objects.get(pk=id)
    shelter.delete()
    return redirect('/myadmin/shelter')  # Change URL if needed



def shelter_edit(request, id):
    shelter = Shelter.objects.get(pk=id)
    
    context = {
        'result': shelter
    }
    return render(request, 'myadmin/shelter_edit.html', context)



def shelter_update(request, id):
    shelter = Shelter.objects.get(pk=id)

    if request.method == 'POST':
        shelter.shelter_name = request.POST.get('shelter_name')
        shelter.price = request.POST.get('price')
        shelter.contact = request.POST.get('contact')
        shelter.capacity = request.POST.get('capacity')
        shelter.available_slot_count = request.POST.get('available_slot_count')

        shelter.address1 = request.POST.get('address1')
        shelter.address2 = request.POST.get('address2')
        shelter.area = request.POST.get('area')
        shelter.city = request.POST.get('city')
        shelter.landmark = request.POST.get('landmark')
        shelter.pincode = request.POST.get('pincode')

        shelter.save()
        return redirect('/myadmin/shelter')  # Change URL if needed

    return render(request, 'myadmin/shelter_edit.html', {'result': shelter})


def product_details(request, id):
    product = Product_form.objects.filter(product_id=id).first()       
    
    return render(request, 'myadmin/product_details.html', {'product': product})


@csrf_exempt
@api_view(['POST'])
def create_shelter(request):
    try:
        data = request.data

        print("REQUEST DATA:", data)  # 🔥 DEBUG

        user_id = data.get("user_id")

        # ✅ CHECK USER
        if not user_id:
            return Response({"message": "User ID required"}, status=400)

        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return Response({"message": "User not found"}, status=404)

        # ✅ CHECK EXISTING SHELTER
        shelter = Shelter.objects.filter(user=user).first()

        if not shelter:
            shelter = Shelter(user=user)

        name = data.get("shelter_name")
        contact = data.get("contact")
        capacity = data.get("capacity")
        price = data.get("price")

        if not name:
            return Response({"message": "Shelter name required"}, status=400)

        if not contact:
            return Response({"message": "Contact required"}, status=400)

        if not capacity:
            return Response({"message": "Capacity required"}, status=400)

        if price is None or price == "":
            return Response({"message": "Price is required"}, status=400)

        try:
            contact = int(contact)
        except:
            return Response({"message": "Invalid contact"}, status=400)

        try:
            capacity = int(capacity)
        except:
            return Response({"message": "Invalid capacity"}, status=400)

        try:
            price = float(price)
        except:
            return Response({"message": "Invalid price"}, status=400)

        shelter.shelter_name = name
        shelter.contact = contact
        shelter.capacity = capacity
        shelter.available_slot_count = capacity

        shelter.price = price

        shelter.address1 = data.get("address1")
        shelter.address2 = data.get("address2")
        shelter.landmark = data.get("landmark")
        shelter.city = data.get("city")
        shelter.area = data.get("area")
        shelter.pincode = data.get("pincode")

        shelter.save()

        return Response({
            "message": "Shelter profile created successfully"
        }, status=201)

    except Exception as e:
        print("CREATE SHELTER ERROR:", str(e))
        return Response({"message": "Server error"}, status=500)



@api_view(['GET'])
def get_shelter_requests(request, shelter_id):

    requests = BoardingRequest.objects.filter(
        shelter_id=shelter_id
    ).select_related('user', 'pet')  # 🔥 PERFORMANCE BOOST

    print("Shelter ID:", shelter_id)
    print("Total Requests:", requests.count())

    data = []
    for r in requests:

        # 🐶 PET IMAGE (SAFE)
        pet_image = None
        if r.pet.pet_image:
            pet_image = request.build_absolute_uri(r.pet.pet_image.url)

        data.append({
            "request_id": r.request_id,
            "user_name": r.user.full_name,   # ✅ better than username
            "pet_name": r.pet.pet_name,
            "pet_image": pet_image,          # ✅ NEW
            "start_date": str(r.start_date),
            "end_date": str(r.end_date),
            "status": r.boarding_status,
        })

    return Response(data)


@api_view(['POST'])
def update_request_status(request):
    request_id = request.data.get("request_id")
    status = request.data.get("status")

    try:
        req = BoardingRequest.objects.get(request_id=request_id)

        # 🔥 ONLY WHEN APPROVED
        if status == "approved":

            shelter = req.shelter

            if shelter.available_slot_count <= 0:
                return Response({
                    "message": "No slots available"
                }, status=400)

            # 🔥 REDUCE SLOT
            shelter.available_slot_count -= 1
            shelter.save()

        req.boarding_status = status
        req.save()

        return Response({"message": "Updated successfully"})

    except BoardingRequest.DoesNotExist:
        return Response({"message": "Request not found"}, status=404)





@api_view(['GET'])
def current_shelter_pets(request, shelter_id):
    today = now().date()

    bookings = BoardingRequest.objects.filter(
        shelter_id=shelter_id,
        boarding_status='approved',
        start_date__lte=today,
        end_date__gte=today
    ).select_related('pet')

    data = []
    for booking in bookings:
        pet = booking.pet

        data.append({
            "pet_id": pet.pet_id,
            "pet_name": pet.pet_name,
            "breed": pet.breed,
            "age": pet.age,
            "gender": pet.gender,
            "image": request.build_absolute_uri(pet.pet_image.url) if pet.pet_image else None
        })

    return Response(data)


@api_view(['GET'])
def shelter_earnings_dashboard(request, shelter_id):

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    payments = ShelterPayment.objects.filter(
        shelter_id=shelter_id,
        payment_status='completed'
    )

    # 📅 FILTER (IMPORTANT FIX)
    if start_date and end_date:
        payments = payments.filter(
            payment_date__date__gte=start_date,
            payment_date__date__lte=end_date
        )

    # 💰 EARNINGS PER DAY
    earnings_qs = payments.annotate(
        date=TruncDate('payment_date')
    ).values('date').annotate(
        total=Sum('amount')
    ).order_by('date')

    # ✅ FORMAT CLEAN DATA
    earnings_chart = [
        {
            "date": str(item["date"]),
            "total": float(item["total"] or 0)
        }
        for item in earnings_qs
    ]

    # 💰 TOTAL
    total_earnings = sum(item["total"] for item in earnings_chart)

    return Response({
        "earnings_chart": earnings_chart,
        "total_earnings": total_earnings
    })

    