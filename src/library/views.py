import json
from pyexpat.errors import messages
from django.shortcuts import redirect, render, get_object_or_404
from .models import Book, Category,Comment
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.admin.views.decorators import staff_member_required
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings
from django.db.models import Avg, Sum, Count
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages
from django.http import FileResponse
import os
from .forms import BookForm, CategoryForm
from accounts.models import CustomUser
from django.template.loader import render_to_string
from accounts.forms import UserSignupForm

# Create your views here.
def home(request):
    books = Book.objects.all()
    category = request.GET.get('category')
    latest_book_with_quote = Book.objects.filter(quote__isnull=False).order_by('-id').first()
    top_viewed_books = Book.objects.filter(status ='published').order_by('-views_count')[:3]  # أعلى 4 كتب حسب المشاهدات
    featured_book = Book.objects.filter(status='published').order_by('-publish_date').first()
    top_comments = Comment.objects.order_by('-rating', '-created_at')[:3]  # أعلى 3 تعليقات حسب التقييم ثم الوقت 
    if category:
        books = books.filter(category__name=category)
    # Calculate average rating for each top viewed book
    top_viewed_books_with_ratings = []
    for book in top_viewed_books:
        average_rating = book.comments.aggregate(Avg('rating'))['rating__avg'] or 0.0
        top_viewed_books_with_ratings.append({
            'book': book,
            'average_rating': average_rating
        })
        
    context = {
        'books': books,
        'current_category': category if category else 'All',
        'categories': Category.objects.values_list('name', flat=True).distinct(),
        'latest_book_with_quote': latest_book_with_quote,
        'top_viewed_books':top_viewed_books_with_ratings,
        'featured_book':featured_book,
        'top_comments': top_comments,
    }
    return render(request,'home.html',context)

def about(request):
    return render(request, 'about.html')

@login_required
def book_list(request):
    # استرداد جميع الكتب مع حساب متوسط التقييم
    books = Book.objects.all().annotate(average_rating=Avg('comments__rating'))
    
    # فلتر حسب التصنيف
    selected_category = request.GET.get('category')
    if selected_category:
        books = books.filter(category__name=selected_category)

    # فلتر حسب اللغة
    selected_language = request.GET.get('language')
    if selected_language:
        books = books.filter(language=selected_language)

    # فلتر حسب التقييم
    selected_rating = request.GET.get('rating')
    if selected_rating:
        try:
            rating_value = float(selected_rating)  # تحويل القيمة إلى float
            books = books.filter(average_rating__gte=rating_value)  # تصفية بناءً على متوسط التقييم
        except ValueError:
            # في حالة إدخال قيمة غير صالحة، يمكن تجاهل الفلتر أو إرجاع خطأ
            pass

    # فلتر حسب تاريخ النشر
    selected_publish_date = request.GET.get('publish_date')
    if selected_publish_date:
        books = books.filter(publish_date__lte=selected_publish_date)

    # الحصول على قائمة التصنيفات واللغات الفريدة
    categories = Category.objects.values_list('name', flat=True).distinct()
    languages = Book.objects.values_list('language', flat=True).distinct()

    # التصفح (Pagination)
    paginator = Paginator(books, 12)  # 12 كتابًا في كل صفحة
    page_number = request.GET.get('page')

    try:
        books_page = paginator.page(page_number)
    except PageNotAnInteger:
        books_page = paginator.page(1)
    except EmptyPage:
        books_page = paginator.page(paginator.num_pages)

    return render(request, 'books.html', {
        'books': books_page,
        'categories': categories,
        'languages': languages,
        'selected_category': selected_category,
        'selected_language': selected_language,
        'selected_rating': selected_rating,
        'selected_publish_date': selected_publish_date,
    })


@login_required
def book_detail(request, book_id):
    # استرداد الكتاب أو إظهار خطأ 404 إذا لم يتم العثور عليه
    book = get_object_or_404(Book, id=book_id)
    
    # إنشاء مفتاح فريد للجلسة بناءً على معرف الكتاب
    session_key = f'book_{book_id}_viewed'
    
    # التحقق مما إذا كان المستخدم قد شاهد الكتاب من قبل
    if not request.session.get(session_key, False):
        # زيادة عدد المشاهدات إذا لم يشاهد الكتاب من قبل
        book.views_count += 1
        book.save()
        
        # تعيين علامة في الجلسة لتجنب زيادة المشاهدات مرة أخرى
        request.session[session_key] = True

    
    if request.method == "POST" and "comment" in request.POST:
        comment_text = request.POST.get("comment")
        rating = request.POST.get("rating", 0)  # Default to 0 if not provided
        if comment_text and rating:
            # Create the comment
            Comment.objects.create(
                book=book,
                user=request.user,
                text=comment_text,
                rating=float(rating)
            )
            # Update book's reviews count
            book.reviews_count = book.comments.count()
            book.save()
            return redirect('library:book_detail', book_id=book.id)
    # معالجة تعديل تعليق موجود
    
    if request.method == "POST" and "edit_comment" in request.POST:
        comment_id = request.POST.get("comment_id")
        comment = get_object_or_404(Comment, id=comment_id, user=request.user)
        time_since_creation = timezone.now() - comment.created_at
        if time_since_creation <= timedelta(hours=1):  # التحقق من مرور ساعة
            comment.text = request.POST.get("edit_text")
            comment.rating = float(request.POST.get("edit_rating", comment.rating))
            comment.save()
            messages.success(request, "Your comment has been updated successfully.")
        else:
            messages.error(request, "You can no longer edit this comment (1-hour limit exceeded).")
        return redirect('library:book_detail', book_id=book.id)
    # معالجة حذف تعليق
    if request.method == "POST" and "delete_comment" in request.POST:
        comment_id = request.POST.get("comment_id")
        comment = get_object_or_404(Comment, id=comment_id, user=request.user)
        time_since_creation = timezone.now() - comment.created_at
        if time_since_creation <= timedelta(hours=1):
            comment.delete()
            book.reviews_count = book.comments.count()
            book.save()
            messages.success(request, "Your comment has been deleted successfully.")
        else:
            messages.error(request, "You can no longer delete this comment (1-hour limit exceeded).")
        return redirect('library:book_detail', book_id=book.id)
    
    comments = book.comments.all()[:3]
    has_more_comments = book.comments.count() > 3
    average_rating = book.comments.aggregate(Avg('rating'))['rating__avg'] or 0.0

    return render(request, 'book_detail.html', {
        'book': book,
        'comments': comments,
        'has_more_comments': has_more_comments,
        'average_rating': average_rating,
    })



@login_required
def download_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    book.download_count += 1
    book.save()
    file_path = book.book_file.path
    if os.path.exists(file_path):
        return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=os.path.basename(file_path))
    else:
        messages.error(request, "File not found.")
        return redirect('library:book_detail', book_id=book.id)

@login_required
def search_results(request):
    category = request.GET.get('category')
    search_term = request.GET.get('q')

    if not search_term and not category:
        messages.error(request, "Please provide a search term or select a category to proceed with the search.")
        return redirect('library:home')

    books = Book.objects.all()
    
    if search_term:
        books = books.filter(title__icontains=search_term)
    if category:
        books = books.filter(category=category)

    # Check if there are any books after filtering
    if not books.exists():
        messages.info(request, "No books found matching your search criteria.")

    context = {
        'books': books,
        'current_category': category if category else 'All',
        'search_term': search_term
    }
    return render(request, 'search_results.html', context)

def success_contact(request):
    return render(request,'includes/success_contact.html')

@login_required
def contact_view(request):
    if request.method == 'POST':
        email = request.user.email 
        message = request.POST.get('message')  
        
        if email and message:
            subject = f"New Message from {request.user.username} ({email})"
            try:
                send_mail(
                    subject,
                    message,
                    email,  
                    ['m.i.aljazzar19@gmail.com'], 
                    fail_silently=False,
                )
                messages.success(request, "Your message has been sent successfully!")
                return redirect('library:success_contact')
            
            except Exception as e:
                messages.error(request, f"Failed to send message: {str(e)}")
        else:
            messages.error(request, "Please fill in all fields.")
    
    return render(request, 'home.html')

@login_required
def all_comments(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    comments = book.comments.all()
    paginator = Paginator(comments, 10)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'all_comments.html', {'book': book, 'comments': page_obj})



@staff_member_required
def add_book(request):
    if request.method == "POST":
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save(commit=False)
            book.added_by = request.user
            book.save()
            messages.success(request, "Book added successfully!")
            return redirect('library:books')
    else:
        form = BookForm()
    return render(request, 'add_book.html', {'form': form})

@staff_member_required
def add_category(request):
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Category added successfully!")
            return redirect('library:books')
    else:
        form = CategoryForm()
    return render(request, 'add_category.html', {'form': form})


from django.db.models.functions import TruncMonth  # لتجميع حسب الشهر

@staff_member_required
def admin_dashboard(request):
    # إحصائيات للـ Dashboard
    total_books = Book.objects.count()
    total_categories = Category.objects.count()
    total_comments = Comment.objects.count()
    total_views = Book.objects.aggregate(total_views=Sum('views_count'))['total_views'] or 0
    total_downloads = Book.objects.aggregate(total_downloads=Sum('download_count'))['total_downloads'] or 0
    draft_books = Book.objects.filter(status='draft').count()
    
    # جلب قائمة المستخدمين والكتب
    users = CustomUser.objects.all()
    books = Book.objects.all()

    # بيانات التصنيفات (للرسم البياني الدائري السابق)
    category_data = Category.objects.annotate(book_count=Count('categories')).values('name', 'book_count')

    # بيانات الكتب حسب تاريخ النشر (تجميع حسب الشهر)
    publish_data = (
        Book.objects
        .annotate(month=TruncMonth('publish_date'))  # تجميع حسب الشهر
        .values('month')
        .annotate(book_count=Count('id'))
        .order_by('month')
    )
    # تحويل التواريخ إلى تنسيق ISO (مثل "2025-03-01") للاستخدام في Chart.js
    publish_data_json = [
        {'date': item['month'].isoformat(), 'book_count': item['book_count']}
        for item in publish_data
    ]

    context = {
        'total_books': total_books,
        'total_categories': total_categories,
        'total_comments': total_comments,
        'total_views': total_views,
        'total_downloads': total_downloads,
        'draft_books': draft_books,
        'users': users,
        'books': books,
        'category_data': json.dumps(list(category_data)),  # للرسم البياني الدائري
        'publish_data': json.dumps(publish_data_json),     # للرسم البياني الخطي
    }
    return render(request, 'admin_dashboard.html', context)

@staff_member_required
def edit_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if request.method == "POST":
        form = BookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            form.save()
            messages.success(request, "Book updated successfully!")
            return redirect('library:admin_dashboard')
    else:
        form = BookForm(instance=book)
    return render(request, 'edit_book.html', {'form': form, 'book': book})

@staff_member_required
def delete_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if request.method == "POST":
        book.delete()
        messages.success(request, "Book deleted successfully!")
        return redirect('library:admin_dashboard')
    return render(request, 'delete_book_confirm.html', {'book': book})

@staff_member_required
def toggle_book_status(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if book.status == 'published':
        book.status = 'draft'
        messages.success(request, f"Book '{book.title}' changed to Draft.")
    elif book.status == 'draft':
        book.status = 'published'
        messages.success(request, f"Book '{book.title}' changed to Published.")
    book.save()
    return redirect('library:admin_dashboard')

@staff_member_required
def delete_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    
    # منع المسؤول من حذف نفسه (اختياري)
    if user == request.user:
        messages.error(request, "You cannot delete yourself!")
        return redirect('library:admin_dashboard')
    
    if request.method == "POST":
        user.delete()
        messages.success(request, f"User '{user.username}' deleted successfully!")
        return redirect('library:admin_dashboard')
    
    # عرض صفحة تأكيد الحذف
    return render(request, 'delete_user_confirm.html', {'user': user})


@staff_member_required
def toggle_user_status(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    
    if user == request.user:
        messages.error(request, "You cannot change your own status!")
        return redirect('library:admin_dashboard')
    
    if user.is_staff:  # إلغاء الصلاحيات
        user.is_staff = False
        user.is_superuser = False
        messages.success(request, f"User '{user.username}' is no longer an admin.")
        html_message = render_to_string('email_admin_revoked.html', {'username': user.username, 'admin_email': settings.DEFAULT_FROM_EMAIL})
        subject = "Your Admin Privileges Have Been Revoked"
    else:  # منح الصلاحيات
        user.is_staff = True
        user.is_superuser = False
        messages.success(request, f"User '{user.username}' is now an admin.")
        html_message = render_to_string('email_admin_granted.html', {'username': user.username, 'admin_email': settings.DEFAULT_FROM_EMAIL})
        subject = "You Have Been Granted Admin Privileges"
    
    send_mail(
        subject,
        message='',  # النص العادي فارغ لأننا نستخدم HTML
        from_email=None,
        recipient_list=[user.email],
        html_message=html_message,
        fail_silently=False,
    )
    
    user.save()
    return redirect('library:admin_dashboard')

@staff_member_required
def add_user(request):
    if request.method == "POST":
        form = UserSignupForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])  # تشفير كلمة المرور
            user.save()
            messages.success(request, "User added successfully!")
            return redirect('library:admin_dashboard')  # العودة إلى لوحة التحكم
        else:
            messages.error(request, "Error adding user. Please check the form.")
            print(form.errors)  # طباعة الأخطاء للتحقق
    else:
        form = UserSignupForm()
    return render(request, 'add_user.html', {'form': form})