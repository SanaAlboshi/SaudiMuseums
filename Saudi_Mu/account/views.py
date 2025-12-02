from django.shortcuts import render, redirect
from django.http import HttpRequest
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db import IntegrityError, transaction
from .models import Profile
from django.db import transaction
from django.core.mail import send_mail
from django.conf import settings
# -----------------------------
# Sign Up
# -----------------------------


def sign_up(request: HttpRequest):
    if request.method == "POST":
        try:
            with transaction.atomic():
                # Create the user
                new_user = User.objects.create_user(
                    username=request.POST["username"],
                    password=request.POST["password"],
                    email=request.POST["email"],
                    first_name=request.POST["first_name"],
                    last_name=request.POST["last_name"]
                )
                new_user.save()

                # Create the profile
                avatar = request.FILES.get("avatar")
                if not avatar:
                    avatar = Profile.avatar.field.get_default()

                profile = Profile.objects.create(
                    user=new_user,
                    avatar=avatar
                )

            # Send welcome email
            send_mail(
                subject="Successfully registered on our site",
                message=f"Hello {new_user.first_name},\n\nYou have successfully registered on our site . Welcome!",
                from_email=settings.DEFAULT_FROM_EMAIL,  
                recipient_list=[new_user.email],
                fail_silently=False,
            )

            # Automatically log in the user
            login(request, new_user)
            messages.success(request, "Registered and logged in successfully! Check your email.")
            return redirect("account:user_profile_view", user_name=new_user.username)

        except IntegrityError:
            messages.error(request, "Username already exists. Please choose another.")
        except Exception as e:
            messages.error(request, "Could not register the user. Please try again.")
            print(e)

    return render(request, "account/signup.html")


# -----------------------------
# Sign In
# -----------------------------
def sign_in(request: HttpRequest):
    if request.method == "POST":
        user = authenticate(
            request,
            username=request.POST["username"],
            password=request.POST["password"]
        )
        if user:
            login(request, user)
            messages.success(request, "Logged in successfully")
            return redirect(request.GET.get("next", "/"))
        else:
            messages.error(request, "Your credentials are wrong, please try again")

    return render(request, "account/signin.html")

# -----------------------------
# Log Out
# -----------------------------

def log_out(request: HttpRequest):
    logout(request)
    messages.success(request, "Logged out successfully")
    return redirect(request.GET.get("next", "/"))

# -----------------------------
# User Profile View
# -----------------------------

def user_profile_view(request: HttpRequest, user_name):
    try:
        user = User.objects.get(username=user_name)
        # تأكد من وجود البروفايل
        profile, created = Profile.objects.get_or_create(user=user)

        # حساب الإحصائيات (بداية بصفر)
        visited_museums_count = getattr(profile, "visited_museums_count", 0)
        bookmarks_count = getattr(profile, "bookmarks_count", 0)
        user_comments = getattr(profile, "user_comments", [])

    except User.DoesNotExist:
        return render(request, '404.html')

    context = {
        "user": user,
        "profile": profile,
        "visited_museums_count": visited_museums_count,
        "bookmarks_count": bookmarks_count,
        "user_comments": user_comments,
    }
    return render(request, 'account/profile.html', context)

# -----------------------------
# Update Profile
# -----------------------------

def update_user_profile(request):
    if not request.user.is_authenticated:
        messages.warning(request, "Only registered users can update their profile", "alert-warning")
        return redirect("account:sign_in")

    user = request.user

    # تأكد أن البروفايل موجود
    profile, created = Profile.objects.get_or_create(user=user)

    if request.method == "POST":
        try:
            with transaction.atomic():
                # تحديث بيانات المستخدم
                user.first_name = request.POST.get("first_name", user.first_name)
                user.last_name = request.POST.get("last_name", user.last_name)
                user.email = request.POST.get("email", user.email)
                user.save()

                # تحديث بيانات البروفايل
                profile.about = request.POST.get("about", profile.about)
                if request.FILES.get("avatar"):
                    profile.avatar = request.FILES["avatar"]
                profile.save()

            messages.success(request, "Profile updated successfully", "alert-success")
            return redirect("account:user_profile_view", user_name=user.username)

        except Exception as e:
            messages.error(request, "Couldn't update profile. Try again.", "alert-danger")
            print("Error updating profile:", e)

    context = {
        "user": user,
        "profile": profile
    }
    return render(request, "account/update_profile.html", context)
