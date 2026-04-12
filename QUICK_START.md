# 🚀 BharatMail - Quick Setup Guide

## Get Running in 5 Minutes

### Step 1: Start Ollama (LLM Server)
```bash
ollama serve
```
✓ Runs on http://localhost:11434  
✓ Auto-pulls Mistral model on first use  
✓ Keep this running in background

### Step 2: Start MongoDB
```bash
mongod
```
✓ Runs on http://localhost:27017  
✓ Auto-creates 'maildb' database  
✓ Keep this running in background

### Step 3: Start Backend (Python)
```bash
cd server
python -m venv .venv
.venv\Scripts\activate     # Windows
# source .venv/bin/activate  # macOS/Linux
pip install -r requirements.txt

# Create .env file
echo MONGO_URI=mongodb://localhost:27017 > .env
echo DB_NAME=maildb >> .env
echo SECRET_KEY=%RANDOM% >> .env

# Start server
python -m uvicorn app.main:app --reload
```
✓ Runs on http://localhost:8000  
✓ Auto-creates indexes on startup

### Step 4: Start Frontend (React)
```bash
cd client
npm install
npm run dev
```
✓ Runs on http://localhost:5173  
✓ HMR enabled for hot reload

### Step 5: Open Application
```
Browser: http://localhost:5173
```

---

## 🎯 First Time Usage

### 1. Register Account
- Click "Register" on landing page
- Username: `yogesh`
- Password: `password123`

### 2. Send Test Email
- Go to Compose → Send email to yourself
- Subject: "Test Email"
- Body: "Can we meet tomorrow at 2 PM?"

### 3. Generate AI Response
- Go to Inbox → Click on sent email
- Click "✨ Generate AI Reply"
- Watch it generate a response!
- Edit if desired
- Click "Use This Response"

### 4. Test Caching
- Go back to Inbox
- Click same email again
- Generate again → **INSTANT!** (from cache)

### 5. Try Queue Processor
- Go to "📬 Queue" tab
- Click "⚡ Pre-generate Responses"
- Watch batch generation
- Click "✓ Send Reply" to send with learning

---

## 📊 System Check

### Check Ollama
```bash
curl http://localhost:11434/api/tags
```
Should return: `{"models": [{"name": "mistral:latest"}]}`

### Check MongoDB
```bash
mongosh maildb
> db.collection.find()
> exit
```

### Check Backend
```bash
curl http://localhost:8000/health
```
Should return: `{"status": "ok"}`

### Check Frontend
Open browser: `http://localhost:5173`

---

## 🔧 Environment Setup

### .env (Server)
```env
MONGO_URI=mongodb://localhost:27017
DB_NAME=maildb
SECRET_KEY=your_random_key_here
```

Generate SECRET_KEY:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## 📁 Project Structure

```
bharatMail/
├── server/              # FastAPI backend
│   ├── app/
│   │   ├── ai/          # LLM, caching, learning
│   │   ├── routers/     # API endpoints
│   │   └── main.py      # App init
│   ├── requirements.txt
│   └── .env
├── client/              # React frontend
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── pages/       # Page components
│   │   ├── api.js       # HTTP client
│   │   └── main.jsx     # Entry
│   ├── package.json
│   └── vite.config.js
└── README.md            # Full documentation
```

---

## 🔒 Ports Used

| Port | Service | URL |
|------|---------|-----|
| 5173 | Frontend (Vite) | http://localhost:5173 |
| 8000 | Backend (FastAPI) | http://localhost:8000 |
| 11434 | Ollama (LLM) | http://localhost:11434 |
| 27017 | MongoDB | mongodb://localhost:27017 |

If ports conflict, change them:

**Frontend:**
```bash
npm run dev -- --port 5174
```

**Backend:**
```bash
uvicorn app.main:app --port 8001
```

---

## 📋 Pre-requisites Checklist

- [ ] Python 3.10+ installed
- [ ] Node.js 18+ installed
- [ ] MongoDB 5.0+ installed
- [ ] Ollama installed
- [ ] 8GB+ RAM available
- [ ] Ports 5173, 8000, 11434, 27017 available

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| "Ollama not available" | `ollama serve` in terminal |
| "MongoDB not running" | `mongod` in terminal |
| "Port already in use" | Change port in run command |
| "Module not found" | `pip install -r requirements.txt` or `npm install` |
| "CORS error" | Update `app/main.py` allow_origins |

---

## 🎓 Learn More

- **Full README**: `bharatMail/README.md`
- **Cache System**: `bharatMail/CACHE_INTEGRATION_COMPLETE.md`
- **API Docs**: `bharatMail/README.md#-api-documentation`
- **Backend Testing**: `server/test_cache.py`

---

## 💡 Tips

1. **Hot Reload**: Frontend auto-reloads on file changes
2. **Backend Reload**: Use `--reload` flag to auto-reload on changes
3. **Debug Logs**: Check browser console and terminal for errors
4. **MongoDB Shell**: Use `mongosh maildb` to inspect data
5. **API Testing**: Use curl, Postman, or client directly

---

**You're all set! 🎉**

Open http://localhost:5173 and start using BharatMail!
