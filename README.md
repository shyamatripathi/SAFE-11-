# SAFE — Symptoms Analysis and Forecasting Engine

SAFE is a web application that monitors your health, predicts your risk level, and keeps you informed through automated emails and an AI-powered chatbot. You fill in your details once — age, weight, symptoms, heart history — and the system takes it from there.

**Live:** https://safe-11.onrender.com/login/

Built with Django, Celery, Google Gemini, and PostgreSQL.

---

## What it does

When you register, SAFE calculates your BMI and runs your profile through a trained machine learning model to classify your health risk as Mild, Moderate, or High. Based on that classification, the system schedules email reminders to nudge you toward seeing a doctor at the right frequency.

You also get access to a chatbot that knows your health context. It uses Google Gemini under the hood, so conversations feel natural rather than scripted. If you mention chest pain, it immediately sends an emergency alert to your email — with a cooldown so it does not spam you.

---

## Tech stack

| Layer | Technology |
|---|---|
| Backend | Django 4.x |
| Database | PostgreSQL 15 |
| Task queue | Celery + Celery Beat |
| Broker | Redis 7 |
| AI chatbot | Google Gemini 1.5 Flash |
| ML model | scikit-learn (joblib) |
| Email | Django SMTP |
| Deployment | Docker + Docker Compose + Gunicorn |

---

## Project structure

```
SAFE2/
├── core/
│   ├── templates/           # HTML templates
│   ├── migrations/
│   ├── email_engine.py      # All email sending logic
│   ├── export_data.py       # Export profiles to CSV
│   ├── forms.py             # Registration and health forms
│   ├── memory.py            # Per-user chatbot memory
│   ├── ml_model.py          # Load model and run predictions
│   ├── models.py            # HealthProfile model
│   ├── safe_chatbot.py      # Gemini chatbot + fallback
│   ├── tasks.py             # Celery tasks
│   ├── urls.py
│   └── views.py
├── safe/
│   ├── settings.py
│   ├── celery.py
│   └── wsgi.py
├── .env
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── safe_model.pkl           # Trained ML model
└── safe_dataset.csv         # Training data export
```

---

## Data model

Every user has one `HealthProfile`. It stores:

| Field | Description |
|---|---|
| `age`, `height`, `weight` | Basic physical stats |
| `bmi` | Auto-calculated on save |
| `symptoms` | Comma-separated list |
| `heart_history` | Boolean flag |
| `severity` | Set automatically: Mild / Moderate / High |
| `last_email_sent` | Tracks reminder cooldown |
| `last_emergency_alert` | Tracks emergency email cooldown |

BMI and severity are recalculated every time a profile is saved.

---

## How severity is determined

The system tries the ML model first. If that fails for any reason, it falls back to a scoring algorithm.

**ML model inputs** (13 features):
```
age, bmi, heart_history,
chest_pain, shortness_of_breath, fever, cough, cold,
headache, nausea, dizziness, fatigue, vomiting
```

**Fallback scoring:**

| Factor | Points |
|---|---|
| Age 60+ | +2 |
| Age 45–59 | +1 |
| BMI 30+ | +2 |
| BMI 25–29 | +1 |
| Heart history | +3 |
| Chest pain | +3 |
| Shortness of breath | +3 |
| Dizziness or vomiting | +2 each |
| Fever, headache, nausea, fatigue, cough, cold | +1 each |

Score 8 or above is High. Score 4–7 is Moderate. Below 4 is Mild.

---

## Emails

There are four types of emails the system sends automatically.

**On registration:**
- A welcome email confirming the account is set up
- A severity assessment email explaining the risk level and how often reminders will come

**Scheduled reminders via Celery Beat:**
- High severity: every 3 days
- Moderate severity: every 7 days
- Mild severity: every 14 days

The task checks `last_email_sent` against the current time and only sends if the cooldown window has passed.

**Emergency alert:**
Triggered when the chatbot detects "chest" and "pain" in the same message. Sends an urgent email advising immediate medical attention. A 6-hour cooldown prevents the same alert from firing repeatedly in one session.

---

## Chatbot

The chatbot uses Google Gemini 1.5 Flash. Each request includes the user's current message, their severity level and known symptoms, and the conversation history from that session stored in `memory.py`.

This means the bot has context. It does not treat every message as if it came from a stranger.

If the Gemini API is unavailable, the fallback function handles the message locally using keyword matching. The priority order is:

1. Emergency keywords (chest pain, unconscious, seizure)
2. Symptom keywords in the current message
3. Stored symptoms from the health profile
4. A severity-based default response

---

## Endpoints

| URL | Description | Auth required |
|---|---|---|
| `/register/` | Create account and health profile | No |
| `/login/` | Log in | No |
| `/logout/` | Log out | No |
| `/dashboard/` | Main dashboard with chatbot | Yes |
| `/update-health/` | Edit health profile | Yes |
| `/chat-api/` | JSON endpoint for chat messages | Yes |

---

## Running with Docker

```bash
# Clone and enter the project
git clone <repo-url>
cd SAFE2

# Set up environment variables
cp .env.example .env

# Build and start
docker-compose up --build

# Run migrations
docker-compose exec web python manage.py migrate

# Create an admin account (optional)
docker-compose exec web python manage.py createsuperuser
```

The app runs on `http://localhost:8000`.

**Services:**

| Service | Role |
|---|---|
| `web` | Django app via Gunicorn |
| `worker` | Celery worker for async tasks |
| `beat` | Celery Beat for scheduled reminders |
| `redis` | Message broker |
| `db` | PostgreSQL database |

---

## Running locally without Docker

```bash
python -m venv venv
source venv/bin/activate

pip install -r requirements.txt

python manage.py migrate

# Redis must be running separately
redis-server

# Start these in separate terminals
celery -A safe worker --loglevel=info
celery -A safe beat --loglevel=info

python manage.py runserver
```

---

## Environment variables

Create a `.env` file in the project root. Do not commit it.

```env
SECRET_KEY=your-django-secret-key
DEBUG=False

DATABASE_URL=postgres://postgres:postgres@db:5432/safe
REDIS_URL=redis://redis:6379/0

GEMINI_API_KEY=your-gemini-api-key

EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=True
```

---

## Exporting training data

```bash
python core/export_data.py
```

Writes all health profiles to `safe_dataset.csv`. Useful for retraining the ML model as more users sign up.

---

## Registration flow

1. User submits the registration form with personal and health details
2. Account is created with a hashed password
3. Health profile is saved — BMI is calculated, severity is predicted
4. Welcome email is sent
5. Severity assessment email is sent with reminder schedule
6. User is logged in and redirected to the dashboard
