from django.shortcuts import render, redirect, get_object_or_404
from .models import CustomUser
from django.contrib import messages
from django.contrib.auth import login, logout
from . import verify

# Create your views here.

def user_signup(request):
    if request.method == "POST":
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        age = request.POST["age"]
        gender = request.POST["gender"]
        user_name = request.POST["username"]
        email = request.POST["email"]
        phone_number = request.POST["phone_number"]
        pass1 = request.POST["password1"]
        pass2 = request.POST["password2"]

        print(
            f"username: {user_name}\n email: {email}\n pass1: {pass1}\n pass2: {pass2}\n phone:{phone_number}"
        )

        if pass1 != pass2:
            return redirect(user_signup)

        if len(phone_number) < 10 or len(phone_number) > 14:
            return redirect(user_signup)

        if len(pass1) < 2:
            return redirect(user_signup)

        try:
            if CustomUser.objects.get(first_name=first_name):
                messages.error(request, "First name already exists")
                return redirect(user_signup)
        except:
            pass

        try:
            if CustomUser.objects.get(last_name=last_name):
                messages.error(request, "Last name already exists")
                return redirect(user_signup)
        except:
            pass

        try:
            if CustomUser.objects.get(username=user_name):
                return redirect(user_signup)
        except:
            pass

        try:
            if CustomUser.objects.get(email=email):
                return redirect(user_signup)
        except:
            pass

        try:
            if CustomUser.objects.get(phone_number=phone_number):
                return redirect(user_signup)
        except:
            pass


        my_user = CustomUser.objects.create(
            first_name=first_name,
            last_name=last_name,
            age=age,
            gender=gender,
            username=user_name,
            email=email,
            phone_number=phone_number,
        )

        my_user.set_password(pass1)
        my_user.save()

        # login(request, my_user)
        verify.send(my_user.phone_number)
        return redirect("otpcheck", phone_number, my_user.id)

    return render(request, "auth/user_signup.html")


def user_login(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        email = request.POST["email"]
        pass1 = request.POST["pass"]

        try:
            user = CustomUser.objects.get(email=email)
            password_matched = user.check_password(pass1)

            if user and password_matched:
                if user.is_superuser:
                    messages.error(request, "You do not have superuser privileges.")
                    return redirect("user_login")
                else:
                    login(request, user)
                    return redirect("home")
            else:
                messages.error(request, "Incorrect email or password")
                return redirect("user_login")

        except CustomUser.DoesNotExist:
            messages.error(request, "User does not exist")
            return redirect("user_login")

    return render(request, "auth/user_login.html")


def otpcheck(request, id, phone_number):
    user = get_object_or_404(CustomUser, id=id)

    if request.method == "POST":
        code = request.POST.get("otp")

        if verify.check(phone_number, code):
            user.is_verified = True
            user.save()
            return redirect("user_login")
        else:
            user.delete()
            return redirect("user_signup")
    else:
        return render(
            request, "auth/otpcheck.html", {"phone_number": phone_number, "id": id}
        )


def user_logout(request):
    logout(request)
    return redirect("home")


def userprofile(request):
    user = request.user

    if request.method == "POST":
        if "first_name" in request.POST:
            edited_first_name = request.POST["first_name"]
            user.first_name = edited_first_name
        if "last_name" in request.POST:
            edited_last_name = request.POST["last_name"]
            user.last_name = edited_last_name
        if "gender" in request.POST:
            edited_gender = request.POST["gender"]
            print(edited_gender, "qqqqqwwww")
            user.gender = edited_gender
        if "age" in request.POST:
            edited_age = request.POST["age"]
            user.age = edited_age
        if "email" in request.POST:
            edited_email = request.POST["email"]
            user.email = edited_email
        if "phone" in request.POST:
            edited_phone = request.POST["phone"]
            user.phone_number = edited_phone

        user.save()
        messages.success(request, "Profile updated successfully")

        # Redirect the user to the profile page or any other appropriate page
        return redirect("userprofile")  # You may need to adjust the URL name

    return render(
        request,
        "auth/userprofile.html",
        {
            "username": user.username,
            "email": user.email,
            "phone": user.phone_number,
            "age": user.age,
            "gender": user.gender,
            "first_name": user.first_name,
            "last_name": user.last_name,
        },
    )


def forgot_password(request):
    if request.method == "POST":
        phone_number = request.POST.get("mobile_number")
        print(phone_number)

        try:
            user = CustomUser.objects.get(phone_number=phone_number)
            print(user.phone_number)

            verify.send(user.phone_number)
            return redirect("forgot_otpcheck", phone_number=phone_number, id=user.id)
        except CustomUser.DoesNotExist:
            messages.error(request, "User with the given mobile number does not exist.")
            return redirect("forgot_password")

    return render(request, "auth/forgot_password.html")


def forgot_otpcheck(request, id, phone_number):
    user = get_object_or_404(CustomUser, id=id)

    if request.method == "POST":
        code = request.POST.get("otp")

        if verify.check(phone_number, code):
            user.is_verified = True
            user.save()

            new_password = request.POST.get("password")
            confirm_password = request.POST.get("confirm_password")

            if new_password == confirm_password:
                user.set_password(new_password)
                user.save()
                messages.success(request, "Password updated successfully.")
            else:
                messages.error(request, "Passwords do not match. Please try again.")
                return redirect("forgot_otpcheck", id=id, phone_number=phone_number)

            return redirect("user_login")
        else:
            messages.error(request, "Entered OTP is incorrect")
            return redirect("forgot_otpcheck", id=id, phone_number=phone_number)
    else:
        return render(
            request,
            "auth/forgot_otpcheck.html",
            {"phone_number": phone_number, "id": id},
        )
