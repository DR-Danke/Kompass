# Generate User Documentation

Generate comprehensive end-user documentation for the application by analyzing the codebase, existing documentation, and features.

## Variables

target_module: $1 (optional - specific module to document, e.g., "quotations", "portfolios", or "all" for full suite)

## Instructions

### 1. Analyze the Application

First, understand what needs to be documented:

```bash
# List all pages to understand features
ls apps/Client/src/pages/kompass/

# List existing documentation
ls ai_docs/*.md

# Check routes for all features
cat apps/Client/src/App.tsx | grep -A 50 "Routes"
```

### 2. Research Each Module

For each module/page, analyze:
- The page component (`apps/Client/src/pages/kompass/<Module>Page.tsx`)
- Related hooks (`apps/Client/src/hooks/kompass/use<Module>.ts`)
- Related components (`apps/Client/src/components/kompass/<Module>*.tsx`)
- API service methods (`apps/Client/src/services/kompassService.ts`)
- Types (`apps/Client/src/types/kompass.ts`)

### 3. Generate Documentation Files

Create/update the following files in `ai_docs/`:

#### If target_module is "all" or not specified, generate full suite:

1. **KOMPASS_USER_GUIDE.md** - Comprehensive feature-by-feature guide
   - Getting started (login, navigation)
   - Each module with step-by-step instructions
   - Tips and best practices

2. **KOMPASS_QUICK_REFERENCE.md** - Quick lookup cheat sheet
   - Navigation quick links
   - Common tasks table
   - Status flows
   - Keyboard shortcuts
   - Required fields reference

3. **KOMPASS_ROLE_WORKFLOWS.md** - Role-based workflow guides
   - Diana (Design Director) workflows
   - Alejandro (Commercial Manager) workflows
   - Ruben (CEO) workflows
   - Cross-team handoffs

4. **KOMPASS_TROUBLESHOOTING_FAQ.md** - Problem solving guide
   - Common issues by category
   - FAQ organized by module
   - Error code reference

5. **KOMPASS_TEAM_ONBOARDING.md** - New team member quick start
   - 15-minute getting started
   - First tasks by role
   - Key concepts
   - Onboarding checklist

#### If target_module is specific (e.g., "quotations"):

Update relevant sections in existing documentation files for that module only.

### 4. Documentation Standards

Follow these standards:

- **Structure**: Use clear headings (H2 for sections, H3 for subsections)
- **Tables**: Use markdown tables for reference data
- **Code blocks**: Use for paths, commands, formulas
- **Lists**: Use bullet points for steps and features
- **Links**: Cross-reference other documentation files
- **Tone**: Professional but approachable, no jargon
- **Length**: Comprehensive but scannable

### 5. Content Requirements

Each module documentation should include:

1. **Purpose**: What the module does and why it matters
2. **Navigation**: How to access it
3. **Main Features**: List of capabilities
4. **Step-by-Step Workflows**: Common tasks with numbered steps
5. **Field Reference**: Required vs optional fields
6. **Status/State Info**: Any status flows or states
7. **Tips**: Best practices and gotchas
8. **Related Modules**: Connections to other features

### 6. Validation

After generating documentation:

```bash
# Verify all files exist
ls -la ai_docs/KOMPASS_*.md

# Check file sizes (should be substantial)
wc -l ai_docs/KOMPASS_*.md

# Verify no broken internal links
grep -r "](KOMPASS_" ai_docs/ | grep -v ".html"
```

## Output Format

Each documentation file should follow this general structure:

```md
# <Document Title>

<Brief description of what this document covers>

---

## Table of Contents

1. [Section 1](#section-1)
2. [Section 2](#section-2)
...

---

## Section 1

<Content>

---

## Section 2

<Content>

---

## Getting Help

<Footer with links to other docs and support>
```

## Report

When complete, output:

```
Documentation generated:
- ai_docs/KOMPASS_USER_GUIDE.md (X lines)
- ai_docs/KOMPASS_QUICK_REFERENCE.md (X lines)
- ai_docs/KOMPASS_ROLE_WORKFLOWS.md (X lines)
- ai_docs/KOMPASS_TROUBLESHOOTING_FAQ.md (X lines)
- ai_docs/KOMPASS_TEAM_ONBOARDING.md (X lines)

Total: X files, Y lines
```
