# 🥗 FreshMind — Flask + React

AI-Powered Smart Pantry App — **Python Backend + React Frontend**

---

## 📁 Project Structure

```
freshmind/
├── backend/
│   ├── app.py              ← Flask API (all routes)
│   ├── database.py         ← SQLite database (copy from root)
│   ├── auth.py             ← Auth logic (copy from root)
│   ├── ai_recipes.py       ← Groq AI (copy from root)
│   ├── image_fetcher.py    ← Wikipedia images (copy from root)
│   ├── notifier.py         ← Expiry notifier (copy from root)
│   ├── requirements.txt    ← Python deps
│   └── .env                ← API keys
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx         ← Router + Auth context
│   │   ├── pages/
│   │   │   ├── Login.jsx
│   │   │   ├── Home.jsx
│   │   │   ├── Pantry.jsx
│   │   │   ├── AddItem.jsx
│   │   │   ├── Recipes.jsx
│   │   │   ├── Dashboard.jsx
│   │   │   └── Settings.jsx
│   │   ├── components/
│   │   │   ├── Layout.jsx  ← Sidebar + topbar
│   │   │   └── NotifBell.jsx ← Notification popup
│   │   ├── api/
│   │   │   └── client.js   ← All API calls (Axios)
│   │   └── index.css       ← Tailwind + custom styles
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
│
├── start.sh                ← One command to start everything
└── README.md
```

---

## 🚀 Quick Start

### Step 1 — Copy your Python files to backend/

```bash
cp database.py      backend/
cp auth.py          backend/
cp ai_recipes.py    backend/
cp image_fetcher.py backend/
cp notifier.py      backend/
cp .env             backend/
cp freshmind.db     backend/   # if exists
```

### Step 2 — Set up backend

```bash
source venv/bin/activate   # or your venv path
pip install -r backend/requirements.txt
```

### Step 3 — Set up frontend

```bash
cd frontend
npm install
cd ..
```

### Step 4 — Run everything

```bash
# Option A: One command (recommended)
chmod +x start.sh
./start.sh

# Option B: Manual (two terminals)
# Terminal 1:
cd backend && python app.py

# Terminal 2:
cd frontend && npm run dev
```

### Step 5 — Open browser

```
http://localhost:5173
```

---

## 🔑 Environment Variables

Create `backend/.env`:

```env
GROQ_API_KEY=your_groq_api_key_here
JWT_SECRET=freshmind_secret_2024
```

---

## 🌐 API Endpoints

| Method | Route                        | Description          |
|--------|------------------------------|----------------------|
| POST   | /api/auth/login              | Login                |
| POST   | /api/auth/register           | Register             |
| GET    | /api/pantry/items            | Get all items        |
| POST   | /api/pantry/items            | Add item             |
| PUT    | /api/pantry/items/:id        | Update item          |
| DELETE | /api/pantry/items/:id        | Delete item          |
| POST   | /api/pantry/items/:id/use    | Mark as used         |
| GET    | /api/pantry/expiring/:days   | Get expiring items   |
| GET    | /api/pantry/history          | Usage history        |
| POST   | /api/ai/recipes              | Generate recipes     |
| POST   | /api/ai/chat                 | AI chat              |
| GET    | /api/image/fetch?name=...    | Fetch food image     |
| GET    | /api/weather                 | Weather data         |
| GET    | /api/users                   | All users (admin)    |
| PUT    | /api/users/password          | Change password      |

---

## 🛠️ Tech Stack

| Layer    | Technology            |
|----------|-----------------------|
| Backend  | Flask + Python        |
| Auth     | JWT tokens            |
| Database | SQLite (same as before)|
| AI       | Groq (llama-3.1)      |
| Frontend | React 18 + Vite       |
| Styling  | Tailwind CSS          |
| Charts   | Recharts              |
| Icons    | Lucide React          |
| HTTP     | Axios                 |

---

## 👥 Demo Credentials

| Username | Password    | Role  |
|----------|-------------|-------|
| admin    | admin123    | Admin |
| person_a | persona123  | Member|
| person_b | personb123  | Member|

---

## 🔄 Differences from Streamlit

| Feature          | Streamlit (old)     | Flask+React (new)    |
|------------------|---------------------|----------------------|
| Speed            | Reruns entire script| Only updates changed |
| Popups/Modals    | Hacky iframes       | Native React         |
| Dark mode        | CSS tricks          | Tailwind `dark:` class|
| Animations       | Limited             | Full CSS/JS control  |
| Notifications    | Broken position:fixed| Perfect dropdown    |
| Scalability      | Single user         | Multi-user ready     |
| Mobile           | Poor                | Responsive           |

---

Built with ❤️ Python & React
