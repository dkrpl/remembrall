# Project Overview
- **Project:** [Web App Name]
- **Core Stack:** TypeScript, Next.js / React, TailwindCSS, PostgreSQL / Prisma
- **Purpose:** Fullstack modern web application with user authentication and dashboard

---

## Feature Manifest
| ID | Fitur | Status | File Terkait | Catatan |
|---|---|---|---|---|
| F-001 | App Scaffolding | DONE | package.json, next.config.ts | Base Next.js configuration |
| F-002 | UI Layout & Design Tokens | DONE | src/components/layout/, globals.css | Responsive layout shell |

---

## Technical Findings
- All database queries MUST run server-side inside Server Actions or route handlers (`src/app/api/`).
- Authentication sessions managed via secure HTTP-only cookies.
