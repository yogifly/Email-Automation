# 📚 BharatMail - Complete Installation Guide

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [System Setup](#system-setup)
3. [Ollama (LLM) Setup](#ollama-llm-setup)
4. [MongoDB Setup](#mongodb-setup)
5. [Backend Setup](#backend-setup)
6. [Frontend Setup](#frontend-setup)
7. [Verification](#verification)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software

| Software | Min Version | Purpose | Download |
|----------|------------|---------|----------|
| Python | 3.10 | Backend runtime | https://python.org |
| Node.js | 18 | Frontend tooling | https://nodejs.org |
| MongoDB | 5.0 | Database | https://mongodb.com |
| Ollama | Latest | Local LLM | https://ollama.ai |
| Git | Any | Version control | https://git-scm.com |

### System Requirements

- **RAM**: 8GB minimum (16GB recommended for smooth LLM inference)
- **Storage**: 5GB for MongoDB + Ollama models
- **Internet**: Required for first-time setup (model downloads)
- **OS**: Windows 10+, macOS 10.15+, or Linux

---

## System Setup

### Windows Setup

#### 1. Install Python

```bash
# Download from python.org or use Windows Store
python --version  # Verify: Python 3.10+
```

#### 2. Install Node.js

```bash
# Download from nodejs.org
node --version    # Verify: v18+
npm --version     # Verify: 9+
```

#### 3. Install MongoDB

**Option A: MongoDB Community Edition**

```bash
# Download from https://www.mongodb.com/try/download/community
# Run installer and follow prompts
# Default installation path: C:\Program Files\MongoDB\Server\

# Start MongoDB
mongod

# Verify connection
mongosh
```

**Option B: MongoDB Atlas (Cloud)**

1. Go to https://www.mongodb.com/cloud/atlas
2. Create free account
3. Create cluster
4. Get connection string
5. Update `.env` with connection string

#### 4. Install Ollama

```bash
# Download from https://ollama.ai
# Run installer
# Start Ollama
ollama serve
```

### macOS Setup

```bash
# Install Homebrew if not present
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python@3.10

# Install Node.js
brew install node

# Install MongoDB
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community

# Install Ollama
brew install ollama
ollama serve
```

### Linux Setup (Ubuntu/Debian)

```bash
# Update package manager
sudo apt update

# Install Python
sudo apt install python3.10 python3.10-venv python3-pip
python3.10 --version

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs

# Install MongoDB
curl -fsSL https://www.mongodb.org/static/pgp/server-7.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list
sudo apt update
sudo apt install mongodb-org
sudo systemctl start mongod

# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh
ollama serve
```

---

## Ollama (LLM) Setup

### Install Models

```bash
# Start Ollama server
ollama serve

# In another terminal, pull Mistral model
ollama pull mistral

# Or pull alternative models
ollama pull llama2
ollama pull neural-chat
```

### Verify Installation

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Should return:
# {"models": [{"name": "mistral:latest", ...}]}
```

### Model Configuration

Default model: **Mistral** (7B parameters, optimal for email responses)

To use different model, update `server/app/ai/ollama_client.py`:

```python
class OllamaConfig:
    base_url: str = "http://localhost:11434"
    model: str = "llama2"  # Change here
    timeout: float = 300.0
    temperature: float = 0.7
    max_tokens: int = 512
```

### Available Models

| Model | Size | Speed | Quality | Use Case |
|-------|------|-------|---------|----------|
| Mistral | 7B | Fast | Good | Email responses ✓ |
| Llama2 | 7B | Medium | Good | General purpose |
| Neural-Chat | 7B | Fast | Good | Conversational |
| Orca | 13B | Slow | Better | Complex reasoning |

---

## MongoDB Setup

### Local MongoDB

#### Start MongoDB (Windows)

```bash
# In PowerShell or CMD
mongod

# Keep this running in background
# Default port: 27017
```

#### Start MongoDB (macOS/Linux)

```bash
# macOS with Homebrew
brew services start mongodb-community

# Linux with systemctl
sudo systemctl start mongod

# Or run directly
mongod --dbpath /var/lib/mongodb
```

#### Verify Connection

```bash
# Open new terminal
mongosh

# Should see prompt: test>

# Create database
use maildb

# Exit
exit
```

### MongoDB Atlas (Cloud)

1. **Create Account**
   - Go to https://www.mongodb.com/cloud/atlas
   - Sign up with email

2. **Create Cluster**
   - Click "Create" → Select "Shared" (free tier)
   - Select region (e.g., US)
   - Click "Create Cluster"

3. **Add Connection**
   - Go to "Database" → "Connect"
   - Create user credentials
   - Whitelist IP address (or 0.0.0.0)
   - Get connection string

4. **Update .env**
   ```env
   MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/maildb?retryWrites=true&w=majority
   DB_NAME=maildb
   ```

---

## Backend Setup

### 1. Clone Repository

```bash
cd d:\bharatMail  # or your project directory
cd server
```

### 2. Create Virtual Environment

```bash
# Create
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (macOS/Linux)
source .venv/bin/activate

# Verify
python --version  # Should be 3.10+
```

### 3. Install Dependencies

```bash
pip install --upgrade pip

pip install -r requirements.txt

# Verify key packages
python -c "import fastapi; import motor; import pymongo; print('OK')"
```

### 4. Configure Environment

```bash
# Create .env file
echo MONGO_URI=mongodb://localhost:27017 > .env
echo DB_NAME=maildb >> .env
echo SECRET_KEY=your_secret_key >> .env
```

**Generate SECRET_KEY:**

```python
python -c "import secrets; print(secrets.token_hex(32))"
# Copy output and paste in .env
```

**Example .env:**

```env
# Database
MONGO_URI=mongodb://localhost:27017
DB_NAME=maildb

# Security
SECRET_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6

# Optional: Ollama config (defaults shown)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral
```

### 5. Start Backend Server

```bash
# Development (with auto-reload)
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Output:

```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

**✓ Backend running on http://localhost:8000**

### Verify Backend

```bash
# Test health endpoint
curl http://localhost:8000/health

# Should return: {"status": "ok"}
```

---

## Frontend Setup

### 1. Navigate to Client Directory

```bash
cd client  # From project root, or cd ../client from server folder
```

### 2. Install Dependencies

```bash
npm install

# Verify
npm --version  # Should be 9+
node --version  # Should be 18+
```

### 3. Configure API Endpoint

**Check `src/api.js`:**

```javascript
const api = axios.create({ baseURL: "http://localhost:8000" });
```

If backend is on different port/host, update the URL.

### 4. Start Development Server

```bash
npm run dev

# Output:
#   VITE v7.1.7  running at:
#   ➜  Local:   http://localhost:5173/
#   ➜  press h to show help
```

**✓ Frontend running on http://localhost:5173**

### Build for Production

```bash
npm run build

# Creates dist/ folder
# Use with: npm run preview
```

---

## Verification

### Step 1: Check All Services Running

**Terminal 1 - Ollama:**
```bash
ollama serve
# Should show: Ollama listening on ...
```

**Terminal 2 - MongoDB:**
```bash
mongod
# Should show: waiting for connections on port 27017
```

**Terminal 3 - Backend:**
```bash
cd server
.venv\Scripts\activate
python -m uvicorn app.main:app --reload
# Should show: Application startup complete
```

**Terminal 4 - Frontend:**
```bash
cd client
npm run dev
# Should show: Local: http://localhost:5173/
```

### Step 2: Test API Endpoints

```bash
# Health check
curl http://localhost:8000/health
# {"status": "ok"}

# Check Ollama models
curl http://localhost:11434/api/tags
# {"models": [{"name": "mistral:latest"}]}

# Check MongoDB connection
mongosh maildb
> db.stats()
```

### Step 3: Test Frontend

Open browser: **http://localhost:5173**

You should see:
- Landing page with login/register
- BharatMail branding
- Working UI

---

## First Time Setup Verification

### 1. Create Account

```
Frontend: http://localhost:5173
1. Click "Register"
2. Enter username: testuser
3. Enter password: testpass123
4. Click "Register"
```

### 2. Login

```
1. Click "Login"
2. Enter credentials
3. You should see Dashboard
```

### 3. Test Response Generation

```
1. Go to "Compose"
2. Send email to yourself
3. Go to "Inbox"
4. Click on email
5. Click "✨ Generate AI Reply"
6. Watch LLM generate response (~2-5 seconds)
7. Edit and send
```

---

## Troubleshooting

### Ollama Issues

**Problem: "Failed to connect to Ollama"**

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not running:
ollama serve

# Check firewall - allow localhost:11434
```

**Problem: "Model not found"**

```bash
# Pull model
ollama pull mistral

# List models
ollama list

# Should show: mistral:latest
```

**Problem: "Slow inference/timeout"**

```bash
# Increase timeout in app/ai/ollama_client.py
OllamaConfig(timeout=600.0)  # 10 minutes

# Check system RAM
# Mistral needs 8GB+ RAM
```

### MongoDB Issues

**Problem: "Connection refused on port 27017"**

```bash
# Start MongoDB
mongod  # Windows, macOS, Linux

# Or with custom path
mongod --dbpath /path/to/data
```

**Problem: "Database 'maildb' doesn't exist"**

```bash
# Create database automatically on first insert
# Or manually:
mongosh maildb
> db.createCollection("test")
> db.test.insertOne({test: true})
```

**Problem: "E11000 duplicate key error"**

```bash
# Reset indexes
cd server
python reset_indexes.py
```

### Backend Issues

**Problem: "ModuleNotFoundError"**

```bash
# Activate virtual environment
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

**Problem: "Port 8000 already in use"**

```bash
# Use different port
python -m uvicorn app.main:app --port 8001

# Or kill process using port
# Windows: netstat -ano | findstr :8000
# macOS/Linux: lsof -i :8000
```

### Frontend Issues

**Problem: "API request fails with 404"**

```bash
# Check backend is running
curl http://localhost:8000/health

# Update API endpoint in src/api.js
const api = axios.create({ baseURL: "http://localhost:8000" });
```

**Problem: "Port 5173 already in use"**

```bash
npm run dev -- --port 5174
```

**Problem: "Module not found (npm error)"**

```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

### General Issues

**Problem: "CORS error in browser console"**

Update `app/main.py`:

```python
CORSMiddleware(
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173"
    ],
    ...
)
```

**Problem: "Slow generation time"**

```bash
# Check system specs
# Mistral 7B: needs 8GB RAM, takes 2-5 seconds
# Use faster model if available:
ollama pull neural-chat  # Faster option
```

---

## Development Workflow

### Daily Startup

```bash
# Terminal 1: Ollama
ollama serve

# Terminal 2: MongoDB  
mongod

# Terminal 3: Backend
cd server && .venv\Scripts\activate && python -m uvicorn app.main:app --reload

# Terminal 4: Frontend
cd client && npm run dev
```

### File Changes

- **Backend**: Auto-reloads with `--reload` flag
- **Frontend**: Auto-reloads on file change (HMR)
- **Database**: Create indexes manually or on server startup

### Testing

```bash
# Backend tests
cd server
python test_cache.py

# Frontend linting
cd client
npm run lint

# Build frontend
npm run build
```

---

## Next Steps

1. **Read Full README**: `bharatMail/README.md`
2. **Try Quick Start**: `bharatMail/QUICK_START.md`
3. **Explore Features**: Use application
4. **Read API Docs**: In README.md
5. **Check Tests**: `server/test_*.py`

---

## Support

- **Documentation**: See README.md
- **Issues**: Check Troubleshooting section above
- **Logs**: Check browser console and terminal output
- **Tests**: Run `test_cache.py` for diagnostics

---

**Installation Complete! 🎉**

You're ready to use BharatMail!

Open: **http://localhost:5173**
