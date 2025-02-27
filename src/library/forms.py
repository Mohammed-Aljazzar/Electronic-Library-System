from django import forms
from .models import Book

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'description', 'author', 'category', 'book_file', 'link', 'poster_image', 'publish_date', 'total_pages', 'language', 'status']


class BookRequestForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'description', 'author', 'category', 'language', 'total_pages']  # Include fields you want in the form
        # Optionally exclude fields that should be set by the system:
        exclude = ['book_file', 'link', 'poster_image', 'publish_date', 'added_by', 'rating', 'reviews_count', 'status', 'views_count']

    # If you need custom validation or additional fields, you can add them here
    # For instance, if you want to customize a field:
    title = forms.CharField(label='Book Title', max_length=255, widget=forms.TextInput(attrs={'placeholder': 'Enter book title'}))
    author = forms.CharField(label='Author', max_length=255, widget=forms.TextInput(attrs={'placeholder': 'Enter author name'}))