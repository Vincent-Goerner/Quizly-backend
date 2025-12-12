# Quizly

## 🔍 Overview
Quizly is a Django-based, AI-Quiz Generator developed as part of the Developer Akademie program. It allows registered users to create, edit, interacte and manage AI generated quizzes based on Youtube video urls.

## ✨ Features

### User Authentication
- Register, login, logout functionality

### Quiz Generation
- Create a ai quiz with only a Youtube-URL

### Quiz Interaction
- Anwser the questions with multiple choice option

### Result Overview
- View quiz results with correct/incorrect answers

### Quiz Managment
- View, edit and delete quizzes
  
### Legal Pages
- Privacy Policy & Imprint pages

## ⚙️ Installation

### Prerequisites
- Python 3.13
- Django 4.0+
- Django REST Framework
- Django-Cors-Headers
- SimpleJWT
- FFmpeg
- YT-dlp
- Openai-Whisper
- Google-Genai
- SQLite (default) or PostgreSQL for production
- Virtual environment recommended (venv or pipenv)

Full list: requirements.txt (Installation guide see below)

### Local Setup
```bash
# 1. Clone the repository

git clone https://github.com/Vincent-Goerner/Quizly-backend.git
cd quizly-backend

# 2. Create and enter virtual environment

python -m venv env

  #Mac and Linux:
    source env/bin/activate

  # On Windows:
    env\Scripts\activate

# 3. Install dependencies

pip install -r requirements.txt

# 4. Run migrations

python manage.py makemigrations
python manage.py migrate

# 5. create superuser

python manage.py createsuperuser

# 6. Start development server

python manage.py runserver
```

## 🚀 API Endpoints (Examples)

### ✍️ Quiz Managment
| Method | Endpoint                | Description                                       |
| ------ | ----------------------- | ------------------------------------------------- |
| GET    | /api/quizzes/           | List all quizzes                                  |
| POST   | /api/createQuiz/        | Create a new quiz                                 |
| GET    | /api/quizzes/{id}/      | Retrieve a single quiz                            |
| PATCH  | /api/quizzes/{id}/      | Update quiz  (only owner)                         |
| DELETE | /api/quizzes/{id}/      | Delete quiz  (only owner)                         |


### 🔐 Authentication
| Method | Endpoint           |
| ------ | ------------------ |
| POST   | /api/register/     |
| POST   | /api/login/        |
| POST   | /api/logout/       |
| POST   | /api/token/refresh/|


## 🚫 Security & .env

This project uses a .env file to manage environment-specific and sensitive settings such as:

SECRET_KEY

DEBUG

The .env file is excluded from version control (.gitignore), but a .env.template is provided as a template.
Please copy .env.template to .env and fill in your own values before running the project.

## 🔧 Development Standards

Clean Code: Methods < 14 lines

Naming: snake_case for functions and variables

No dead/commented-out code

PEP-8 Compliance: All Python files follow PEP-8 guidelines


## 📄 License

Open-source project for educational purposes. Not intended for commercial use.
