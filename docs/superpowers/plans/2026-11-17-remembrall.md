# Remembrall Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Membangun sistem memori terintegrasi `remembrall` yang menggabungkan disk-based state (`planning-with-files`), kurasi anti-bloat (`auto-memory-pro`), dan pemicu otomatis (*always-on rule*) untuk mencegah AI lupa status fitur dan memboroskan token.

**Architecture:** Terdiri dari 3 komponen utama: template berkas status fisik di root proyek (`.remembrall.md`), berkas skill lengkap (`.agents/skills/remembrall/SKILL.md`), dan aturan selalu aktif (`.agents/rules/remembrall.md`) yang mengikat AI untuk auto-check sebelum pemindaian file dan auto-update sebelum menyatakan tugas selesai.

**Tech Stack:** Markdown, Antigravity Customization Architecture (Skills & Rules), YAML Frontmatter, PowerShell / Node.js test validation.

**Spec:** [2026-11-17-remembrall-design.md](file:///D:/Project/skill/docs/superpowers/specs/2026-11-17-remembrall-design.md)

## Global Constraints
- File memori harus disimpan persis di `.remembrall.md` pada root workspace.
- Format skill harus mengikuti spesifikasi standar `SKILL.md` dengan frontmatter `name: remembrall` dan deskripsi yang jelas.
- Batas panjang berkas `.remembrall.md` harus dijaga di bawah 120 baris dengan panduan *pruning* aktif.
- Rule pemicu harus berada di `.agents/rules/remembrall.md` dengan metadata `always_on`.

## Review Focus
- **Input / Kasus 1: Proyek baru tanpa `.remembrall.md` sebelumnya.** Ekspektasi: AI mendeteksi ketiadaan file dan menginisialisasi dari template tanpa melempar error.
- **Input / Kasus 2: Tabel fitur mendekati batas 100 baris.** Ekspektasi: Panduan *pruning* di skill memangkas fitur-fitur berstatus `DONE` lama menjadi 1 baris ringkas per modul.
- **Input / Kasus 3: Tugas selesai tapi AI belum update status.** Ekspektasi: Hard gate pada rule mencegah AI menyatakan tugas selesai sebelum memperbarui `.remembrall.md`.
- **Input / Kasus 4: Pengguna mengedit kode di luar AI.** Ekspektasi: Protokol `sync` dapat mendeteksi perubahan status secara mandiri.
- **Input / Kasus 5: File memori dirusak / invalid format.** Ekspektasi: AI dapat memulihkan format tabel standar tanpa menghapus riwayat fitur yang sudah ada.

---

### Task 1: Buat Template Manifest Memori (`.remembrall.md`)

**Files:**
- Create: `.remembrall.md`
- Test: `tests/verify-manifest.ps1`

**Interfaces:**
- Consumes: Struktur rancangan dari [2026-11-17-remembrall-design.md](file:///D:/Project/skill/docs/superpowers/specs/2026-11-17-remembrall-design.md).
- Produces: Berkas template aktif `.remembrall.md` yang memuat seksi Project Overview, Feature Manifest (Tabel), dan Technical Findings.

- [ ] **Step 1: Tulis skrip verifikasi awal yang memeriksa eksistensi dan struktur `.remembrall.md`**
  Buat `tests/verify-manifest.ps1` untuk memvalidasi keberadaan seksi `# Project Overview`, `## Feature Manifest`, dan `## Technical Findings`.

- [ ] **Step 2: Jalankan skrip verifikasi untuk memastikan gagal (RED)**
  Run: `powershell -ExecutionPolicy Bypass -File tests/verify-manifest.ps1`
  Expected: FAIL karena `.remembrall.md` belum dibuat.

- [ ] **Step 3: Implementasikan template `.remembrall.md`**
  Tulis berkas `.remembrall.md` dengan format tabel standar (`ID`, `Fitur`, `Status`, `File Terkait`, `Catatan`) dan seksi temuan teknis.

- [ ] **Step 4: Jalankan verifikasi untuk memastikan lolos (GREEN)**
  Run: `powershell -ExecutionPolicy Bypass -File tests/verify-manifest.ps1`
  Expected: PASS

- [ ] **Step 5: Commit**
  Run git commit / checkpoint untuk template awal.

---

### Task 2: Buat Skill Definition `remembrall` (`.agents/skills/remembrall/SKILL.md`)

**Files:**
- Create: `.agents/skills/remembrall/SKILL.md`
- Test: `tests/verify-skill.ps1`

**Interfaces:**
- Consumes: Template `.remembrall.md` dari Task 1.
- Produces: Skill `remembrall` dengan instruksi lengkap untuk Check, Update, Pruning, dan Sync.

- [ ] **Step 1: Tulis skrip verifikasi untuk struktur skill**
  Buat `tests/verify-skill.ps1` yang memverifikasi bahwa berkas memiliki frontmatter YAML (`name: remembrall`, `description: Use when...`), serta seksi protokol Update, Pruning, dan Zero Re-scan.

- [ ] **Step 2: Jalankan skrip verifikasi untuk memastikan gagal (RED)**
  Run: `powershell -ExecutionPolicy Bypass -File tests/verify-skill.ps1`
  Expected: FAIL

- [ ] **Step 3: Implementasikan `.agents/skills/remembrall/SKILL.md`**
  Tulis dokumen skill lengkap yang mengadaptasi aturan `planning-with-files` dan `auto-memory-pro`:
  - Kapan membaca memori (sebelum pencarian file).
  - Cara memperbarui tabel status saat fitur selesai.
  - Aturan *pruning* jika baris mendekati 100 baris.
  - Protokol sinkronisasi manual (`git status` sync).

- [ ] **Step 4: Jalankan verifikasi untuk memastikan lolos (GREEN)**
  Run: `powershell -ExecutionPolicy Bypass -File tests/verify-skill.ps1`
  Expected: PASS

- [ ] **Step 5: Commit**
  Run git commit / checkpoint untuk skill definition.

---

### Task 3: Buat Always-On Rule `remembrall` (`.agents/rules/remembrall.md`)

**Files:**
- Create: `.agents/rules/remembrall.md`
- Test: `tests/verify-rule.ps1`

**Interfaces:**
- Consumes: Skill `remembrall` dari Task 2 dan template `.remembrall.md` dari Task 1.
- Produces: Aturan otomatis yang mengikat perilaku AI di setiap interaksi.

- [ ] **Step 1: Tulis skrip verifikasi untuk aturan otomatis**
  Buat `tests/verify-rule.ps1` yang memeriksa apakah rule memiliki metadata frontmatter valid (`trigger: always_on`), instruksi pre-flight (baca `.remembrall.md`), dan post-flight hard gate.

- [ ] **Step 2: Jalankan verifikasi untuk memastikan gagal (RED)**
  Run: `powershell -ExecutionPolicy Bypass -File tests/verify-rule.ps1`
  Expected: FAIL

- [ ] **Step 3: Implementasikan `.agents/rules/remembrall.md`**
  Tulis aturan super ringkas (<15 baris, hemat token) yang mengikat AI untuk:
  1. Membaca `.remembrall.md` sebelum melakukan scan file/codebase besar.
  2. Memperbarui status fitur di `.remembrall.md` sebelum menyatakan pekerjaan selesai.

- [ ] **Step 4: Jalankan verifikasi untuk memastikan lolos (GREEN)**
  Run: `powershell -ExecutionPolicy Bypass -File tests/verify-rule.ps1`
  Expected: PASS

- [ ] **Step 5: Commit**
  Run git commit / checkpoint untuk always-on rule.

---

### Task 4: Uji Integrasi End-to-End (E2E Verification)

**Files:**
- Create: `tests/run-all-tests.ps1`
- Test: Semua berkas yang dihasilkan di Task 1, 2, dan 3.

**Interfaces:**
- Consumes: Task 1, Task 2, Task 3 deliverables.
- Produces: Laporan hasil pengujian keseluruhan yang membuktikan sistem memori siap pakai.

- [ ] **Step 1: Buat runner pengujian menyeluruh `tests/run-all-tests.ps1`**
  Menjalankan validasi manifest, validasi skill, validasi rule, dan simulasi pembacaan memori.

- [ ] **Step 2: Jalankan `tests/run-all-tests.ps1`**
  Run: `powershell -ExecutionPolicy Bypass -File tests/run-all-tests.ps1`
  Expected: Semua pemeriksaan (Manifest, Skill, Rule) menghasilkan status SUCCESS.

- [ ] **Step 3: Verifikasi manual konsumsi baris & token**
  Pastikan `.remembrall.md` berada di bawah batas token dan struktur Markdown terformat dengan rapi.
