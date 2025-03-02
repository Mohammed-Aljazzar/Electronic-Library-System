from django.urls import path
from . import views


app_name = 'library'

urlpatterns = [
    path('', views.home, name='home'),
    path('books/', views.book_list, name='books'),
    path('user/add/', views.add_user, name='add_user'),  
    path('books/<int:book_id>/', views.book_detail, name='book_detail'),
    path('books/<int:book_id>/download/', views.download_book, name='download_book'),
    path('book/<int:book_id>/comments/', views.all_comments, name='all_comments'),
    path('search/', views.search_results, name='search_results'),
    path('contact/', views.contact_view, name='contact'),
    path('success_contact/', views.success_contact, name='success_contact'),
    path('add-book/', views.add_book, name='add_book'),
    path('add-category/', views.add_category, name='add_category'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('edit-book/<int:book_id>/', views.edit_book, name='edit_book'),
    path('delete-book/<int:book_id>/', views.delete_book, name='delete_book'),
    path('book/toggle-status/<int:book_id>/', views.toggle_book_status, name='toggle_book_status'),
    path('user/delete/<int:user_id>/', views.delete_user, name='delete_user'), 
    path('user/toggle-status/<int:user_id>/', views.toggle_user_status, name='toggle_user_status'),  
    path('about/', views.about, name='about'), 
    
]

