# ServiceDesk AI - ADW Implementation Prompts

**Document Version:** 1.1 (With Context Sections)
**Created:** January 4, 2026
**Purpose:** GitHub issue prompts for parallel ADW execution

---

## Quick Reference

| Metric | Value |
|--------|-------|
| Total Issues | 25 |
| Parallel Phases | 8 |
| Max Concurrent ADWs | 4 |
| Backend Files | ~20 new files |
| Frontend Files | ~15 new files |
| Database Tables | 10 new tables |
| API Endpoints | ~30 new endpoints |

---

## Dependency Graph

```
Phase 1: Foundation
    └── SD-001 (Database & DTOs)
            │
            ▼
Phase 2: Backend Services (4 parallel)
    ├── SD-002 (Ticket Service)
    ├── SD-003 (Knowledge Service)
    ├── SD-004 (Technician Service)
    └── SD-005 (AI Classification)
            │
            ▼
Phase 3: API Routes (4 parallel)
    ├── SD-006 (Ticket Routes) ←── SD-002, SD-005
    ├── SD-007 (KB Routes) ←── SD-003
    ├── SD-008 (Tech Routes) ←── SD-004
    └── SD-009 (Analytics Routes)
            │
            ├─────────────────────┬─────────────────────┐
            ▼                     ▼                     ▼
Phase 4: Frontend Core      Phase 6: Multi-Channel   Phase 7: AI Enhancement
    ├── SD-010 (Types)          ├── SD-018 (Email)      ├── SD-021 (Routing)
    ├── SD-011 (Dashboard)      ├── SD-019 (WhatsApp)   ├── SD-022 (SLA)
    ├── SD-012 (List)           └── SD-020 (Notify)     └── SD-023 (Surveys)
    └── SD-013 (Form)
            │
            ▼
Phase 5: Frontend Advanced (4 parallel)
    ├── SD-014 (Detail View)
    ├── SD-015 (KB Browser)
    ├── SD-016 (Analytics UI)
    └── SD-017 (Tech Management)
            │
            ▼
Phase 8: Testing & Polish (2 parallel)
    ├── SD-024 (E2E Tests)
    └── SD-025 (Documentation)
```

---

## Technology Stack

| Component | Technology |
|-----------|------------|
| Backend | FastAPI + Python 3.11 |
| Database | Supabase PostgreSQL |
| Auth | Supabase Auth |
| AI Classification | OpenAI GPT-4o |
| Frontend | React 19 + MUI + TypeScript |
| Storage | Supabase Storage |
| Email Webhooks | Supabase Edge Functions |
| WhatsApp | Kapso.ai (placeholder) |

---

## Phase 1: Foundation (Sequential)

### SD-001: Database Schema & Core DTOs

**Title:** `[ServiceDesk] Phase 1: Database Schema and Core DTOs`

**Body:**
```markdown
## Context
**Project:** ServiceDesk AI Implementation for System Zero
**Overview:** We are building an AI-powered IT support platform with intelligent ticket management, automated classification, multi-channel support (web, email, WhatsApp), knowledge base, technician dashboard, and analytics. The implementation is divided into 8 phases with 25 total issues.

**Current Phase:** Phase 1 of 8 - Foundation
**Current Issue:** SD-001 (Issue 1 of 25)
**Parallel Execution:** NO - This issue must be completed FIRST as it creates the database schema and core types that all other issues depend on.

**What comes next:** After this issue, Phase 2 begins with 4 parallel backend service implementations (SD-002, SD-003, SD-004, SD-005).

---

## Description
Create the foundational database schema and core DTOs for the ServiceDesk module.

## Requirements

### Database Tables (backend/database/migration_add_servicedesk_tables.sql)
1. `sd_organizations` - Client organizations
2. `sd_departments` - Department hierarchy
3. `sd_technicians` - Support staff with credentials
4. `sd_tickets` - Core ticket entity with 30+ fields
5. `sd_ticket_messages` - Conversation thread
6. `sd_ticket_attachments` - File attachments
7. `sd_knowledge_articles` - Self-service content
8. `sd_satisfaction_feedback` - Post-resolution surveys
9. `sd_ticket_patterns` - AI learning patterns
10. `sd_technician_expertise` - Skill mapping

### DTOs (backend/src/interface/servicedesk_dtos.py)
- Enums: TicketStatus, TicketPriority, TicketCategory, TicketChannel, TechnicianStatus
- Request DTOs: CreateTicket, UpdateTicket, CreateMessage, AssignTicket
- Response DTOs: TicketResponse, TicketListResponse, TechnicianResponse
- Analytics DTOs: TicketStats, SLAMetrics, SatisfactionMetrics

### Repository (backend/src/repositorio/servicedesk_repository.py)
- TicketRepository with CRUD operations
- TechnicianRepository
- KnowledgeRepository
- AnalyticsRepository

## Acceptance Criteria
- [ ] All 10 database tables created with proper constraints and indexes
- [ ] RLS policies configured for role-based access
- [ ] All DTOs defined with Pydantic validation
- [ ] Base repository classes implemented

## Technical Notes
- Follow existing patterns from `migration_add_interview_tables.sql`
- Use UUID primary keys with `gen_random_uuid()`
- Include audit fields (created_at, updated_at)
- Add foreign key constraints with ON DELETE CASCADE

Include workflow: adw_plan_build_test_iso model_set heavy
```

**ADW Command:**
```bash
cd adws && uv run adw_plan_build_test_iso.py SD-001
```

---

## Phase 2: Backend Core Services (4 Parallel)

### SD-002: Ticket Service

**Title:** `[ServiceDesk] Phase 2A: Ticket Service - CRUD & Workflow`

**Body:**
```markdown
## Context
**Project:** ServiceDesk AI Implementation for System Zero
**Overview:** We are building an AI-powered IT support platform with intelligent ticket management, automated classification, multi-channel support (web, email, WhatsApp), knowledge base, technician dashboard, and analytics. The implementation is divided into 8 phases with 25 total issues.

**Current Phase:** Phase 2 of 8 - Backend Core Services
**Current Issue:** SD-002 (Issue 2 of 25)
**Parallel Execution:** YES - This issue runs IN PARALLEL with SD-003, SD-004, and SD-005. All 4 backend services are being developed simultaneously in separate worktrees.

**What was completed:** Phase 1 (SD-001) - Database schema and core DTOs are now available.
**What comes next:** After Phase 2, we move to Phase 3 (API Routes) which also runs 4 issues in parallel.

---

## Description
Implement the core ticket service with CRUD operations and status workflow management.

## Requirements

### File: backend/src/core/servicios/servicedesk/ticket_service.py

#### Core Methods
- `create_ticket(request, user_id)` - Create new ticket with auto-classification
- `get_ticket(ticket_id)` - Get single ticket with messages
- `list_tickets(filters, pagination)` - List with filtering
- `update_ticket(ticket_id, updates)` - Update ticket fields
- `delete_ticket(ticket_id)` - Soft delete

#### Status Workflow
- `update_status(ticket_id, new_status, user_id)` - Validate transitions
- Status flow: Backlog → In Progress → Waiting User → Resolved → Closed
- Emit status change messages to ticket thread

#### SLA Management
- `calculate_sla_deadline(priority, impact)` - Based on priority matrix
- `check_sla_status(ticket_id)` - Returns: on_track, warning, breached
- Priority matrix: Critical=1h, High=4h, Medium=8h, Low=24h

#### Assignment
- `assign_ticket(ticket_id, technician_id, user_id)` - Manual assignment
- `unassign_ticket(ticket_id)` - Return to backlog

## Dependencies
- Phase 1 (SD-001) must be complete
- Requires: servicedesk_repository.py, servicedesk_dtos.py

## Acceptance Criteria
- [ ] All CRUD operations working
- [ ] Status transitions validated
- [ ] SLA calculations accurate
- [ ] Assignment logic implemented
- [ ] Unit tests passing

Include workflow: adw_plan_build_test_iso model_set heavy
``` 
WIP
---

### SD-003: Knowledge Base Service

**Title:** `[ServiceDesk] Phase 2B: Knowledge Base Service`

**Body:**
```markdown
## Context
**Project:** ServiceDesk AI Implementation for System Zero
**Overview:** We are building an AI-powered IT support platform with intelligent ticket management, automated classification, multi-channel support (web, email, WhatsApp), knowledge base, technician dashboard, and analytics. The implementation is divided into 8 phases with 25 total issues.

**Current Phase:** Phase 2 of 8 - Backend Core Services
**Current Issue:** SD-003 (Issue 3 of 25)
**Parallel Execution:** YES - This issue runs IN PARALLEL with SD-002, SD-004, and SD-005. All 4 backend services are being developed simultaneously in separate worktrees.

**What was completed:** Phase 1 (SD-001) - Database schema and core DTOs are now available.
**What comes next:** After Phase 2, we move to Phase 3 (API Routes) which also runs 4 issues in parallel.

---

## Description
Implement knowledge base service for self-service content management and semantic search.

## Requirements

### File: backend/src/core/servicios/servicedesk/knowledge_service.py

#### Article Management
- `create_article(request, user_id)` - Create with category/tags
- `update_article(article_id, updates)` - Edit content
- `delete_article(article_id)` - Soft delete
- `list_articles(category, tags)` - Browse by category

#### Search
- `search_articles(query, limit)` - Semantic search using embeddings
- `suggest_articles(ticket_content)` - Real-time suggestions during ticket creation
- Integration with existing RAG embedding service

#### Analytics
- `increment_view_count(article_id)` - Track views
- `rate_article(article_id, helpful)` - Helpfulness rating
- `get_popular_articles(limit)` - Most viewed

## Dependencies
- Phase 1 (SD-001) must be complete
- Leverage existing RAG services: `backend/src/core/servicios/rag/embedding_service.py`

## Acceptance Criteria
- [ ] Article CRUD working
- [ ] Semantic search returning relevant results
- [ ] View/rating tracking functional
- [ ] Unit tests passing

Include workflow: adw_plan_build_test_iso
```

---

### SD-004: Technician Service

**Title:** `[ServiceDesk] Phase 2C: Technician Management Service`

**Body:**
```markdown
## Context
**Project:** ServiceDesk AI Implementation for System Zero
**Overview:** We are building an AI-powered IT support platform with intelligent ticket management, automated classification, multi-channel support (web, email, WhatsApp), knowledge base, technician dashboard, and analytics. The implementation is divided into 8 phases with 25 total issues.

**Current Phase:** Phase 2 of 8 - Backend Core Services
**Current Issue:** SD-004 (Issue 4 of 25)
**Parallel Execution:** YES - This issue runs IN PARALLEL with SD-002, SD-003, and SD-005. All 4 backend services are being developed simultaneously in separate worktrees.

**What was completed:** Phase 1 (SD-001) - Database schema and core DTOs are now available.
**What comes next:** After Phase 2, we move to Phase 3 (API Routes) which also runs 4 issues in parallel.

---

## Description
Implement technician management including credentials, expertise tracking, and workload metrics.

## Requirements

### File: backend/src/core/servicios/servicedesk/technician_service.py

#### Account Management
- `create_technician(request)` - Create with auto-generated credentials
- `update_technician(tech_id, updates)` - Edit profile
- `activate_technician(tech_id)` / `deactivate_technician(tech_id)`
- `list_technicians(filters)` - With status filtering

#### Authentication
- `authenticate(username, password)` - Validate credentials
- `change_password(tech_id, old_pw, new_pw)` - Self-service
- `reset_password(tech_id)` - Admin reset with token
- Password hashing with bcrypt

#### Expertise & Workload
- `update_expertise(tech_id, categories)` - Skill mapping
- `get_workload(tech_id)` - Current assigned tickets count
- `get_performance(tech_id, date_range)` - Resolution metrics

## Dependencies
- Phase 1 (SD-001) must be complete

## Acceptance Criteria
- [ ] Technician CRUD working
- [ ] Password hashing secure
- [ ] Expertise tracking functional
- [ ] Workload calculations accurate
- [ ] Unit tests passing

Include workflow: adw_plan_build_test_iso
```

---

### SD-005: AI Classification Service

**Title:** `[ServiceDesk] Phase 2D: AI Classification & Entity Extraction`

**Body:**
```markdown
## Context
**Project:** ServiceDesk AI Implementation for System Zero
**Overview:** We are building an AI-powered IT support platform with intelligent ticket management, automated classification, multi-channel support (web, email, WhatsApp), knowledge base, technician dashboard, and analytics. The implementation is divided into 8 phases with 25 total issues.

**Current Phase:** Phase 2 of 8 - Backend Core Services
**Current Issue:** SD-005 (Issue 5 of 25)
**Parallel Execution:** YES - This issue runs IN PARALLEL with SD-002, SD-003, and SD-004. All 4 backend services are being developed simultaneously in separate worktrees.

**What was completed:** Phase 1 (SD-001) - Database schema and core DTOs are now available.
**What comes next:** After Phase 2, we move to Phase 3 (API Routes) which also runs 4 issues in parallel.

---

## Description
Implement AI-powered ticket classification and entity extraction using OpenAI GPT-4o.

## Requirements

### File: backend/src/core/servicios/servicedesk/classification_service.py

#### Ticket Classification
- `classify_ticket(subject, description)` - Returns:
  - category (technical, billing, general, escalation)
  - subcategory (hardware, software, network, etc.)
  - priority (low, medium, high, urgent)
  - impact (individual, department, organization)
  - confidence_score (0-1)

#### Entity Extraction
- `extract_entities(content)` - Returns:
  - organization_name
  - department_location
  - affected_systems
  - user_details
  - keywords

#### Pattern Learning
- `record_correction(ticket_id, original, corrected)` - Learn from technician corrections
- `get_classification_accuracy()` - Track model performance

### Prompt Engineering
- Use structured output format (JSON)
- Include context from knowledge base
- Fallback to rule-based classification if API fails

## Dependencies
- Phase 1 (SD-001) must be complete
- Use existing OpenAI integration patterns from RAG module

## Acceptance Criteria
- [ ] Classification returning valid categories
- [ ] Entity extraction finding key information
- [ ] Confidence scores calibrated
- [ ] Fallback working when API unavailable
- [ ] Unit tests with mocked API

Include workflow: adw_plan_build_test_iso model_set heavy
```

---

**Phase 2 Parallel Execution:**
```bash
cd adws
uv run adw_plan_build_test_iso.py SD-002 &
uv run adw_plan_build_test_iso.py SD-003 &
uv run adw_plan_build_test_iso.py SD-004 &
uv run adw_plan_build_test_iso.py SD-005 &
wait
```

---

## Phase 3: API Routes (4 Parallel)

### SD-006: Ticket Routes

**Title:** `[ServiceDesk] Phase 3A: Ticket API Routes`

**Body:**
```markdown
## Context
**Project:** ServiceDesk AI Implementation for System Zero
**Overview:** We are building an AI-powered IT support platform with intelligent ticket management, automated classification, multi-channel support (web, email, WhatsApp), knowledge base, technician dashboard, and analytics. The implementation is divided into 8 phases with 25 total issues.

**Current Phase:** Phase 3 of 8 - API Routes
**Current Issue:** SD-006 (Issue 6 of 25)
**Parallel Execution:** YES - This issue runs IN PARALLEL with SD-007, SD-008, and SD-009. All 4 API route files are being developed simultaneously in separate worktrees.

**What was completed:** Phase 1 (SD-001) and Phase 2 (SD-002 to SD-005) - Database, DTOs, and all backend services are now available.
**What comes next:** After Phase 3, we move to Phase 4 (Frontend Core), Phase 6 (Multi-Channel), and Phase 7 (AI Enhancement) which can run in parallel.

---

## Description
Implement FastAPI routes for ticket management.

## Requirements

### File: backend/src/adapter/rest/servicedesk_routes.py

#### Endpoints
POST   /api/servicedesk/tickets              - Create ticket
GET    /api/servicedesk/tickets              - List tickets (with filters)
GET    /api/servicedesk/tickets/{id}         - Get single ticket
PUT    /api/servicedesk/tickets/{id}         - Update ticket
DELETE /api/servicedesk/tickets/{id}         - Delete ticket
POST   /api/servicedesk/tickets/{id}/assign  - Assign to technician
PUT    /api/servicedesk/tickets/{id}/status  - Update status
GET    /api/servicedesk/tickets/{id}/messages - Get conversation
POST   /api/servicedesk/tickets/{id}/messages - Add message
POST   /api/servicedesk/tickets/{id}/attachments - Upload file
GET    /api/servicedesk/tickets/my           - User's own tickets
GET    /api/servicedesk/tickets/assigned     - Technician's assigned
GET    /api/servicedesk/tickets/backlog      - Unassigned tickets

#### RBAC
- End users: Create tickets, view own tickets
- Technicians: View all, assign, update status
- Admins: Full access

## Dependencies
- Phase 2 (SD-002, SD-005) must be complete

## Acceptance Criteria
- [ ] All endpoints functional
- [ ] RBAC enforced
- [ ] File upload working
- [ ] Pagination implemented
- [ ] OpenAPI docs generated

Include workflow: adw_plan_build_test_iso
```

---

### SD-007: Knowledge Base Routes

**Title:** `[ServiceDesk] Phase 3B: Knowledge Base API Routes`

**Body:**
```markdown
## Context
**Project:** ServiceDesk AI Implementation for System Zero
**Overview:** We are building an AI-powered IT support platform with intelligent ticket management, automated classification, multi-channel support (web, email, WhatsApp), knowledge base, technician dashboard, and analytics. The implementation is divided into 8 phases with 25 total issues.

**Current Phase:** Phase 3 of 8 - API Routes
**Current Issue:** SD-007 (Issue 7 of 25)
**Parallel Execution:** YES - This issue runs IN PARALLEL with SD-006, SD-008, and SD-009. All 4 API route files are being developed simultaneously in separate worktrees.

**What was completed:** Phase 1 (SD-001) and Phase 2 (SD-002 to SD-005) - Database, DTOs, and all backend services are now available.
**What comes next:** After Phase 3, we move to Phase 4 (Frontend Core), Phase 6 (Multi-Channel), and Phase 7 (AI Enhancement) which can run in parallel.

---

## Description
Implement FastAPI routes for knowledge base.

## Requirements

### File: backend/src/adapter/rest/servicedesk_routes.py (add to existing)

#### Endpoints
GET    /api/servicedesk/knowledge           - List articles
POST   /api/servicedesk/knowledge           - Create article (admin)
GET    /api/servicedesk/knowledge/{id}      - Get article
PUT    /api/servicedesk/knowledge/{id}      - Update article (admin)
DELETE /api/servicedesk/knowledge/{id}      - Delete article (admin)
GET    /api/servicedesk/knowledge/search    - Semantic search
POST   /api/servicedesk/knowledge/suggest   - Get suggestions for ticket
POST   /api/servicedesk/knowledge/{id}/rate - Rate helpfulness

#### RBAC
- All authenticated: Read, search, rate
- Admins only: Create, update, delete

## Dependencies
- Phase 2 (SD-003) must be complete

## Acceptance Criteria
- [ ] All endpoints functional
- [ ] Search returning relevant results
- [ ] Suggestions working during ticket creation
- [ ] RBAC enforced

Include workflow: adw_plan_build_test_iso
```

---

### SD-008: Technician Routes

**Title:** `[ServiceDesk] Phase 3C: Technician Management API Routes`

**Body:**
```markdown
## Context
**Project:** ServiceDesk AI Implementation for System Zero
**Overview:** We are building an AI-powered IT support platform with intelligent ticket management, automated classification, multi-channel support (web, email, WhatsApp), knowledge base, technician dashboard, and analytics. The implementation is divided into 8 phases with 25 total issues.

**Current Phase:** Phase 3 of 8 - API Routes
**Current Issue:** SD-008 (Issue 8 of 25)
**Parallel Execution:** YES - This issue runs IN PARALLEL with SD-006, SD-007, and SD-009. All 4 API route files are being developed simultaneously in separate worktrees.

**What was completed:** Phase 1 (SD-001) and Phase 2 (SD-002 to SD-005) - Database, DTOs, and all backend services are now available.
**What comes next:** After Phase 3, we move to Phase 4 (Frontend Core), Phase 6 (Multi-Channel), and Phase 7 (AI Enhancement) which can run in parallel.

---

## Description
Implement FastAPI routes for technician management.

## Requirements

### File: backend/src/adapter/rest/servicedesk_routes.py (add to existing)

#### Endpoints
GET    /api/servicedesk/technicians              - List technicians
POST   /api/servicedesk/technicians              - Create technician (admin)
GET    /api/servicedesk/technicians/{id}         - Get technician
PUT    /api/servicedesk/technicians/{id}         - Update technician
PUT    /api/servicedesk/technicians/{id}/status  - Activate/deactivate
GET    /api/servicedesk/technicians/{id}/performance - Performance metrics
POST   /api/servicedesk/technicians/login        - Technician login
POST   /api/servicedesk/technicians/change-password - Change password
POST   /api/servicedesk/technicians/forgot-password - Request reset
POST   /api/servicedesk/technicians/reset-password - Complete reset

#### RBAC
- Admins: Full management
- Technicians: View own profile, change password

## Dependencies
- Phase 2 (SD-004) must be complete

## Acceptance Criteria
- [ ] All endpoints functional
- [ ] Authentication working
- [ ] Password reset flow complete
- [ ] RBAC enforced

Include workflow: adw_plan_build_test_iso
```

---

### SD-009: Analytics Routes

**Title:** `[ServiceDesk] Phase 3D: Analytics API Routes`

**Body:**
```markdown
## Context
**Project:** ServiceDesk AI Implementation for System Zero
**Overview:** We are building an AI-powered IT support platform with intelligent ticket management, automated classification, multi-channel support (web, email, WhatsApp), knowledge base, technician dashboard, and analytics. The implementation is divided into 8 phases with 25 total issues.

**Current Phase:** Phase 3 of 8 - API Routes
**Current Issue:** SD-009 (Issue 9 of 25)
**Parallel Execution:** YES - This issue runs IN PARALLEL with SD-006, SD-007, and SD-008. All 4 API route files are being developed simultaneously in separate worktrees.

**What was completed:** Phase 1 (SD-001) and Phase 2 (SD-002 to SD-005) - Database, DTOs, and all backend services are now available.
**What comes next:** After Phase 3, we move to Phase 4 (Frontend Core), Phase 6 (Multi-Channel), and Phase 7 (AI Enhancement) which can run in parallel.

---

## Description
Implement FastAPI routes for analytics and reporting.

## Requirements

### File: backend/src/adapter/rest/servicedesk_routes.py (add to existing)

#### Endpoints
GET    /api/servicedesk/analytics/overview        - Dashboard KPIs
GET    /api/servicedesk/analytics/tickets         - Ticket metrics
GET    /api/servicedesk/analytics/satisfaction    - Satisfaction scores
GET    /api/servicedesk/analytics/sla             - SLA compliance
GET    /api/servicedesk/analytics/technicians     - Team performance
GET    /api/servicedesk/analytics/categories      - Category breakdown
GET    /api/servicedesk/analytics/trends          - Time-series data

#### Features
- Date range filtering
- Export to CSV/Excel
- Real-time calculation

#### RBAC
- Admins and Managers only

## Dependencies
- Phase 2 services must be complete

## Acceptance Criteria
- [ ] All analytics endpoints returning accurate data
- [ ] Date filtering working
- [ ] Performance optimized for large datasets
- [ ] RBAC enforced

Include workflow: adw_plan_build_test_iso
```

---

**Phase 3 Parallel Execution:**
```bash
cd adws
uv run adw_plan_build_test_iso.py SD-006 &
uv run adw_plan_build_test_iso.py SD-007 &
uv run adw_plan_build_test_iso.py SD-008 &
uv run adw_plan_build_test_iso.py SD-009 &
wait
```

---

## Phase 4: Frontend Core (Sequential Start, Then Parallel)

### SD-010: Frontend Types & Service Layer

**Title:** `[ServiceDesk] Phase 4A: Frontend Types and API Service`

**Body:**
```markdown
## Context
**Project:** ServiceDesk AI Implementation for System Zero
**Overview:** We are building an AI-powered IT support platform with intelligent ticket management, automated classification, multi-channel support (web, email, WhatsApp), knowledge base, technician dashboard, and analytics. The implementation is divided into 8 phases with 25 total issues.

**Current Phase:** Phase 4 of 8 - Frontend Core
**Current Issue:** SD-010 (Issue 10 of 25)
**Parallel Execution:** NO - This issue must complete FIRST within Phase 4 because it creates the TypeScript types and service layer that SD-011, SD-012, and SD-013 depend on. After this completes, the remaining 3 issues in Phase 4 run in parallel.

**What was completed:** Phase 1-3 (SD-001 to SD-009) - Full backend is now available with database, services, and API routes.
**What comes next:** SD-011, SD-012, SD-013 will run in parallel after this completes.

---

## Description
Create TypeScript types and API service layer for ServiceDesk frontend.

## Requirements

### File: frontend/src/types/servicedesk.ts
// Enums
export type TicketStatus = 'backlog' | 'in_progress' | 'waiting_user' | 'resolved' | 'closed';
export type TicketPriority = 'low' | 'medium' | 'high' | 'urgent';
export type TicketCategory = 'technical' | 'billing' | 'general' | 'escalation';
export type TicketChannel = 'web' | 'email' | 'whatsapp';

// Interfaces
export interface Ticket { ... }
export interface TicketMessage { ... }
export interface Technician { ... }
export interface KnowledgeArticle { ... }
export interface TicketStats { ... }
// ... all required types

### File: frontend/src/services/servicedeskService.ts
export const servicedeskService = {
  // Tickets
  getTickets: (filters) => Promise<Ticket[]>,
  createTicket: (data) => Promise<Ticket>,
  updateTicket: (id, data) => Promise<Ticket>,
  // ... all API methods
};

## Dependencies
- Phase 3 (API routes) must be complete

## Acceptance Criteria
- [ ] All types defined matching backend DTOs
- [ ] Service methods for all endpoints
- [ ] Proper error handling
- [ ] TypeScript strict mode passing

Include workflow: adw_plan_build_iso
```

---

### SD-011: ServiceDesk Dashboard Page

**Title:** `[ServiceDesk] Phase 4B: Dashboard Page with Stats`

**Body:**
```markdown
## Context
**Project:** ServiceDesk AI Implementation for System Zero
**Overview:** We are building an AI-powered IT support platform with intelligent ticket management, automated classification, multi-channel support (web, email, WhatsApp), knowledge base, technician dashboard, and analytics. The implementation is divided into 8 phases with 25 total issues.

**Current Phase:** Phase 4 of 8 - Frontend Core
**Current Issue:** SD-011 (Issue 11 of 25)
**Parallel Execution:** YES - This issue runs IN PARALLEL with SD-012 and SD-013 (after SD-010 completes). All 3 frontend components are being developed simultaneously in separate worktrees.

**What was completed:** SD-010 (Frontend types and service layer) just completed.
**What comes next:** After Phase 4, we move to Phase 5 (Frontend Advanced) with 4 more parallel frontend issues.

---

## Description
Create the main ServiceDesk dashboard page with statistics and navigation.

## Requirements

### File: frontend/src/pages/servicedesk/ServicedeskDashboard.tsx

#### Layout
- Header with "Service Desk" title
- Stats cards grid (4 cards):
  - Total Open Tickets
  - Urgent/High Priority
  - Pending Assignment
  - SLA At Risk
- Tab panel:
  - Tab 1: Open Queue (default)
  - Tab 2: Create Ticket
  - Tab 3: Knowledge Base
  - Tab 4: Analytics (admin only)

#### Features
- Real-time stats refresh
- Tab navigation
- Role-based tab visibility
- Responsive design

### File: frontend/src/App.tsx (modify)
- Add route: `/servicedesk` → ServicedeskDashboard

### File: frontend/src/components/ui/FKSidebarWithCollapse.tsx (modify)
- Add ServiceDesk menu section with icons

## Dependencies
- Phase 4A (SD-010) must be complete

## Acceptance Criteria
- [ ] Dashboard rendering with stats
- [ ] Tabs working
- [ ] Route accessible
- [ ] Sidebar navigation added
- [ ] Responsive on mobile

Include workflow: adw_plan_build_iso
```

---

### SD-012: Ticket List Component

**Title:** `[ServiceDesk] Phase 4C: Ticket List and Filter Components`

**Body:**
```markdown
## Context
**Project:** ServiceDesk AI Implementation for System Zero
**Overview:** We are building an AI-powered IT support platform with intelligent ticket management, automated classification, multi-channel support (web, email, WhatsApp), knowledge base, technician dashboard, and analytics. The implementation is divided into 8 phases with 25 total issues.

**Current Phase:** Phase 4 of 8 - Frontend Core
**Current Issue:** SD-012 (Issue 12 of 25)
**Parallel Execution:** YES - This issue runs IN PARALLEL with SD-011 and SD-013 (after SD-010 completes). All 3 frontend components are being developed simultaneously in separate worktrees.

**What was completed:** SD-010 (Frontend types and service layer) just completed.
**What comes next:** After Phase 4, we move to Phase 5 (Frontend Advanced) with 4 more parallel frontend issues.

---

## Description
Create ticket list component with filtering and sorting capabilities.

## Requirements

### File: frontend/src/components/servicedesk/FKServicedeskTicketList.tsx

#### Features
- Data grid with columns:
  - Ticket # (link to detail)
  - Subject
  - Status (color-coded badge)
  - Priority (icon + color)
  - Category
  - Assigned To
  - SLA Countdown (color-coded)
  - Created At
- Filtering by: status, priority, category, assigned, date range
- Sorting by any column
- Pagination

### File: frontend/src/components/servicedesk/FKServicedeskFilterPanel.tsx
- Filter dropdowns
- Date range picker
- Search input
- Clear filters button

### File: frontend/src/components/servicedesk/ServicedeskStatusBadge.tsx
- Status chip with color coding:
  - Backlog: gray
  - In Progress: blue
  - Waiting User: yellow
  - Resolved: green
  - Closed: gray

### File: frontend/src/components/servicedesk/ServicedeskPriorityBadge.tsx
- Priority indicator with icon and color:
  - Urgent: red with alarm icon
  - High: orange
  - Medium: yellow
  - Low: green

## Dependencies
- Phase 4A (SD-010) must be complete

## Acceptance Criteria
- [ ] List rendering with all columns
- [ ] Filtering working
- [ ] Sorting working
- [ ] Pagination functional
- [ ] SLA countdown updating

Include workflow: adw_plan_build_iso
```

---

### SD-013: Ticket Form Component

**Title:** `[ServiceDesk] Phase 4D: Ticket Create/Edit Form`

**Body:**
```markdown
## Context
**Project:** ServiceDesk AI Implementation for System Zero
**Overview:** We are building an AI-powered IT support platform with intelligent ticket management, automated classification, multi-channel support (web, email, WhatsApp), knowledge base, technician dashboard, and analytics. The implementation is divided into 8 phases with 25 total issues.

**Current Phase:** Phase 4 of 8 - Frontend Core
**Current Issue:** SD-013 (Issue 13 of 25)
**Parallel Execution:** YES - This issue runs IN PARALLEL with SD-011 and SD-012 (after SD-010 completes). All 3 frontend components are being developed simultaneously in separate worktrees.

**What was completed:** SD-010 (Frontend types and service layer) just completed.
**What comes next:** After Phase 4, we move to Phase 5 (Frontend Advanced) with 4 more parallel frontend issues.

---

## Description
Create ticket creation and editing form with knowledge base suggestions.

## Requirements

### File: frontend/src/components/forms/FKServicedeskTicketForm.tsx

#### Form Fields
- Subject (TextField, required)
- Description (TextField multiline, required)
- Category (Select dropdown)
- Priority (Select dropdown, default: medium)
- Contact Name (TextField, pre-filled from auth)
- Contact Email (TextField, pre-filled from auth)
- Contact Phone (TextField, optional)
- Attachments (File upload, multiple, max 10MB each)

#### Features
- Real-time knowledge base suggestions as user types
- Display suggested articles in sidebar
- "This solved my problem" button to cancel ticket creation
- Form validation with error messages
- Loading state during submission
- Success confirmation with ticket number

#### Knowledge Suggestions Panel
- Shows up to 5 relevant articles
- Each article: title, snippet, "View" button
- Updates as subject/description changes (debounced)

## Dependencies
- Phase 4A (SD-010) must be complete

## Acceptance Criteria
- [ ] Form validation working
- [ ] File upload functional
- [ ] Knowledge suggestions appearing
- [ ] Submit creating ticket
- [ ] Error handling complete

Include workflow: adw_plan_build_iso
```

---

**Phase 4 Execution:**
```bash
cd adws
# Types first (sequential)
uv run adw_plan_build_iso.py SD-010
# Then parallel
uv run adw_plan_build_iso.py SD-011 &
uv run adw_plan_build_iso.py SD-012 &
uv run adw_plan_build_iso.py SD-013 &
wait
```

---

## Phase 5: Frontend Advanced (4 Parallel)

### SD-014: Ticket Detail View

**Title:** `[ServiceDesk] Phase 5A: Ticket Detail View with Conversation`

**Body:**
```markdown
## Context
**Project:** ServiceDesk AI Implementation for System Zero
**Overview:** We are building an AI-powered IT support platform with intelligent ticket management, automated classification, multi-channel support (web, email, WhatsApp), knowledge base, technician dashboard, and analytics. The implementation is divided into 8 phases with 25 total issues.

**Current Phase:** Phase 5 of 8 - Frontend Advanced
**Current Issue:** SD-014 (Issue 14 of 25)
**Parallel Execution:** YES - This issue runs IN PARALLEL with SD-015, SD-016, and SD-017. All 4 advanced frontend pages are being developed simultaneously in separate worktrees.

**What was completed:** Phase 4 (SD-010 to SD-013) - Frontend types, service layer, dashboard, list, and form components are now available.
**What comes next:** After Phase 5, we move to Phase 8 (Testing & Polish) which is the final phase.

---

## Description
Create comprehensive ticket detail view with conversation thread and actions.

## Requirements

### File: frontend/src/pages/servicedesk/ServicedeskTicketDetail.tsx

#### Layout (Two-column)
**Left Column (70%)**
- Ticket header: # + Subject + Status badge
- SLA countdown bar with color coding
- Requester info card
- Conversation thread (chronological):
  - User comments (left aligned, light bg)
  - Technician comments (right aligned, primary color bg)
  - System messages (center, gray italic)
  - Internal notes (right, yellow bg, tech only)
- Reply input with:
  - Toggle: Public comment / Internal note
  - Rich text editor
  - Attachment upload
  - Submit button

**Right Column (30%)**
- Status selector with action buttons:
  - "Start Work" (Backlog → In Progress)
  - "Mark Waiting" (→ Waiting User)
  - "Resolve" (→ Resolved)
- Assignment dropdown with "Assign to Me"
- Priority selector
- Category selector
- Attachments list
- Satisfaction survey (when Resolved)

### File: frontend/src/App.tsx (modify)
- Add route: `/servicedesk/:ticketId` → ServicedeskTicketDetail

## Dependencies
- Phase 4 components must be complete

## Acceptance Criteria
- [ ] Detail view rendering all sections
- [ ] Conversation thread displaying correctly
- [ ] Reply submission working
- [ ] Status transitions functional
- [ ] Assignment working
- [ ] Satisfaction survey appearing

Include workflow: adw_plan_build_iso
```

---

### SD-015: Knowledge Base Browser

**Title:** `[ServiceDesk] Phase 5B: Knowledge Base Browser and Search`

**Body:**
```markdown
## Context
**Project:** ServiceDesk AI Implementation for System Zero
**Overview:** We are building an AI-powered IT support platform with intelligent ticket management, automated classification, multi-channel support (web, email, WhatsApp), knowledge base, technician dashboard, and analytics. The implementation is divided into 8 phases with 25 total issues.

**Current Phase:** Phase 5 of 8 - Frontend Advanced
**Current Issue:** SD-015 (Issue 15 of 25)
**Parallel Execution:** YES - This issue runs IN PARALLEL with SD-014, SD-016, and SD-017. All 4 advanced frontend pages are being developed simultaneously in separate worktrees.

**What was completed:** Phase 4 (SD-010 to SD-013) - Frontend types, service layer, dashboard, list, and form components are now available.
**What comes next:** After Phase 5, we move to Phase 8 (Testing & Polish) which is the final phase.

---

## Description
Create public knowledge base browser with search and article viewing.

## Requirements

### File: frontend/src/pages/servicedesk/ServicedeskKnowledge.tsx

#### Layout
- Search bar (prominent, top)
- Category sidebar (left)
- Article grid/list (main area)
- Popular articles section

#### Features
- Semantic search with results ranking
- Category filtering
- Article cards with:
  - Title
  - Snippet
  - Category tag
  - View count
  - Helpfulness rating

### File: frontend/src/components/servicedesk/ServicedeskArticleView.tsx
- Full article display with rich text
- "Was this helpful?" Yes/No buttons
- Related articles suggestions
- Back to search button

### File: frontend/src/App.tsx (modify)
- Add route: `/servicedesk/knowledge` → ServicedeskKnowledge
- Add route: `/servicedesk/knowledge/:articleId` → Article detail

## Dependencies
- Phase 4 (SD-010) must be complete

## Acceptance Criteria
- [ ] Search returning relevant results
- [ ] Category filtering working
- [ ] Article view rendering
- [ ] Helpfulness rating functional
- [ ] Responsive design

Include workflow: adw_plan_build_iso
```

---

### SD-016: Analytics Dashboard

**Title:** `[ServiceDesk] Phase 5C: Analytics Dashboard with Charts`

**Body:**
```markdown
## Context
**Project:** ServiceDesk AI Implementation for System Zero
**Overview:** We are building an AI-powered IT support platform with intelligent ticket management, automated classification, multi-channel support (web, email, WhatsApp), knowledge base, technician dashboard, and analytics. The implementation is divided into 8 phases with 25 total issues.

**Current Phase:** Phase 5 of 8 - Frontend Advanced
**Current Issue:** SD-016 (Issue 16 of 25)
**Parallel Execution:** YES - This issue runs IN PARALLEL with SD-014, SD-015, and SD-017. All 4 advanced frontend pages are being developed simultaneously in separate worktrees.

**What was completed:** Phase 4 (SD-010 to SD-013) - Frontend types, service layer, dashboard, list, and form components are now available.
**What comes next:** After Phase 5, we move to Phase 8 (Testing & Polish) which is the final phase.

---

## Description
Create comprehensive analytics dashboard for administrators.

## Requirements

### File: frontend/src/pages/servicedesk/ServicedeskAnalytics.tsx

#### Sections
1. **Overview Cards** (Top row)
   - Total tickets (all time)
   - Average resolution time
   - SLA compliance %
   - Satisfaction score

2. **Ticket Trends** (Line chart)
   - Tickets created vs resolved over time
   - Date range selector

3. **Category Distribution** (Pie/Donut chart)
   - Breakdown by category
   - Click to filter

4. **Technician Performance** (Data table)
   - Name, Resolved count, Avg time, Satisfaction
   - Sortable columns

5. **SLA Compliance** (Bar chart)
   - By priority level
   - Met vs Breached

6. **Satisfaction Breakdown** (Horizontal bars)
   - Overall score
   - Response time rating
   - Technical expertise rating
   - Communication rating

#### Features
- Date range picker (affects all charts)
- Export to CSV button
- Auto-refresh toggle

## Dependencies
- Phase 3 (SD-009) analytics routes must be complete

## Acceptance Criteria
- [ ] All charts rendering with real data
- [ ] Date filtering working
- [ ] Export functional
- [ ] Admin-only access enforced

Include workflow: adw_plan_build_iso
```

---

### SD-017: Technician Management UI

**Title:** `[ServiceDesk] Phase 5D: Technician Management Interface`

**Body:**
```markdown
## Context
**Project:** ServiceDesk AI Implementation for System Zero
**Overview:** We are building an AI-powered IT support platform with intelligent ticket management, automated classification, multi-channel support (web, email, WhatsApp), knowledge base, technician dashboard, and analytics. The implementation is divided into 8 phases with 25 total issues.

**Current Phase:** Phase 5 of 8 - Frontend Advanced
**Current Issue:** SD-017 (Issue 17 of 25)
**Parallel Execution:** YES - This issue runs IN PARALLEL with SD-014, SD-015, and SD-016. All 4 advanced frontend pages are being developed simultaneously in separate worktrees.

**What was completed:** Phase 4 (SD-010 to SD-013) - Frontend types, service layer, dashboard, list, and form components are now available.
**What comes next:** After Phase 5, we move to Phase 8 (Testing & Polish) which is the final phase.

---

## Description
Create admin interface for managing technician accounts.

## Requirements

### File: frontend/src/pages/servicedesk/ServicedeskTechnicians.tsx

#### Layout
- "Add Technician" button (top right)
- Technicians data grid:
  - Name, Username, Email
  - Status (Active/Inactive badge)
  - Expertise tags
  - Current workload (ticket count)
  - Performance score
  - Actions (Edit, Toggle Status)

### File: frontend/src/components/forms/FKServicedeskTechnicianForm.tsx
- Dialog/drawer form for create/edit
- Fields:
  - Full name
  - Email
  - Username (auto-suggest from email)
  - Expertise categories (multi-select)
  - Active status toggle
- Auto-generate password option
- Show generated credentials on success

### Features
- Search technicians by name/email
- Filter by status, expertise
- Bulk actions: Activate/Deactivate selected

## Dependencies
- Phase 3 (SD-008) technician routes must be complete

## Acceptance Criteria
- [ ] List displaying all technicians
- [ ] Create form working
- [ ] Edit form pre-populating
- [ ] Status toggle functional
- [ ] Admin-only access enforced

Include workflow: adw_plan_build_iso
```

---

**Phase 5 Parallel Execution:**
```bash
cd adws
uv run adw_plan_build_iso.py SD-014 &
uv run adw_plan_build_iso.py SD-015 &
uv run adw_plan_build_iso.py SD-016 &
uv run adw_plan_build_iso.py SD-017 &
wait
```

---

## Phase 6: Multi-Channel Integration (3 Issues)

### SD-018: Email Webhook Integration

**Title:** `[ServiceDesk] Phase 6A: Email-to-Ticket Webhook`

**Body:**
```markdown
## Context
**Project:** ServiceDesk AI Implementation for System Zero
**Overview:** We are building an AI-powered IT support platform with intelligent ticket management, automated classification, multi-channel support (web, email, WhatsApp), knowledge base, technician dashboard, and analytics. The implementation is divided into 8 phases with 25 total issues.

**Current Phase:** Phase 6 of 8 - Multi-Channel Integration
**Current Issue:** SD-018 (Issue 18 of 25)
**Parallel Execution:** YES - This issue runs IN PARALLEL with SD-019 (WhatsApp placeholder). Phase 6 can run concurrently with Phase 4, 5, and 7 since they are independent feature tracks.

**What was completed:** Phase 1-3 (SD-001 to SD-009) - Full backend is available.
**What comes next:** SD-020 (Notification Service) depends on SD-018 and SD-019 completing first.

---

## Description
Implement email webhook to automatically create tickets from incoming emails.

## Requirements

### File: backend/src/adapter/rest/servicedesk_webhook_routes.py

#### Endpoint
POST /api/servicedesk/webhooks/email

#### Processing
1. Parse email headers (From, Subject, In-Reply-To)
2. Extract body content (handle MIME multipart)
3. Download attachments
4. Detect if reply to existing ticket (In-Reply-To header)
5. If new: Create ticket with AI classification
6. If reply: Add message to existing ticket thread
7. Send confirmation email to sender

#### Email Parsing
- Handle plain text and HTML bodies
- Extract text from HTML
- Handle encoded subjects
- Parse email addresses

### File: backend/src/core/servicios/servicedesk/email_service.py
- Email parsing logic
- Reply detection
- Confirmation email sending

## Dependencies
- Phase 2 (SD-002, SD-005) must be complete

## Acceptance Criteria
- [ ] Webhook receiving emails
- [ ] New tickets created correctly
- [ ] Replies appended to threads
- [ ] Attachments saved
- [ ] Confirmation emails sent

Include workflow: adw_plan_build_test_iso
```

---

### SD-019: WhatsApp/Kapso.ai Integration (Placeholder)

**Title:** `[ServiceDesk] Phase 6B: WhatsApp Integration Structure (Kapso.ai Ready)`

**Body:**
```markdown
## Context
**Project:** ServiceDesk AI Implementation for System Zero
**Overview:** We are building an AI-powered IT support platform with intelligent ticket management, automated classification, multi-channel support (web, email, WhatsApp), knowledge base, technician dashboard, and analytics. The implementation is divided into 8 phases with 25 total issues.

**Current Phase:** Phase 6 of 8 - Multi-Channel Integration
**Current Issue:** SD-019 (Issue 19 of 25)
**Parallel Execution:** YES - This issue runs IN PARALLEL with SD-018 (Email webhook). Phase 6 can run concurrently with Phase 4, 5, and 7 since they are independent feature tracks.

**What was completed:** Phase 1-3 (SD-001 to SD-009) - Full backend is available.
**What comes next:** SD-020 (Notification Service) depends on SD-018 and SD-019 completing first.

---

## Description
Create placeholder structure for WhatsApp integration via Kapso.ai. Full integration will be completed when Kapso.ai API access is available.

## Requirements

### File: backend/src/adapter/rest/servicedesk_webhook_routes.py (add)

#### Endpoints (Placeholder)
GET  /api/servicedesk/webhooks/whatsapp  - Webhook verification
POST /api/servicedesk/webhooks/whatsapp  - Message receiver (placeholder)

#### Interface Definition
Define interfaces for future Kapso.ai integration:
- `WhatsAppMessage` - Incoming message structure
- `WhatsAppResponse` - Outgoing message structure
- `KapsoWebhookPayload` - Kapso.ai specific payload format

### File: backend/src/core/servicios/servicedesk/whatsapp_service.py
Create service with placeholder methods:
- `parse_incoming_message(payload)` - Parse Kapso.ai webhook
- `create_ticket_from_whatsapp(message)` - Ticket creation logic
- `send_whatsapp_notification(phone, message)` - Placeholder for outbound
- Configuration for Kapso.ai API credentials

### Message Types to Support (Future)
- text - Create/update ticket
- image - Attachment
- document - Attachment
- audio - Transcribe and attach

## Note
Full Kapso.ai integration will be implemented when API access is provisioned.
Current implementation focuses on:
1. Database schema ready for WhatsApp channel
2. Service interface defined
3. Webhook endpoints ready to receive messages
4. Ticket creation logic reusable from email channel

## Dependencies
- Phase 2 (SD-002, SD-005) must be complete

## Acceptance Criteria
- [ ] Webhook endpoints responding
- [ ] Service interfaces defined
- [ ] Database supports whatsapp channel
- [ ] Documentation for Kapso.ai integration

Include workflow: adw_plan_build_iso
```

---

### SD-020: Notification Service

**Title:** `[ServiceDesk] Phase 6C: Multi-Channel Notification Service`

**Body:**
```markdown
## Context
**Project:** ServiceDesk AI Implementation for System Zero
**Overview:** We are building an AI-powered IT support platform with intelligent ticket management, automated classification, multi-channel support (web, email, WhatsApp), knowledge base, technician dashboard, and analytics. The implementation is divided into 8 phases with 25 total issues.

**Current Phase:** Phase 6 of 8 - Multi-Channel Integration
**Current Issue:** SD-020 (Issue 20 of 25)
**Parallel Execution:** NO - This issue must run AFTER SD-018 and SD-019 complete because it depends on both email and WhatsApp services being available.

**What was completed:** SD-018 (Email) and SD-019 (WhatsApp placeholder) just completed.
**What comes next:** After Phase 6, Phase 8 (Testing & Polish) completes the implementation.

---

## Description
Implement unified notification service for email and WhatsApp notifications.

## Requirements

### File: backend/src/core/servicios/servicedesk/notification_service.py

#### Notification Types
- `ticket_created` - Confirmation to requester
- `ticket_assigned` - Alert to technician
- `status_changed` - Update to requester
- `new_message` - Alert to relevant party
- `sla_warning` - Alert to technician + admin
- `ticket_resolved` - Satisfaction survey link

#### Channel Selection
- Determine channel based on ticket origin (web→email, whatsapp→whatsapp)
- Fall back to email if WhatsApp fails

#### Templates
- Define email templates with placeholders
- Define WhatsApp message templates

### File: backend/src/core/servicios/servicedesk/email_sender.py
- SMTP/API email sending
- Template rendering

## Dependencies
- Phase 6A and 6B (SD-018, SD-019)

## Acceptance Criteria
- [ ] All notification types working
- [ ] Email sending functional
- [ ] WhatsApp sending functional
- [ ] Channel fallback working
- [ ] Templates rendering correctly

Include workflow: adw_plan_build_test_iso
```

---

**Phase 6 Execution:**
```bash
cd adws
uv run adw_plan_build_test_iso.py SD-018 &
uv run adw_plan_build_iso.py SD-019 &
wait
uv run adw_plan_build_test_iso.py SD-020
```

---

## Phase 7: AI Enhancement (3 Parallel)

### SD-021: Smart Routing Algorithm

**Title:** `[ServiceDesk] Phase 7A: Smart Routing Auto-Assignment`

**Body:**
```markdown
## Context
**Project:** ServiceDesk AI Implementation for System Zero
**Overview:** We are building an AI-powered IT support platform with intelligent ticket management, automated classification, multi-channel support (web, email, WhatsApp), knowledge base, technician dashboard, and analytics. The implementation is divided into 8 phases with 25 total issues.

**Current Phase:** Phase 7 of 8 - AI Enhancement
**Current Issue:** SD-021 (Issue 21 of 25)
**Parallel Execution:** YES - This issue runs IN PARALLEL with SD-022 and SD-023. Phase 7 can run concurrently with Phase 4, 5, and 6 since they are independent feature tracks.

**What was completed:** Phase 1-3 (SD-001 to SD-009) - Full backend with ticket and technician services is available.
**What comes next:** After Phase 7, Phase 8 (Testing & Polish) completes the implementation.

---

## Description
Implement intelligent auto-assignment based on expertise, workload, and performance.

## Requirements

### File: backend/src/core/servicios/servicedesk/routing_service.py

#### Algorithm Factors
1. **Expertise Match** (40% weight)
   - Category/subcategory specialization
   - Historical resolution success in category

2. **Current Workload** (30% weight)
   - Open tickets assigned
   - SLA pressure of current tickets

3. **Performance Score** (20% weight)
   - Average resolution time
   - Satisfaction ratings

4. **Availability** (10% weight)
   - Active status
   - Last activity timestamp

#### Methods
- `find_best_technician(ticket)` - Returns ranked list
- `auto_assign(ticket_id)` - Assign to top candidate
- `rebalance_workload()` - Redistribute overloaded techs

#### Fallback
- If no qualified technician, leave in Backlog
- Alert admin if backlog grows

## Dependencies
- Phase 2 (SD-002, SD-004) must be complete

## Acceptance Criteria
- [ ] Routing algorithm selecting appropriate technicians
- [ ] Workload balanced across team
- [ ] Fallback working correctly
- [ ] Performance improving with more data

Include workflow: adw_plan_build_test_iso model_set heavy
```

---

### SD-022: Advanced SLA Management

**Title:** `[ServiceDesk] Phase 7B: Advanced SLA Tracking and Alerts`

**Body:**
```markdown
## Context
**Project:** ServiceDesk AI Implementation for System Zero
**Overview:** We are building an AI-powered IT support platform with intelligent ticket management, automated classification, multi-channel support (web, email, WhatsApp), knowledge base, technician dashboard, and analytics. The implementation is divided into 8 phases with 25 total issues.

**Current Phase:** Phase 7 of 8 - AI Enhancement
**Current Issue:** SD-022 (Issue 22 of 25)
**Parallel Execution:** YES - This issue runs IN PARALLEL with SD-021 and SD-023. Phase 7 can run concurrently with Phase 4, 5, and 6 since they are independent feature tracks.

**What was completed:** Phase 1-3 (SD-001 to SD-009) - Full backend with ticket service is available.
**What comes next:** After Phase 7, Phase 8 (Testing & Polish) completes the implementation.

---

## Description
Implement comprehensive SLA management with predictive warnings and escalation.

## Requirements

### File: backend/src/core/servicios/servicedesk/sla_service.py

#### SLA Matrix
SLA_MATRIX = {
    'urgent': {'response': 15, 'resolution': 60},      # minutes
    'high': {'response': 60, 'resolution': 240},
    'medium': {'response': 240, 'resolution': 480},
    'low': {'response': 480, 'resolution': 1440},
}

#### Methods
- `calculate_deadline(priority, impact, created_at)` - Compute SLA deadline
- `get_sla_status(ticket_id)` - Returns: on_track, warning (25% left), breached
- `check_all_slas()` - Background job to check all open tickets
- `escalate_ticket(ticket_id)` - Auto-escalate breached tickets

#### Predictive Warnings
- Predict likelihood of breach based on:
  - Current status
  - Technician workload
  - Historical resolution times
- Alert when >70% likely to breach

### Background Job
- Run every 5 minutes
- Check SLA status of all open tickets
- Send warnings for at-risk tickets
- Auto-escalate breached tickets

## Dependencies
- Phase 2 (SD-002) must be complete

## Acceptance Criteria
- [ ] SLA calculations accurate
- [ ] Warnings sent at correct thresholds
- [ ] Escalation triggering
- [ ] Predictive alerts working
- [ ] Background job running

Include workflow: adw_plan_build_test_iso
```

---

### SD-023: Satisfaction Survey System

**Title:** `[ServiceDesk] Phase 7C: Satisfaction Survey and Feedback`

**Body:**
```markdown
## Context
**Project:** ServiceDesk AI Implementation for System Zero
**Overview:** We are building an AI-powered IT support platform with intelligent ticket management, automated classification, multi-channel support (web, email, WhatsApp), knowledge base, technician dashboard, and analytics. The implementation is divided into 8 phases with 25 total issues.

**Current Phase:** Phase 7 of 8 - AI Enhancement
**Current Issue:** SD-023 (Issue 23 of 25)
**Parallel Execution:** YES - This issue runs IN PARALLEL with SD-021 and SD-022. Phase 7 can run concurrently with Phase 4, 5, and 6 since they are independent feature tracks.

**What was completed:** Phase 1-3 (SD-001 to SD-009) - Full backend is available. Phase 5 (SD-014) ticket detail view should be complete for the frontend component.
**What comes next:** After Phase 7, Phase 8 (Testing & Polish) completes the implementation.

---

## Description
Implement post-resolution satisfaction surveys with multi-dimensional ratings.

## Requirements

### File: backend/src/core/servicios/servicedesk/satisfaction_service.py

#### Survey Dimensions
1. Overall satisfaction (1-5 stars)
2. Response time rating (1-5)
3. Technical expertise rating (1-5)
4. Communication quality rating (1-5)
5. Free-text comments (optional)

#### Methods
- `create_survey_link(ticket_id)` - Generate unique survey URL
- `submit_feedback(ticket_id, ratings, comment)` - Record feedback
- `get_ticket_feedback(ticket_id)` - Retrieve feedback
- `aggregate_technician_ratings(tech_id)` - Calculate averages

### Frontend Component: frontend/src/components/servicedesk/ServicedeskSurveyForm.tsx
- Star rating inputs
- Comment textarea
- Submit button
- Thank you message

#### Trigger
- Survey link sent when ticket status → Resolved
- Survey form appears in ticket detail view
- One submission allowed per ticket

## Dependencies
- Phase 5 (SD-014) ticket detail must be complete

## Acceptance Criteria
- [ ] Survey form rendering
- [ ] All dimensions captured
- [ ] Feedback saved to database
- [ ] Aggregation calculations correct
- [ ] Analytics reflecting feedback

Include workflow: adw_plan_build_iso
```

---

**Phase 7 Parallel Execution:**
```bash
cd adws
uv run adw_plan_build_test_iso.py SD-021 &
uv run adw_plan_build_test_iso.py SD-022 &
uv run adw_plan_build_iso.py SD-023 &
wait
```

---

## Phase 8: Testing & Polish (2 Parallel)

### SD-024: E2E Testing Suite

**Title:** `[ServiceDesk] Phase 8A: End-to-End Test Suite`

**Body:**
```markdown
## Context
**Project:** ServiceDesk AI Implementation for System Zero
**Overview:** We are building an AI-powered IT support platform with intelligent ticket management, automated classification, multi-channel support (web, email, WhatsApp), knowledge base, technician dashboard, and analytics. The implementation is divided into 8 phases with 25 total issues.

**Current Phase:** Phase 8 of 8 - Testing & Polish (FINAL PHASE)
**Current Issue:** SD-024 (Issue 24 of 25)
**Parallel Execution:** YES - This issue runs IN PARALLEL with SD-025 (Documentation). These are the final 2 issues that complete the entire ServiceDesk implementation.

**What was completed:** ALL previous phases (SD-001 to SD-023) - Complete backend, frontend, multi-channel, and AI enhancement features are now available.
**What comes next:** After SD-024 and SD-025 complete, the ServiceDesk module is DONE and ready for production deployment.

---

## Description
Create comprehensive E2E test suite for ServiceDesk module.

## Requirements

### Test Scenarios

#### Ticket Lifecycle
1. Create ticket as end user
2. AI classification assigns category/priority
3. Auto-assign to technician
4. Technician views in dashboard
5. Technician updates status
6. Technician resolves
7. User receives notification
8. User submits satisfaction survey

#### Knowledge Base
1. Admin creates article
2. User searches and finds article
3. Article suggestions during ticket creation
4. User rates article helpfulness

#### Multi-Channel
1. Email creates ticket
2. Email reply updates ticket
3. WhatsApp message creates ticket

#### Analytics
1. Admin views dashboard with correct stats
2. Date filtering updates charts
3. Export to CSV works

### Test Files
- backend/tests/test_servicedesk/
  - test_ticket_service.py
  - test_classification_service.py
  - test_routing_service.py
  - test_api_routes.py

## Dependencies
- All previous phases must be complete

## Acceptance Criteria
- [ ] All test scenarios passing
- [ ] Coverage > 80%
- [ ] No flaky tests
- [ ] Tests run in < 5 minutes

Include workflow: adw_plan_build_test_iso model_set heavy
```

---

### SD-025: Documentation and Polish

**Title:** `[ServiceDesk] Phase 8B: Documentation and UI Polish`

**Body:**
```markdown
## Context
**Project:** ServiceDesk AI Implementation for System Zero
**Overview:** We are building an AI-powered IT support platform with intelligent ticket management, automated classification, multi-channel support (web, email, WhatsApp), knowledge base, technician dashboard, and analytics. The implementation is divided into 8 phases with 25 total issues.

**Current Phase:** Phase 8 of 8 - Testing & Polish (FINAL PHASE)
**Current Issue:** SD-025 (Issue 25 of 25 - FINAL ISSUE)
**Parallel Execution:** YES - This issue runs IN PARALLEL with SD-024 (E2E Tests). These are the final 2 issues that complete the entire ServiceDesk implementation.

**What was completed:** ALL previous phases (SD-001 to SD-023) - Complete backend, frontend, multi-channel, and AI enhancement features are now available.
**What comes next:** After SD-024 and SD-025 complete, the ServiceDesk module is DONE and ready for production deployment.

---

## Description
Create documentation and polish UI for production readiness.

## Requirements

### Documentation

#### File: ai_docs/SERVICEDESK_MODULE_GUIDE.md
1. Module overview
2. Architecture diagram
3. API endpoint reference
4. Database schema
5. AI integration details
6. Configuration options
7. Deployment guide

#### File: ai_docs/SERVICEDESK_USER_GUIDE.md
1. End user guide (creating tickets, tracking)
2. Technician guide (dashboard, workflow)
3. Admin guide (analytics, management)

### UI Polish
- Consistent spacing and alignment
- Loading skeletons for all data views
- Empty states with helpful messages
- Error boundaries with friendly messages
- Mobile responsiveness audit
- Accessibility audit (ARIA labels)

### CLAUDE.md Update
- Add ServiceDesk module section
- Document new routes and services
- Update project structure

## Dependencies
- All previous phases must be complete

## Acceptance Criteria
- [ ] Documentation complete and accurate
- [ ] UI consistent across all views
- [ ] Mobile responsive
- [ ] Accessibility passing
- [ ] CLAUDE.md updated

Include workflow: adw_plan_build_document_iso
```

---

**Phase 8 Parallel Execution:**
```bash
cd adws
uv run adw_plan_build_test_iso.py SD-024 &
uv run adw_plan_build_document_iso.py SD-025 &
wait
```

---

## Complete Execution Script

Save as `adws/run_servicedesk_implementation.sh`:

```bash
#!/bin/bash
# ServiceDesk AI Implementation - Parallel ADW Execution
# Usage: ./run_servicedesk_implementation.sh

set -e
cd "$(dirname "$0")"

echo "=========================================="
echo "ServiceDesk AI Implementation"
echo "=========================================="

# Phase 1: Foundation (Sequential)
echo ""
echo "=== PHASE 1: Foundation ==="
uv run adw_plan_build_test_iso.py SD-001
echo "Phase 1 complete."

# Phase 2: Backend Core Services (4 parallel)
echo ""
echo "=== PHASE 2: Backend Core Services (4 parallel) ==="
uv run adw_plan_build_test_iso.py SD-002 &
uv run adw_plan_build_test_iso.py SD-003 &
uv run adw_plan_build_test_iso.py SD-004 &
uv run adw_plan_build_test_iso.py SD-005 &
wait
echo "Phase 2 complete."

# Phase 3: API Routes (4 parallel)
echo ""
echo "=== PHASE 3: API Routes (4 parallel) ==="
uv run adw_plan_build_test_iso.py SD-006 &
uv run adw_plan_build_test_iso.py SD-007 &
uv run adw_plan_build_test_iso.py SD-008 &
uv run adw_plan_build_test_iso.py SD-009 &
wait
echo "Phase 3 complete."

# Phase 4: Frontend Core (sequential first, then parallel)
echo ""
echo "=== PHASE 4: Frontend Core ==="
uv run adw_plan_build_iso.py SD-010  # Types first
uv run adw_plan_build_iso.py SD-011 &
uv run adw_plan_build_iso.py SD-012 &
uv run adw_plan_build_iso.py SD-013 &
wait
echo "Phase 4 complete."

# Phase 5: Frontend Advanced (4 parallel)
echo ""
echo "=== PHASE 5: Frontend Advanced (4 parallel) ==="
uv run adw_plan_build_iso.py SD-014 &
uv run adw_plan_build_iso.py SD-015 &
uv run adw_plan_build_iso.py SD-016 &
uv run adw_plan_build_iso.py SD-017 &
wait
echo "Phase 5 complete."

# Phase 6: Multi-Channel (sequential dependency)
echo ""
echo "=== PHASE 6: Multi-Channel Integration ==="
uv run adw_plan_build_test_iso.py SD-018 &
uv run adw_plan_build_iso.py SD-019 &
wait
uv run adw_plan_build_test_iso.py SD-020
echo "Phase 6 complete."

# Phase 7: AI Enhancement (3 parallel)
echo ""
echo "=== PHASE 7: AI Enhancement (3 parallel) ==="
uv run adw_plan_build_test_iso.py SD-021 &
uv run adw_plan_build_test_iso.py SD-022 &
uv run adw_plan_build_iso.py SD-023 &
wait
echo "Phase 7 complete."

# Phase 8: Testing & Polish (2 parallel)
echo ""
echo "=== PHASE 8: Testing & Polish (2 parallel) ==="
uv run adw_plan_build_test_iso.py SD-024 &
uv run adw_plan_build_document_iso.py SD-025 &
wait
echo "Phase 8 complete."

echo ""
echo "=========================================="
echo "ServiceDesk AI Implementation Complete!"
echo "=========================================="
```

---

## Files Summary

### Backend Files to Create
```
backend/database/migration_add_servicedesk_tables.sql
backend/src/interface/servicedesk_dtos.py
backend/src/repositorio/servicedesk_repository.py
backend/src/core/servicios/servicedesk/
├── __init__.py
├── ticket_service.py
├── knowledge_service.py
├── technician_service.py
├── classification_service.py
├── routing_service.py
├── sla_service.py
├── satisfaction_service.py
├── email_service.py
├── whatsapp_service.py
└── notification_service.py
backend/src/adapter/rest/servicedesk_routes.py
backend/src/adapter/rest/servicedesk_webhook_routes.py
backend/tests/test_servicedesk/
```

### Frontend Files to Create
```
frontend/src/types/servicedesk.ts
frontend/src/services/servicedeskService.ts
frontend/src/pages/servicedesk/
├── ServicedeskDashboard.tsx
├── ServicedeskTicketDetail.tsx
├── ServicedeskKnowledge.tsx
├── ServicedeskAnalytics.tsx
└── ServicedeskTechnicians.tsx
frontend/src/components/servicedesk/
├── FKServicedeskTicketList.tsx
├── FKServicedeskFilterPanel.tsx
├── ServicedeskStatusBadge.tsx
├── ServicedeskPriorityBadge.tsx
└── ServicedeskArticleView.tsx
frontend/src/components/forms/
├── FKServicedeskTicketForm.tsx
├── FKServicedeskTechnicianForm.tsx
└── ServicedeskSurveyForm.tsx
```

### Files to Modify
```
backend/main.py                                    # Register routes
frontend/src/App.tsx                              # Add routes
frontend/src/components/ui/FKSidebarWithCollapse.tsx  # Add menu
frontend/src/types/index.ts                       # Add role if needed
CLAUDE.md                                         # Add module docs
```
