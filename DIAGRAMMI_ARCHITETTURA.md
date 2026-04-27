# 📐 Diagrammi Architettura — UFLOW

---

## 1. Stack Attuale vs Stack Post-Migrazione

### ❌ Stack Attuale (Prima)
```
┌─────────────────────────────────────────┐
│         UTENTE (Browser)                 │
│      http://localhost:5000              │
└────────────────┬────────────────────────┘
                 │ HTTP
                 ▼
┌─────────────────────────────────────────┐
│    FLASK APP (Python)                    │
│  app.py, templates/, routes              │
│  - Login/Registrazione                   │
│  - Gestione offerte, fornitori           │
│  - Simulatore margini                    │
│  - Export Excel, PDF                     │
└────────────────┬────────────────────────┘
                 │ SQL Query
                 ▼
┌─────────────────────────────────────────┐
│   SQLite (Local File)                    │
│   database.db                            │
│   - Utenti                               │
│   - Offerte, Fornitori                   │
│   - Simulazioni, Portafogli              │
└─────────────────────────────────────────┘
```

---

### ✅ Stack Post-Migrazione (Dopo)

```
┌────────────────────────────────────────────────────────────────┐
│                   INTERNET USERS                                │
│         https://uflow-XXXXX.vercel.app                         │
└─────────────────────┬──────────────────────────────────────────┘
                      │ HTTPS
         ┌────────────┴────────────┐
         │                         │
         ▼                         ▼
┌─────────────────┐      ┌──────────────────────┐
│  VERCEL SERVER  │      │  GITHUB REPOSITORY   │
│  (App Host)     │      │  (Source Control)    │
│  - Flask App    │◄─────┤  - app.py            │
│  - Build & Run  │      │  - templates/        │
│  - Auto-deploy  │      │  - requirements.txt  │
│  - Serverless   │      │  - vercel.json       │
└────────┬────────┘      └──────────────────────┘
         │                         ▲
         │ SQL Query               │ Auto-deploy
         │                    (git push main)
         ▼
    ┌──────────────────────────────────────┐
    │   SUPABASE (PostgreSQL Cloud)        │
    │   db.[PROJECT].supabase.co:5432      │
    │                                      │
    │   ├─ utenti                          │
    │   ├─ offerte                         │
    │   ├─ fornitori                       │
    │   ├─ piani_provvigionali             │
    │   ├─ portafogli                      │
    │   ├─ clienti_portafoglio             │
    │   ├─ agenti                          │
    │   └─ simulazioni                     │
    │                                      │
    │   Dashboard SQL Editor               │
    │   Automated Backups                  │
    │   SSL/TLS Encryption                 │
    └──────────────────────────────────────┘
```

---

## 2. Flusso Autenticazione & Autorizzazione

```
┌──────────────────────────┐
│   USER ACCEDE APP        │
│   https://uflow....      │
└────────────┬─────────────┘
             │
             ▼
    ┌────────────────────┐
    │  Già loggato?      │
    │  (Cookie sesssione)│
    └───┬────────┬───────┘
        │YES     │NO
        │        ▼
        │    ┌────────────────────┐
        │    │  /login            │
        │    │  Form registrazione│
        │    │  o login           │
        │    └────────┬───────────┘
        │             │
        │             ▼
        │    ┌────────────────────────────┐
        │    │ Query: SELECT * FROM      │
        │    │   utenti WHERE email=?    │
        │    └────────┬───────────────────┘
        │             │
        │             ├─ Email NON trovata:
        │             │  └─ CREATE user, hash pwd
        │             │
        │             └─ Email trovata:
        │                ├─ check_password_hash?
        │                ├─ YES → login ok
        │                └─ NO  → error "password sbagliata"
        │
        ├─ YES (login ok)
        │  └─ flask_login.login_user()
        │  └─ Set cookie
        │
        ▼
┌──────────────────────────┐
│  DASHBOARD (/)           │
│  User vede i propri dati │
└─────────────────────────┘

┌──────────────────────────┐
│  ROUTE PROTECTION        │
└─────────────────────────┘

@login_required            @admin_required
     │                            │
     ▼                            ▼
Accesso solo se              Accesso solo se
logged_in && 
sesssione valida     is_admin=1 && logged_in

ESEMPI:
✅ /offerte           → @login_required
✅ /fornitori         → @login_required + @admin_required
✅ /simulatore        → @login_required
✅ /admin_utenti      → @login_required + @admin_required
✅ /login             → NO decorator (pubblica)
```

---

## 3. Flusso Simulatore (Cuore dell'App)

```
┌────────────────────────────┐
│  USER accede /simulatore   │
└──────────┬─────────────────┘
           │
           ▼
    ┌──────────────────────┐
    │ GET /simulatore      │
    │ Load form con        │
    │ - Dropdown offerte   │
    │ - Dropdown fornitori │
    │ - Dropdown piani     │
    │ - Input consumo      │
    └──────────┬───────────┘
               │
               ▼
     ┌─────────────────────────────────┐
     │ USER seleziona e clicca "SIMULA"│
     └──────────┬────────────────────────┘
                │ POST /api/simula
                │ {
                │  offerta_id,
                │  fornitore_id,
                │  piano_id,
                │  consumo_medio,
                │  note
                │ }
                ▼
        ┌─────────────────────────────────────┐
        │ QUERY DATABASE                       │
        │ SELECT * FROM offerte WHERE id=?    │
        │ SELECT * FROM fornitori WHERE id=?  │
        │ SELECT * FROM piani WHERE id=?      │
        └──────────────┬──────────────────────┘
                       │
                       ▼
        ┌─────────────────────────────────────┐
        │ CALCOLO (Python function)            │
        │ r = calcola_simulazione(             │
        │   offerta_dict,                      │
        │   fornitore_dict,                    │
        │   piano_dict,                        │
        │   consumo                            │
        │ )                                    │
        │                                      │
        │ FORMULE:                             │
        │ ─────────────────────────────────    │
        │ 1. Margine Spread Annuo:             │
        │    (spread_vend - spread_acq) ×      │
        │    consumo × 365                     │
        │                                      │
        │ 2. Margine QF Annuo:                 │
        │    quota_fissa × 12                  │
        │                                      │
        │ 3. Margine Lordo:                    │
        │    spread_annuo + qf_annuo           │
        │                                      │
        │ 4. Provvigioni Agente/Sub/Area Mgr: │
        │    gettone + ricorrente × consumo    │
        │                                      │
        │ 5. Margine Netto:                    │
        │    lordo - provvigioni_totale        │
        │                                      │
        │ 6. % Margine:                        │
        │    (netto / lordo) × 100             │
        └─────────────────────┬────────────────┘
                              │
                              ▼
                 ┌──────────────────────────┐
                 │ INSERT INTO simulazioni  │
                 │   (calcoli + metadata)   │
                 └──────────────┬───────────┘
                                │
                                ▼
            ┌─────────────────────────────────┐
            │ RESPONSE JSON                    │
            │ {                               │
            │   ok: true,                     │
            │   margine_netto: 45.23,         │
            │   margine_lordo: 120.50,        │
            │   provvigioni: 75.27,           │
            │   ...                           │
            │ }                               │
            └──────────────┬──────────────────┘
                           │
                           ▼
                  ┌──────────────────────┐
                  │ Browser:             │
                  │ - Mostra risultati   │
                  │ - Grafici (Chart.js?)│
                  │ - Button "Salva"     │
                  │ - Button "Export PDF"│
                  │ - Button "Export CSV"│
                  └────────────────────┘

┌─────────────────────────────────────────┐
│  EXPORT EXCEL                           │
├─────────────────────────────────────────┤
│ POST /simulatore/export_excel           │
│  │                                       │
│  ├─ openpyxl.Workbook()                 │
│  │                                       │
│  ├─ Foglio 1: RIEPILOGO                 │
│  │  ├─ Header: marche/logo              │
│  │  ├─ Sezione: Offerta selezionata     │
│  │  ├─ Sezione: Dati fornitore          │
│  │  ├─ Sezione: Piano provvigionale     │
│  │  └─ Tabella risultati (5 col × 15 r) │
│  │                                       │
│  ├─ Foglio 2: STORICO SIMULAZIONI       │
│  │  └─ Tabella con ultime 50 sim        │
│  │                                       │
│  ├─ Formatting (borders, colors, fonts) │
│  │                                       │
│  └─ return send_file(wb.save(...))      │
│      (download .xlsx al browser)        │
└─────────────────────────────────────────┘
```

---

## 4. Schema Database Relazionale

```
┌──────────────────────────────────────────┐
│              UTENTI                      │
├──────────────────────────────────────────┤
│ id (PK)                 [INT]            │
│ email (UNIQUE)          [TEXT]           │
│ password (hash)         [TEXT]           │
│ is_admin                [INT: 0/1]       │
│ created_at              [TIMESTAMP]      │
└──────────────┬───────────────────────────┘
               │ (1 utente ha N offerte)
               │ (1 utente ha N fornitori)
               │ (1 utente ha N piani)
               │ (1 utente ha N portafogli)
               │ (1 utente ha N agenti)
               │ (1 utente ha N simulazioni)
        ┌──────┴──────┐
        │ FK          │ FK
        ▼             ▼
┌───────────────┐    ┌──────────────────────┐
│    OFFERTE    │    │    FORNITORI         │
├───────────────┤    ├──────────────────────┤
│ id (PK)       │    │ id (PK)              │
│ user_id (FK)  │    │ user_id (FK)         │
│ nome_offerta  │    │ nome                 │
│ tipo          │    │ commodity            │
│ canale        │    │ spread_acquisto      │
│ commodity     │    │ costo_gestione_pdp   │
│ tipo_consumo  │    │ tipologia_pagamento  │
│ spread        │    │ is_demo              │
│ quota_fissa   │    │ created_at           │
│ consumo_medio │    └──────────────────────┘
│ ricorrente_*  │
│ sconto        │    ┌──────────────────────┐
│ stato         │    │ PIANI_PROVVIGIONALI  │
│ is_demo       │    ├──────────────────────┤
│ created_at    │    │ id (PK)              │
└───────────────┘    │ user_id (FK)         │
                     │ nome_piano           │
                     │ gettone_agente       │
                     │ gettone_sub_agente   │
                     │ ricorrente_*_agente  │
                     │ ricorrente_*_sub_*   │
                     │ ricorrente_*_area_mgr│
                     │ is_demo              │
                     │ created_at           │
                     └──────────────────────┘

┌─────────────────────────┐
│     PORTAFOGLI          │
├─────────────────────────┤
│ id (PK)                 │
│ user_id (FK)            │
│ nome                    │
│ descrizione             │
│ agente_id (FK)          │
│ is_demo                 │
│ created_at              │
└────────────┬────────────┘
             │ (1 portafoglio ha N clienti)
             │
             ▼
┌───────────────────────────────────────┐
│      CLIENTI_PORTAFOGLIO              │
├───────────────────────────────────────┤
│ id (PK)                               │
│ portafoglio_id (FK)                   │
│ user_id (FK)                          │
│ nome_cliente                          │
│ offerta_id (FK → offerte)             │
│ piano_id (FK → piani_provvigionali)   │
│ consumo_override                      │
│ note                                  │
│ [+ 15 campi calcolati (spread, margin)]
│ created_at                            │
└───────────────────────────────────────┘

┌──────────────────────┐
│      AGENTI          │
├──────────────────────┤
│ id (PK)              │
│ user_id (FK)         │
│ nome                 │
│ cognome              │
│ email                │
│ telefono             │
│ ruolo                │
│ zona                 │
│ parent_id (FK: agente padre, per gerarchia)
│ piano_id (FK)        │
│ data_attivazione     │
│ stato                │
│ target_margine_annuo │
│ target_clienti       │
│ created_at           │
└──────────────────────┘

┌────────────────────────────────┐
│       SIMULAZIONI              │
├────────────────────────────────┤
│ id (PK)                        │
│ user_id (FK)                   │
│ nome_offerta                   │
│ nome_fornitore                 │
│ nome_piano                     │
│ commodity                      │
│ tipo_consumo                   │
│ consumo_medio                  │
│ spread_vendita                 │
│ quota_fissa                    │
│ spread_acquisto                │
│ costo_gestione_pdp             │
│ [+ 7 campi calcolati (margini)]│
│ provvigione_agente             │
│ totale_provvigioni             │
│ note                           │
│ is_demo                        │
│ created_at                     │
└────────────────────────────────┘
```

---

## 5. Flusso Deploy (GitHub → Vercel → Live)

```
┌─────────────────────────────────────┐
│  DEVELOPER                          │
│  (editing app.py / templates)       │
└────────────┬────────────────────────┘
             │ git add -A
             │ git commit -m "..."
             ▼
    ┌────────────────────┐
    │   LOCAL GIT REPO   │
    │   main branch      │
    └────────────┬───────┘
                 │ git push origin main
                 ▼
    ┌────────────────────────────┐
    │   GITHUB REPOSITORY        │
    │   github.com/[user]/uflow  │
    │                            │
    │   - app.py                 │
    │   - requirements.txt        │
    │   - vercel.json            │
    │   - templates/             │
    └────────────┬───────────────┘
                 │ Webhook trigger
                 │ (GitHub → Vercel)
                 ▼
    ┌────────────────────────────┐
    │   VERCEL BUILD SERVER      │
    │   (Automatic)              │
    │                            │
    │   1. Clone repo            │
    │   2. pip install           │
    │      -r requirements.txt   │
    │   3. Build analysis        │
    │   4. Detect Python + Flask │
    │   5. Create container      │
    └────────────┬───────────────┘
                 │ Build SUCCESS
                 ▼
    ┌─────────────────────────────────┐
    │   VERCEL SERVERLESS            │
    │   uflow-XXXXX.vercel.app       │
    │                                │
    │   ✅ Online & Live            │
    │   ✅ HTTPS enabled            │
    │   ✅ SSL cert auto            │
    │   ✅ 99.9% uptime SLA         │
    │                                │
    │   Ogni richiesta HTTP:          │
    │   - Istanzia container         │
    │   - Esegui Flask app           │
    │   - Carica da Supabase DB      │
    │   - Response al browser        │
    └─────────────────────────────────┘

OPZIONALE: Rolling Back
─────────────────────────
Se il deploy fallisce o ha bug:

git revert HEAD              (crea commit che undo il prev)
git push origin main         (Vercel detecta change)
Vercel auto-rollback         (torna a versione prev)
```

---

## 6. Ciclo Vita Richiesta HTTP

```
┌──────────────────────────────────────┐
│  BROWSER USER                        │
│  https://uflow-XXXXX.vercel.app     │
└────────────┬─────────────────────────┘
             │ GET /simulatore
             │ (con cookie session)
             ▼
    ┌────────────────────────────┐
    │  VERCEL LOAD BALANCER      │
    │  (reroute a server pool)   │
    └────────────┬───────────────┘
                 │ Route to Python worker
                 ▼
    ┌────────────────────────────┐
    │  FLASK APP (wsgi server)   │
    │  @app.route('/simulatore') │
    │                            │
    │  1. Controlla @login_req   │
    │  2. Load session cookie    │
    │  3. Query: SELECT from DB  │
    │  4. Render HTML template   │
    │  5. Return response        │
    └────────────┬───────────────┘
                 │ SQL Query
                 ▼
    ┌────────────────────────────┐
    │  SUPABASE POSTGRESQL       │
    │  Query ottimizzata         │
    │  return rows               │
    └────────────┬───────────────┘
                 │ Result set
                 ▼
    ┌────────────────────────────┐
    │  FLASK Template Rendering  │
    │  Jinja2 + CSS/JS           │
    └────────────┬───────────────┘
                 │ HTTP 200 OK
                 │ Content-Type: text/html
                 ▼
    ┌──────────────────────────┐
    │  BROWSER                 │
    │  - Parse HTML            │
    │  - Load CSS              │
    │  - Esegui JavaScript     │
    │  - Render page           │
    └──────────────────────────┘
```

---

## 7. Sicurezza — Layers

```
┌────────────────────────────────────────────┐
│  1. HTTPS/TLS                              │
│  ✅ Vercel auto fornisce SSL certificate   │
│  ✅ Encrypt dati in transit                 │
│  ✅ Previene MITM attacks                   │
└────────────────────────────────────────────┘
                      ▼
┌────────────────────────────────────────────┐
│  2. Password Hashing (werkzeug)            │
│  ✅ generate_password_hash() → bcrypt      │
│  ✅ Stored in DB: $2b$12$XXXXX...         │
│  ✅ Verify: check_password_hash()          │
└────────────────────────────────────────────┘
                      ▼
┌────────────────────────────────────────────┐
│  3. Session Cookies (Flask-Login)          │
│  ✅ HttpOnly flag (no JS access)           │
│  ✅ Secure flag (HTTPS only)               │
│  ✅ SameSite=Lax (CSRF protection)         │
│  ✅ Expiry automatico                      │
└────────────────────────────────────────────┘
                      ▼
┌────────────────────────────────────────────┐
│  4. Role-Based Authorization               │
│  ✅ @login_required → check session valid  │
│  ✅ @admin_required → check is_admin=1     │
│  ✅ user_id filter in queries              │
└────────────────────────────────────────────┘
                      ▼
┌────────────────────────────────────────────┐
│  5. SQL Injection Prevention                │
│  ✅ Parametrized queries (? placeholders)  │
│  ✅ psycopg2 handle escaping               │
│  ✅ NO string concatenation                │
└────────────────────────────────────────────┘
                      ▼
┌────────────────────────────────────────────┐
│  6. Database Encryption (Supabase)         │
│  ✅ SSL/TLS connection                     │
│  ✅ Data at rest encryption (optional)     │
│  ✅ Automated backups encrypted            │
└────────────────────────────────────────────┘
                      ▼
┌────────────────────────────────────────────┐
│  7. Environment Variables (Secrets)        │
│  ✅ DATABASE_URL never in code             │
│  ✅ SECRET_KEY stored in Vercel Vault      │
│  ✅ .env file in .gitignore                │
└────────────────────────────────────────────┘
```

---

## 8. Monitoring & Debugging (Post-Deploy)

```
DASHBOARD VERCEL
┌─────────────────────────────────┐
│ https://vercel.com/dashboard    │
├─────────────────────────────────┤
│ Deployments                      │
│ ├─ Status (✅ SUCCESS / ❌ FAIL) │
│ ├─ Build Log (stdout/stderr)    │
│ └─ Runtime Logs                 │
│                                 │
│ Metrics                         │
│ ├─ Response time                │
│ ├─ Status code distribution     │
│ ├─ Edge location hits           │
│ └─ Bandwidth usage              │
│                                 │
│ Settings                        │
│ ├─ Environment Variables        │
│ ├─ Custom Domains               │
│ └─ GitHub Integration           │
└─────────────────────────────────┘

DASHBOARD SUPABASE
┌──────────────────────────────────┐
│ https://supabase.com/projects    │
├──────────────────────────────────┤
│ SQL Editor                        │
│ ├─ Run test queries              │
│ ├─ Create/modify tables          │
│ └─ Check data integrity          │
│                                  │
│ Logs (real-time)                 │
│ ├─ Query logs                    │
│ ├─ Auth logs                     │
│ └─ API calls logs                │
│                                  │
│ Backups                          │
│ ├─ Daily automatic snapshots     │
│ ├─ Point-in-time recovery        │
│ └─ Manual backup/restore         │
│                                  │
│ Settings                         │
│ ├─ Network IP whitelist          │
│ ├─ Connection pooling            │
│ └─ Password reset                │
└──────────────────────────────────┘

BROWSER DEVELOPER CONSOLE
┌──────────────────────────┐
│ F12 → Console tab        │
├──────────────────────────┤
│ Errors (JS)              │
│ Network tab:             │
│ ├─ API calls             │
│ ├─ Response headers      │
│ ├─ Response body         │
│ └─ Status codes          │
│                          │
│ Application tab:         │
│ ├─ Cookies (session ID)  │
│ ├─ Local Storage         │
│ └─ Session Storage       │
└──────────────────────────┘
```

---

**Fine diagrammi**. Questi visuals descrivono in dettaglio come UFLOW funziona dal design al runtime. 🎯
