from django.contrib import admin
from django.utils.html import format_html
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    # الحقول المعروضة في قائمة المستخدمين
    list_display = ('display_profile_picture', 'username', 'address', 'residence', 'profession')
    list_display_links = ('username',)  # جعل اسم المستخدم قابلاً للنقر
    search_fields = ('username', 'address', 'residence', 'profession')  # حقول البحث
    list_filter = ('residence', 'profession', 'gender')  # التصفية حسب الحقول

    # دالة لعرض الصورة في قائمة المستخدمين
    def display_profile_picture(self, obj):
        if obj.profile_picture:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 50%;" />', obj.profile_picture.url)
        return "No Image"

    display_profile_picture.short_description = 'Profile Picture'  # عنوان العمود

    # ترتيب الحقول في صفحة التعديل
    fieldsets = (
        ('Basic Information', {
            'fields': ('username', 'email', 'first_name', 'last_name', 'gender', 'profile_picture')
        }),
        ('Contact Information', {
            'fields': ('phone_number', 'country_code', 'address', 'residence')
        }),
        ('Professional Information', {
            'fields': ('profession', 'can_add_books')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined')
        }),
    )