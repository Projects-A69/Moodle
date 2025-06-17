<p align="center">
  <img src="src/utils/UDI_logo.png" alt="UDI Learnify Logo" width="150"/>
</p>

<h1 align="center">Learnify – Modern E-learning Platform</h1>

---

## 🧭 Introduction

**Learnify** is a full-featured, full-stack e-learning platform designed for students, teachers, and administrators. It offers a robust and secure environment to manage educational content, interact with users, and track course progress. Built using modern technologies, Learnify ensures a smooth experience across devices with support for dark/light modes and real-time feedback.

---

## ⚙️ Technologies Used

### 🔧 Backend – FastAPI (Python)
- FastAPI, SQLAlchemy, Alembic
- PostgreSQL database
- JWT (OAuth2 password flow) authentication
- Email via `smtplib`, `email.mime.text`
- AWS S3 + Boto3 for file uploads
- PIL (Pillow) for image processing
- dotenv for environment configs
- `unittest` for testing (99%+ coverage)

### 🎨 Frontend – Vue.js
- Vue 3 with Composition API
- Vite as the build tool
- Vue Router
- Tailwind CSS for styling
- `shadcn/vue`, `lucide-react`, Framer Motion

---

## 🚀 Getting Started

### 🔙 Backend Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/learnify.git
   cd learnify/backend
Create and Activate a Virtual Environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
Install Dependencies
pip install -r requirements.txt
Configure Environment Variables
Create a .env file in the backend/ directory with the following content:

DATABASE_URL=postgresql://user:password@localhost:5432/learnify
JWT_SECRET_KEY=your_secret_key
JWT_EXPIRATION=3600
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_email_app_password
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_BUCKET_NAME=learnify-media
Run Migrations
alembic upgrade head
Start the Backend Server
uvicorn src.main:app --reload
🌐 Frontend Setup
Navigate to the Frontend Folder
cd ../frontend
Install Dependencies
npm install
Run the Frontend Dev Server
npm run dev
✨ Features

👨‍🎓 Students
Register and upload profile picture
Enroll in public/premium courses
Rate courses and track progress
Auto logout on token expiration
👩‍🏫 Teachers
Register and wait for admin approval
Manage courses, sections, and resources
Approve enrollments
Get notified on student requests
🛡️ Admins
Approve/reject teachers
Manage users and course visibility
View course ratings and student enrollments
🌍 System-wide
Role-based access control
Responsive UI with dark/light theme
Secure JWT authentication
Email notifications and image uploads
Clean design with hover effects and animations
🗃️ Database Schema

<p align="center"> <img src="src/utils/diagram.png" alt="Database Schema" width="700"/> </p>
🧪 Running Tests

python -m unittest discover tests
Covers:

User auth + registration
Role logic (Admin, Teacher, Student)
Email handling
Course management
📁 Project Structure

learnify/
├── backend/
│   ├── src/
│   │   ├── api/
│   │   ├── core/
│   │   ├── crud/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── utils/
│   │   └── main.py
│   └── tests/
├── frontend/
│   ├── components/
│   ├── layouts/
│   ├── pages/
│   └── App.vue
└── public/
    ├── logo.png
    └── db-diagram.png