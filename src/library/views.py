from pyexpat.errors import messages
from django.shortcuts import redirect, render, get_object_or_404
from .models import Book, Category,Comment
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.admin.views.decorators import staff_member_required
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings
from django.db.models import Avg
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages
from django.http import FileResponse
import os

# Create your views here.
def home(request):
    books = Book.objects.all()
    category = request.GET.get('category')
    latest_book_with_quote = Book.objects.filter(quote__isnull=False).order_by('-id').first()
    top_viewed_books = Book.objects.order_by('-views_count')[:3]  # أعلى 4 كتب حسب المشاهدات

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
    }
    return render(request,'home.html',context)

@login_required
def book_list(request):
    # استرداد جميع الكتب
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
        books = books.filter(rating__gte=selected_rating)  # الكتب ذات التقييم أكبر من أو يساوي القيمة المحددة

    # فلتر حسب تاريخ النشر
    selected_publish_date = request.GET.get('publish_date')
    if selected_publish_date:
        books = books.filter(publish_date__lte=selected_publish_date)  # الكتب المنشورة قبل أو في التاريخ المحدد

    # الحصول على قائمة التصنيفات واللغات الفريدة
    categories = Category.objects.values_list('name', flat=True).distinct()
    languages = Book.objects.values_list('language', flat=True).distinct()

    paginator = Paginator(books, 12)  # 9 كتب في كل صفحة
    page_number = request.GET.get('page')  # الحصول على رقم الصفحة من الطلب

    try:
        books = paginator.page(page_number)  # الحصول على الكتب في الصفحة المطلوبة
    except PageNotAnInteger:
        books = paginator.page(1)  # إذا لم يكن رقم الصفحة صحيحًا، عرض الصفحة الأولى
    except EmptyPage:
        books = paginator.page(paginator.num_pages)  # إذا كانت الصفحة فارغة، عرض الصفحة الأخيرة

    return render(request, 'books.html', {
        'books': books,
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