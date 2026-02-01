# Update In-App Documentation Page

Update the DocumentationPage.tsx component with current documentation content.

## Variables

None required.

## Instructions

### 1. Analyze Current Documentation

Review existing documentation files:

```bash
ls -la ai_docs/KOMPASS_*.md ai_docs/KOMPASS_*.html
```

### 2. Review Current Documentation Page

```bash
cat apps/Client/src/pages/kompass/DocumentationPage.tsx
```

### 3. Update Content Sections

The DocumentationPage should have these tabs:

- **Tab 1: Getting Started** - Welcome, role cards, key concepts
- **Tab 2: Quick Reference** - Create actions, shortcuts, status flows
- **Tab 3: Workflows** - Step-by-step workflow cards
- **Tab 4: FAQ** - Accordion FAQ by category
- **Tab 5: Diagrams** - Links to workflow diagrams

### 4. Ensure Route and Menu Exist

Verify integration:

```bash
grep -n "docs" apps/Client/src/App.tsx
grep -n "Help" apps/Client/src/components/layout/Sidebar.tsx
```

### 5. Update Static Assets

```bash
mkdir -p apps/Client/public/docs
cp ai_docs/KOMPASS_WORKFLOW_DIAGRAMS.html apps/Client/public/docs/
```

### 6. Validation

```bash
cd apps/Client && npm run typecheck
cd apps/Client && npm run build
```

## Report

Output:
```
Documentation page updated:
- apps/Client/src/pages/kompass/DocumentationPage.tsx

Integration verified:
- Route: /docs
- Menu: Help & Docs
- Static: apps/Client/public/docs/KOMPASS_WORKFLOW_DIAGRAMS.html

Validation: PASSED
```
