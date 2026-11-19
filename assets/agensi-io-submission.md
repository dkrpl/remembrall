# agensi.io Listing Submission Cheat-Sheet

## 1. Skill Name
Remembrall - Zero-Amnesia Persistent Memory Engine

---

## 2. Summary
Remembrall is a zero-dependency persistent memory and deterministic state engine for AI coding agents (Claude Code, Cursor, Windsurf, Codex, Antigravity). It eliminates context amnesia and repetitive workspace scanning, slashing cumulative token consumption by 83% while accelerating multi-turn agent workflows by 4x to 8x.

---

## 3. The request (what the buyer types)
Check our project state in Remembrall: summarize where we left off, what's currently in progress, and let's start working on the next planned feature without re-scanning the entire repo.

---

## 4. The result (what your agent delivers)
I have retrieved your project state directly from `.remembrall.md` without running any broad workspace directory scans or recursive greps (intake consumed ~120 tokens compared to ~15,000 tokens for a blind scan).

### Project State Summary
* **Active Line Budget:** 48 / 120 lines (Token-optimized)
* **Total Tracked Features:** 12 Features (10 Completed, 1 In Progress, 1 Planned)
* **Memory Health:** In Sync (0 unrecorded code drift detected)

---

### Feature Status Manifest

| ID | Feature Name | Status | Scoped Files | Implementation Notes |
|---|---|---|---|---|
| F-009 | JWT Session Revocation | DONE | `src/auth/session.ts`, `tests/auth.test.ts` | Fully verified with Redis blacklist fallback |
| F-010 | User Profile Avatars | DONE | `src/api/users.ts`, `src/storage/s3.ts` | S3 multipart upload with sharp optimization |
| F-011 | Stripe Webhook Listener | WIP | `src/billing/webhook.ts` | Signature verification passed; implementing refund events |
| F-012 | Two-Factor Auth (2FA) | PLANNED | `src/auth/totp.ts`, `src/auth/routes.ts` | RFC 6238 TOTP authenticator app support |

---

### Architectural Invariants & Constraints
1. **Zero-Source-Mutation:** Only update manifest status tables; never truncate or refactor application code outside the current scoped feature.
2. **Offline-First Security:** Never transmit raw credentials or secret keys to third-party logging or cloud analytics.
3. **Verification Hard Gate:** All new authentication routes require 100% test pass rate via `tests/totp.test.ts` before status transitions to `DONE`.

---

### Recommended Next Steps for `F-012` (Two-Factor Authentication)

1. **Pre-Flight Invariant Alignment:**
   Inspect `src/auth/totp.ts` to confirm compatibility with standard authenticator apps (Google Authenticator, 1Password) using the native crypto standard library.
2. **Status Transition:**
   Update the manifest to active development status:
   `remembrall set F-012 WIP --note "Implementing RFC 6238 TOTP generation and token validation"`
3. **Execution & Verification:**
   * Write failing unit tests in `tests/totp.test.ts` testing secret generation, QR URI output, and 30-second time-drift tolerance.
   * Implement minimal functional logic in `src/auth/totp.ts`.
   * Run `remembrall gatekeeper` to verify zero file drift, ensure line budget remains under 120 lines, and mark as `DONE`.

Would you like me to begin scaffolding the unit tests for `F-012`?
