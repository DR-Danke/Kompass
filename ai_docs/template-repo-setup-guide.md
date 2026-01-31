# Template Repository Setup Guide

This guide documents all files needed to bootstrap a new repository with the Paqueteo/Tendery architecture, look/feel, and ADW (AI Developer Workflow) system.

---

## Table of Contents

1. [Overview](#1-overview)
2. [ADW System Files](#2-adw-system-files)
3. [Claude Commands](#3-claude-commands)
4. [Root Configuration Files](#4-root-configuration-files)
5. [Frontend Architecture](#5-frontend-architecture)
6. [Backend Architecture](#6-backend-architecture)
7. [Database Structure](#7-database-structure)
8. [Empty Directories to Preserve](#8-empty-directories-to-preserve)
9. [File Counts Summary](#9-file-counts-summary)
10. [Quick Start Checklist](#10-quick-start-checklist)
11. [Customization Guide](#11-customization-guide)

---

## 1. Overview

### Purpose
Create new full-stack projects with:
- **Clean Architecture** - Layered separation (routes → services → repositories → database)
- **SOLID Principles** - Single responsibility, dependency injection, interface segregation
- **ADW System** - AI Developer Workflow for automated issue processing
- **JWT Authentication** - Custom auth with role-based access control
- **React + FastAPI** - Modern frontend/backend stack

### Technology Stack

| Layer | Technology |
|-------|------------|
| Frontend | React 19, TypeScript 5, Vite 5, Material-UI 5 |
| Backend | Python 3.11, FastAPI, Pydantic 2 |
| Database | PostgreSQL (Supabase direct connection) |
| Auth | Custom JWT (python-jose, bcrypt) |
| Deployment | Vercel (frontend), Render (backend) |

### Architecture Principles

```
Frontend:  pages/ → components/ → hooks/ → services/ → api/
           (UI)     (Reusable)   (State)   (Logic)    (HTTP)

Backend:   api/ → services/ → repository/ → database
           (Routes) (Business Logic) (Data Access)
```

---

## 2. ADW System Files

The ADW (AI Developer Workflow) system enables automated issue processing through Claude Code CLI.

### 2.1 Core Modules (`adws/adw_modules/`) - 10 files

| File | Purpose | Keep As-Is |
|------|---------|------------|
| `__init__.py` | Package initialization | ✅ |
| `agent.py` | Claude Code CLI integration, slash command execution | ✅ |
| `data_types.py` | Pydantic models (GitHub API, ADW state, enums) | ✅ |
| `git_ops.py` | Git operations with worktree support | ✅ |
| `github.py` | GitHub API operations via `gh` CLI | ✅ |
| `state.py` | ADW workflow state persistence | ✅ |
| `utils.py` | Logger, JSON parsing, environment validation | ✅ |
| `workflow_ops.py` | Core workflow orchestration logic | ✅ |
| `worktree_ops.py` | Isolated worktree and port management | ✅ |
| `r2_uploader.py` | Cloudflare R2 screenshot upload (optional) | ✅ |

### 2.2 Workflow Scripts (`adws/`) - 15 files

#### Entry Point Workflows (Create Worktrees)
| File | Purpose |
|------|---------|
| `adw_plan_iso.py` | Isolated planning: worktree → classify → plan → PR |
| `adw_patch_iso.py` | Quick patch workflow for 'adw_patch' keyword issues |

#### Dependent Workflows (Require Existing Worktree)
| File | Purpose |
|------|---------|
| `adw_build_iso.py` | Implementation phase in isolation |
| `adw_test_iso.py` | Testing phase with allocated ports |
| `adw_review_iso.py` | Review/validation with screenshots |
| `adw_document_iso.py` | Documentation generation |
| `adw_ship_iso.py` | PR approval and merge |

#### Orchestrator Workflows (Compose Multiple Phases)
| File | Purpose |
|------|---------|
| `adw_plan_build_iso.py` | Plan + Build |
| `adw_plan_build_test_iso.py` | Plan + Build + Test |
| `adw_plan_build_test_review_iso.py` | Plan + Build + Test + Review |
| `adw_plan_build_review_iso.py` | Plan + Build + Review (skip test) |
| `adw_plan_build_document_iso.py` | Plan + Build + Document |
| `adw_sdlc_iso.py` | Complete SDLC: Plan → Build → Test → Review → Document |
| `adw_sdlc_zte_iso.py` | Zero-Touch Execution: SDLC + auto-merge |

### 2.3 Triggers (`adws/adw_triggers/`) - 3 files

| File | Purpose |
|------|---------|
| `__init__.py` | Package initialization |
| `trigger_cron.py` | Polling-based trigger (20-second interval) |
| `trigger_webhook.py` | FastAPI webhook server for GitHub events |

### 2.4 Documentation

| File | Purpose |
|------|---------|
| `adws/README.md` | Comprehensive ADW system documentation (~780 lines) |

---

## 3. Claude Commands

### 3.1 Essential Commands (`.claude/commands/`) - 28 files

#### SDLC Planning (4 files)
```
bug.md           - Create bug fix plans
feature.md       - Create feature implementation plans
chore.md         - Create chore/refactoring plans
patch.md         - Create patch/hotfix plans
```

#### Classification (2 files)
```
classify_issue.md  - Classify incoming issues by type
classify_adw.md    - Classify with ADW ID assignment
```

#### Implementation (2 files)
```
implement.md       - Implementation task runner
prime.md           - Prime/initialize codebase understanding
```

#### Testing (7 files)
```
test.md                  - Run validation test suite
test_api.md              - Run backend API tests
test_e2e.md              - Run E2E tests with Playwright
test_static.md           - Static analysis, linting, type checking
smoke_test.md            - Quick smoke tests
resolve_failed_test.md   - Resolve failed tests
resolve_failed_e2e_test.md - Resolve failed E2E tests
```

#### Documentation (3 files)
```
document.md          - Generate feature documentation
review.md            - Review work against specs
conditional_docs.md  - Documentation routing (CRITICAL - customize for your project)
```

#### Git Operations (7 files)
```
commit.md              - Generate formatted git commits
pull_request.md        - Create pull requests
new_branch.md          - Create new feature branches
generate_branch_name.md - Generate branch names from issue info
checkout_main.md       - Switch to main branch
cleanup_worktrees.md   - Clean up git worktrees
install_worktree.md    - Install new git worktrees
```

#### Environment (3 files)
```
start.md        - Start development environment
install.md      - Install dependencies
prepare_app.md  - Prepare app for development
tools.md        - List available tools
```

### 3.2 Files to Remove (Project-Specific)

```
.claude/commands/e2e/              - All E2E test commands (~52 files)
.claude/commands/e2e/e2e_onhold/   - On-hold E2E tests (~34 files)
health_check.md                    - Project-specific health check
track_agentic_kpis.md              - Project KPI tracking
in_loop_review.md                  - Custom review loop
Merge_Iso.md                       - Isolated merge feature
```

---

## 4. Root Configuration Files

### 4.1 Keep As-Is

| File | Purpose |
|------|---------|
| `.mcp.json` | MCP server configuration |
| `playwright-mcp-config.json` | Playwright settings |
| `.gitignore` | Git ignore patterns |

### 4.2 Create from Template

#### `.env.sample`
```bash
# Database (Supabase PostgreSQL direct connection)
DATABASE_URL=postgresql://postgres.[project-ref]:[password]@[host]:5432/postgres

# JWT Authentication
JWT_SECRET_KEY=your-secret-key-min-32-chars
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440

# CORS
CORS_ORIGINS=["http://localhost:5173","http://localhost:8000"]

# Server
SERVER_PORT=8000
USE_MOCK_APIS=true
```

### 4.3 Customize for New Project

#### `CLAUDE.md` - Update These Sections
- Project Overview (name, description, components)
- Key URLs
- Environment variables
- Database tables
- Component naming prefix (PQ → your prefix)

#### `README.md`
- Replace with new project documentation

---

## 5. Frontend Architecture

### 5.1 Infrastructure (Keep As-Is)

| File | Purpose |
|------|---------|
| `package.json` | Dependencies and scripts |
| `vite.config.js` | Vite configuration with `@/` alias |
| `tsconfig.json` | TypeScript configuration (strict mode) |
| `tsconfig.node.json` | Node TypeScript config |
| `index.html` | Entry HTML (update title) |
| `.eslintrc.cjs` | ESLint configuration |
| `vercel.json` | Deployment configuration |

### 5.2 Core Files (Keep As-Is)

#### API Client (`src/api/clients/index.ts`)
```typescript
// Axios client with JWT interceptor
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api',
  headers: { 'Content-Type': 'application/json' },
});

// Request interceptor: adds Bearer token
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor: handles 401
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);
```

#### Auth Types (`src/types/auth.ts`)
```typescript
export interface User {
  id: string;
  email: string;
  first_name?: string;
  last_name?: string;
  role: 'admin' | 'manager' | 'user' | 'viewer';
  is_active: boolean;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => void;
}
```

#### Auth Context (`src/contexts/AuthContext.tsx`)
```typescript
export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'));
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const validateToken = async () => {
      if (token) {
        try {
          const currentUser = await authService.getCurrentUser();
          setUser(currentUser);
        } catch {
          localStorage.removeItem('token');
          setToken(null);
        }
      }
      setIsLoading(false);
    };
    validateToken();
  }, []);

  const login = async (credentials: LoginCredentials) => {
    const response = await authService.login(credentials);
    localStorage.setItem('token', response.access_token);
    setToken(response.access_token);
    setUser(response.user);
  };

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, token, isAuthenticated: !!token && !!user, isLoading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};
```

#### Protected Route (`src/components/auth/ProtectedRoute.tsx`)
```typescript
export const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();
  const location = useLocation();

  if (isLoading) return <CircularProgress />;
  if (!isAuthenticated) return <Navigate to="/login" state={{ from: location }} replace />;

  return <>{children}</>;
};
```

#### Role Protected Route (`src/components/auth/RoleProtectedRoute.tsx`)
```typescript
interface RoleProtectedRouteProps {
  children: React.ReactNode;
  allowedRoles: string[];
}

export const RoleProtectedRoute: React.FC<RoleProtectedRouteProps> = ({ children, allowedRoles }) => {
  const { user, isAuthenticated, isLoading } = useAuth();

  if (isLoading) return <CircularProgress />;
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  if (!user || !allowedRoles.includes(user.role)) {
    return <AccessDeniedPage userRole={user?.role} />;
  }

  return <>{children}</>;
};
```

### 5.3 Keep Structure, Simplify Content

| File | Action |
|------|--------|
| `src/main.tsx` | Keep provider pattern, remove app-specific providers |
| `src/App.tsx` | Keep routing structure, empty routes |
| `src/theme/index.ts` | Keep createTheme, update colors/branding |
| `src/components/layout/PQMainLayout.tsx` | Keep layout structure, rename prefix |
| `src/components/layout/PQSidebar.tsx` | Keep structure, empty nav items |
| `src/hooks/useSidebarState.ts` | Keep as pattern example |

### 5.4 Remove (Application-Specific)

```
src/components/tendery/     - All TY-prefixed components
src/components/integrated/  - Paqueteo components
src/components/vehicle/     - Domain components
src/components/map/         - Domain components
src/pages/tendery/          - Tendery pages
src/services/tendery/       - Tendery services
src/hooks/tendery/          - Tendery hooks
src/types/tendery/          - Tendery types
src/contexts/VehicleContext.tsx - Domain contexts
```

---

## 6. Backend Architecture

### 6.1 Infrastructure (Keep As-Is)

#### `main.py` - FastAPI Setup
```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Database init, background tasks
    print("INFO [Main]: Starting application...")
    if settings.DATABASE_URL:
        init_database()
    yield
    # Shutdown: Cleanup
    print("INFO [Main]: Shutting down...")

def create_app() -> FastAPI:
    app = FastAPI(title="Your API", lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.get_cors_origins(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register routers
    app.include_router(health_router, prefix="/api")
    app.include_router(auth_router, prefix="/api/auth")

    return app

app = create_app()
```

#### `requirements.txt` - Core Dependencies
```
# Web Framework
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
pydantic>=2.0.0
pydantic-settings>=2.0.0

# Database
psycopg2-binary>=2.9.9

# Authentication
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
bcrypt>=4.0.0

# HTTP Client
httpx>=0.25.0

# Testing
pytest>=8.0.0
pytest-asyncio>=0.23.0
```

### 6.2 Configuration (`app/config/`)

#### `settings.py`
```python
from functools import lru_cache
from typing import List, Optional
from pydantic_settings import BaseSettings
import json

class Settings(BaseSettings):
    # Database
    DATABASE_URL: Optional[str] = None

    # JWT Authentication
    JWT_SECRET_KEY: str = "change-this-in-production-min-32-chars"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440

    # CORS
    CORS_ORIGINS: str = '["http://localhost:5173","http://localhost:8000"]'

    # Server
    SERVER_PORT: int = 8000
    USE_MOCK_APIS: bool = True

    def get_cors_origins(self) -> List[str]:
        try:
            return json.loads(self.CORS_ORIGINS)
        except json.JSONDecodeError:
            return ["http://localhost:5173"]

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()
```

#### `database.py`
```python
from typing import Optional
import psycopg2
from psycopg2.extensions import connection
from .settings import get_settings

def get_database_connection() -> Optional[connection]:
    settings = get_settings()
    if not settings.DATABASE_URL:
        print("WARN [Database]: DATABASE_URL not set")
        return None
    try:
        conn = psycopg2.connect(settings.DATABASE_URL)
        return conn
    except Exception as e:
        print(f"ERROR [Database]: Connection failed: {e}")
        return None

def close_database_connection(conn: Optional[connection]) -> None:
    if conn:
        try:
            conn.close()
        except Exception as e:
            print(f"ERROR [Database]: Failed to close connection: {e}")
```

### 6.3 Authentication System (Keep As-Is)

#### `app/api/auth_routes.py`
```python
from fastapi import APIRouter, HTTPException, Depends
from uuid import UUID
from ..models.auth_dto import UserRegisterDTO, UserLoginDTO, TokenResponseDTO, UserResponseDTO
from ..services.auth_service import auth_service
from ..repository.user_repository import user_repository
from .dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=TokenResponseDTO, status_code=201)
async def register(data: UserRegisterDTO) -> TokenResponseDTO:
    existing = user_repository.get_user_by_email(data.email)
    if existing:
        raise HTTPException(400, "Email already registered")

    password_hash = auth_service.hash_password(data.password)
    user = user_repository.create_user(
        email=data.email,
        password_hash=password_hash,
        first_name=data.first_name,
        last_name=data.last_name,
    )
    token = auth_service.create_access_token({"sub": str(user["id"])})
    return TokenResponseDTO(access_token=token, user=UserResponseDTO(**user))

@router.post("/login", response_model=TokenResponseDTO)
async def login(data: UserLoginDTO) -> TokenResponseDTO:
    user = user_repository.get_user_by_email(data.email)
    if not user or not auth_service.verify_password(data.password, user["password_hash"]):
        raise HTTPException(401, "Invalid credentials")
    if not user.get("is_active"):
        raise HTTPException(401, "Account is inactive")

    token = auth_service.create_access_token({"sub": str(user["id"])})
    return TokenResponseDTO(access_token=token, user=UserResponseDTO(**user))

@router.get("/me", response_model=UserResponseDTO)
async def get_me(current_user: dict = Depends(get_current_user)) -> UserResponseDTO:
    return UserResponseDTO(**current_user)
```

#### `app/api/dependencies.py`
```python
from typing import Any, Dict
from uuid import UUID
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from ..services.auth_service import auth_service
from ..repository.user_repository import user_repository

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> Dict[str, Any]:
    token = credentials.credentials
    payload = auth_service.decode_access_token(token)

    if not payload:
        raise HTTPException(401, "Invalid or expired token")

    user_id = payload.get("sub")
    user = user_repository.get_user_by_id(UUID(user_id))

    if not user or not user.get("is_active"):
        raise HTTPException(401, "User not found or inactive")

    return {
        "id": str(user["id"]),
        "email": user["email"],
        "first_name": user.get("first_name"),
        "last_name": user.get("last_name"),
        "role": user["role"],
        "is_active": user["is_active"],
    }
```

#### `app/api/rbac_dependencies.py`
```python
from typing import Any, Callable, Dict, List
from fastapi import Depends, HTTPException
from .dependencies import get_current_user

def require_roles(allowed_roles: List[str]) -> Callable:
    async def role_checker(
        current_user: Dict[str, Any] = Depends(get_current_user),
    ) -> Dict[str, Any]:
        user_role = current_user.get("role")
        if user_role not in allowed_roles:
            raise HTTPException(403, f"Required roles: {', '.join(allowed_roles)}")
        return current_user
    return role_checker
```

#### `app/services/auth_service.py`
```python
from datetime import datetime, timedelta, timezone
from typing import Optional
import bcrypt
from jose import JWTError, jwt
from ..config import get_settings

class AuthService:
    def hash_password(self, password: str) -> str:
        hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        return hashed.decode("utf-8")

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8")
        )

    def create_access_token(self, data: dict) -> str:
        settings = get_settings()
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    def decode_access_token(self, token: str) -> Optional[dict]:
        settings = get_settings()
        try:
            return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        except JWTError as e:
            print(f"WARN [AuthService]: Token decode failed: {e}")
            return None

auth_service = AuthService()
```

#### `app/models/auth_dto.py`
```python
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr

class UserRegisterDTO(BaseModel):
    email: EmailStr
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class UserLoginDTO(BaseModel):
    email: EmailStr
    password: str

class UserResponseDTO(BaseModel):
    id: UUID
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: str
    is_active: bool

    model_config = {"from_attributes": True}

class TokenResponseDTO(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponseDTO
```

#### `app/repository/user_repository.py`
```python
from typing import Any, Dict, Optional
from uuid import UUID
from ..config.database import get_database_connection, close_database_connection

class UserRepository:
    def create_user(
        self,
        email: str,
        password_hash: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        role: str = "user",
    ) -> Optional[Dict[str, Any]]:
        conn = get_database_connection()
        if not conn:
            return None
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO users (email, password_hash, first_name, last_name, role)
                    VALUES (LOWER(%s), %s, %s, %s, %s)
                    RETURNING id, email, password_hash, first_name, last_name, role, is_active
                """, (email, password_hash, first_name, last_name, role))
                conn.commit()
                row = cur.fetchone()
                return {
                    "id": row[0], "email": row[1], "password_hash": row[2],
                    "first_name": row[3], "last_name": row[4], "role": row[5], "is_active": row[6]
                }
        except Exception as e:
            print(f"ERROR [UserRepository]: Failed to create user: {e}")
            conn.rollback()
            return None
        finally:
            close_database_connection(conn)

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        conn = get_database_connection()
        if not conn:
            return None
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, email, password_hash, first_name, last_name, role, is_active
                    FROM users WHERE email = LOWER(%s)
                """, (email,))
                row = cur.fetchone()
                if not row:
                    return None
                return {
                    "id": row[0], "email": row[1], "password_hash": row[2],
                    "first_name": row[3], "last_name": row[4], "role": row[5], "is_active": row[6]
                }
        except Exception as e:
            print(f"ERROR [UserRepository]: Failed to get user: {e}")
            return None
        finally:
            close_database_connection(conn)

    def get_user_by_id(self, user_id: UUID) -> Optional[Dict[str, Any]]:
        conn = get_database_connection()
        if not conn:
            return None
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, email, password_hash, first_name, last_name, role, is_active
                    FROM users WHERE id = %s
                """, (str(user_id),))
                row = cur.fetchone()
                if not row:
                    return None
                return {
                    "id": row[0], "email": row[1], "password_hash": row[2],
                    "first_name": row[3], "last_name": row[4], "role": row[5], "is_active": row[6]
                }
        except Exception as e:
            print(f"ERROR [UserRepository]: Failed to get user: {e}")
            return None
        finally:
            close_database_connection(conn)

user_repository = UserRepository()
```

### 6.4 Health Check (`app/api/health.py`)
```python
from datetime import datetime, timezone
from fastapi import APIRouter
from pydantic import BaseModel
from ..config import get_settings

router = APIRouter()

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str
    service: str

@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(timezone.utc).isoformat(),
        version="1.0.0",
        service="your-api",
    )
```

### 6.5 Remove (Application-Specific)

```
app/api/tendery/           - All Tendery routes
app/services/tendery/      - All Tendery services
app/repository/tendery/    - All Tendery repositories
app/models/tendery/        - All Tendery DTOs
app/whatsapp/              - WhatsApp integration
app/api/integrated_routes.py - Paqueteo allocation
```

---

## 7. Database Structure

### 7.1 Core Schema (`database/schema.sql`)

```sql
-- Users table for authentication
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    role VARCHAR(50) DEFAULT 'user' NOT NULL,
    is_active BOOLEAN DEFAULT true NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for email lookups
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- Auto-update updated_at trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

### 7.2 Database Initialization (`database/init_db.py`)

```python
from typing import Optional
from app.config.database import get_database_connection, close_database_connection

def init_database() -> bool:
    conn = get_database_connection()
    if not conn:
        print("WARN [InitDB]: No database connection")
        return False

    try:
        with open("database/schema.sql", "r") as f:
            schema = f.read()

        with conn.cursor() as cur:
            cur.execute(schema)
        conn.commit()
        print("INFO [InitDB]: Database initialized successfully")
        return True
    except Exception as e:
        print(f"ERROR [InitDB]: Failed to initialize database: {e}")
        conn.rollback()
        return False
    finally:
        close_database_connection(conn)
```

### 7.3 Migrations Structure

```
database/migrations/
├── __init__.py
├── 001_initial_schema.sql
├── 002_add_feature_tables.sql
└── ...
```

---

## 8. Empty Directories to Preserve

Create these directories with `.gitkeep` files:

```
specs/          - Implementation plans (created by ADW)
app_docs/       - Feature documentation (created by ADW)
agents/         - ADW runtime outputs
trees/          - Worktree isolation (created by ADW)
ai_docs/        - AI-generated guides
e2e_screenshots/ - E2E test screenshots
```

---

## 9. File Counts Summary

| Category | Keep | Remove | Notes |
|----------|------|--------|-------|
| ADW Core Modules | 10 | 0 | All essential |
| ADW Scripts | 15 | 1 | Remove legacy |
| ADW Triggers | 3 | 0 | All essential |
| Claude Commands | 28 | 91 | Remove E2E and project-specific |
| Frontend Core | ~15 | ~80 | Keep auth, layout, patterns |
| Backend Core | ~15 | ~200 | Keep auth, health, patterns |
| Specs | 0 | 156 | All project-specific |
| App Docs | 0 | 123 | All project-specific |

**Total to keep:** ~90 files
**Total to remove:** ~650 files

---

## 10. Quick Start Checklist

### 10.1 Initial Setup

- [ ] Clone template repository
- [ ] Update `CLAUDE.md` with new project info
- [ ] Update `README.md` with new project info
- [ ] Choose component prefix (e.g., `XX` for `XXButton.tsx`)
- [ ] Update `package.json` name and description
- [ ] Update `main.py` FastAPI title

### 10.2 Environment Setup

- [ ] Copy `.env.sample` to `.env`
- [ ] Set `DATABASE_URL` for Supabase
- [ ] Generate secure `JWT_SECRET_KEY` (32+ chars)
- [ ] Configure `CORS_ORIGINS` for your domains

### 10.3 Database Setup

- [ ] Create Supabase project
- [ ] Run `database/schema.sql`
- [ ] Create initial admin user

### 10.4 Frontend Setup

```bash
cd apps/Client
npm install
npm run dev
```

### 10.5 Backend Setup

```bash
cd apps/Server
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 10.6 ADW Setup

- [ ] Configure GitHub repository
- [ ] Set up GitHub webhook (optional)
- [ ] Test with: `uv run adws/adw_plan_iso.py <issue_number>`

---

## 11. Customization Guide

### 11.1 Naming Conventions

Replace the `PQ` prefix throughout:

| Original | New Project Example |
|----------|---------------------|
| `PQMainLayout` | `XXMainLayout` |
| `PQSidebar` | `XXSidebar` |
| `PQContentHeader` | `XXContentHeader` |

For domain modules (like Tendery):

| Original | New Project Example |
|----------|---------------------|
| `TYQuotationForm` | `YYOrderForm` |
| `ty_quotes` | `yy_orders` |
| `/api/tendery/*` | `/api/yourmodule/*` |

### 11.2 Theme Customization

Update `apps/Client/src/theme/index.ts`:

```typescript
const theme = createTheme({
  palette: {
    primary: { main: '#YOUR_PRIMARY_COLOR' },
    secondary: { main: '#YOUR_SECONDARY_COLOR' },
  },
});

export const SIDEBAR_DARK_BG = '#1a1d21'; // Or your sidebar color
```

### 11.3 Sidebar Navigation

Update `apps/Client/src/components/layout/PQSidebar.tsx`:

```typescript
const navSections = [
  {
    title: 'Your Module',
    items: [
      { title: 'Dashboard', icon: DashboardIcon, path: '/dashboard' },
      { title: 'Feature 1', icon: Feature1Icon, path: '/feature-1' },
    ],
  },
];
```

### 11.4 Adding New Routes

In `apps/Client/src/App.tsx`:

```tsx
<Routes>
  <Route path="/login" element={<LoginPage />} />
  <Route path="/" element={
    <ProtectedRoute>
      <RoleProtectedRoute allowedRoles={['admin', 'manager', 'user']}>
        <PQMainLayout>
          <Routes>
            <Route index element={<DashboardPage />} />
            <Route path="new-feature" element={<NewFeaturePage />} />
          </Routes>
        </PQMainLayout>
      </RoleProtectedRoute>
    </ProtectedRoute>
  } />
</Routes>
```

### 11.5 Adding New Backend Routes

1. Create route file: `app/api/your_feature_routes.py`
2. Create service: `app/services/your_feature_service.py`
3. Create repository: `app/repository/your_feature_repository.py`
4. Create DTOs: `app/models/your_feature_dto.py`
5. Register in `main.py`:

```python
from app.api.your_feature_routes import router as your_feature_router
app.include_router(your_feature_router, prefix="/api/your-feature")
```

### 11.6 Claude Commands Customization

Update `.claude/commands/conditional_docs.md` to reference your project's documentation structure.

Update `.claude/commands/start.md` with your project's startup commands.

---

## Architecture Patterns Reference

### Provider Layering (Frontend)
```
BrowserRouter
└── AuthProvider
    └── YourFeatureProvider
        └── ThemeProvider
            └── App
```

### Protected Routes
```tsx
<ProtectedRoute>           {/* Checks isAuthenticated */}
  <RoleProtectedRoute>     {/* Checks role */}
    <PageComponent />
  </RoleProtectedRoute>
</ProtectedRoute>
```

### Service-Based API Abstraction
```
Page Component
└── Custom Hook (useFeature)
    └── Service (featureService)
        └── apiClient (axios)
```

### Backend Clean Architecture
```
Route (HTTP layer)
└── Service (business logic)
    └── Repository (data access)
        └── Database (PostgreSQL)
```

### Logging Pattern
```python
print(f"INFO [ModuleName]: Action description")
print(f"WARN [ModuleName]: Warning message")
print(f"ERROR [ModuleName]: Error: {e}")
```

---

*Generated for Paqueteo/Tendery architecture template - v1.0*
