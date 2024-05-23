# Course Management Web Application

## Overview

This web application provides a platform for managing courses, users (students and admins), and payments. It is built using Flask and integrates with Stripe for handling payments. The application supports user authentication, course management, messaging, and PDF receipt generation.

## Features

- **User Authentication**

  - JWT-based authentication for students and admins.
  - Login and signup routes for students and admins.

- **Profile Management**

  - Profile viewing and updating for students and admins.

- **Course Management**

  - View all courses.
  - Admin-specific course creation, updating, and deletion.
  - Student-specific course enrollment and viewing.
  - Course modules management.

- **Messaging System**

  - Messaging between students and admins.
  - Fetch admins or students based on email substring.

- **Payment Processing with Stripe**
  - Initiate Stripe checkout session for course payments.
  - Generate and download PDF receipts for successful purchases.
  - Handle purchase cancellation.

## Technologies Used

- Flask
- SQLAlchemy
- Stripe API
- JWT (JSON Web Tokens)
- ReportLab (for PDF generation)

## Getting Started

### Prerequisites

- Python 3.x
- Flask
- SQLAlchemy
- Stripe
- ReportLab

### Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/yourusername/your-repo-name.git
   cd your-repo-name
   ```

2. **Create and activate a virtual environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install the required dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up your configuration:**

   - Create a `config.py` file in the root directory and add your configuration settings:
     ```python
     SECRET_KEY = 'your_secret_key'
     SQLALCHEMY_DATABASE_URI = 'sqlite:///your-database.db'
     STRIPE_API_KEY = 'your_stripe_api_key'
     ```

5. **Initialize the database:**

   ```bash
   flask db init
   flask db migrate
   flask db upgrade
   ```

6. **Run the application:**
   ```bash
   flask run
   ```

### API Endpoints

#### Authentication

- **Student Login**

  - `POST /student/login`
  - Request Body: `{"email": "student@example.com", "password": "password123"}`

- **Admin Login**

  - `POST /admin/login`
  - Request Body: `{"email": "admin@example.com", "password": "password123"}`

- **Student Signup**

  - `POST /signup/student`
  - Request Body: `{"email": "student@example.com", "password": "password123", "username": "studentusername"}`

- **Admin Signup**
  - `POST /signup/admin`
  - Request Body: `{"email": "admin@example.com", "password": "password123"}`

#### Profile Management

- **Student Profile**

  - `GET /profile/student`
  - `POST /profile/student`
  - Headers: `{"jwttoken": "your_jwt_token"}`

- **Admin Profile**
  - `GET /profile/admin`
  - `POST /profile/admin`
  - Headers: `{"jwttoken": "your_jwt_token"}`

#### Course Management

- **Get All Courses**

  - `GET /course`

- **Admin Courses**

  - `GET /courses/admin`
  - `POST /courses/admin`
  - `PATCH /courses/admin`
  - Headers: `{"jwttoken": "your_jwt_token"}`

- **Delete Admin Course**

  - `DELETE /courses/admin/<int:courseId>`
  - Headers: `{"jwttoken": "your_jwt_token"}`

- **Student Courses**

  - `GET /courses/student`
  - Headers: `{"jwttoken": "your_jwt_token"}`

- **Student Course Details**

  - `GET /student/course/<int:course_id>`
  - Headers: `{"jwttoken": "your_jwt_token"}`

- **Student Course Modules**
  - `GET /student/course/<int:course_id>/module`
  - Headers: `{"jwttoken": "your_jwt_token"}`

#### Messaging System

- **Send Message to Admin**

  - `POST /messages/student`
  - Headers: `{"jwttoken": "your_jwt_token"}`

- **Messages from Admin to Student**

  - `GET /messages/from-admin`
  - Headers: `{"jwttoken": "your_jwt_token"}`

- **Admin Messages**

  - `GET /messages/admin`
  - `POST /messages/admin`
  - Headers: `{"jwttoken": "your_jwt_token"}`

- **Fetch Admins by Email Substring**

  - `GET /admins`
  - Headers: `{"jwttoken": "your_jwt_token"}`

- **Fetch Students by Email Substring**
  - `GET /studentsmail`
  - Headers: `{"jwttoken": "your_jwt_token"}`

#### Payment Processing

- **Checkout**

  - `GET /checkout/<int:course_id>`
  - Headers: `{"jwttoken": "your_jwt_token"}`

- **Success**

  - `GET /success`
  - Headers: `{"jwttoken": "your_jwt_token"}`

- **Cancel**
  - `GET /cancel`

## License

This project is licensed under [LICENSE](LICENSE).

## Contact

For questions or support, please contact:

- Name: John Muthabuku
- Email: thabuksjohn@gmail.com
