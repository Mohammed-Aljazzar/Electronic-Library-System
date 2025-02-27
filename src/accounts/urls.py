from django.urls import path, reverse_lazy
from . import views
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView

app_name = 'accounts'
urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('update-profile/', views.update_profile, name='update_profile'),
    path('change_password/', auth_views.PasswordChangeView.as_view(template_name='change_password.html',success_url='/accounts/change_password/done/') , name='password_change'),
    path('change_password/done/', auth_views.PasswordChangeDoneView.as_view(template_name='change_password_done.html') , name='password_change_done'),



     path('password-reset/', 
         auth_views.PasswordResetView.as_view(
             success_url=reverse_lazy('accounts:password_reset_done'),
             email_template_name='password_reset_email.html',
             template_name='password_reset.html'
         ), 
         name='password_reset'),

     path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name='password_reset_done.html'
         ), 
         name='password_reset_done'),



     path('password-reset-confirm/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             success_url=reverse_lazy('accounts:password_reset_complete'),
             template_name='password_reset_confirm.html'
         ), 
         name='password_reset_confirm'),

     path('password-reset-complete/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='password_reset_complete.html'
         ), 
         name='password_reset_complete'),
         
     path('delete-account/', views.delete_account, name='delete_account'),
     path('privacy-policy/', views.privacy_policy, name='privacy_policy'),

]

