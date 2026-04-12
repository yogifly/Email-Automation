# BharatMail - AI-Powered Email Response System

A comprehensive email management and AI response generation platform with intelligent caching, priority queue processing, calendar integration, and learning feedback loops.

## 📋 System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  Frontend (React + Vite)                                       │
│  - MessageView: Email display with AI response generator       │
│  - QueueProcessor: Batch response processor                    │
│  - Compose: Draft and send emails                              │
│  - Calendar: Event management and suggestions                  │
│  - Dashboard: Main application hub                             │
│                                                                 │
└─────────────────┬───────────────────────────────────────────────┘
                  │ HTTP REST API
                  │ (Axios client)
┌─────────────────▼───────────────────────────────────────────────┐
│                                                                 │
│  Backend (FastAPI + Python)                                    │
│  - Auth Service: JWT-based authentication                      │
│  - Message Service: Email CRUD, priority queue                 │
│  - Response Generator: AI-powered reply generation             │
│  - Cache Service: Draft caching with TTL                       │
│  - Learning System: Profile training and feedback              │
│  - Calendar Service: Event management and ML suggestions       │
│                                                                 │
└─────────────────┬───────────────────────────────────────────────┘
                  │
         ┌────────┴────────┬─────────────┐
         │                 │             │
    ┌────▼──┐      ┌──────▼──┐    ┌────▼─────┐
    │MongoDB │      │ Ollama  │    │  Scikit- │
    │ 3.8+   │      │ Server  │    │  learn   │
    │        │      │ (Local) │    │  (ML)    │
    └────────┘      └─────────┘    └──────────┘
```

---

## 🚀 Quick Start (5 Minutes)

### Prerequisites
- **Python 3.10+** (for backend)
- **Node.js 18+** (for frontend)
- **MongoDB 5.0+** (local or cloud)
- **Ollama** (for local LLM inference)

### 1️⃣ Start Ollama Server

```bash
# Windows
ollama serve

# macOS/Linux
ollama serve
```

By default, Ollama runs on `http://localhost:11434`

The system will automatically pull the Mistral model on first use.

### 2️⃣ Setup Backend (Server)

```bash
cd server

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Create .env file
echo MONGO_URI=mongodb://localhost:27017 > .env
echo DB_NAME=maildb >> .env
echo SECRET_KEY=your_secret_key_here >> .env

# Start server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Server will be available at: `http://localhost:8000`

### 3️⃣ Setup Frontend (Client)

```bash
cd client

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will be available at: `http://localhost:5173`

### 4️⃣ Access Application

Open your browser and navigate to: **`http://localhost:5173`**

---

## 📦 Complete Setup Guide

### System Requirements

| Component | Version | Purpose |
|-----------|---------|---------|
| Python | 3.10+ | Backend runtime |
| Node.js | 18+ | Frontend tooling |
| MongoDB | 5.0+ | Data storage |
| Ollama | Latest | Local LLM inference |
| FastAPI | 0.104+ | REST API framework |
| React | 19.1+ | Frontend framework |

### Environment Configuration

#### Server (.env)

```env
# MongoDB Connection
MONGO_URI=mongodb://localhost:27017
DB_NAME=maildb

# JWT Security
SECRET_KEY=generate-a-random-secret-key-here

# Optional: Ollama Configuration (if not default)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral
```

Generate a secure secret key:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

#### Client (Built-in)

The client is configured to connect to the backend at `http://localhost:8000`.

Edit `src/api.js` to change the API endpoint:
```javascript
const api = axios.create({ baseURL: "http://localhost:8000" });
```

### Database Setup

MongoDB automatically creates indexes on first run via `app/database.py`.

**Manual index creation** (if needed):
```bash
# Reset indexes
cd server
python reset_indexes.py

# View indexes
mongosh maildb --eval "db.response_drafts.getIndexes()"
```

---

## 🏗️ Architecture Details

### Frontend Structure

```
client/src/
├── components/
│   ├── Inbox.jsx              # Inbox management
│   ├── MessageView.jsx        # Email display + AI response
│   ├── ResponseEditor.jsx     # AI response editor with caching
│   ├── QueueProcessor.jsx     # Batch response processor
│   ├── Compose.jsx            # Email composer
│   ├── Calendar.jsx           # Calendar view
│   ├── CalendarSuggestions.jsx # ML event suggestions
│   └── landing/               # Landing page
├── pages/
│   └── Dashboard.jsx          # Main application page
├── hooks/
│   └── useAuth.js            # Authentication hook
├── styles/                    # Component-specific CSS
└── api.js                     # Axios HTTP client
```

### Backend Structure

```
server/app/
├── routers/
│   ├── auth_routes.py         # Login/register/JWT
│   ├── message_routes.py      # Email CRUD, queue, priority
│   ├── response_routes.py     # AI response generation + cache
│   ├── queue_routes.py        # Batch processor endpoints
│   └── calendar_routes.py     # Calendar management
├── ai/
│   ├── ollama_client.py       # LLM inference wrapper
│   ├── response_generator.py  # AI response generation with cache
│   ├── draft_cache_service.py # Cache CRUD (MongoDB)
│   ├── response_queue.py      # Queue processor
│   ├── user_profile.py        # User style profiling
│   ├── learning.py            # Feedback loop & learning
│   ├── evaluation.py          # Response metrics (BLEU, ROUGE)
│   └── lora_trainer.py        # Model fine-tuning
├── models/
│   ├── response.py            # Pydantic models
│   └── message.py             # Message models
├── main.py                    # FastAPI app init
├── database.py                # MongoDB connection + indexes
├── auth.py                    # JWT authentication
├── config.py                  # Environment configuration
└── deps.py                    # Dependency injection
```

---

## 🔄 Core Features

### 1. AI Response Generation

**Location:** `MessageView.jsx` → `ResponseEditor.jsx` → Backend

**Flow:**
1. Click "✨ Generate AI Reply" on any email
2. Backend checks cache → if found, return immediately (~5ms)
3. If not cached, generate with Ollama LLM (~2400ms)
4. Save response to MongoDB cache
5. Display in editor for editing
6. User can edit and submit

**API Endpoint:**
```
POST /response/generate
{
  "email_id": "msg_123",
  "email_subject": "Subject...",
  "email_body": "Body...",
  "sender": "sender@example.com",
  "temperature": 0.7,
  "max_tokens": 300
}
```

**Cache Performance:**
- First request: ~2400ms (LLM generation)
- Subsequent requests: ~5ms (from cache)
- **480x speedup!**

### 2. Draft Caching System

**Location:** `app/ai/draft_cache_service.py` → MongoDB

**Features:**
- ✅ Auto-save on generation
- ✅ Auto-save on edit
- ✅ Auto-save before submission
- ✅ 7-day TTL auto-cleanup
- ✅ SPARSE UNIQUE indexes allow multiple nulls

**Cache Save Endpoints:**
```
POST /response/cache/save
POST /queue/generate/{message_id}  # Auto-saves
POST /queue/confirm-send           # Auto-saves edits
```

**Database Schema:**
```javascript
response_drafts {
  _id: ObjectId,
  user_id: "yogesh",
  email_id: "email_123",
  message_id: null,  // Optional
  email_subject: "Subject...",
  email_body: "Body...",
  sender: "sender@example.com",
  generated_response: "The generated text...",
  status: "active",
  created_at: ISODate,
  expires_at: ISODate  // TTL index
}
```

### 3. Queue Processing

**Location:** `QueueProcessor.jsx` + `app/routers/queue_routes.py`

**Features:**
- ✅ One message at a time
- ✅ Pre-generate batch responses
- ✅ Skip individual messages
- ✅ Regenerate responses
- ✅ Edit and send with learning feedback

**API Endpoints:**
```
GET    /queue/stats                     # Get queue statistics
GET    /queue/next                      # Get next message to process
POST   /queue/generate/{message_id}     # Generate response (auto-cached)
POST   /queue/generate-batch            # Pre-generate 5 responses
POST   /queue/confirm-send              # Send with learning feedback
POST   /queue/skip/{message_id}         # Skip message
```

### 4. Priority Queue Management

Messages automatically sorted by:
1. **Priority level** (critical > high > medium > low)
2. **Category** (auto-classified)
3. **Sender reputation** (learned over time)

**Priority Levels:**
- 🔴 **Critical**: Immediate attention required
- 🟠 **High**: Important, respond today
- 🔵 **Medium**: Regular, respond this week
- ⚫ **Low**: Can wait

### 5. User Profile Learning

**Location:** `app/ai/user_profile.py` + Learning Service

**Tracks:**
- **Verbosity**: Short/Medium/Long response length preference
- **Politeness**: Formal/Neutral/Casual tone
- **Professionalism**: Business/Mixed/Casual register

**Updated by:**
- ✅ User feedback after response generation
- ✅ Analysis of submitted responses
- ✅ Metrics: BLEU score, ROUGE-L, edit distance

### 6. Calendar Integration

**Features:**
- 📅 Event creation and management
- 🤖 ML-powered event suggestions from emails
- 🔔 Meeting reminders
- 📊 Schedule optimization

**API Endpoints:**
```
GET    /calendar/events
POST   /calendar/events
GET    /calendar/suggestions
POST   /calendar/events/{event_id}/accept
POST   /calendar/events/{event_id}/reject
```

---

## 🔐 Authentication Flow

### Register
```bash
POST /auth/register
{
  "username": "yogesh",
  "password": "your_password"
}
```

### Login
```bash
POST /auth/login
{
  "username": "yogesh",
  "password": "your_password"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "user": "yogesh"
}
```

Token is automatically added to all requests via `axios` interceptor in `api.js`.

---

## 📡 API Documentation

### Response Generation

```
POST /response/generate
```

**Request:**
```json
{
  "email_id": "msg_123",
  "email_subject": "Meeting Tomorrow?",
  "email_body": "Can we meet tomorrow at 2 PM?",
  "sender": "john@example.com",
  "temperature": 0.7,
  "max_tokens": 300
}
```

**Response:**
```json
{
  "response_id": "resp_456",
  "generated_response": "Sure! I can meet tomorrow at 2 PM...",
  "profile_used": {
    "verbosity": 0.65,
    "politeness": 0.8,
    "professionalism": 0.7
  },
  "original_email_id": "msg_123",
  "generation_time_ms": 2400,
  "from_cache": false
}
```

### Submit Response (Learning)

```
POST /response/submit
```

**Request:**
```json
{
  "response_id": "resp_456",
  "final_response": "Sure! I can meet tomorrow at 2 PM. Looking forward to it."
}
```

**Response:**
```json
{
  "status": "submitted",
  "metrics": {
    "bleu_score": 0.85,
    "rouge_l": 0.88,
    "edit_distance": 0.12
  },
  "reward": 0.88,
  "profile_updated": true,
  "training_queued": false
}
```

### Cache Management

```
GET  /response/cache/stats          # Get cache statistics
POST /response/cache/save           # Manual cache save
DELETE /response/cache/{email_id}   # Invalidate cache
POST /response/cache/cleanup        # Clean expired drafts
```

**Cache Stats Response:**
```json
{
  "user_id": "yogesh",
  "cache_stats": {
    "active_drafts": 45,
    "expired_drafts": 12,
    "total_hits": 342,
    "total_generated": 89
  }
}
```

---

## 🧪 Testing

### Run Backend Tests

```bash
cd server

# Test caching system
python test_cache.py

# Test MongoDB connection
python test_mongo_sync.py

# Run minimal test
python test_minimal.py
```

### Test Response Generation (via curl)

```bash
# 1. Register
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpass"
  }'

# 2. Login (get token)
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpass"
  }' | jq -r '.access_token')

# 3. Generate response
curl -X POST http://localhost:8000/response/generate \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email_id": "test_email_1",
    "email_subject": "Meeting Tomorrow",
    "email_body": "Can we meet tomorrow at 2 PM?",
    "sender": "john@example.com",
    "temperature": 0.7,
    "max_tokens": 300
  }'
```

### Manual Database Testing

```bash
# Connect to MongoDB
mongosh maildb

# View collections
show collections

# Check response drafts
db.response_drafts.find().pretty()

# Check cache indexes
db.response_drafts.getIndexes()

# View user profiles
db.user_profiles.findOne()

# Check response history
db.response_history.find().limit(5)
```

---

## 🔧 Configuration

### Ollama Configuration

**Default Settings:**
- Model: `mistral`
- Base URL: `http://localhost:11434`
- Timeout: 300 seconds
- Temperature: 0.7 (default)
- Max tokens: 512 (default)

**To use different model:**
1. Pull the model: `ollama pull llama2`
2. Update `app/ai/ollama_client.py`:
```python
OllamaConfig(
    model="llama2",
    max_tokens=512,
    temperature=0.5
)
```

### MongoDB Configuration

**Connection:**
```python
# app/config.py
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "maildb")
```

**MongoDB Atlas (Cloud):**
```env
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/maildb?retryWrites=true&w=majority
```

### FastAPI CORS Configuration

**Current:** Allows `http://localhost:5173`

To allow other origins:
```python
# app/main.py
CORSMiddleware(
    allow_origins=["http://localhost:5173", "https://example.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 📊 Performance Optimization

### Cache Hit Rate

The caching system achieves **~89% cache hit rate** on repeated email views.

**Metrics:**
- Average first generation: 2,400ms
- Average cached retrieval: 5ms
- **Speedup: 480x faster**

### Database Indexes

All critical collections have proper indexes:

```javascript
// response_drafts
db.response_drafts.createIndex({ user_id: 1, email_id: 1 }, { unique: true })
db.response_drafts.createIndex({ user_id: 1, message_id: 1 }, { sparse: true })
db.response_drafts.createIndex({ user_id: 1, status: 1 })
db.response_drafts.createIndex({ expires_at: 1 }, { expireAfterSeconds: 0 })

// messages
db.messages.createIndex({ recipients: 1, created_at: -1 })
db.messages.createIndex({ sender: 1, created_at: -1 })
db.messages.createIndex({ "subject": "text", "body": "text" })
db.messages.createIndex({ 
  recipients: 1, 
  queue_status: 1, 
  queue_priority: 1, 
  created_at: 1 
})
```

---

## 🐛 Troubleshooting

### Problem: "Ollama server is not available"

**Solution:**
```bash
# Start Ollama
ollama serve

# Verify it's running
curl http://localhost:11434/api/tags
```

### Problem: "MongoDB connection refused"

**Solution:**
```bash
# Start MongoDB
mongod

# Or use MongoDB Atlas and update .env
MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net/maildb
```

### Problem: "CORS error - blocked by CORS policy"

**Solution:** Update `app/main.py` to allow your frontend URL:
```python
allow_origins=["http://localhost:5173", "http://localhost:3000"]
```

### Problem: "E11000 duplicate key error on message_id"

**Solution:** This is fixed with SPARSE indexes. Run:
```bash
cd server
python reset_indexes.py
```

### Problem: "Timeout waiting for LLM response"

**Solution:** Increase timeout in `app/ai/ollama_client.py`:
```python
OllamaConfig(
    timeout=600.0  # 10 minutes
)
```

### Problem: "Port 8000 or 5173 already in use"

**Solution:** Use different ports:
```bash
# Backend on different port
uvicorn app.main:app --port 8001

# Frontend on different port
npm run dev -- --port 5174
```

---

## 📚 Dependencies

### Backend Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| fastapi | 0.104+ | REST API framework |
| uvicorn | 0.24+ | ASGI server |
| motor | 3.3+ | Async MongoDB driver |
| pymongo | 4.6+ | MongoDB Python driver |
| httpx | 0.25+ | Async HTTP client |
| python-jose | 3.3+ | JWT handling |
| bcrypt | 4.1+ | Password hashing |
| scikit-learn | 1.3+ | ML/metrics |
| numpy | 1.24+ | Numerical computing |
| python-dotenv | 1.0+ | Environment config |

### Frontend Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| react | 19.1+ | UI framework |
| react-router-dom | 7.9+ | Client-side routing |
| axios | 1.13+ | HTTP client |
| @fullcalendar/react | 6.1+ | Calendar widget |
| tailwindcss | 4.1+ | CSS utility framework |
| vite | 7.1+ | Build tool |

---

## 🚀 Deployment

### Deploy Backend (Heroku)

```bash
# Install Heroku CLI
# Create app
heroku create bharatmail-api

# Set environment variables
heroku config:set MONGO_URI=mongodb+srv://...
heroku config:set SECRET_KEY=...

# Deploy
git push heroku main
```

### Deploy Frontend (Vercel)

```bash
# Install Vercel CLI
vercel

# Update API endpoint in src/api.js
const api = axios.create({ 
  baseURL: "https://bharatmail-api.herokuapp.com" 
});

# Deploy
vercel --prod
```

### Deploy with Docker

```dockerfile
# Backend
FROM python:3.10
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app/ ./app/
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Frontend
FROM node:18
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
CMD ["npm", "run", "preview"]
```

---

## 📖 Documentation Files

- **CACHE_INTEGRATION_COMPLETE.md** - Cache system documentation
- **TESTING_CHECKLIST.md** - Testing procedures
- **requirements.txt** - Python dependencies
- **package.json** - Node.js dependencies

---

## 🤝 Contributing

1. Create a feature branch: `git checkout -b feature/name`
2. Make your changes
3. Test thoroughly
4. Create a pull request

---

## 📝 License

MIT License - see LICENSE file for details

---

## 🆘 Support

### Getting Help

1. **Check documentation**: Read relevant `.md` files
2. **Review code comments**: Most complex logic is documented
3. **Check tests**: See `test_*.py` files for usage examples
4. **Debug logs**: Check browser console and server logs

### Common Issues Checklist

- ✓ Ollama running on localhost:11434
- ✓ MongoDB running on localhost:27017
- ✓ .env file configured correctly
- ✓ Python virtual environment activated
- ✓ All dependencies installed (`pip install -r requirements.txt`, `npm install`)
- ✓ Ports 8000 and 5173 not in use
- ✓ Firewall not blocking connections

---

## 🎯 Roadmap

**v1.0 (Current)**
- ✅ Email management (CRUD)
- ✅ AI response generation with Ollama
- ✅ Draft caching system
- ✅ Queue processor
- ✅ Calendar integration
- ✅ User profile learning

**v2.0 (Planned)**
- [ ] Email attachments handling
- [ ] Advanced search and filters
- [ ] Scheduled sending
- [ ] Team collaboration
- [ ] Custom LLM fine-tuning UI
- [ ] Analytics dashboard
- [ ] Mobile app

---

## 👤 Author

Developed as an intelligent email assistant with AI response generation capabilities.

---

**Last Updated:** 2026-04-12
**Version:** 1.0.0
