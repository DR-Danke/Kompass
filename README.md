# [Your Project Name]

Brief description of your project.

## Tech Stack

- **Frontend**: React 19, TypeScript, Vite, Material-UI
- **Backend**: Python 3.11, FastAPI, Pydantic 2
- **Database**: PostgreSQL (Supabase)
- **Auth**: Custom JWT with RBAC

## Quick Start

### Prerequisites

- Node.js 18+
- Python 3.11.9
- uv (Python package manager)
- poppler-utils (required for PDF processing in Supplier Certification)
  - Ubuntu/Debian: `sudo apt-get install poppler-utils`
  - macOS: `brew install poppler`
  - Windows: Download from [poppler releases](https://github.com/osber/poppler-windows/releases) and add to PATH

### Setup

1. Clone the repository
2. Copy `.env.sample` to `.env` and configure
3. Start the backend:
   ```bash
   cd apps/Server
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```
4. Start the frontend:
   ```bash
   cd apps/Client
   npm install
   npm run dev
   ```

## Project Structure

```
├── apps/
│   ├── Client/          # React frontend
│   └── Server/          # FastAPI backend
├── adws/                # AI Developer Workflow system
├── .claude/commands/    # Claude Code slash commands
├── specs/               # Implementation plans
├── app_docs/            # Feature documentation
└── ai_docs/             # AI-generated guides
```

## ADW System

This project includes the AI Developer Workflow (ADW) system for automated issue processing.

### Quick Commands

```bash
# Process single issue
uv run adws/adw_plan_iso.py <issue-number>

# Complete SDLC
uv run adws/adw_sdlc_iso.py <issue-number>

# Zero-Touch Execution (auto-merge)
uv run adws/adw_sdlc_zte_iso.py <issue-number>
```

See `adws/README.md` for full documentation.

## License

[Your License]
