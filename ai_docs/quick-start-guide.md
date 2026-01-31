# Quick Start Guide

This guide helps you bootstrap a new project from this template in minutes.

---

## Step 1: Copy the Template

```bash
cp -r codebase_template/ /path/to/your-new-project/
cd /path/to/your-new-project/
git init
```

---

## Step 2: Update Project Identity

### 2.1 Update `CLAUDE.md`

Replace these placeholders:
- `[YOUR PROJECT NAME]` → Your project name
- `[Component 1]` → Your key components
- `[XX] Prefix` → Your component prefix (e.g., `PQ`, `TY`, `XX`)

### 2.2 Update `README.md`

- Replace `[Your Project Name]` with your project name
- Update description and features
- Set `[Your License]`

### 2.3 Update `package.json`

```json
{
  "name": "your-project-client",
  ...
}
```

### 2.4 Update `apps/Client/index.html`

```html
<title>Your App Name</title>
```

### 2.5 Update `apps/Server/main.py`

```python
app = FastAPI(
    title="Your API",
    description="API for Your Application",
    ...
)
```

---

## Step 3: Configure Environment

### 3.1 Create `.env` file

```bash
cp .env.sample .env
```

### 3.2 Set required values

```bash
# Database
DATABASE_URL=postgresql://postgres.[project]:[password]@[host]:5432/postgres

# JWT (generate a secure key)
JWT_SECRET_KEY=your-secure-32-character-minimum-key

# CORS
CORS_ORIGINS=["http://localhost:5173"]
```

---

## Step 4: Setup Database

### 4.1 Create Supabase Project

1. Go to https://supabase.com
2. Create new project
3. Copy connection string from Settings → Database

### 4.2 Run Schema

```bash
cd apps/Server
psql $DATABASE_URL -f database/schema.sql
```

Or the schema runs automatically on first server start.

---

## Step 5: Install Dependencies

### Frontend

```bash
cd apps/Client
npm install
```

### Backend

```bash
cd apps/Server
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

## Step 6: Start Development

### Terminal 1: Backend

```bash
cd apps/Server
source venv/bin/activate
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Terminal 2: Frontend

```bash
cd apps/Client
npm run dev
```

### Access

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000/api
- API Docs: http://localhost:8000/docs

---

## Step 7: Create First User

Use the API docs or curl:

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "your-password",
    "first_name": "Admin",
    "last_name": "User"
  }'
```

Then update role in database:
```sql
UPDATE users SET role = 'admin' WHERE email = 'admin@example.com';
```

---

## Step 8: Setup ADW (Optional)

If you want AI-powered issue processing:

### 8.1 Install Claude Code CLI

```bash
npm install -g @anthropic-ai/claude-code
claude login  # Authenticate with Anthropic
```

### 8.2 Configure ADW

Add to `.env`:
```bash
CLAUDE_CODE_PATH=claude
```

### 8.3 Test ADW

Create a GitHub issue, then run:
```bash
uv run adws/adw_plan_iso.py <issue-number>
```

---

## Common Customizations

### Add a New Page

1. Create `apps/Client/src/pages/NewPage.tsx`
2. Add route in `apps/Client/src/App.tsx`
3. Add nav item in `apps/Client/src/components/layout/Sidebar.tsx`

### Add a New API Endpoint

1. Create `apps/Server/app/api/new_routes.py`
2. Create `apps/Server/app/services/new_service.py`
3. Create `apps/Server/app/repository/new_repository.py`
4. Create `apps/Server/app/models/new_dto.py`
5. Register in `apps/Server/main.py`:
   ```python
   app.include_router(new_router, prefix="/api/new")
   ```

### Add Database Table

1. Add to `apps/Server/database/schema.sql`
2. Create migration in `apps/Server/database/migrations/`

---

## File Reference

| What | Where |
|------|-------|
| Frontend entry | `apps/Client/src/main.tsx` |
| React routes | `apps/Client/src/App.tsx` |
| Auth context | `apps/Client/src/contexts/AuthContext.tsx` |
| API client | `apps/Client/src/api/clients/index.ts` |
| Theme | `apps/Client/src/theme/index.ts` |
| Backend entry | `apps/Server/main.py` |
| Settings | `apps/Server/app/config/settings.py` |
| Auth routes | `apps/Server/app/api/auth_routes.py` |
| JWT deps | `apps/Server/app/api/dependencies.py` |
| RBAC | `apps/Server/app/api/rbac_dependencies.py` |
| DB schema | `apps/Server/database/schema.sql` |

---

## Troubleshooting

### "CORS error"
- Check `CORS_ORIGINS` in `.env` includes your frontend URL

### "401 Unauthorized"
- Token expired - login again
- Check JWT_SECRET_KEY is same across restarts

### "Database connection failed"
- Check DATABASE_URL format
- Ensure Supabase project is running

### "Module not found" (Python)
- Activate venv: `source venv/bin/activate`
- Install deps: `pip install -r requirements.txt`

### "Cannot find module" (React)
- Run `npm install`
- Check `@/` alias in `tsconfig.json`

---

For detailed architecture documentation, see `ai_docs/template-repo-setup-guide.md`.
