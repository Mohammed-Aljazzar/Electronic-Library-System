from django.urls import path
from . import views


app_name = 'library'

urlpatterns = [
    path('', views.home, name='home'),
    path('books/', views.book_list, name='books'),
    path('books/<int:book_id>/', views.book_detail, name='book_detail'),
    path('books/<int:book_id>/download/', views.download_book, name='download_book'),
    path('book/<int:book_id>/comments/', views.all_comments, name='all_comments'),
    path('search/', views.search_results, name='search_results'),
    path('contact/', views.contact_view, name='contact'),
    path('success_contact/', views.success_contact, name='success_contact'),
]

