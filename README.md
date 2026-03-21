# 🥗 FreshMind — AI-Powered Smart Pantry Assistant

> Reduce food waste, save money, and cook smarter with AI-powered pantry management.

![FreshMind](https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=1200&auto=format&fit=crop&q=80)

---

## 📌 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [API Endpoints](#api-endpoints)
- [Team](#team)

---

## 🧠 Overview

FreshMind is a full-stack web application that helps you manage your pantry smartly. It tracks expiry dates, suggests AI-powered recipes from items you already have, and helps reduce food waste — all with a clean, modern UI.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔐 Auth | Login, Register, JWT-based sessions |
| 📦 Pantry Management | Add, edit, delete, mark items as used |
| 🔔 Expiry Alerts | Real-time notifications for items expiring soon |
| 🤖 AI Recipes | Groq-powered recipe suggestions from your pantry |
| 💬 AI Chat | Ask the AI anything about cooking |
| 📊 Dashboard | Charts for category breakdown, waste tracking |
| 🖼️ Image Fetcher | Auto-fetch food images from Wikipedia |
| 📷 Camera Upload | Add item images via camera or local file |
| 🌙 Dark Mode | Full dark/light theme support |
| 👑 Admin Panel | Login history, user stats (admin only) |
| 🌤️ Weather | Live weather with pantry storage tips |
| 👥 Multi-user | Each user sees only their own data |

---

## 🛠️ Tech Stack

### Backend
- **Python 3.12**
- **Flask** — REST API
- **SQLite** — Database
- **JWT** — Authentication
- **Groq API** — AI (llama-3.1-8b-instant)
- **Flask-CORS** — Cross-origin support

### Frontend
- **React 18**
- **Vite** — Build tool
- **Tailwind CSS** — Styling
- **React Router v6** — Navigation
- **Axios** — API calls
- **Recharts** — Dashboard charts
- **Lucide React** — Icons

---

## 📁 Project Structure

```
freshmind/
├── backend/
│   ├── app.py              # Flask API routes
│   ├── database.py         # SQLite CRUD operations
│   ├── auth.py             # User authentication
│   ├── ai_recipes.py       # Groq AI integration
│   ├── image_fetcher.py    # Wikipedia image fetcher
│   ├── notifier.py         # Expiry notifications
│   └── .env                # Environment variables
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx          # Root + routing
│   │   ├── main.jsx         # Entry point
│   │   ├── index.css        # Global styles
│   │   ├── api/
│   │   │   └── client.js    # Axios API client
│   │   ├── components/
│   │   │   ├── Layout.jsx   # Sidebar + topbar
│   │   │   └── NotifBell.jsx# Notification popup
│   │   └── pages/
│   │       ├── Login.jsx    # Login + Register
│   │       ├── Home.jsx     # Dashboard home
│   │       ├── Pantry.jsx   # Pantry management
│   │       ├── AddItem.jsx  # Add new item
│   │       ├── Recipes.jsx  # AI recipes + chat
│   │       ├── Dashboard.jsx# Analytics charts
│   │       ├── Settings.jsx # Profile + password
│   │       └── Admin.jsx    # Admin panel
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── index.html
│
├── .gitignore
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.12+
- Node.js 18+
- Groq API key (free at [console.groq.com](https://console.groq.com))

### 1. Clone the repo

```bash
git clone https://github.com/sncharanraj/freshmind.git
cd freshmind
```

### 2. Setup Backend

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# Install dependencies
pip install flask flask-cors pyjwt python-dotenv \
            requests groq pillow pyzbar

# Create .env file
cp .env.example .env
# Add your GROQ_API_KEY to .env

# Run backend
cd backend
python app.py
# Runs on http://localhost:5000
```

### 3. Setup Frontend

```bash
cd frontend

# Install dependencies
npm install

# Run frontend
npm run dev
# Runs on http://localhost:5173
```

### 4. Open the app

```
http://localhost:5173
```

---

## 🔐 Demo Accounts

| Role | Username | Password |
|---|---|---|
| 👑 Admin | `admin` | `admin123` |
| 👤 Person A | `person_a` | `persona123` |
| 👤 Person B | `person_b` | `personb123` |

---

## 🌍 Environment Variables

Create a `.env` file in the `backend/` folder:

```env
GROQ_API_KEY=your_groq_api_key_here
JWT_SECRET=your_jwt_secret_here
```

Get your free Groq API key at [console.groq.com](https://console.groq.com)

---

## 📡 API Endpoints

### Auth
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/login` | Login |
| POST | `/api/auth/register` | Register |
| GET | `/api/auth/me` | Current user |

### Pantry
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/pantry/items` | Get all items |
| POST | `/api/pantry/items` | Add item |
| PUT | `/api/pantry/items/:id` | Update item |
| DELETE | `/api/pantry/items/:id` | Delete item |
| POST | `/api/pantry/items/:id/use` | Mark as used |
| GET | `/api/pantry/expiring/:days` | Get expiring items |
| GET | `/api/pantry/history` | Usage history |

### AI
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/ai/recipes` | Generate recipes |
| POST | `/api/ai/chat` | Chat with AI |

### Admin (admin only)
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/admin/users` | All users |
| GET | `/api/admin/login-history` | Login history |
| GET | `/api/admin/login-stats` | Login stats per user |

---

## 👥 Team

| Role | Name | GitHub |
|---|---|---|
| 🔧 Backend | S N Charanraj | [@sncharanraj](https://github.com/sncharanraj) |
| 🎨 Frontend | Sudeep K | [@Sudeep-25](https://github.com/Sudeep-25) |

---

## 📄 License

This project is for educational purposes.

---

<p align="center">Built with ❤️ using Python & React</p>
