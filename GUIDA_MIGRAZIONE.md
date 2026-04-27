# 🔧 Guida Operativa — Migrazione a Supabase + Vercel + GitHub

**Tempo Totale**: ~2 ore | **Difficoltà**: Bassa (l'app è già pronta)

---

## 📋 Prerequisiti

1. Account GitHub (gratuito) — https://github.com/join
2. Account Supabase (gratuito) — https://supabase.com
3. Account Vercel (gratuito) — https://vercel.com
4. Git installato su PC — https://git-scm.com/
5. Python 3.10+ (già hai)
6. Un terminale (PowerShell, cmd, o bash)

---

## 🎬 Esecuzione

### **STEP 1: Preparazione GitHub (15 min)**

#### 1.1 Crea repo su GitHub
1. Apri https://github.com/new
2. Nome repo: `uflow`
3. Descrizione: `Energy margin simulator — Flask + PostgreSQL + Vercel`
4. Visibility: **Public** (per accesso Vercel/Supabase)
5. **Crea repo**

#### 1.2 Inizializza git localmente
```bash
# Apri PowerShell nella cartella UFLOW
cd C:\Users\FedericoVedani-Soevi\Desktop\UFLOW

# Inizializza repo
git init
git config user.name "Federico Vedani-Soevi"
git config user.email "fvedani23@gmail.com"
```

#### 1.3 Aggiungi file al staging
```bash
git add -A
git status  # Verifica che veda tutti i file
```

#### 1.4 Commit iniziale
```bash
git commit -m "Initial commit: Flask energy simulator with PostgreSQL wrapper, Vercel config, demo data"
```

#### 1.5 Collega al repo remoto e pusha
```bash
git branch -M main
git remote add origin https://github.com/[TUO_USERNAME]/uflow.git
git push -u origin main
# Inserisci username GitHub e personal access token (o password)
```

**Verifica**: Apri https://github.com/[TUO_USERNAME]/uflow → vedi i file

---

### **STEP 2: Setup Supabase (20 min)**

#### 2.1 Crea progetto Supabase
1. Apri https://supabase.com
2. Sign in con GitHub
3. Clicca **"New Project"**
4. **Name**: `uflow`
5. **Database Password**: (genera qualcosa di sicuro, es. `SupabaseSecure2024!`)
6. **Region**: Europe / Frankfurt (più vicino)
7. Clicca **"Create new project"** → attendi 2-3 min

#### 2.2 Recupera Database URL
1. Nel dashboard Supabase, vai a **Settings** (in basso a sx)
2. Clicca **Database**
3. Scroll fino a **Connection String** → **URI**
4. Copia la stringa:
   ```
   postgresql://postgres:[PASSWORD]@db.XXXXXXXXXXXXX.supabase.co:5432/postgres
   ```
   (sostituisci `[PASSWORD]` con la password inserita sopra)

#### 2.3 Configura .env locale
1. Apri il file `.env` nella cartella UFLOW (o crealo se non esiste)
2. Incolla:
   ```
   DATABASE_URL=postgresql://postgres:[PASSWORD]@db.XXXXXXXXXXXXX.supabase.co:5432/postgres
   SECRET_KEY=SupabaseSecret2024!SessionKey!EnergySim123!
   ADMIN_EMAILS=fvedani23@gmail.com
   ```

#### 2.4 Test locale con Supabase
```bash
# Vai nella cartella UFLOW
cd C:\Users\FedericoVedani-Soevi\Desktop\UFLOW

# Installa dipendenze (se non fatto)
pip install -r requirements.txt

# Avvia app
python app.py

# Apri browser: http://localhost:5000
```

**Cosa deve succedere**:
- ✅ Homepage carica
- ✅ Click "Registrati"
- ✅ Registrati con email admin (fvedani23@gmail.com)
- ✅ Login successful
- ✅ Dashboard con dati demo (7 offerte, 8 fornitori)

**Verifica dati in Supabase**:
1. Vai https://supabase.com → Dashboard uflow
2. Clicca **SQL Editor** (in basso a sx)
3. Esegui:
   ```sql
   SELECT COUNT(*) FROM utenti;
   SELECT COUNT(*) FROM offerte;
   ```
   Deve mostrare: utenti=1, offerte=7

---

### **STEP 3: Setup Vercel (15 min)**

#### 3.1 Crea account Vercel
1. Apri https://vercel.com/signup
2. Clicca **"Continue with GitHub"**
3. Autorizza Vercel
4. Sei loggato ✅

#### 3.2 Importa repo GitHub su Vercel
1. Dashboard Vercel → **"Add New..."** → **"Project"**
2. Clicca **"Import Git Repository"**
3. Cerca `uflow` → clicca su quello
4. Clicca **"Import"**

#### 3.3 Configura Environment Variables
Sulla pagina di configurazione del progetto:

**Aggiungi 3 variabili**:

| Key | Value |
|-----|-------|
| `DATABASE_URL` | `postgresql://postgres:[PASSWORD]@db.XXXXX.supabase.co:5432/postgres` |
| `SECRET_KEY` | `SupabaseSecret2024!SessionKey!EnergySim123!` |
| `ADMIN_EMAILS` | `fvedani23@gmail.com` |

Clicca **"Deploy"** → attendi 3-5 minuti

#### 3.4 Accedi al progetto online
- Vercel mostra URL tipo: `https://uflow-XXXXX.vercel.app`
- Apri in browser → deve caricare homepage

**Test**:
- Registrati con una **nuova email** (non admin per ora)
- Login → Dashboard carico con dati
- Apri /simulatore → calcoli funzionano
- Logout

---

### **STEP 4: Test Multi-User (20 min)**

#### 4.1 Test 1: Isolamento dati per user
```
User A (fvedani23@gmail.com - ADMIN)
├─ Offerte: 7 demo
├─ Fornitori: visibili (global)
└─ Portafogli: vuoti (da creare)

User B (test.user.b@gmail.com - NORMAL)
├─ Offerte: 0 (crea proprie)
├─ Fornitori: visibili (global)
└─ Portafogli: 0
```

1. **Accedi come User A (admin)**: 
   - Homepage → Dashboard con dati demo ✅
   - /fornitori → vedi lista (solo admin) ✅

2. **Accedi come User B (normal)**:
   - Homepage → Dashboard vuoto ✅
   - /fornitori → **ACCESSO NEGATO** (forbidden) ✅
   - /offerte → lista vuota ✅
   - Crea offerta → salva ✅
   - Accedi come User A → non vedi offerta User B ✅

#### 4.2 Test 2: Simulatore e Calcoli
```bash
User A:
1. /simulatore
2. Seleziona: FLEXI LUCE DOM + Enel Energia + Base Agente + consumo 3.5
3. Click "Simula"
4. Verifica calcoli:
   - Margine spread annuo ≈ (0.0055 - 0.0018) × 3.5 × 365 ≈ 47€
   - Margine QF annuo = 9.50 × 12 = 114€
   - Lordo ≈ 161€
5. Export Excel → scarica file ✅
```

#### 4.3 Test 3: Persistenza Dati
```bash
User A (on https://uflow-XXXXX.vercel.app):
1. Logout
2. Chiudi browser
3. Attendi 5 secondi
4. Riapri browser, vai URL app
5. Login → dati ancora lì ✅
```

---

### **STEP 5: Pulizia Repository (10 min)**

#### 5.1 Rimuovi file SQLite dal repo
```bash
# Rimuovi file DB locali
git rm --cached database.db database.db-shm database.db-wal

# Aggiorna .gitignore
echo "database.db*" >> .gitignore

# Commit
git add .gitignore
git commit -m "Remove SQLite files, use PostgreSQL only"
git push origin main
```

#### 5.2 Aggiorna file .env.example (template)
Verifica che `.env.example` sia corretto:
```
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.[PROJECT].supabase.co:5432/postgres
SECRET_KEY=cambia-in-produzione
ADMIN_EMAILS=fvedani23@gmail.com
```

Questo è il template che altri sviluppatori copieranno.

---

### **STEP 6: Configura Auto-Deploy (5 min)**

#### 6.1 Verifica che Vercel auto-deploya su push
1. Fai una piccola modifica su GitHub (es. aggiorna README)
2. Commit e push:
   ```bash
   git add .
   git commit -m "Update README with deployment info"
   git push origin main
   ```
3. Vai su https://vercel.com → Dashboard progetto
4. Guarda **Deployments** → vedi nuovo build in progress
5. Attendi completamento (1-2 min)
6. Accedi a https://uflow-XXXXX.vercel.app → vedi la modifica ✅

---

## ✅ Checklist Finale di Verifica

Spunta tutti i box:

### Locale
- [ ] Git repo inizializzato localmente
- [ ] `.env` contiene DATABASE_URL da Supabase
- [ ] `python app.py` parte senza errori
- [ ] http://localhost:5000 carica homepage
- [ ] Puoi registrarti e loggare
- [ ] Dati demo visibili dopo primo login admin

### GitHub
- [ ] Repo creato su https://github.com
- [ ] Tutti i file pushati (vedi su github.com/[user]/uflow)
- [ ] `.gitignore` esclude `.env` e `database.db*`
- [ ] Main branch è default

### Supabase
- [ ] Progetto creato su supabase.com
- [ ] DATABASE_URL funzionante (testato localmente)
- [ ] Schema auto-creato (8 tabelle visibili in SQL Editor)
- [ ] Dati test presenti

### Vercel
- [ ] Progetto creato su vercel.com
- [ ] Collegato al repo GitHub
- [ ] 3 env vars configurate (DATABASE_URL, SECRET_KEY, ADMIN_EMAILS)
- [ ] Deploy SUCCESS (checkmark verde)
- [ ] URL https://uflow-XXXXX.vercel.app funzionante

### Funzionalità Online
- [ ] Homepage carica
- [ ] Registrazione funziona
- [ ] Login funziona
- [ ] Logout funziona
- [ ] /offerte carica (lista vuota per user normal)
- [ ] /simulatore funziona e calcoli sono corretti
- [ ] Export Excel scarica file
- [ ] /fornitori visibile solo per admin
- [ ] Dati persistono dopo logout/login

---

## 🐛 Troubleshooting

### ❌ "ERROR: DATABASE_URL non impostata"
**Soluzione**:
1. Vai Vercel dashboard → Settings → Environment Variables
2. Verifica che `DATABASE_URL` sia presente e corretta
3. Clicca **Redeploy** → Deployments → Re-deploy

### ❌ "Connection timeout su Supabase"
**Soluzione**:
1. Verifica PASSWORD in DATABASE_URL (copia da Supabase → Settings → Database)
2. In Supabase → Settings → Network, abilita "Allow all IP addresses" (dev)
3. Test `psql -c "SELECT 1" postgresql://...`

### ❌ "502 Bad Gateway" su Vercel
**Soluzione**:
1. Vai Vercel → Deployments → click latest → guarda **Logs**
2. Cerca linea rossa (error)
3. Likely cause: import error o missing env var
4. Fix e `git push origin main` per re-deploy

### ❌ "No module named 'flask'"
**Soluzione**: 
1. Vercel automaticamente installa `requirements.txt`
2. Se errore persiste, verifica che `requirements.txt` sia nella root
3. Re-deploy

---

## 📞 Supporto

- **Supabase Docs**: https://supabase.com/docs
- **Vercel Docs**: https://vercel.com/docs
- **Flask Docs**: https://flask.palletsprojects.com
- **psycopg2 Docs**: https://www.psycopg.org

---

**Congratulazioni!** 🎉  
App UFLOW è ora live su internet con database PostgreSQL remoto e auto-deploy da GitHub.

Prossimi passi opzionali:
- [ ] Aggiungi custom domain Vercel
- [ ] Abilita 2FA su Supabase
- [ ] Configura backup automatici Supabase
- [ ] Monitora analytics Vercel (Graphs)
