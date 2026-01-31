# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Full-stack application template with React frontend and FastAPI backend, featuring an AI Developer Workflow (ADW) system for automated issue processing.

**Deployment:**
- Frontend: Vercel (`apps/Client`)
- Backend: Render (`apps/Server`)
- Database: Supabase PostgreSQL (direct connection, NO Supabase Auth)

## Development Commands

### Frontend

```bash
cd apps/Client
npm install
npm run dev          # Dev server (http://localhost:5173)
npm run build        # Production build
npm run lint         # ESLint
npm run typecheck    # TypeScript check
```

### Backend

```bash
cd apps/Server
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Testing and linting
.venv/bin/pytest tests/ -v --tb=short
.venv/bin/ruff check .
```

### Key URLs
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000/api
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/api/health

### WSL2 Environment

Both servers must bind to `0.0.0.0` for Windows browser access:
- Backend: `--host 0.0.0.0`
- Frontend: `npm run dev -- --host 0.0.0.0`

## Slash Commands

Key development commands available via Claude Code:

- `/start` - Start frontend and backend servers
- `/install` - Install dependencies and set up environment
- `/test` - Run comprehensive test suite (static analysis, unit tests, builds)
- `/test_api` - Run API integration tests
- `/test_e2e` - Run end-to-end tests
- `/commit` - Generate and create git commit
- `/pull_request` - Create GitHub pull request
- `/review` - Review code changes
- `/feature`, `/bug`, `/chore`, `/patch` - Planning commands for different issue types

## ADW System (AI Developer Workflow)

Automated development system using isolated git worktrees. ADW workflows run Claude Code agents to process GitHub issues autonomously.

### Quick ADW Commands

```bash
cd adws/

# Process a single issue (plan + build)
uv run adw_plan_build_iso.py <issue-number>

# With testing
uv run adw_plan_build_test_iso.py <issue-number>

# Complete SDLC workflow
uv run adw_sdlc_iso.py <issue-number>

# Zero-Touch Execution (auto-merge to main)
uv run adw_sdlc_zte_iso.py <issue-number>
```

### ADW Architecture

- Isolated worktrees at `trees/<adw_id>/` with dedicated ports
- State files at `agents/<adw_id>/adw_state.json`
- Port ranges: backend 9100-9114, frontend 9200-9214
- Supports up to 15 concurrent workflows

See `adws/README.md` for full documentation.

## Architecture

### Clean Architecture Layers

```
Frontend:  pages/ → components/ → hooks/ → services/ → api/
           (UI)     (Reusable)   (State)   (Logic)    (HTTP)

Backend:   api/ → services/ → repository/ → database
           (Routes) (Business Logic) (Data Access)
```

### Entry Points
- Frontend: `apps/Client/src/main.tsx`
- Backend: `apps/Server/main.py`

### Technology Stack

**Frontend:** React 19, TypeScript 5, Vite 5, Material-UI 5, React Router 6, react-hook-form, Axios

**Backend:** Python 3.11.9 (required for Render), FastAPI 0.104+, Pydantic 2, psycopg2, python-jose (JWT), passlib/bcrypt

## Authentication

Custom JWT with role-based access control (NO Supabase Auth).

### JWT Flow
1. POST `/api/auth/login` with credentials
2. Backend validates against users table (bcrypt)
3. Returns JWT token
4. Frontend stores in localStorage
5. All requests include `Authorization: Bearer <token>`

### Roles
- `admin`: Full access, user management
- `manager`: Full operational access
- `user`: Standard access
- `viewer`: Read-only

### Backend Auth Pattern

```python
from app.api.dependencies import get_current_user
from app.api.rbac_dependencies import require_roles

@router.get("/items")
async def get_items(current_user: dict = Depends(get_current_user)):
    pass

@router.delete("/items/{id}")
async def delete_item(current_user: dict = Depends(require_roles(['admin', 'manager']))):
    pass
```

### Frontend Auth Pattern

```typescript
const { user, isAuthenticated, login, logout } = useAuth();

<ProtectedRoute><DashboardPage /></ProtectedRoute>
<RoleProtectedRoute allowedRoles={['admin']}><AdminPage /></RoleProtectedRoute>
```

## Code Standards

- **TypeScript**: No `any` types, use `@/` path alias
- **Python**: Type hints on all functions, docstrings for public APIs
- **Forms**: Always use react-hook-form with Material-UI
- **Logging**: Use `print(f"INFO [ServiceName]: ...")` (Python) or `console.log(\`INFO [ComponentName]: ...\`)` (TypeScript)
- **File size**: Soft limit of 1000 lines per file

## Environment Variables

### Frontend (.env)
```bash
VITE_API_URL=http://localhost:8000/api
VITE_APP_NAME=Your App Name
```

### Backend (.env)
```bash
DATABASE_URL=postgresql://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:5432/postgres
JWT_SECRET_KEY=your-secret-key-min-32-chars
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440
CORS_ORIGINS=["http://localhost:5173"]
PYTHON_VERSION=3.11.9
```

### ADW System
```bash
CLAUDE_CODE_PATH=claude
ANTHROPIC_API_KEY=  # Optional if using Claude Max via OAuth
GITHUB_PAT=         # Optional if using default gh auth
```

## Deployment

### Vercel (Frontend)
- Root Directory: `apps/Client`
- Build Command: `npm run build`
- Output Directory: `dist`

### Render (Backend)
- Root Directory: `apps/Server`
- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- **CRITICAL**: Set `PYTHON_VERSION=3.11.9` in environment

### CORS Configuration
Must be JSON array format:
```bash
CORS_ORIGINS=["http://localhost:5173","https://your-app.vercel.app"]
```
