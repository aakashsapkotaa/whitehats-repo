# 🎓 EduHub – Community-Driven Educational Resource Sharing Platform

[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com)
[![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-brightgreen.svg)](https://www.mongodb.com/atlas)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)

**EduHub** is a community-driven platform where students share, discover, and collaborate on educational resources. Upload notes, past papers, and slides — earn **EduTokens**, join **study groups**, and climb the **leaderboard**.

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔐 **JWT Authentication** | Register/Login with bcrypt hashing, role-based access |
| 📚 **Resource Upload** | Upload PDFs, DOCX, slides with metadata (title, subject, semester, tags) |
| 🔒 **Access Control** | Public/Private resources with college-based restrictions |
| 🔍 **Search & Filter** | Full-text search, filter by semester/type/privacy |
| ⭐ **Ratings & Reviews** | 1–5 star ratings, one review per user per resource |
| 💬 **Comments & Likes** | Community engagement — like, comment, discuss on resources |
| 👥 **Community Groups** | Create/join study groups, share resources, group discussions |
| 🪙 **EduToken System** | Earn tokens for uploads, views, OCR usage — gamified learning |
| 🏆 **Leaderboard** | Top users ranked by EduTokens and explore score |
| 👁️ **OCR — Image/PDF to Text** | Extract text from images and PDFs using OCR (free API) |
| 🛡️ **Malware Scanning** | SHA256 duplicate check + VirusTotal integration (optional) |
| 🚩 **Report System** | Flag inappropriate resources for admin review |
| 🔧 **Admin Panel** | Ban users, delete files, view reports and scan logs |
| ⚡ **Rate Limiting** | 60 req/min via slowapi to prevent abuse |
| 💬 **Motivational Quotes** | Random quotes on login page for motivation |

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI (Python 3.10+) |
| Database | MongoDB Atlas (pymongo) |
| Frontend | HTML + Vanilla CSS + Vanilla JS |
| Templates | Jinja2 |
| Auth | JWT (python-jose) + bcrypt (passlib) |
| OCR | OCR.space API (free tier) + Tesseract fallback |
| File Storage | Local `uploads/` folder |
| Malware Scan | VirusTotal API (optional) |
| Rate Limiting | slowapi |

## 🚀 Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/aakashsapkotaa/whitehats-repo.git
cd whitehats-repo

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment (.env)
# MONGO_URL=mongodb+srv://<user>:<pass>@<cluster>.mongodb.net/?retryWrites=true&w=majority
# JWT_SECRET=your-secret-key

# 5. Run the server
uvicorn app.main:app --reload --port 8000
```

Open **http://localhost:8000** → Register → Start sharing! 🎉

## 📁 Project Structure

```
app/
  main.py              # FastAPI entry + router wiring + startup
  database.py          # MongoDB connection + collections + indexes
  auth.py              # JWT + bcrypt + role-based dependencies
  models.py            # Pydantic request schemas
  routes/
    auth_routes.py     # Register, Login, Profile, Avatar upload
    resource_routes.py # CRUD + Search + Access Control + Group tagging
    review_routes.py   # Star ratings & reviews
    community_routes.py # Likes, Comments, Reports, Trust Score
    group_routes.py    # Study groups: Create, Join, Leave, Discuss
    token_routes.py    # EduToken balance, history, leaderboard
    ocr_routes.py      # Image/PDF → Text extraction
    admin_routes.py    # Ban/Unban users, delete files, reports
    quote_routes.py    # Random motivational quotes
    page_routes.py     # Jinja2 HTML page rendering
  utils/
    scanner.py         # SHA256 hashing + VirusTotal malware scan
    tokens.py          # EduToken award system
templates/             # 11 HTML pages (Jinja2 templates)
static/
  css/style.css        # Glass-UI dark theme with animations
  js/main.js           # Shared JS utilities
  images/              # Logo assets
uploads/               # Uploaded files (gitignored)
```

## 🔗 API Endpoints

### Auth
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/register` | Register new user |
| POST | `/api/login` | Login → JWT token |
| GET | `/api/me` | Current user profile |
| POST | `/api/avatar` | Upload profile avatar |

### Resources
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/resources` | Upload resource (with optional group_id) |
| GET | `/api/resources` | List/search/filter resources |
| GET | `/api/resources/{id}` | Resource detail |
| PUT | `/api/resources/{id}` | Edit own resource |
| DELETE | `/api/resources/{id}` | Delete own resource |
| GET | `/api/resources/{id}/download` | Download file |

### Community
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/resources/{id}/like` | Toggle like |
| GET | `/api/resources/{id}/likes` | Like count + user status |
| POST | `/api/resources/{id}/comments` | Post comment |
| GET | `/api/resources/{id}/comments` | List comments |
| POST | `/api/resources/{id}/report` | Report resource |
| GET | `/api/community/trust/{user_id}` | Trust score |

### Study Groups
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/groups` | Create group |
| GET | `/api/groups` | List all groups |
| GET | `/api/groups/my` | My groups |
| GET | `/api/groups/{id}` | Group detail + posts |
| POST | `/api/groups/{id}/join` | Join group |
| POST | `/api/groups/{id}/leave` | Leave group |
| POST | `/api/groups/{id}/post` | Post discussion |
| DELETE | `/api/groups/{id}` | Delete group (creator) |

### Tokens & Leaderboard
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/tokens/me` | My token balance |
| GET | `/api/tokens/history` | Token transaction log |
| GET | `/api/leaderboard` | Top 20 by EduTokens |

### OCR
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/ocr/extract` | Extract text from image/PDF |
| GET | `/api/ocr/history` | OCR history |

### Reviews & Admin
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/resources/{id}/reviews` | Add/update review |
| GET | `/api/resources/{id}/reviews` | List reviews |
| GET | `/api/quotes/random` | Random quote |
| GET | `/api/admin/flagged` | Reported files |
| GET | `/api/admin/malicious` | Malware scan logs |
| POST | `/api/admin/ban/{user_id}` | Ban user |
| POST | `/api/admin/unban/{user_id}` | Unban user |
| DELETE | `/api/admin/resources/{id}` | Admin delete resource |
| GET | `/api/admin/users` | List all users |

## 🪙 EduToken Rewards

| Action | Tokens |
|--------|--------|
| Safe Upload | +10 |
| Malware Caught | +15 |
| Daily Login | +5 |
| OCR Usage | +2 |
| Explore (View Resource) | +1 |
| High Rated File | +5 |
| Create Group | +5 |

## 👥 Team — WhiteHats 🎩
