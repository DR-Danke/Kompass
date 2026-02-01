# Generate Documentation Suite

Master command to generate the complete documentation suite.

## Variables

issue_number: $1 (optional)
adw_id: $2 (optional)

## Instructions

### Step 1: Research Application

```bash
ls apps/Client/src/pages/kompass/
ls ai_docs/
```

### Step 2: Generate User Documentation

Create in ai_docs/:
- KOMPASS_USER_GUIDE.md
- KOMPASS_QUICK_REFERENCE.md
- KOMPASS_ROLE_WORKFLOWS.md
- KOMPASS_TROUBLESHOOTING_FAQ.md
- KOMPASS_TEAM_ONBOARDING.md

### Step 3: Generate Workflow Diagrams

Create ai_docs/KOMPASS_WORKFLOW_DIAGRAMS.html with Mermaid:
- System Overview
- Data Model
- Quotation Workflow
- Status Flows
- Client Pipeline
- Import Workflow
- Portfolio Workflow
- Pricing Calculation
- User Journeys
- API Flows

### Step 4: Update In-App Documentation

Create/update DocumentationPage.tsx with 5 tabs:
1. Getting Started
2. Quick Reference
3. Workflows
4. FAQ
5. Diagrams

Ensure route exists: /docs
Ensure menu exists: Help & Docs

### Step 5: Copy Static Assets

```bash
mkdir -p apps/Client/public/docs
cp ai_docs/KOMPASS_WORKFLOW_DIAGRAMS.html apps/Client/public/docs/
```

### Step 6: Validation

```bash
cd apps/Client && npm run typecheck
cd apps/Client && npm run build
```

## Report

Output summary of files created and validation status.
