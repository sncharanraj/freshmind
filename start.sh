#!/bin/bash
# start.sh — Start FreshMind (Flask + React)
# Run from the freshmind/ root directory

echo ""
echo "🥗 Starting FreshMind..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# ── Check Python venv ──
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo "✅ Python venv activated"
elif [ -f "../venv/bin/activate" ]; then
    source ../venv/bin/activate
    echo "✅ Python venv activated"
else
    echo "⚠️  No venv found — using system Python"
fi

# ── Copy existing DB files to backend if needed ──
if [ -f "freshmind.db" ] && [ ! -f "backend/freshmind.db" ]; then
    cp freshmind.db backend/freshmind.db
    echo "✅ Copied existing database to backend/"
fi

# ── Copy .env to backend if needed ──
if [ -f ".env" ] && [ ! -f "backend/.env" ]; then
    cp .env backend/.env
    echo "✅ Copied .env to backend/"
fi

# ── Copy Python modules to backend if needed ──
for f in database.py auth.py ai_recipes.py image_fetcher.py notifier.py; do
    if [ -f "$f" ] && [ ! -f "backend/$f" ]; then
        cp "$f" "backend/$f"
        echo "✅ Copied $f to backend/"
    fi
done

# ── Install backend deps ──
echo ""
echo "📦 Installing Python dependencies..."
pip install -r backend/requirements.txt -q
echo "✅ Backend deps ready"

# ── Install frontend deps ──
echo ""
echo "📦 Installing frontend dependencies..."
cd frontend && npm install --silent && cd ..
echo "✅ Frontend deps ready"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 Starting servers..."
echo "   Flask API  → http://localhost:5000"
echo "   React App  → http://localhost:5173"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# ── Start Flask in background ──
cd ~/freshmind/backend && python app.py &
FLASK_PID=$!
echo "✅ Flask started (PID: $FLASK_PID)"

# ── Start React frontend ──
cd freshmind/frontend && npm run dev &
VITE_PID=$!
echo "✅ React started (PID: $VITE_PID)"

echo ""
echo "🌐 Open → http://localhost:5173"
echo "Press Ctrl+C to stop both servers"
echo ""

# ── Wait and cleanup on exit ──
trap "echo ''; echo '🛑 Stopping...'; kill $FLASK_PID $VITE_PID 2>/dev/null; exit" INT TERM
wait
