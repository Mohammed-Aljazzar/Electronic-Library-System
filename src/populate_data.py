import os
import django
from django.core.files import File
from django.utils import timezone
from datetime import date
import random
import cloudinary
import cloudinary.uploader
import cloudinary.api

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from accounts.models import CustomUser
from library.models import Category, Book, Comment

# Configure Cloudinary
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME', 'dpthr5ymy'),
    api_key=os.getenv('CLOUDINARY_API_KEY', '671232771225394'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET', 'XQY5dqF9zi1fj6yChAScg_59888')
)

def create_file(filename, content="Dummy content"):
    """Create a file (dummy or real) for uploading to Cloudinary."""
    # Check if a real file exists in temp_media
    temp_path = os.path.join('temp_media', filename)
    if os.path.exists(temp_path):
        return open(temp_path, 'rb')
    # Otherwise, create a dummy file
    with open(filename, 'w') as f:
        f.write(content)
    return open(filename, 'rb')

def populate():
    # 1. Create a superuser
    try:
        # Create or use a profile picture file
        profile_picture_file = create_file('profile_pictures/admin_profile.jpg')
        profile_picture_response = cloudinary.uploader.upload(profile_picture_file, resource_type="image")
        
        superuser = CustomUser.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='Admin@123!',  # Stronger password
            address='123 Admin St',
            profession='Administrator',
            residence='Admin City',
            phone_number='1234567890',
            country_code='+1',
            gender='M',
            profile_picture=profile_picture_response['url'],  # Use Cloudinary URL
            can_add_books=True  # Superuser can add books
        )
        print("Superuser 'admin' created successfully.")
        
        # Clean up file
        profile_picture_file.close()
        if not os.path.exists(os.path.join('temp_media', 'profile_pictures/admin_profile.jpg')):
            os.remove(profile_picture_file.name)
    except Exception as e:
        print(f"Error creating superuser: {e}")
        return  # Exit if superuser creation fails

    # 2. Create regular users (who cannot add books)
    users_data = [
        {
            'username': 'ahmed',
            'email': 'ahmed211@example.com',
            'password': 'user123',
            'address': '123 User1 St',
            'profession': 'Teacher',
            'residence': 'User1 City',
            'phone_number': '1112223333',
            'country_code': '+1',
            'gender': 'F',
            'profile_picture': 'profile_pictures/user1.jpg',
            'can_add_books': False  # Regular user cannot add books
        },
        {
            'username': 'sameh',
            'email': 'sameh2019@example.com',
            'password': 'user123',
            'address': '456 User2 St',
            'profession': 'Student',
            'residence': 'User2 City',
            'phone_number': '4445556666',
            'country_code': '+1',
            'gender': 'M',
            'profile_picture': 'profile_pictures/user2.jpg',
            'can_add_books': False  # Regular user cannot add books
        },
    ]

    users = []
    for user_data in users_data:
        try:
            # Create or use a profile picture file
            profile_picture_file = create_file(user_data['profile_picture'])
            profile_picture_response = cloudinary.uploader.upload(profile_picture_file, resource_type="image")

            user, created = CustomUser.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': user_data['email'],
                    'address': user_data['address'],
                    'profession': user_data['profession'],
                    'residence': user_data['residence'],
                    'phone_number': user_data['phone_number'],
                    'country_code': user_data['country_code'],
                    'gender': user_data['gender'],
                    'profile_picture': profile_picture_response['url'],  # Use Cloudinary URL
                    'can_add_books': user_data['can_add_books']
                }
            )
            if created:
                user.set_password(user_data['password'])
                user.save()
            users.append(user)
            print(f"User '{user.username}' created successfully.")

            # Clean up file
            profile_picture_file.close()
            if not os.path.exists(os.path.join('temp_media', user_data['profile_picture'])):
                os.remove(profile_picture_file.name)
        except Exception as e:
            print(f"Error creating user {user_data['username']}: {e}")

    # 3. Create categories
    categories_data = [
        {'name': 'Technology', 'description': 'Technology books and world.'},
        {'name': 'History', 'description': 'Books based on historical events and facts.'},
        {'name': 'Science', 'description': 'Books about scientific topics.'},
    ]

    categories = []
    for cat_data in categories_data:
        category, created = Category.objects.get_or_create(
            name=cat_data['name'],
            defaults={'description': cat_data['description']}
        )
        categories.append(category)
        print(f"Category '{category.name}' created successfully.")

    # 4. Create books (only added by superuser)
    books_data = [
        {
            'title': 'R For Data Science',
            'description': 'R for Data Science, written by Hadley Wickham and Garrett Grolemund...',
            'author': 'Hadley Wickham and Garrett Grolemund',
            'category': categories[0],  # Technology
            'book_file': 'books/files/great_novel.pdf',
            'link': 'https://drive.google.com/file/d/128occVvihArdgqN4Yo19gaBcYRd4RYpr/preview',
            'poster_image': 'books/posters/r_for_data_science.png',
            'publish_date': date(2020, 1, 15),
            'added_by': superuser,  # Only superuser adds books
            'total_pages': 520,
            'language': 'English',
            'status': 'published',
            'views_count': 150,
            'quote': 'A journey of a thousand miles begins with a single step.',
            'download_count': 50
        },
        {
            'title': 'The Science in Social Science',
            'description': '"The Science in Social Science" explores scientific methods in social sciences...',
            'author': 'Princeton University Press',
            'category': categories[2],  # Science
            'book_file': 'books/files/science_unveiled.pdf',
            'link': 'https://drive.google.com/file/d/1IlMuaYVjEN-GP8Ld8Ig6JlNcBtzo0kC7/preview',
            'poster_image': 'books/posters/science.png',
            'publish_date': date(2021, 6, 10),
            'added_by': superuser,  # Only superuser adds books
            'total_pages': 33,
            'language': 'English',
            'status': 'published',
            'views_count': 200,
            'quote': 'Science is the key to understanding the universe.',
            'download_count': 80
        },
        {
            'title': 'The History Book',
            'description': 'The ultimate aim of history is human self-knowledge...',
            'author': 'Alexandra Beeden, Sam Kennedy',
            'category': categories[1],  # History
            'book_file': 'books/files/history_world.pdf',
            'link': 'https://example.com/history_world',
            'poster_image': 'books/posters/history-book.png',
            'publish_date': date(2019, 3, 22),
            'added_by': superuser,  # Only superuser adds books
            'total_pages': 354,
            'language': 'English',
            'status': 'published',
            'views_count': 50,
            'quote': 'History teaches us the lessons of the past.',
            'download_count': 20
        },
    ]

    books = []
    for book_data in books_data:
        # Create or use files and upload to Cloudinary
        book_file = create_file(book_data['book_file'])
        poster_image = create_file(book_data['poster_image'])

        book_file_response = cloudinary.uploader.upload(book_file, resource_type="auto")
        poster_image_response = cloudinary.uploader.upload(poster_image, resource_type="image")

        book = Book.objects.create(
            title=book_data['title'],
            description=book_data['description'],
            author=book_data['author'],
            category=book_data['category'],
            book_file=book_file_response['url'],  # Use Cloudinary URL
            link=book_data['link'],
            poster_image=poster_image_response['url'],  # Use Cloudinary URL
            publish_date=book_data['publish_date'],
            added_by=book_data['added_by'],
            total_pages=book_data['total_pages'],
            language=book_data['language'],
            status=book_data['status'],
            views_count=book_data['views_count'],
            quote=book_data['quote'],
            download_count=book_data['download_count']
        )
        books.append(book)
        print(f"Book '{book.title}' created successfully.")

        # Clean up files
        book_file.close()
        poster_image.close()
        if not os.path.exists(os.path.join('temp_media', book_data['book_file'])):
            os.remove(book_file.name)
        if not os.path.exists(os.path.join('temp_media', book_data['poster_image'])):
            os.remove(poster_image.name)

    # 5. Create comments (users can still comment, just not add books)
    comments_data = [
        {
            'book': books[0],  # R For Data Science
            'user': users[1],  # sameh
            'text': 'Amazing book! I loved the storyline.',
            'rating': 4.5
        },
        {
            'book': books[0],  # R For Data Science
            'user': superuser,  # admin
            'text': 'A must-read for data science lovers.',
            'rating': 5.0
        },
        {
            'book': books[1],  # The Science in Social Science
            'user': users[1],  # sameh
            'text': 'Very informative and well-written.',
            'rating': 4.0
        },
    ]

    for comment_data in comments_data:
        comment = Comment.objects.create(
            book=comment_data['book'],
            user=comment_data['user'],
            text=comment_data['text'],
            rating=comment_data['rating']
        )
        print(f"Comment by {comment.user.username} on {comment.book.title} created successfully.")

if __name__ == "__main__":
    print("Populating demo data...")
    populate()
    print("Demo data populated successfully!")