# Electronic Library System

Welcome to the **Electronic Library System**, a modern web-based platform built with Django to manage and provide access to a digital collection of books. This system caters to readers, researchers, and administrators, offering a seamless experience for browsing, managing, and engaging with books.

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Technologies](#technologies)
- [Installation](#installation)
- [Usage](#usage)
- [Screenshots](#screenshots)
- [Contributing](#contributing)
- [License](#license)

## Overview
The Electronic Library System is designed to digitize and streamline library operations. It provides a user-friendly interface for browsing books, adding new content, tracking user engagement, and managing library resources. Established in 2025, this project aims to foster a love for reading and learning by offering accessible tools and resources.

## Features
### General Features
- Book Browsing: Explore a wide collection of books with filters for categories, languages, ratings, and publication dates.
- Search Functionality: Search books by title or category with instant results.
- User Authentication: Secure login and registration system with profile management.
- Responsive Design: Fully responsive layout for desktop, tablet, and mobile devices.

### Admin Features
- Book Management: Add, edit, delete, and toggle the status (draft/published) of books.
- Category Management: Add new categories to organize books.
- User Management: Add, delete, and toggle admin status for users.
- Statistics Dashboard: Real-time insights with total books, categories, comments, views, downloads, and draft books.
- Charts: Pie chart for books by category and line chart for books by publish date.

### User Engagement
- Comments and Ratings: Users can add comments and rate books (0-5 stars).
- Top Viewed Books: Displays the top 3 most viewed books on the homepage.
- Featured Book: Highlights the latest published book with a description and link to details.
- Testimonials: Carousel showcasing top 3 comments with user photos and ratings (stacked vertically on mobile).
- Inspired Quote: Displays a quote from the latest book or a default quote.

### Additional Pages
- About Page: Information about the system, mission, features, and contact details.
- Contact Form: Allows users to send messages to the admin.

## Technologies
- Backend: Django (Python)
- Frontend: HTML, CSS, Bootstrap 5, JavaScript
- Database: SQLite (default, can be configured for PostgreSQL or others)
- Charts: Chart.js for visualizations
- Static Files: Django static files management
- Dependencies: Managed via `requirements.txt`

## Installation
### Prerequisites
- Python 3.8+
- Git
- Virtualenv (recommended)

### Steps
1. **Clone the Repository:**
   ```bash
   git clone https://github.com/yourusername/electronic-library-system.git
   cd electronic-library-system
   ```

2. **Set Up Virtual Environment:**
  ```bash
  python -m venv venv
  source venv/bin/activate  # On Windows: venv\Scripts\activate
  ```

3. **Install Dependencies:**
  ```bash
  pip install -r requirements.txt
  ```

4. **Configure Settings:**
  - Update settings.py with your database, email, and media settings if needed:
  ```bash
  DATABASES = {
      'default': {
          'ENGINE': 'django.db.backends.sqlite3',
          'NAME': BASE_DIR / 'db.sqlite3',
      }
  }
  MEDIA_URL = '/media/'
  MEDIA_ROOT = BASE_DIR / 'media'
  ```

5. **Run Migrations:**
  ```bash
  python manage.py makemigrations
  python manage.py migrate
  ```

6. **Create Superuser:**
  ```bash
  python manage.py createsuperuser
  ```

7. **Collect Static Files:**
  ```bash
  python manage.py collectstatic
  ```

8. **Run the Server:**
  ```bash
  python manage.py runserver
  ```
  Open your browser at http://127.0.0.1:8000/.

## Usage
- **Homepage:** Access at / to browse top books, featured book, testimonials, and contact form.
- **Books Page:** Visit /books/ to filter and view all published books (requires login).
- **Admin Dashboard:** Access at /admin-dashboard/ (requires staff status) to manage books, users, and view statistics.
- **About Page:** Visit /about/ for system information.
- **Login/Register:** Use /accounts/login/ and /accounts/signup/ for user authentication.

## Screenshots
Here are some snapshots of the Electronic Library System in action:
- Homepage:
  
   ![Home Page](src/screenshots/home.png)  

   ![Home Page](src/screenshots/home2.png)  

   ![Home Page](src/screenshots/home3.png)  

   ![Home Page](src/screenshots/home4.png)  

- Books Page:
  
   ![Books Page](src/screenshots/books.png)
  
   ![Books Page](src/screenshots/book2.png)  

   ![Books Page](src/screenshots/book3.png)  
  
 
- Admin Dashboard:

   ![Admin Dashboard](src/screenshots/dashboard.png)
  
   ![Admin Dashboard](src/screenshots/dashboard2.png)  

- About Page:

   ![About Page](src/screenshots/about.png)  

## Contributing
Contributions are welcome! Please follow these steps:
- Fork the repository.
- Create a new branch (git checkout -b feature/your-feature).
- Commit your changes (git commit -m "Add your feature").
- Push to the branch (git push origin feature/your-feature).
- Open a Pull Request.
  
## License
This project is licensed under the MIT License. See the LICENSE file for details.

- **Contact:** For inquiries or support, reach out at m.i.aljazzar19@gmail.com.





