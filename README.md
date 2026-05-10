# 📸 PhotoShare — Scalable Cloud-Native Photo Platform
### COM769 Coursework 2 | Ulster University / QAHE

> A scalable, cloud-native photo sharing web application built with **FastAPI** + **React 18** + **Azure** services.  
> Conceptually similar to Instagram — creators upload, consumers discover.

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Browser                          │
│              React 18 + Vite SPA (Tailwind CSS)                 │
└────────────────────────┬────────────────────────────────────────┘
                         │ REST API calls (JSON)
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              Azure App Service (PaaS)                           │
│              FastAPI (Python 3.11) + Uvicorn                    │
│   ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐  │
│   │  /auth   │ │ /photos  │ │/comments │ │ /ratings /search │  │
│   └──────────┘ └──────────┘ └──────────┘ └──────────────────┘  │
└──────┬──────────────┬──────────────────────────────────────────-┘
       │              │
       ▼              ▼
┌──────────────┐  ┌──────────────────────────────────────────────┐
│  Azure SQL   │  │          Azure Blob Storage                  │
│  Database    │  │  Container: photos  |  Container: thumbnails │
│  (Relational)│  └──────────────────────────────────────────────┘
└──────────────┘
       │
       ▼
┌──────────────────────────────────┐
│  Azure AI Vision + Language      │
│  (Image tags + Sentiment)        │
└──────────────────────────────────┘

CI/CD: GitHub Actions → Azure App Service
Source Control: GitHub (collaborative development)
```

---

## ✨ Features

### Core (Required)
- **Creator accounts** — upload photos with Title, Caption, Location, People tagged
- **Consumer accounts** — browse, search, comment, rate photos
- **Role-based access control** — JWT authentication with RBAC
- **Admin panel** — create/manage creator accounts, platform stats

### Advanced Features (for Distinction marks)
1. **Azure AI Computer Vision** — automatic image tag detection and description generation
2. **Azure Language Sentiment Analysis** — analyses comments for positive/negative/neutral sentiment
3. **CI/CD Pipeline** — GitHub Actions automatically tests and deploys on push to `main`
4. **JWT Identity Framework** — stateless authentication with role-based permissions
5. **Thumbnail generation** — Pillow auto-generates 400×400 thumbnails on upload

### Scalability
- **Azure App Service** (PaaS) — auto-scaling based on load, built-in load balancing
- **Azure Blob Storage** — virtually unlimited scalable media storage
- **Azure SQL Database** — managed, scalable relational DB with connection pooling
- **Stateless JWT** — tokens enable horizontal scaling without session state
- **SQLAlchemy connection pool** — `pool_size=10, max_overflow=20`
- **Docker support** — containerised deployment for Kubernetes/ACI

---

## 📁 Project Structure

```
photoshare/
├── backend/                    # FastAPI application
│   ├── main.py                 # App entry point + CORS
│   ├── config.py               # Pydantic settings (reads .env)
│   ├── database.py             # SQLAlchemy models + engine
│   ├── auth_utils.py           # JWT + password hashing
│   ├── schemas.py              # Pydantic request/response models
│   ├── storage_service.py      # Azure Blob / local filesystem
│   ├── ai_service.py           # Azure Vision + Sentiment
│   ├── static_files.py         # Serves React build in production
│   ├── startup.sh              # Azure App Service startup script
│   ├── Dockerfile              # Container image
│   ├── requirements.txt        # Python dependencies
│   ├── tests.py                # Automated test suite (pytest)
│   ├── .env.example            # Environment variable template
│   └── routers/
│       ├── auth.py             # /api/auth — login, register, me
│       ├── photos.py           # /api/photos — CRUD + upload
│       ├── comments.py         # /api/comments — with sentiment
│       ├── ratings.py          # /api/ratings — 1-5 star system
│       ├── search.py           # /api/search — full-text search
│       ├── users.py            # /api/users — profiles
│       └── admin.py            # /api/admin — creator mgmt + stats
│
├── frontend/                   # React 18 + Vite application
│   ├── src/
│   │   ├── App.jsx             # Router
│   │   ├── main.jsx            # Entry point
│   │   ├── index.css           # Global styles + dark theme
│   │   ├── components/
│   │   │   ├── Navbar.jsx
│   │   │   ├── PhotoCard.jsx
│   │   │   └── StarRating.jsx
│   │   ├── pages/
│   │   │   ├── Home.jsx        # Consumer view — photo grid
│   │   │   ├── Login.jsx
│   │   │   ├── Register.jsx
│   │   │   ├── PhotoDetail.jsx # Comments, ratings, AI tags
│   │   │   ├── Upload.jsx      # Drag-and-drop upload (creator)
│   │   │   ├── CreatorDashboard.jsx
│   │   │   ├── AdminDashboard.jsx
│   │   │   └── SearchResults.jsx
│   │   ├── store/
│   │   │   └── authStore.js    # Zustand auth state
│   │   └── utils/
│   │       └── api.js          # Axios client + all API calls
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
│
├── .github/
│   └── workflows/
│       └── ci-cd.yml           # GitHub Actions CI/CD pipeline
├── docker-compose.yml          # Local Docker development
└── README.md
```

---

## 🚀 Quick Start — Local Development

### Prerequisites
- Python 3.11+
- Node.js 20+
- Git

### Step 1 — Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/photoshare.git
cd photoshare
```

### Step 2 — Backend setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate it:
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies (core only for local dev — skips Azure SDKs)
pip install fastapi uvicorn sqlalchemy pydantic pydantic-settings \
            python-jose[cryptography] passlib[bcrypt] python-multipart \
            pillow python-dotenv pytest httpx pytest-asyncio \
            "pydantic[email]"

# OR install everything including Azure SDKs:
pip install -r requirements.txt

# Copy env template
cp .env.example .env
# The defaults work out of the box — uses SQLite + local file storage
```

### Step 3 — Start the backend

```bash
# Still in backend/ with venv activated
python main.py
```

You should see:
```
✅ Database tables created successfully
⚠️  Using local filesystem storage (Azure not configured)
⚠️  Azure AI Vision not configured — analysis disabled
INFO:     Uvicorn running on http://0.0.0.0:8000
```

The **API docs** are now at: http://localhost:8000/docs

### Step 4 — Seed the admin account

Open a new terminal or use curl / the docs UI:

```bash
curl -X POST http://localhost:8000/api/admin/seed
```

Response: `{"message":"Admin account created","username":"admin","password":"Admin@1234"}`

### Step 5 — Frontend setup

```bash
cd ../frontend

# Install dependencies
npm install

# Start the dev server (proxies /api calls to localhost:8000)
npm run dev
```

Open **http://localhost:5173** in your browser.

---

## 👤 User Accounts & Roles

| Role | How to create | Capabilities |
|------|--------------|-------------|
| **Admin** | `POST /api/admin/seed` | Everything; create creators |
| **Creator** | Admin creates via Admin Dashboard or API | Upload photos, manage own photos |
| **Consumer** | Self-register at `/register` | Browse, search, comment, rate |

### Default accounts after seeding:
- Admin: `admin` / `Admin@1234`

### Creating a creator (as admin):
1. Log in as admin → go to `/admin`
2. Click **New Creator** → fill in the form

---

## 🧪 Running Tests

```bash
cd backend
# Activate venv first

# Run all tests
pytest tests.py -v

# Run a specific test class
pytest tests.py::TestAuth -v
pytest tests.py::TestPhotos -v
pytest tests.py::TestComments -v
pytest tests.py::TestRatings -v
pytest tests.py::TestSearch -v
```

Expected output: **23 tests passing**

---

## 🐳 Docker (Local)

```bash
# From project root — starts both backend and frontend
docker-compose up --build

# Backend: http://localhost:8000
# Frontend: http://localhost:5173
# API docs: http://localhost:8000/docs
```

---

## ☁️ Azure Deployment (Step-by-Step)

### Prerequisites
- Azure account (free tier works)
- Azure CLI installed: `az login`

### Step 1 — Create Azure resources

```bash
# Set variables
RESOURCE_GROUP="photoshare-rg"
LOCATION="uksouth"
APP_NAME="photoshare-app-$(date +%s)"  # must be globally unique
STORAGE_ACCOUNT="photosharestorage$(date +%s | tail -c 5)"
SQL_SERVER="photoshare-sql-$(date +%s)"
SQL_DB="photoshare"

# Create resource group
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create Azure App Service plan (free tier)
az appservice plan create \
  --name photoshare-plan \
  --resource-group $RESOURCE_GROUP \
  --sku B1 \
  --is-linux

# Create Web App
az webapp create \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --plan photoshare-plan \
  --runtime "PYTHON|3.11"

# Create Storage Account
az storage account create \
  --name $STORAGE_ACCOUNT \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --sku Standard_LRS

# Create blob containers
az storage container create --name photos --account-name $STORAGE_ACCOUNT --public-access blob
az storage container create --name thumbnails --account-name $STORAGE_ACCOUNT --public-access blob

# Get storage connection string (save this!)
az storage account show-connection-string \
  --name $STORAGE_ACCOUNT \
  --resource-group $RESOURCE_GROUP \
  --query connectionString -o tsv
```

### Step 2 — Create Azure SQL Database (optional, SQLite works too)

```bash
SQL_ADMIN_USER="photoshare_admin"
SQL_ADMIN_PASS="YourStr0ngP@ssword!"

az sql server create \
  --name $SQL_SERVER \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --admin-user $SQL_ADMIN_USER \
  --admin-password $SQL_ADMIN_PASS

az sql db create \
  --name $SQL_DB \
  --server $SQL_SERVER \
  --resource-group $RESOURCE_GROUP \
  --service-objective Basic

# Allow Azure services to access SQL
az sql server firewall-rule create \
  --name AllowAzureServices \
  --server $SQL_SERVER \
  --resource-group $RESOURCE_GROUP \
  --start-ip-address 0.0.0.0 \
  --end-ip-address 0.0.0.0
```

### Step 3 — Configure App Service environment variables

```bash
az webapp config appsettings set \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --settings \
    SECRET_KEY="your-very-long-random-secret-key-here" \
    DEBUG="false" \
    AZURE_STORAGE_CONNECTION_STRING="<paste connection string from Step 1>" \
    AZURE_SQL_SERVER="$SQL_SERVER.database.windows.net" \
    AZURE_SQL_DATABASE="$SQL_DB" \
    AZURE_SQL_USERNAME="$SQL_ADMIN_USER" \
    AZURE_SQL_PASSWORD="$SQL_ADMIN_PASS" \
    SCM_DO_BUILD_DURING_DEPLOYMENT="true"
```

### Step 4 — Build frontend and package with backend

```bash
# Build React app
cd frontend
npm install
npm run build

# Copy built files to backend static folder
cp -r dist ../backend/static

cd ../backend
```

### Step 5 — Deploy to Azure

```bash
# Option A: ZIP deploy (simplest)
cd backend
zip -r ../deploy.zip . -x "venv/*" -x "__pycache__/*" -x "*.pyc" -x "test*.db"
az webapp deployment source config-zip \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --src ../deploy.zip

# Set startup command
az webapp config set \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --startup-file "bash startup.sh"
```

### Step 6 — Seed admin and verify

```bash
APP_URL="https://$APP_NAME.azurewebsites.net"
echo "App URL: $APP_URL"

# Seed admin account
curl -X POST "$APP_URL/api/admin/seed"

# Health check
curl "$APP_URL/api/health"
```

### Step 7 — Optional: Azure AI Vision

```bash
# Create Cognitive Services resource
az cognitiveservices account create \
  --name photoshare-vision \
  --resource-group $RESOURCE_GROUP \
  --kind ComputerVision \
  --sku F0 \
  --location $LOCATION

# Get key and endpoint
az cognitiveservices account keys list \
  --name photoshare-vision \
  --resource-group $RESOURCE_GROUP

az cognitiveservices account show \
  --name photoshare-vision \
  --resource-group $RESOURCE_GROUP \
  --query "properties.endpoint" -o tsv

# Add to App Service settings
az webapp config appsettings set \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --settings \
    AZURE_VISION_KEY="<your-key>" \
    AZURE_VISION_ENDPOINT="<your-endpoint>"
```

---

## 🔄 CI/CD Pipeline (GitHub Actions)

The pipeline in `.github/workflows/ci-cd.yml` automatically:
1. **On every push/PR**: runs pytest backend tests
2. **On every push**: builds the React frontend  
3. **On push to `main`**: deploys to Azure App Service

### Setup:
1. Push code to GitHub
2. In GitHub repo → Settings → Secrets → add:
   - `AZURE_WEBAPP_PUBLISH_PROFILE` — download from Azure Portal (App Service → Get publish profile)
   - `ACR_LOGIN_SERVER`, `ACR_USERNAME`, `ACR_PASSWORD` — for Docker (optional)

---

## 📡 API Reference

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/api/auth/register` | — | Register consumer account |
| `POST` | `/api/auth/login` | — | Login, get JWT token |
| `GET` | `/api/auth/me` | ✓ | Current user profile |
| `GET` | `/api/photos` | — | List photos (paginated, sortable) |
| `POST` | `/api/photos/upload` | Creator | Upload photo + metadata |
| `GET` | `/api/photos/{id}` | — | Get photo (increments view count) |
| `PUT` | `/api/photos/{id}` | Creator | Update photo metadata |
| `DELETE` | `/api/photos/{id}` | Creator | Delete own photo |
| `GET` | `/api/photos/my` | Creator | List own photos |
| `GET` | `/api/comments/{photo_id}` | — | List comments |
| `POST` | `/api/comments/{photo_id}` | ✓ | Add comment (w/ sentiment) |
| `DELETE` | `/api/comments/{id}` | ✓ | Delete own comment |
| `POST` | `/api/ratings/{photo_id}` | ✓ | Rate photo (1-5 stars) |
| `GET` | `/api/search?q={query}` | — | Search photos |
| `POST` | `/api/admin/seed` | — | Create default admin (one-time) |
| `POST` | `/api/admin/creators` | Admin | Create creator account |
| `GET` | `/api/admin/users` | Admin | List all users |
| `GET` | `/api/admin/stats` | Admin | Platform statistics |
| `GET` | `/api/health` | — | Health check |

Interactive API docs: `http://localhost:8000/docs`

---

## 🔧 Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `SECRET_KEY` | Yes | JWT signing key (change in prod!) |
| `DATABASE_URL` | Dev only | SQLite URL (default: `sqlite:///./photoshare.db`) |
| `AZURE_SQL_SERVER` | Prod | Azure SQL server hostname |
| `AZURE_SQL_DATABASE` | Prod | Database name |
| `AZURE_SQL_USERNAME` | Prod | SQL admin username |
| `AZURE_SQL_PASSWORD` | Prod | SQL admin password |
| `AZURE_STORAGE_CONNECTION_STRING` | Prod | Blob storage connection string |
| `AZURE_VISION_KEY` | Optional | AI Vision API key |
| `AZURE_VISION_ENDPOINT` | Optional | AI Vision endpoint URL |
| `DEBUG` | — | `true` for dev, `false` for prod |

---

## 🛡️ Security Features

- **JWT tokens** — 7-day expiry, role embedded in payload
- **bcrypt password hashing** — industry standard (via Passlib)
- **RBAC** — every endpoint enforces creator/consumer/admin roles
- **SQL injection prevention** — SQLAlchemy ORM parameterised queries
- **File validation** — type and size checks on upload
- **CORS** — configured for production frontend URL
- **Non-root Docker user** — reduced attack surface

---

## 📊 Scalability Design Decisions

| Concern | Solution | Justification |
|---------|----------|--------------|
| Media storage | Azure Blob Storage | Virtually unlimited, geo-redundant, CDN-ready |
| Database | Azure SQL (managed) | Auto-backup, point-in-time restore, elastic scale |
| App hosting | Azure App Service | PaaS auto-scaling, zero infrastructure management |
| Stateless sessions | JWT tokens | Enables horizontal scaling — no sticky sessions |
| Image bandwidth | Thumbnail generation | 400×400px thumbnails reduce load by ~90% |
| Connection efficiency | SQLAlchemy pool (10+20) | Prevents connection exhaustion under load |
| Containerisation | Docker + compose | Enables Kubernetes/ACI deployment |
| Deployment | GitHub Actions CI/CD | Zero-downtime automated deployments |

---

## 🐛 Troubleshooting

**Backend won't start:**
```bash
# Make sure venv is active
source venv/bin/activate
# Check Python version
python --version  # needs 3.11+
```

**Frontend can't reach API:**
```bash
# Check vite.config.js proxy — backend must be on port 8000
# Check backend is running: curl http://localhost:8000/api/health
```

**Upload fails:**
```bash
# Check uploads/ directory exists
ls backend/uploads/photos/
# On Linux/Mac: mkdir -p backend/uploads/photos backend/uploads/thumbnails
```

**Azure deployment issues:**
```bash
# Check App Service logs
az webapp log tail --name $APP_NAME --resource-group $RESOURCE_GROUP
```

---

## 📚 References

1. Microsoft Corporation (2017) *Cloud Application Architecture Guide*. Microsoft Press. Available at: https://learn.microsoft.com/en-us/azure/architecture/
2. FastAPI Documentation (2024). Available at: https://fastapi.tiangolo.com/
3. Azure App Service Documentation (2024). Available at: https://docs.microsoft.com/azure/app-service/
4. Azure Blob Storage Documentation (2024). Available at: https://docs.microsoft.com/azure/storage/blobs/
5. Azure AI Vision Documentation (2024). Available at: https://learn.microsoft.com/en-us/azure/ai-services/computer-vision/
6. Caldato, C. (2020) *Cloud Native for the Enterprise*. O'Reilly Media.
7. Murphy, N., et al. (2016) *Site Reliability Engineering*. O'Reilly Media.
8. React Documentation (2024). Available at: https://react.dev/
9. SQLAlchemy Documentation (2024). Available at: https://docs.sqlalchemy.org/

---

*COM769 Scalable Advanced Software Systems — Ulster University / QAHE*
