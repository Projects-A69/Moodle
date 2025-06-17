<p align="center">
  <img src="src/utils/UDI_logo.png" alt="UDI Platform Logo" width="150"/>
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
* **Dependency & Env Management:** `pyproject.toml`, `uv`, `.env.template`
* **Testing:** `unittest`
* **Containerization:** Docker

### 🎨 Frontend – Vue.js

* **Framework:** Vue 3 with Composition API
* **Routing:** Vue Router (structured in `router/index.js`)
* **Build Tool:** Vite
* **Styling:** Base CSS Variables with Light/Dark theme support
* **State & API Handling:** LocalStorage, Axios, JWT decode
* **Components:** Dashboard layout, role-based dynamic views (Student, Teacher, Admin)
* **Pages:** Login, Register, Course, Section, Profile, Admin Panels
* **Containerization:** Docker

---

## 🚀 Getting Started

### 📦 Backend Setup (`Moodle` Repository)

1. **Clone the Repository**

   ```bash
   git clone https://github.com/Projects-A69/Moodle.git
   cd Moodle/backend
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

   Then configure:

   * `JWT_SECRET_KEY`, `DATABASE_URL`, `EMAIL_USERNAME`, `AWS_ACCESS_KEY_ID`, etc.

4. **Run the Backend Server**

   ```bash
   uvicorn src.main:app --reload
   ```

Or use Docker Compose:

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

3. **Environment Configuration**

   ```bash
   cp .env.template .env
   ```

   Update:

   ```env
   VITE_API_URL=http://localhost:8000
   ```

4. **Run the Dev Server**

   ```bash
   npm run dev
   ```

Or run via Docker:

```bash
docker compose up --build
```

---

## ✨ Key Features

### 👨‍🎓 Students

* Browse and enroll in available courses
* Track enrolled courses and progress
* View sections and content
* Rate completed courses

### 👩‍🏫 Teachers

* Register and wait for admin approval
* Create and manage courses and sections
* Approve student enrollment requests via email
* View course feedback

### 🛡️ Admins

* Approve or reject teachers
* Manage users and course visibility
* Delete or hide courses
* Access ratings and student enrollment data

### 🌐 Core System Features

* Secure JWT authentication and auto-logout
* Email notification system with approval tokens
* Drag-and-drop image upload to AWS S3
* Light/Dark mode UI with CSS variables
* Fully Dockerized frontend/backend setup

---

## 🗃️ Database Schema

<p align="center">
  <img src="src/utils/diagram.png" alt="Database Schema" width="700"/>
</p>

---

## 🧪 Running Tests

```bash
python -m unittest discover tests
```

**Test Coverage Includes:**

* User registration and login
* Admin and teacher workflows
* Email token generation and validation
* Secure password handling and JWT

---

## 📁 Project Structure Overview

```
Projects-A69/
├── Moodle/                # Backend repo
│   ├── backend/
│   │   ├── src/
│   │   │   ├── api/
│   │   │   ├── core/
│   │   │   ├── crud/
│   │   │   ├── models/
│   │   │   ├── schemas/
│   │   │   ├── utils/
│   │   │   └── main.py
│   │   └── .env.template
│   ├── uv.lock
│   └── pyproject.toml
├── Moodle-frontend/      # Frontend repo
│   ├── src/
│   │   ├── views/
│   │   ├── components/
│   │   ├── router/
│   │   ├── assets/
│   │   └── App.vue
│   ├── .env.template
│   └── package.json
└── docker-compose.yml
```

---

## 📌 Final Notes

UDI reflects best practices in modern full-stack development:

* Clean separation of concerns (FastAPI + Vue)
* Real-world features like image upload, email workflows, and role-based dashboards
* Modular, testable, and easy to extend

Built with ❤️ by Uasim, Dimitar, and Ivan to power the future of digital learning.
