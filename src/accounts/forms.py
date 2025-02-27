from django import forms
from .models import CustomUser
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm

User = get_user_model()

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(label="Username or Email")

    def clean_username(self):
        username = self.cleaned_data['username']
        # تحقق مما إذا كان الإدخال بريدًا إلكترونيًا
        if '@' in username:
            try:
                user = User.objects.get(email=username)
                return user.username  # إرجاع اسم المستخدم المرتبط بالبريد الإلكتروني
            except User.DoesNotExist:
                raise forms.ValidationError("No account found with this email.")
        return username  # إذا كان اسم مستخدم، يتم إرجاعه كما هو


class UserSignupForm(forms.ModelForm):
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")
    # phone_number = forms.CharField(validators=[RegexValidator(regex=r'^\+?1?9̣,̣1̣5̣$')], label="Phone Number")

    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'phone_number', 'country_code', 'address', 'profession', 'residence', 'gender', 'profile_picture', 'password']
        widgets = {
            'password': forms.PasswordInput(),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Sign Up'))
    
    def clean_confirm_password(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if password != confirm_password:
            raise ValidationError("Passwords do not match.")
        return confirm_password
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column('username', css_class='form-group col-md-6'),
                Column('first_name', css_class='form-group col-md-6'),
                css_class='form-row'
            ),
            Row(
                Column('last_name', css_class='form-group col-md-6'),
                Column('email', css_class='form-group col-md-6'),
                css_class='form-row'
            ),
            Row(
                Column('phone_number', css_class='form-group col-md-6'),
                Column('country_code', css_class='form-group col-md-6'),
                css_class='form-row'
            ),
            Row(
                Column('address', css_class='form-group col-md-12'),
                css_class='form-row'
            ),
            Row(
                Column('profession', css_class='form-group col-md-6'),
                Column('residence', css_class='form-group col-md-6'),
                css_class='form-row'
            ),
            Row(
                Column('gender', css_class='form-group col-md-6'),
                Column('profile_picture', css_class='form-group col-md-6'),
                css_class='form-row'
            ),
            Row(
                Column('password1', css_class='form-group col-md-6'),
                Column('password2', css_class='form-group col-md-6'),
                css_class='form-row'
            ),
            Submit('submit', 'Sign Up', css_class='btn btn-primary')
        )

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            'username', 'email', 'first_name', 'last_name', 'address', 
            'profession', 'residence', 'phone_number', 'country_code', 
            'gender', 'profile_picture'
        ]

