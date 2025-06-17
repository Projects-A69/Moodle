<p align="center">
  <img src="public/UDI_logo.png" alt="UDI Platform Logo" width="150"/>
</p>

<h1 align="center">UDI – Unified Digital Instruction Platform</h1>
<p align="center"><i>Created by Uasim, Dimitar, and Ivan</i></p>

---

## 🧭 Introduction

**UDI** is a full-stack e-learning platform developed by the Projects-A69 team, designed for students, teachers, and administrators. It combines clean architecture, role-based access, a responsive interface, and secure user authentication to manage digital education in an intuitive and scalable way.

---

## ⚙️ Technologies Used

### 🔧 Backend – FastAPI (Python)

* **Framework:** FastAPI, SQLAlchemy
* **Database:** PostgreSQL (NeonDB hosted)
* **Authentication:** JWT (OAuth2 password flow)
* **Email:** Gmail SMTP via `smtplib`, `email.mime.text`
* **File Storage:** AWS S3 via Boto3
* **Image Processing:** Pillow (PIL)
* **Config Management:** `pydantic-settings`
* **Dependency & Env Management:** `pyproject.toml`, `uv`, `.env.template`, `uv.lock`
* **Testing:** `unittest` (with full CRUD + router test suite)
* **Containerization:** Docker

### 🎨 Frontend – Vue.js

* **Framework:** Vue 3 with Composition API
* **Routing:** Vue Router (defined in `router/index.js`)
* **Build Tool:** Vite
* **Styling:** CSS variables and transitions, dark/light mode support
* **State/API Handling:** LocalStorage for roles, JWT decoding, Axios
* **Component Layout:** Header, Sidebar, Responsive Dashboard (`App.vue`, `Dashboard.vue`)
* **Views:** Pages for Home, Login, Register, Course, Section, Ratings, Profile, Tag management, Admin, Teacher, and Student panels
* **Containerization:** Docker

---

## 🚀 Getting Started

### 📦 Backend Setup (`Moodle` Repository)

1. **Clone the Repository**

   ```bash
   git clone https://github.com/Projects-A69/Moodle.git
   cd Moodle
   ```

2. **Sync Dependencies using `uv`**

   ```bash
   uv venv
   uv pip install -r uv.lock
   ```

3. **Environment Configuration**

   ```bash
   cp .env.template .env
   ```

   Configure environment variables such as:

   * `JWT_SECRET_KEY`, `DATABASE_URL`, `EMAIL_USERNAME`, `AWS_BUCKET_NAME`, etc.

4. **Run the Backend Server**

   ```bash
   uvicorn src.main:app --reload
   ```

Or using Docker Compose:

```bash
docker compose up --build
```

---

### 🌐 Frontend Setup (`Moodle-frontend` Repository)

1. **Clone the Frontend Repository**

   ```bash
   git clone https://github.com/Projects-A69/Moodle-frontend.git
   cd Moodle-frontend
   ```

2. **Install Dependencies**

   ```bash
   npm install
   ```

3. **Configure Environment**

   ```bash
   cp .env.template .env
   ```

   Example:

   ```env
   VITE_API_URL=http://localhost:8000
   ```

4. **Start Development Server**

   ```bash
   npm run dev
   ```

Or via Docker Compose:

```bash
docker compose up --build
```

---

## ✨ Key Features

### 👨‍🎓 Students

* Register and manage profile
* Enroll in public/premium courses
* View course sections and rate courses
* Track visited sections and favorite courses

### 👩‍🏫 Teachers

* Register and await admin approval
* Create/update/delete courses and sections
* View course ratings and manage enrollment requests
* Profile and LinkedIn support

### 🛡️ Admins

* Approve or reject pending teacher registrations
* Manage all users and roles
* Hide/delete courses, view ratings and enrollments
* Full access to system resources

### 🌍 General System Features

* Secure token-based login with expiration checks
* Email notifications with timed approval links
* S3 image storage for avatars and course covers
* Mobile-responsive dashboard layout
* Dark/light mode with CSS variable themes

---

## 🗃️ Database Schema

<p align="center">
  <img src="public/diagram.png" alt="Database Schema" width="700"/>
</p>

---

## 🧪 Running Tests

```bash
python -m unittest discover tests
```

Test Suite Includes:

* CRUD + route tests for each major model (Admin, Student, Teacher, Course, Section, Tag, User)
* Email and token utilities
* Role-based restrictions and logic

---

## 📁 Project Structure Overview

```
Projects-A69/
├── Moodle/                # Backend repo
│   ├── src/
│   │   ├── api/v1/endpoints/
│   │   ├── core/
│   │   ├── crud/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── utils/
│   │   └── main.py
│   ├── tests/
│   ├── pyproject.toml
│   ├── uv.lock
│   ├── Dockerfile
│   └── .env.template
├── Moodle-frontend/       # Frontend repo
│   ├── src/
│   │   ├── views/
│   │   ├── components/layout/
│   │   ├── assets/
│   │   ├── router/
│   │   ├── App.vue
│   │   └── main.js
│   ├── public/
│   │   ├── learnify.png
│   │   ├── UDI_logo.png
│   │   ├── default_pp.jpg
│   │   └── hacker_video.mp4
│   ├── Dockerfile
│   ├── vite.config.mjs
│   ├── package.json
│   └── .env.template
└── docker-compose.yml
```

---

## 📌 Final Notes

UDI reflects real-world architecture and teamwork, with full support for:

* JWT authentication
* Modular Vue + FastAPI architecture
* Dockerized development
* Responsive UI with theme support
* Role-separated access and responsibility

Made with ❤️ by Uasim, Dimitar, and Ivan for digital education excellence.
