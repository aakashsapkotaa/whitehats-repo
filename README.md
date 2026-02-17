# EduHub – Educational Resource Sharing Platform

A hackathon-ready educational resource sharing platform built with **FastAPI**, **MongoDB**, and **Jinja2**.

## Features

- 🔐 **JWT Authentication** – Register/login with bcrypt password hashing
- 📚 **Resource Upload** – Upload PDFs, DOCX, slides with metadata (title, subject, semester, tags)
- 🔒 **Access Control** – Public/Private resources with college-based restrictions
- 🔍 **Search & Filter** – Search by title/subject/tags, filter by semester/type/privacy
- ⭐ **Ratings & Reviews** – 1-5 star ratings, one review per user per resource
- 💬 **Motivational Quotes** – Random quote loader on login page
- 🎨 **Glass UI Design** – Beautiful dark theme with animations

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI (Python) |
| Database | MongoDB Atlas (pymongo) |
| Frontend | HTML + Bootstrap + Vanilla JS |
| Templates | Jinja2 |
| Auth | JWT + bcrypt |
| File Storage | Local `uploads/` folder |

## Setup

```bash
# 1. Clone the repo
git clone https://github.com/aakashsapkotaa/whitehats-repo.git
cd whitehats-repo

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure .env (create or edit)
# MONGO_URL=mongodb+srv://<user>:<pass>@<cluster>.mongodb.net/?retryWrites=true&w=majority
# JWT_SECRET=your-secret-key

# 5. Run the server
uvicorn app.main:app --reload --port 8000
```

Open **http://localhost:8000** in your browser.

## Project Structure

```
app/
  main.py          # FastAPI app entry + router wiring
  database.py      # MongoDB connection
  auth.py          # JWT + bcrypt + get_current_user dependency
  models.py        # Pydantic schemas
  routes/
    auth_routes.py      # Register, Login, Profile, Avatar
    resource_routes.py  # CRUD + Search + Access Control
    review_routes.py    # Ratings & Reviews
    quote_routes.py     # Random quote + seeding
    page_routes.py      # Jinja2 page rendering
templates/             # HTML templates (Jinja2)
static/
  css/style.css    # Glass-UI dark theme
  js/main.js       # Shared JS utilities
  images/          # Logo assets
uploads/           # Uploaded files (gitignored)
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/register` | Register new user |
| POST | `/api/login` | Login and get JWT |
| GET | `/api/me` | Get current user profile |
| POST | `/api/avatar` | Upload avatar |
| POST | `/api/resources` | Upload resource |
| GET | `/api/resources` | List/search/filter resources |
| GET | `/api/resources/{id}` | Get resource detail |
| PUT | `/api/resources/{id}` | Edit own resource |
| DELETE | `/api/resources/{id}` | Delete own resource |
| GET | `/api/resources/{id}/download` | Download file |
| POST | `/api/resources/{id}/reviews` | Add/update review |
| GET | `/api/resources/{id}/reviews` | List reviews |
| GET | `/api/quotes/random` | Get random quote |

## Team – WhiteHats 🎩
