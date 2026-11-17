# Design Doc: Remembrall (Persistent Feature & Context Memory)

## 1. Intent and The Why
Saat percakapan atau sesi kerja berlangsung lama, model AI mengalami degradasi konteks atau pergantian sesi yang menyebabkan AI lupa fitur mana yang sudah selesai dikerjakan. Akibatnya, AI sering kali memindai ulang seluruh codebase dari awal (*full scan*), yang memakan waktu lama dan memboroskan kuota token secara signifikan (5.000–30.000 token per scan).

`remembrall` dirancang sebagai sistem memori eksternal berbasis file fisik di proyek, mengombinasikan keunggulan arsitektur papan atas di Skill Leaderboard:
- **`planning-with-files` (Manus AI style):** Disk-based persistence (kebal context reset, `/clear`, atau prompt panjang) dan zero-rescan architecture.
- **`auto-memory-pro`:** Kurasi ketat, anti-bloat (<100 baris), dan promosi aturan penting.
- **`remembrall` Always-On Auto-Trigger:** Refleks otomatis membaca di awal dan memperbarui di akhir tugas.

---

## 2. Goals, Non-Goals, and Anti-Goals

### Goals
- Menyediakan manifest status fitur yang super ringkas (<100–120 baris, konsumsi token minimal).
- Memastikan AI selalu membaca status fitur sebelum melakukan eksplorasi file/kode (Zero Re-scan).
- Memastikan AI memperbarui status secara otomatis setelah fitur selesai dikerjakan melalui *hard gate*.
- Menyimpan *Technical Findings* (arsitektur & konvensi kunci) agar AI tidak perlu membaca 20+ file hanya untuk memahami sistem.
- Menjaga persistensi tetap utuh meskipun sesi obrolan di-reset atau dipadatkan (`/clear` / context compaction).

### Non-Goals
- Bukan sistem pencatat log percakapan kata-per-kata (chat history transcript).
- Bukan pengganti version control (Git) atau commit log.

### Anti-Goals
- **Anti-bloat:** Tidak boleh menjadi novel naratif yang panjang. Entri lama yang sudah stabil dirangkum (*pruned*) agar overhead token tetap konstan dan sangat murah (~150-250 token).

---

## 3. Constraints
- Format memori berupa Markdown standar (`.remembrall.md`) di root proyek agar mudah dibaca/diedit manusia.
- Kompatibel dengan sistem kustomisasi Antigravity / Gemini CLI (`.agents/skills/` dan `.agents/rules/`).
- Token overhead pada konteks awal harus tetap terukur (<250 token untuk pembacaan status).

---

## 4. Approaches & Combinations Considered
1. **Standalone Skill (Manual):** AI sering lupa memanggil skill jika konteks percakapan sudah penuh.
2. **Scripted JSON CLI:** Terlalu lambat dan rumit (*overkill*) karena bergantung pada eksekusi subproses terminal.
3. **Hybrid Architecture (Dipilih):**
   - Disk-Based State ala `planning-with-files`.
   - Kurasi & Anti-Bloat ala `auto-memory-pro`.
   - Always-On Auto-Trigger ala `remembrall`.

---

## 5. Architecture & Components

1. **Berkas Memori Aktif (`.remembrall.md`):**
   - Terletak di root proyek.
   - Terdiri dari 3 seksi utama:
     - `# Project Overview`: Ringkasan 2 baris (stack, arsitektur inti).
     - `## Feature Manifest`: Tabel status fitur `[ID | Fitur | Status (DONE/WIP/PLANNED) | File Terkait | Catatan Ringkas]`.
     - `## Technical Findings & Key Decisions`: 3–5 poin arsitektur kunci (misal: ORM yang dipakai, pola routing, aturan khusus).

2. **Skill Definition (`.agents/skills/remembrall/SKILL.md`):**
   - Standard Operating Procedure (SOP) untuk:
     - Format penulisan dan update tabel status.
     - Protokol *pruning* jika baris mendekati 100 baris.
     - Prosedur sinkronisasi manual jika ada perubahan dari luar AI (`git status` sync).

3. **Always-On Rule (`.agents/rules/remembrall.md`):**
   - Pemicu otomatis di setiap sesi dan giliran:
     - **Pre-flight:** Selalu baca `.remembrall.md` sebelum menjalankan pencarian/pemindaian file global.
     - **Post-flight Hard Gate:** Dilarang menyatakan tugas selesai sebelum status fitur dan file terkait di `.remembrall.md` diperbarui.

---

## 6. Known Weaknesses & Mitigations
1. **Desynchronization Risk:** AI menyelesaikan kode tapi lupa catat status.
   - *Mitigasi:* Hard gate pada rule sebelum respon penyelesaian.
2. **Loss of Detail saat Pruning:** Fitur lama kehilangan catatan detail.
   - *Mitigasi:* Detail arsitektur rumit disimpan di `docs/` terpisah, memori aktif hanya menyimpan indeks status.
3. **Manual Edits Drift:** Pengguna mengedit kode di luar AI.
   - *Mitigasi:* Perintah sinkronisasi cepat (`remembrall sync`).
4. **Overhead Token Awal:** Memakan ~150-250 token di awal sesi.
   - *Mitigasi:* Jauh lebih hemat daripada full-scan proyek (yang memakan 5.000–30.000 token).
5. **Git Merge Conflict:** Beberapa orang mengedit `.remembrall.md` bersamaan.
   - *Mitigasi:* Format tabel berbasis baris independen (*append-friendly*).
