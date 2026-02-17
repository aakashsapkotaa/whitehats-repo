# 🏆 EduHub — Hackathon Pitch Document

## 🎯 Problem Statement

Students across colleges face a fragmented learning experience:
- **Notes are scattered** across WhatsApp groups, Google Drive links, and personal devices
- **No quality control** — duplicate files, malware-infected uploads, and outdated content
- **No collaboration** — students study in silos with no way to form study groups
- **No motivation** — sharing knowledge goes unrewarded

> **How might we build a unified, secure, and gamified platform where students share knowledge, collaborate in communities, and get rewarded?**

---

## 💡 Our Solution: EduHub

**EduHub** is a **community-driven educational resource sharing platform** that combines:

1. **Resource sharing** with metadata, search, and access control
2. **Community groups** for collaborative studying
3. **Gamification** with EduTokens and leaderboards
4. **Security** with malware scanning and duplicate detection
5. **OCR** for extracting text from images and PDFs

---

## ✨ Key Features

### 1. 📚 Smart Resource Sharing
- Upload PDFs, slides, past papers with full metadata (subject, semester, tags)
- **Public/Private access control** — Private resources only visible to same-college students
- **SHA256 duplicate detection** — prevents re-uploading the same file
- **Full-text search** with filters by semester, type, and privacy

### 2. 👥 Community Groups
- **Create study groups** by category (Engineering, Exam Prep, Projects, etc.)
- **Join/Leave** groups with one click
- **Group discussions** — real-time discussion feed within each group
- **Share resources to groups** — tag uploads to a specific community

### 3. 🪙 EduToken Gamification
- Earn tokens for every valuable action:
  - **+10** for safe uploads
  - **+15** for catching malware
  - **+5** for daily login
  - **+2** for OCR usage
  - **+1** for exploring resources
- **Leaderboard** — top users ranked by token count
- **Explore Score** — tracks curiosity and engagement

### 4. 👁️ OCR — Image & PDF to Text
- Upload any image (JPG, PNG, etc.) or **PDF** and extract text
- **Dual-engine OCR**: tries local Tesseract → falls back to OCR.space free API
- Works **out-of-the-box** without system dependencies
- Full OCR history per user

### 5. 🛡️ Security Layer
- **Malware scanning** via VirusTotal API integration
- **SHA256 file hashing** for duplicate prevention
- **Rate limiting** (60 req/min) to prevent abuse
- **Admin panel** for managing reports, banning users, and removing content

### 6. 💬 Community Engagement
- **Like/Unlike** resources (toggle)
- **Comment** on resources with threaded discussions
- **Star ratings & reviews** (1–5 stars, one review per user)
- **Report** inappropriate content → goes to admin panel
- **Trust Score** — reputation system based on uploads, ratings, and reports

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│                     Client                       │
│         HTML + CSS + Vanilla JavaScript           │
│  (Dashboard, Browse, Upload, Community, OCR...)   │
└──────────────────────┬──────────────────────────┘
                       │ REST API (JSON)
┌──────────────────────▼──────────────────────────┐
│               FastAPI Backend                    │
│  ┌──────────┐ ┌──────────┐ ┌──────────────────┐ │
│  │ Auth     │ │ Resources│ │ Community Groups │ │
│  │ (JWT+    │ │ (CRUD,   │ │ (Create, Join,   │ │
│  │ bcrypt)  │ │ Search)  │ │ Discuss, Share)  │ │
│  └──────────┘ └──────────┘ └──────────────────┘ │
│  ┌──────────┐ ┌──────────┐ ┌──────────────────┐ │
│  │ OCR      │ │ Tokens & │ │ Admin Panel      │ │
│  │ (API +   │ │ Leaderb. │ │ (Reports, Bans)  │ │
│  │ Tesser.) │ │          │ │                  │ │
│  └──────────┘ └──────────┘ └──────────────────┘ │
│  ┌──────────┐ ┌──────────┐ ┌──────────────────┐ │
│  │ Malware  │ │ Reviews  │ │ Community        │ │
│  │ Scanner  │ │ & Ratings│ │ (Likes,Comments) │ │
│  └──────────┘ └──────────┘ └──────────────────┘ │
└──────────────────────┬──────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────┐
│              MongoDB Atlas                       │
│  users │ resources │ reviews │ groups │ likes    │
│  comments │ reports │ ocr_results │ token_logs   │
│  scan_logs │ quotes │ group_posts                │
└─────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Component | Technology | Why |
|-----------|-----------|-----|
| **Backend** | FastAPI (Python) | Async, auto-docs, type-safe, fast |
| **Database** | MongoDB Atlas | Flexible schema, free cloud tier |
| **Auth** | JWT + bcrypt | Stateless, secure, industry standard |
| **Frontend** | HTML + Vanilla CSS + JS | Zero build step, fast iteration |
| **OCR** | OCR.space API + Tesseract | Free, no system deps needed |
| **Malware Scan** | VirusTotal API | Industry-grade file scanning |
| **Rate Limiting** | slowapi | Prevents abuse |

---

## 🎮 Demo Flow

1. **Register** → Create account with college, branch, semester
2. **Dashboard** → See stats (EduTokens, Explore Score, Resources)
3. **Upload** → Share notes with metadata, earn +10 tokens
4. **Browse** → Search/filter by subject, semester, type
5. **Community** → Create/join study groups, discuss, share resources
6. **OCR** → Upload image/PDF → extract text instantly
7. **Leaderboard** → See who's contributing the most
8. **Like, Comment, Rate** → Engage with community content

---

## 🌟 What Makes EduHub Unique

| Feature | Other Platforms | EduHub |
|---------|----------------|--------|
| Gamification | ❌ None | ✅ EduTokens + Leaderboard |
| Community Groups | ❌ Just file dumps | ✅ Create groups, discuss, share |
| Malware Scanning | ❌ No security | ✅ VirusTotal + SHA256 |
| OCR | ❌ Not available | ✅ Image + PDF → Text |
| Access Control | ❌ Open or closed | ✅ Public + College-private |
| Duplicate Prevention | ❌ Same file uploaded 10x | ✅ SHA256 hash check |
| Trust Score | ❌ No reputation | ✅ Community trust algorithm |

---

## 📊 Scalability

- **MongoDB Atlas** — cloud-hosted, auto-scaling
- **Stateless JWT auth** — horizontal scale ready
- **Modular FastAPI routers** — each feature is a separate module
- **Rate limiting** — built-in abuse prevention
- **File deduplication** — saves storage via hash checking

---

## 🚀 Future Roadmap

- 🤖 AI-powered content recommendations
- 📱 Progressive Web App (PWA) for mobile
- 🔔 Push notifications for group activity
- 📊 Analytics dashboard for resource engagement
- 🌐 Multi-language OCR support
- 🎓 Certificate generation for top contributors

---

## 👥 Team WhiteHats 🎩

Built with ❤️ for the hackathon by Team WhiteHats.
