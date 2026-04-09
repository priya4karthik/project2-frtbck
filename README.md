# 🤖 AI Form Assistant — Django

A smart registration form that validates inputs in real time using JavaScript
and calls the **Anthropic Claude API** to give users live, contextual improvement
suggestions as they type — all backed by a Django REST-style backend.

---

## ✨ Features

| Layer | What it does |
|---|---|
| **Bootstrap 5 UI** | Responsive, polished design with progress bar & field groups |
| **JS Validation** | Per-field real-time feedback before any server round-trip |
| **Debounced AI** | Calls Claude API 1.8 s after the user stops typing |
| **AJAX endpoint** | `POST /ai-suggest/` streams suggestions without page reload |
| **Django backend** | Server-side validation via `ModelForm` (security layer) |
| **SQLite storage** | Every submission saved with the AI feedback attached |
| **Django Admin** | Full CRUD at `/admin/` |
| **WhiteNoise** | Static files served directly — no separate CDN needed |
| **Production-ready** | `.env` support, HSTS, SSL redirect, gunicorn `Procfile` |

---

## 🗂️ Project Structure

```
ai_form_assistant/
├── manage.py
├── settings.py          ← Django settings (reads .env)
├── urls.py              ← Root URL router
├── wsgi.py              ← WSGI entry point
├── requirements.txt     ← Django + gunicorn + whitenoise + dotenv
├── Procfile             ← For Heroku / Railway / Render
├── .env.example         ← Copy to .env and fill your keys
├── form_app/
│   ├── admin.py         ← Registers FormSubmission in admin
│   ├── apps.py
│   ├── forms.py         ← ModelForm with custom validators
│   ├── models.py        ← FormSubmission model
│   ├── urls.py          ← App-level URL patterns
│   └── views.py         ← form_view, ai_suggest_view, submissions_view
└── templates/
    ├── base.html        ← Navbar, fonts, CSS variables
    └── form_app/
        ├── form.html        ← Smart form with live AI panel
        ├── success.html     ← Post-submit AI feedback page
        └── submissions.html ← All submissions table
```

---

## 🚀 Local Setup (Step-by-Step)

### 1. Clone / extract the project
```bash
cd ai_form_assistant
```

### 2. Create and activate a virtual environment
```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
```bash
cp .env.example .env
# Open .env and set:
#   ANTHROPIC_API_KEY=sk-ant-...
#   SECRET_KEY=some-long-random-string
```

### 5. Apply migrations
```bash
python manage.py makemigrations form_app
python manage.py migrate
```

### 6. (Optional) Create a Django superuser
```bash
python manage.py createsuperuser
```

### 7. Run the development server
```bash
python manage.py runserver
```

Open **http://127.0.0.1:8000** — the form is live!

| URL | Purpose |
|---|---|
| `/` | Smart registration form |
| `/ai-suggest/` | AJAX AI suggestions endpoint |
| `/submissions/` | All submissions list |
| `/admin/` | Django admin panel |

---

## ☁️ Deploying to Railway (free tier)

1. Push the project to a GitHub repo
2. Go to [railway.app](https://railway.app) → **New Project → Deploy from GitHub**
3. Set environment variables in the Railway dashboard:
   - `ANTHROPIC_API_KEY`
   - `SECRET_KEY`
   - `DEBUG=False`
   - `ALLOWED_HOSTS=your-app.railway.app`
4. Railway auto-detects the `Procfile` and runs gunicorn
5. Run migrations via Railway's shell:
   ```bash
   python manage.py migrate
   python manage.py collectstatic --noinput
   ```

---

## ☁️ Deploying to Render

1. Create a **Web Service** pointing to your GitHub repo
2. Build command: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
3. Start command: `gunicorn wsgi:application`
4. Add env vars: `ANTHROPIC_API_KEY`, `SECRET_KEY`, `DEBUG=False`, `ALLOWED_HOSTS`

---

## 🔑 Getting an Anthropic API Key

1. Visit **https://console.anthropic.com/**
2. Sign up / log in
3. Go to **API Keys** → **Create Key**
4. Copy the key (starts with `sk-ant-`) into your `.env` file

---

## 🔒 Security Notes

- Never commit `.env` to version control (add it to `.gitignore`)
- In production set `DEBUG=False`
- Rotate `SECRET_KEY` from the insecure default
- For a real production database use PostgreSQL via `dj-database-url`

---

## 📐 How the AI Integration Works

```
User types in form field
        │
        ▼  (debounced 1.8 s)
JS gathers all field values
        │
        ▼
AJAX POST /ai-suggest/
  { full_name, email, phone, … }
        │
        ▼
Django view builds a prompt
        │
        ▼
urllib.request → Anthropic API
  claude-opus-4-5 model
        │
        ▼
JSON { "suggestion": "• …" }
        │
        ▼
JS renders bullet list in AI panel
```

On **final submit**, the same AI call is made server-side and the suggestion
is stored alongside the form data in the database.
