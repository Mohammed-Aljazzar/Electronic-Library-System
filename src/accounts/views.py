from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.core.mail import send_mail
from accounts.models import CustomUser
from .forms import User, UserSignupForm, ProfileUpdateForm
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse_lazy
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from .forms import CustomLoginForm  # استيراد النموذج المخصص
from .utils import send_welcome_email  # استيراد الوظيفة
import cloudinary
import cloudinary.uploader
import logging



logger = logging.getLogger(__name__)
# def signup_view(request):
#     if request.method == "POST":
#         form = UserSignupForm(request.POST, request.FILES)
#         if form.is_valid():
#             user = form.save(commit=False)
#             user.set_password(form.cleaned_data['password'])
#             user.save()
#             login(request, user)  # تسجيل الدخول بعد التسجيل
#             messages.success(request, "Account created successfully!")

#             # إرسال البريد الإلكتروني الترحيبي
#             send_welcome_email(user.email, user.username)

#             return redirect('library:home')  # التوجيه إلى الصفحة الرئيسية
#     else:
#         form = UserSignupForm()

#     return render(request, 'signup.html', {'form': form})


def signup_view(request):
    if request.method == "POST":
        form = UserSignupForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            
            if 'profile_picture' in request.FILES:
                try:
                    upload_result = cloudinary.uploader.upload(
                        request.FILES['profile_picture'],
                        folder='profile_pictures/',
                        resource_type='image'
                    )
                    user.profile_picture = upload_result['secure_url']
                except Exception as e:
                    messages.error(request, "Failed to upload profile picture. Please try again.")
                    return redirect('accounts:signup_view')
            
            user.save()
            login(request, user)
            messages.success(request, "Account created successfully!")
            send_welcome_email(user.email, user.username)
            return redirect('library:home')
        else:
            messages.error(request, "An error occurred in the form. Check the data.")
    else:
        form = UserSignupForm()
    return render(request, 'signup.html', {'form': form})

# def signup_view(request):
#     if request.method == "POST":
#         form = UserSignupForm(request.POST, request.FILES)
#         if form.is_valid():
#             user = form.save(commit=False)
#             user.set_password(form.cleaned_data['password'])
#             user.save()
#             login(request, user)  # تسجيل الدخول بعد التسجيل
#             messages.success(request, "Account created successfully!")
#             return redirect('library:home')  # التوجيه إلى الصفحة الرئيسية
#     else:
#         form = UserSignupForm()

#     return render(request, 'signup.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "You have successfully logged in.")
            
            # التحقق مما إذا كان المستخدم أدمن (is_staff أو is_superuser)
            if user.is_staff or user.is_superuser:
                return redirect('library:admin_dashboard')  # توجيه الأدمن إلى Dashboard
            else:
                return redirect('library:home')  # توجيه المستخدم العادي إلى الصفحة الرئيسية
        else:
            messages.error(request, "Invalid username or password")
    else:
        form = CustomLoginForm()

    return render(request, 'login.html', {'form': form})


# @login_required
# def update_profile(request):
#     if request.method == 'POST':
#         form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
#         if form.is_valid():
#             form.save()
#             messages.success(request, "Profile updated successfully")
#             return redirect('accounts:update_profile')  # توجيه المستخدم إلى صفحة الملف الشخصي بعد التحديث
#     else:
#         form = ProfileUpdateForm(instance=request.user)

#     return render(request, 'update_profile.html', {'form': form})
    
@login_required
def update_profile(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            user = form.save(commit=False)
            
            if 'profile_picture' in request.FILES:
                try:
                    upload_result = cloudinary.uploader.upload(
                        request.FILES['profile_picture'],
                        folder='profile_pictures/',
                        resource_type='image',
                        overwrite=True,
                        invalidate=True
                    )
                    user.profile_picture = upload_result['secure_url']
                except Exception as e:
                    messages.error(request, "Failed to upload profile picture. Please try again.")
                    return redirect('accounts:update_profile')
            
            user.save()
            messages.success(request, "Profile updated successfully")
            return redirect('accounts:update_profile')
        else:
            messages.error(request, "An error occurred in the form. Check the data.")
    else:
        form = ProfileUpdateForm(instance=request.user)
    return render(request, 'update_profile.html', {'form': form})

@login_required
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        email = user.email
        user.delete()
        logout(request)
        messages.success(request, 'Your account has been successfully deleted.')
        
        subject = 'Your Account Has Been Deleted'
        message = 'Your account has been successfully deleted by our team. We thank you for using our site.'
        from_email = 'm.i.aljazzar19@gmail.com'
        recipient_list = [email]
        send_mail(subject, message, from_email, recipient_list, fail_silently=False)
        return redirect('library:home')
    else:
        messages.error(request, 'Invalid confirmation link.')  

    return render(request, 'confirm_delete.html')


def privacy_policy(request):
    return render(request, 'includes/privacy_policy.html')


def logout_view(request):
    logout(request)  # يقوم بتسجيل الخروج من النظام
    messages.success(request, "You have successfully logged out.")
    return redirect('library:home')