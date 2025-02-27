from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from accounts.models import CustomUser



class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Category Name")
    description = models.TextField(blank=True, null=True, verbose_name="Description")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"


class Book(models.Model):

    STATUS = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
    ]

    title = models.CharField(max_length=255, verbose_name="Title")
    description = models.TextField(verbose_name="Brief Description")
    author = models.CharField(max_length=255, verbose_name="Author")
    category = models.ForeignKey('Category', on_delete=models.CASCADE, verbose_name="Category", related_name="categories")  # تعديل هنا
    book_file = models.FileField(upload_to='books/files/', verbose_name="Book File")
    link = models.URLField(blank=True, null=True, verbose_name="Link")
    poster_image = models.ImageField(upload_to='books/posters/', verbose_name="Poster Image")
    publish_date = models.DateField(verbose_name="Publish Date")
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Added By")
    total_pages = models.PositiveIntegerField(verbose_name="Total Pages")
    language = models.CharField(max_length=50, verbose_name="Language")
    status = models.CharField(max_length=20, choices=STATUS, default='pending', verbose_name="Status")
    views_count = models.PositiveIntegerField(default=0, verbose_name="Views Count")
    quote = models.TextField(blank=True, null=True, verbose_name="Quote")
    download_count = models.PositiveIntegerField(default=0, verbose_name="Download Count")  
    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Book"
        verbose_name_plural = "Books"

class Comment(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField(verbose_name="Comment")
    rating = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        default=0,
        verbose_name="Rating"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.book.title}"

    class Meta:
        verbose_name = "Comment"
        verbose_name_plural = "Comments"
        ordering = ['-created_at']