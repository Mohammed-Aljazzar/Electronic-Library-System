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

def signup_view(request):
    if request.method == "POST":
        form = UserSignupForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)  # تسجيل الدخول بعد التسجيل
            messages.success(request, "Account created successfully!")

            # إرسال البريد الإلكتروني الترحيبي
            send_welcome_email(user.email, user.username)

            return redirect('library:home')  # التوجيه إلى الصفحة الرئيسية
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
        form = CustomLoginForm(request, data=request.POST)  # استخدام النموذج المخصص
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "You have successfully logged in.")
            return redirect('library:home')  # التوجيه إلى الصفحة الرئيسية
        else:
            messages.error(request, "Invalid username or password")
    else:
        form = CustomLoginForm()  # استخدام النموذج المخصص

    return render(request, 'login.html', {'form': form})

@login_required
def update_profile(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully")
            return redirect('accounts:update_profile')  # توجيه المستخدم إلى صفحة الملف الشخصي بعد التحديث
    else:
        form = ProfileUpdateForm(instance=request.user)

    return render(request, 'update_profile.html', {'form': form})


def logout_view(request):
    logout(request)  # يقوم بتسجيل الخروج من النظام
    messages.success(request, "You have successfully logged out.")
    return redirect('library:home')
    

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


# from django.core.mail import send_mail
# from django.urls import reverse
# from django.contrib.sites.shortcuts import get_current_site
# from django.utils.encoding import force_bytes, force_str
# from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
# @login_required
# def delete_account(request):
#     if request.method == 'POST':
#         user = request.user
#         token = user.generate_token()  # This now stores in cache
        
#         current_site = get_current_site(request)
#         domain = current_site.domain
        
#         confirm_url = reverse('accounts:confirm-account-deletion', kwargs={'uidb64': urlsafe_base64_encode(force_bytes(user.pk)), 'token': token})
#         confirm_link = f"http://{domain}{confirm_url}"
        
#         subject = 'Confirm Account Deletion'
#         message = f'Please click the following link to confirm the deletion of your account: {confirm_link}'
#         from_email = 'm.i.aljazzar19@gmail.com'
#         recipient_list = [user.email]
        
#         send_mail(subject, message, from_email, recipient_list, fail_silently=False)
        
#         messages.success(request, 'A confirmation email has been sent to your email address. Please check your inbox to confirm account deletion.')
#         return redirect('library:home')
    
#     return render(request, 'confirm_delete.html')

# @login_required
# def confirm_account_deletion(request, uidb64, token):
#     try:
#         uid = force_str(urlsafe_base64_decode(uidb64))
#         user = CustomUser.objects.get(pk=uid)
#     except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
#         user = None

#     if user is not None and user.check_token(token):
#         user.delete()
#         logout(request)
#         messages.success(request, 'Your account has been successfully deleted.')
#     else:
#         messages.error(request, 'Account deletion failed. The confirmation link is invalid or expired.')

#     return redirect('library:home')