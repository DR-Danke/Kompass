# Merge Multiple Branches & Create PR

Merge multiple feature/fix branches into a single release branch, run a production risk assessment, push to GitHub, and create a pull request.

## Variables

branches: $ARGUMENTS

## Instructions

You will merge the listed branches from `main` into a new feature branch, assess production risk, and create a PR. Follow all steps in order.

## Run

### Phase 1: Fetch & Inspect

1. Run `git checkout main && git pull origin main` to ensure main is current.

2. For each branch name provided in the `branches` variable:
   - Search for the exact remote ref using `git ls-remote origin | grep <branch-name>` since branch names may contain special characters (backticks, etc.)
   - Fetch each branch. If refs contain special characters, use `git fetch origin 'refs/heads/<exact-ref>':refs/remotes/origin/<clean-alias>` to create clean local aliases.

3. For each branch, inspect what it changes relative to main:
   - `git log origin/main..<branch-ref> --oneline` — commit history
   - `git diff origin/main...<branch-ref> --stat` — files changed

4. Check for overlapping files between all branch pairs using `git diff --name-only` comparisons. Report any files changed by multiple branches — these are potential conflict zones.

### Phase 2: Create Feature Branch & Merge

5. Generate a descriptive feature branch name in the format: `merge-<issue-numbers>-<short-description>` (e.g., `merge-520-521-522-improvements`).

6. Run `git checkout -b <branch-name>` from main.

7. Merge each branch one at a time using `git merge <branch-ref> --no-edit`:
   - If the merge is clean, proceed to the next branch.
   - If there are conflicts:
     - **Boilerplate files** (`.mcp.json`, `playwright-mcp-config.json`, `tsconfig.tsbuildinfo`, `app_docs/agentic_kpis.md`): Take the incoming version.
     - **`.claude/commands/conditional_docs.md`**: Keep ALL entries from both sides.
     - **Code files** (`.tsx`, `.ts`, `.py`, `.json`, etc.): Read the conflicted file, understand both sides, and combine changes. These branches are typically complementary — different concerns in the same file.
   - After resolving conflicts, `git add` the resolved files and `git commit --no-edit`.

8. After all merges, verify no conflict markers remain: `git diff origin/main -- '*.tsx' '*.ts' '*.py' '*.json' | grep -c '<<<<<<'`

### Phase 3: Production Risk Assessment

9. Analyze the combined diff against main and produce a risk assessment covering:

   **Classify each change by blast radius:**
   - Check if changes touch **backend** files (`apps/Server/`): API routes (`app/api/`), services (`app/services/`), repositories (`app/repository/`), models, database migrations
   - Check if changes touch **frontend** files (`apps/Client/`): components, pages, services, hooks, types, utils
   - Check if changes touch **infrastructure**: `.env`, `render.yaml`, `vercel.json`, deployment configs
   - Check if changes touch **database**: schema files (`apps/Server/database/`), migrations, seed data
   - Check if changes touch **auth**: JWT, RBAC, login, protected routes (`AuthContext`, `ProtectedRoute`, `RoleProtectedRoute`)
   - Check if changes touch **routing**: React Router routes (`App.tsx`), URL paths, navigation

   **Assess each branch individually:**
   For each merged branch, assign a risk level:
   - **Near zero**: Purely additive (new components, new files, docs). No existing behavior modified.
   - **Minimal**: Mechanical refactoring (import changes, extract utility). Same logic, different organization.
   - **Low**: Behavioral changes gated by feature flags or environment variables. Changes to error handling that improve resilience.
   - **Medium**: Changes to business logic, calculations, data flow, or API contracts. Changes visible to end users.
   - **High**: Database migrations, auth changes, breaking API changes, routing changes, infrastructure modifications.

   **Calculate overall risk:**
   - If ALL branches are Near zero/Minimal → **Very Low (<5%)**
   - If any branch is Low → **Low (~5-10%)**
   - If any branch is Medium → **Medium (~10-25%)**
   - If any branch is High → **High (>25%)** — flag for careful review

   **Output format for the risk assessment:**
   ```
   ### Risk Assessment: <Overall Risk Level>
   - <bullet points explaining WHY this risk level>
   - Per-branch breakdown table with risk level and justification
   - Key confidence factors (what makes this safe/risky)
   - Most likely regression scenario (if any)
   ```

### Phase 4: Push & Create PR

10. Run `git push -u origin <branch-name>` to push the feature branch.

11. Create a PR using `gh pr create` with this structure:
    - **Title**: Short, descriptive (under 70 chars). Example: `Merge CI improvements: pricing fix, import wizard, client CRM`
    - **Body**:
      ```
      ## Summary
      Merges N continuous improvement branches (issues #X, #Y, #Z) into a single release branch.

      ### Branches merged
      | Issue | Branch | Type | Description |
      |-------|--------|------|-------------|
      (one row per branch)

      ### Risk Assessment: <Level>
      (paste the risk assessment from Phase 3)

      **Stats:** X files changed, +Y / −Z lines

      ## Test plan
      - [ ] (one test item per branch, specific to what changed)

      🤖 Generated with [Claude Code](https://claude.com/claude-code)
      ```

12. If the PR already exists, update it with `gh pr edit` instead.

## Report

Return:
1. The PR URL
2. The risk assessment summary (one line)
3. Count of merge conflicts resolved
