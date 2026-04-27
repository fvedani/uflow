# 📊 UFLOW — Analisi Architettura e Piano di Migrazione

## 🎯 Overview Applicazione

**UFLOW** è un simulatore di margini per il mercato dell'energia elettrica e gas in Italia.

- **Stack**: Python + Flask + SQLite (attualmente) → PostgreSQL (via Supabase)
- **Tipo**: Web app full-stack con backend che calcola margini/provvigioni
- **Utenti**: Agenti energetici, fornitori, admin
- **Database**: 7 tabelle principali (utenti, offerte, fornitori, piani_provvigionali, portafogli, clienti_portafoglio, agenti, simulazioni)

---

## 📁 Struttura del Progetto

```
UFLOW/
├── app.py                          # Main Flask app (49KB, tutte le route e logica)
├── requirements.txt                # Dipendenze (Flask, login, openpyxl, psycopg2, reportlab)
├── vercel.json                     # Config Vercel (già presente)
├── .env.example                    # Template variabili d'ambiente
├── .env                            # Vars attuali (DATABASE_URL, SECRET_KEY, ADMIN_EMAILS)
├── database.db*                    # SQLite locale (verrà rimosso)
├── templates/                      # 12 HTML templates
│   ├── base.html                   # Layout + CSS globale
│   ├── login.html                  # Registrazione/login
│   ├── dashboard.html              # Home utente
│   ├── offerte.html                # Gestione offerte CTE
│   ├── fornitori.html              # Gestione fornitori (admin only)
│   ├── provvigioni.html            # Gestione piani provvigionali
│   ├── simulatore.html             # Simulatore margini + export Excel
│   ├── portafogli.html             # Gestione portafogli clienti
│   ├── agenti.html                 # Gestione agenti
│   ├── confronto.html              # Comparativa offerte
│   ├── admin_utenti.html           # Gestione utenti (admin)
│   └── landing.html                # Home page pubblica
└── __pycache__/                    # Compilati Python (ignorare)
```

---

## 🗄️ Schema Database

### 1. **utenti**
```sql
id (SERIAL PK) | email (UNIQUE) | password (hash) | is_admin (0/1) | created_at
```
- Autenticazione con Flask-Login
- is_admin determina accesso a funzioni riservate

### 2. **offerte**
```sql
id | user_id (FK) | nome_offerta | tipo | canale | commodity (LUCE/GAS)
tipo_consumo (DOMESTICO/BUSINESS/INDUSTRIALE) | spread | quota_fissa | consumo_medio
ricorrente_mese | ricorrente_consumo | sconto | stato (ATTIVA/ARCHIVIO)
is_demo | created_at
```
- **Funzione**: Definisce le offerte che il simulatore usa per i calcoli
- **Logica**: Ogni utente ha le proprie offerte (multi-tenant)

### 3. **fornitori**
```sql
id | user_id | nome | commodity | spread_acquisto | costo_gestione_pdp
tipologia_pagamento (Open credit/Anticipo) | is_demo | created_at
```
- **Funzione**: Costi di acquisto energia dalla fonte
- **Gestiti da**: Admin globale (non isolato per user)

### 4. **piani_provvigionali**
```sql
id | user_id | nome_piano | gettone_agente | gettone_sub_agente
ricorrente_mese_agente | ricorrente_consumo_agente | [sub_agente] | [area_manager]
is_demo | created_at
```
- **Funzione**: Definisce come agenti/sub-agenti/area manager vengono pagati
- **Usato in**: Calcolo provvigioni sulla simulazione

### 5. **portafogli**
```sql
id | user_id | nome | descrizione | agente_id | is_demo | created_at
```
- **Funzione**: Raggruppa clienti di un agente

### 6. **clienti_portafoglio**
```sql
id | portafoglio_id | user_id | nome_cliente | offerta_id | piano_id | consumo_override
[+ 15 campi calcolati: nome_offerta, spread_vendita, margine_lordo, etc.]
```
- **Funzione**: Clienti effettivi nel portafoglio con margini calcolati

### 7. **agenti**
```sql
id | user_id | nome | cognome | email | telefono | ruolo (AGENTE/SUB_AGENTE/AREA_MANAGER)
zona | parent_id | piano_id | data_attivazione | stato | note | target_margine_annuo | target_clienti
```
- **Funzione**: Organizzazione gerarchica agenti

### 8. **simulazioni**
```sql
id | user_id | nome_offerta | nome_fornitore | nome_piano | commodity | tipo_consumo
consumo_medio | spread_vendita | quota_fissa | spread_acquisto | costo_gestione_pdp
[+ 7 campi calcolati: margine_spread_annuo, margine_lordo, provvigioni, ecc.]
| note | is_demo | created_at
```
- **Funzione**: Storico delle simulazioni eseguite (ultime 8 settimane con dati demo)

---

## 🔄 Flusso Logico Principale

### 1. **Login/Registrazione** (`/login`, `/register`)
- Crea o verifica utente in DB
- Imposta cookie di sessione Flask-Login
- Carica dati demo se admin e DB vuoto

### 2. **Gestione Offerte** (`/offerte`)
- CRUD offerte (spread, quota fissa, consumi tipo)
- Ogni offerta appartiene a un user

### 3. **Gestione Fornitori** (`/fornitori`, **admin only**)
- CRUD fornitori (spread acquisto, costo gestione)
- Globale (non per user)

### 4. **Gestione Piani Provvigionali** (`/provvigioni`)
- CRUD piani (gettoni e ricorrenti per agente/sub-agente/area manager)
- Per calcolare provvigioni nelle simulazioni

### 5. **Simulatore** (`/simulatore`)
- Utente seleziona: offerta + fornitore + piano + consumo personalizzato
- **Calcolo** (funzione `calcola_simulazione`):
  - Margine spread annuo = (spread_vendita - spread_acquisto) × consumo × 365
  - Margine QF annuo = quota_fissa × 12
  - Margine lordo = spread_annuo + QF_annuo
  - Provvigioni = calcoli complessi su gettoni + ricorrenti
  - Margine netto = lordo - provvigioni
- Salva in tabella `simulazioni`
- **Export Excel**: Genera workbook con dati e grafici

### 6. **Portafogli Clienti** (`/portafogli`)
- Agente crea portafoglio
- Aggiunge clienti con offerta/piano/consumo
- Calcoli ricorsivi di margini per cliente
- Dashboard con KPI (margine medio, n° clienti, targets)

### 7. **Gestione Agenti** (`/agenti`)
- Creazione gerarchia (agente → sub-agente → area manager)
- Tracciamento stato, zona, targets

### 8. **Admin** (`/admin_utenti`)
- Reset utenti
- Gestione globale

---

## 🔐 Autenticazione e Autorizzazione

- **Login**: Flask-Login con `UserMixin` + password hash bcrypt (werkzeug)
- **Ruoli**: 
  - User normale → CRUD propri dati (offerte, portafogli, simulazioni, agenti)
  - Admin (email in `ADMIN_EMAILS`) → gestisce fornitori globali + utenti
- **Protection**: `@login_required`, `@admin_required` su route sensibili

---

## 📊 Librerie Chiave

| Libreria | Uso |
|----------|-----|
| **Flask 3.0.3** | Web framework |
| **Flask-Login 0.6.3** | Gestione sessioni utente |
| **psycopg2-binary** | Driver PostgreSQL (già aggiunto!) |
| **openpyxl 3.1.2** | Export/import Excel |
| **reportlab 4.2.2** | Generazione PDF (simulazioni, portafogli) |
| **python-dotenv 1.0.1** | Caricamento .env |

---

## ✨ Stato Attuale — Già Pronto per Supabase

✅ **Buone notizie:**

1. **app.py ha già un wrapper PostgreSQL** (righe 60-169)
   - `DbWrapper` converte psycopg2 in interfaccia sqlite3-like
   - Traduce `?` → `%s`, `"COL"` → `'COL'`
   - Supporta `lastrowid` per INSERT

2. **DATABASE_URL è già una var d'ambiente**
   - `.env.example` mostra il formato Supabase
   - Code legge da `os.environ.get('DATABASE_URL')`

3. **Vercel.json è già configurato**
   - Usa `@vercel/python` per Flask
   - Route mappatura corretta

4. **Requirements.txt include psycopg2-binary**
   - Già pronto per PostgreSQL

5. **Dati demo sono generati al primo avvio**
   - Quando admin accede, `init_db()` → `seed_demo()`

---

## 🚀 Piano di Migrazione Step-by-Step

### **Fase 1: Preparazione Locale (30 min)**

#### 1.1 Crea repo GitHub
```bash
cd C:\Users\FedericoVedani-Soevi\Desktop\UFLOW
git init
git add -A
git commit -m "Initial commit: Flask energy simulator with PostgreSQL wrapper"
git branch -M main
# Crea repo su github.com, poi:
git remote add origin https://github.com/[user]/uflow.git
git push -u origin main
```

#### 1.2 Configura .env per Supabase locale (test)
- Accedi a [supabase.com](https://supabase.com)
- Crea progetto PostgreSQL gratuito
- Copia `postgresql://...@db.[PROJECT].supabase.co:5432/postgres`
- Aggiorna `.env`:
  ```
  DATABASE_URL=postgresql://postgres:[PASSWORD]@db.[PROJECT].supabase.co:5432/postgres
  SECRET_KEY=<genera con: python -c "import secrets; print(secrets.token_hex(32))">
  ADMIN_EMAILS=fvedani23@gmail.com
  ```

#### 1.3 Test locale con Supabase
```bash
pip install -r requirements.txt
python app.py
# Apri http://localhost:5000
# Login con email admin → dati demo si caricano
# Verifica dati in Supabase dashboard → SQL Editor
```

### **Fase 2: Preparazione Vercel (20 min)**

#### 2.1 Crea account Vercel
- Accedi a [vercel.com](https://vercel.com)
- Connetti GitHub account
- Import UFLOW repo

#### 2.2 Configura Environment Variables su Vercel
Nel Vercel dashboard del progetto → Settings → Environment Variables:
```
DATABASE_URL = postgresql://postgres:[PASSWORD]@db.[PROJECT].supabase.co:5432/postgres
SECRET_KEY = <stesso di locale>
ADMIN_EMAILS = fvedani23@gmail.com
```

#### 2.3 Deploy iniziale
```bash
git push origin main
# Vercel detecta Python + vercel.json → automatico build & deploy
```

### **Fase 3: Validazione Online (30 min)**

#### 3.1 Test post-deploy
- Vai a `https://[progetto].vercel.app`
- Login con email admin
- Verifica:
  - ✅ Pagina login carica
  - ✅ Registrazione funziona
  - ✅ Dashboard si popola con dati demo
  - ✅ Simulatore calcola correttamente
  - ✅ Export Excel scarica
  - ✅ Dati salvati persistono

#### 3.2 Test multi-user
- Crea 2-3 account di test
- Verifica isolamento dati per user (offerte separate)
- Verifica che admin vede tutto

#### 3.3 Logs & Monitoring
- Vercel → Logs: controlla errori runtime
- Supabase → SQL Editor: verifica schema e dati
- Browser console: controlla errori JS

### **Fase 4: Pulizia e Ottimizzazioni (20 min)**

#### 4.1 Rimuovi file SQLite dal repo
```bash
git rm database.db database.db-shm database.db-wal
echo "database.db*" >> .gitignore
git add .gitignore
git commit -m "Remove SQLite files, use PostgreSQL only"
git push origin main
```

#### 4.2 Aggiorna README.md
```markdown
# UFLOW — Energy Margin Simulator

## Quick Start (Desenvolvimento Local)

1. Clone repo e installa dipendenze
   ```bash
   git clone https://github.com/[user]/uflow.git
   pip install -r requirements.txt
   ```

2. Crea account Supabase (free tier OK)
3. Copia URL PostgreSQL nel file `.env`
4. Avvia:
   ```bash
   python app.py
   ```
5. Accedi su http://localhost:5000

## Production (Vercel + Supabase)

- Vercel auto-deploya su push a `main`
- Supabase mantiene i dati
- GitHub repo = source of truth

```

#### 4.3 Configura GitHub branch protection
- Settings → Branches → Add rule per `main`
- Require pull request reviews (opzionale, per piccoli team)

---

## 🐛 Possibili Issues & Soluzioni

| Problema | Causa | Soluzione |
|----------|-------|----------|
| `ERROR: DATABASE_URL not set` | Var non in Vercel env | Aggiungi a Vercel Settings → Env Vars |
| DB connection timeout | Firewall Supabase | Supabase → Settings → Network → Allow all IPs (dev) |
| `psycopg2` import fails | Missing binary | Già in requirements.txt, Vercel installa |
| Export Excel fails | Permesso file temp | Vercel /tmp è writable, OK |
| Slow query on portfolio | N+1 queries | Ottimizzazione futura (index in Supabase) |
| 502 Bad Gateway | App crash | Check Vercel logs per Python traceback |

---

## 📈 Checklist di Verifica Finale

- [ ] **GitHub**: Repo creato, main branch con ultimo codice
- [ ] **Supabase**: Progetto attivo, DATABASE_URL copiato, schema auto-creato
- [ ] **Vercel**: Progetto importato, env vars configurate, deploy SUCCESS
- [ ] **URL Live**: App funziona su https://[progetto].vercel.app
- [ ] **Login**: Registrazione + login + logout funzionano
- [ ] **CRUD**: Create offerta → Read → Update → Delete OK
- [ ] **Simulazioni**: Calcoli corretti, export Excel funziona
- [ ] **Data Persistence**: Logout e riaccess → dati ancora lì
- [ ] **Admin**: Email in ADMIN_EMAILS vede pannello admin
- [ ] **Fornitori**: Solo admin può gestire fornitori
- [ ] **Dati Demo**: Primo accesso admin popola 7 offerte + 8 fornitori + dati test

---

## 🎯 Risultato Finale

| Aspetto | Locale | Online |
|---------|--------|--------|
| **Framework** | Flask | Flask |
| **Database** | PostgreSQL (Supabase) | PostgreSQL (Supabase) |
| **Hosting** | localhost:5000 | vercel.app |
| **Repository** | GitHub | GitHub |
| **Email Sender** | (N/A) | (N/A) |
| **Files** | /tmp (temp Excel) | /tmp (temp Excel) |
| **HTTPS** | ❌ | ✅ |
| **Auto-deploy** | ❌ | ✅ (on git push) |

---

## 💡 Prossimi Step Facoltativi (Post-Deploy)

1. **Email Notifications** (Sendgrid/AWS SES per reminder simulazioni)
2. **Analytics** (Supabase PostgREST API per dashboard real-time)
3. **Caching** (Redis per query pesanti su portafogli grandi)
4. **Mobile Responsive** (Tailwind CSS per migliorare UI attuale)
5. **2FA** (TOTP per admin accounts)
6. **Audit Logs** (Registra chi ha fatto cosa e quando)

---

**Tempo Totale Stimato**: ~2 ore dal repo GitHub al deploy live con Supabase + Vercel ✨
