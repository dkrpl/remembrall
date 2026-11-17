# Remembrall Disaster Recovery Playbook

## Scenario 1: Git Merge Conflict on `.remembrall.md`
**Symptoms:** Git conflict markers (`<<<<<<< HEAD`, `=======`, `>>>>>>> branch`) inside `.remembrall.md`.
**Resolution:**
1. Open `.remembrall.md`.
2. For the Feature Manifest table:
   - If incoming features have distinct IDs (`F-007` vs `F-008`), keep both rows.
   - If incoming features share the same ID but one is `DONE` and the other is `WIP`, keep `DONE`.
3. For Technical Findings: Combine unique invariant bullets.
4. Remove conflict markers and run `python .agents/skills/remembrall/scripts/remembrall.py validate`.

---

## Scenario 2: Corrupted or Malformed Table Syntax
**Symptoms:** Agent fails to parse features or rows are missing delimiters.
**Resolution:**
Run validation:
```bash
python .agents/skills/remembrall/scripts/remembrall.py validate
```
If errors occur:
1. Ensure table header follows exact Markdown syntax: `| ID | Fitur | Status | File Terkait | Catatan |`.
2. Ensure separator row contains `|---|---|---|---|---|`.
3. Check that every row starts and ends with a pipe character (`|`).

---

## Scenario 3: Accidental Deletion of `.remembrall.md`
**Symptoms:** `.remembrall.md` was deleted during a clean or rebase.
**Resolution:**
1. Check Git history: `git checkout HEAD -- .remembrall.md`
2. If untracked, run:
```bash
python .agents/skills/remembrall/scripts/remembrall.py init --template minimal
```
Then run `python .agents/skills/remembrall/scripts/remembrall.py add ...` for major known modules.
