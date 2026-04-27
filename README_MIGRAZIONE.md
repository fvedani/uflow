# 🚀 UFLOW Migration Guide — Quick Summary

## 📌 What is UFLOW?

**Energy Margin Simulator** — Flask web app that calculates profit margins for energy offers (electricity & gas).

- **Users**: Energy agents, providers, administrators
- **Key Features**: Margin calculator, portfolio management, historical simulations, Excel export
- **Stack**: Python Flask + PostgreSQL (already ready!)
- **DB**: 8 tables with user isolation (multi-tenant)

---

## ✨ Why This App is Already Ready for Cloud

| What | Status | Why |
|------|--------|-----|
| PostgreSQL driver | ✅ Ready | `psycopg2-binary` in requirements.txt |
| DB abstraction layer | ✅ Ready | Custom wrapper converts sqlite3 syntax to PostgreSQL |
| Environment config | ✅ Ready | Reads DATABASE_URL from .env |
| Vercel setup | ✅ Ready | vercel.json already configured for Flask |
| No local file deps | ✅ Ready | Only uses /tmp for Excel exports (Vercel supports) |
| Sessions/Auth | ✅ Ready | Flask-Login, no custom session store |

**Translation**: The app only needs 3 things to go live: GitHub repo, Supabase credentials, and Vercel deployment.

---

## 🎯 Migration Overview

### Timeline: ~2 hours
### Effort: Low (mostly copy-paste)
### Risk: Minimal (app is stateless + no breaking changes)

```
STEP 1: GitHub (15 min)
├─ Create repo
├─ git init + git push
└─ Verify files on github.com

STEP 2: Supabase (20 min)
├─ Create PostgreSQL project
├─ Test locally with Flask
└─ Verify data in dashboard

STEP 3: Vercel (15 min)
├─ Import GitHub repo
├─ Add 3 env variables
└─ Deploy

STEP 4: Test (20 min)
├─ Login/register
├─ Run simulations
├─ Export Excel
└─ Verify persistence

STEP 5: Cleanup (10 min)
├─ Remove SQLite files from git
├─ Update .gitignore
└─ Final commit/push
```

---

## 📚 Documentation Files (In This Folder)

1. **ANALISI_ARCHITETTURA.md** (10 min read)
   - Complete app overview
   - Database schema (8 tables)
   - Feature flows
   - Migration checklist

2. **GUIDA_MIGRAZIONE.md** (15 min read)
   - Step-by-step operational guide
   - Exact commands to run
   - Troubleshooting section
   - Verification checklist

3. **DIAGRAMMI_ARCHITETTURA.md** (5 min read)
   - Visual architecture diagrams
   - Request flows
   - Security layers
   - Deployment pipeline

4. **This File** (2 min read)
   - Quick reference
   - Key links
   - Next steps

---

## 🔑 Key Credentials You'll Need

Create accounts at:

| Service | Free Tier | Sign-up |
|---------|-----------|---------|
| **GitHub** | Unlimited public repos | https://github.com/join |
| **Supabase** | 500MB DB, 2GB bandwidth | https://supabase.com |
| **Vercel** | 1 app, auto-scaling | https://vercel.com/signup |

**Total Cost**: $0 (free tier sufficient for demo/testing)

---

## 📋 Checklist Before Starting

- [ ] Python 3.10+ installed (`python --version`)
- [ ] Git installed (`git --version`)
- [ ] Can open PowerShell/Terminal in UFLOW folder
- [ ] GitHub account ready
- [ ] Supabase account ready
- [ ] Vercel account ready

---

## 🔄 Architecture — Before & After

**BEFORE** (Local):
```
You → localhost:5000 → Flask → SQLite (database.db)
```

**AFTER** (Live):
```
Internet User → https://uflow-XXXXX.vercel.app → Flask (Vercel) → PostgreSQL (Supabase)
                                   ↑
                            Auto-deployed from
                            GitHub on git push
```

---

## ⚠️ Important Notes

1. **No Code Changes Needed**
   - App is ready as-is
   - Just swap SQLite → PostgreSQL (already in code)
   - All routes work unchanged

2. **Data Migration**
   - Local SQLite → Supabase PostgreSQL
   - Auto-happens on first app.py run
   - `init_db()` creates all tables
   - `seed_demo()` loads test data for admins

3. **Users & Auth**
   - Admin email (you): `fvedani23@gmail.com`
   - Others can register freely
   - Passwords auto-hashed with bcrypt
   - Sessions stored in Flask (stateless → auto-scalable)

4. **What Happens After Deploy**
   - Every `git push origin main` triggers auto-deploy
   - Vercel rebuilds app (~1 min)
   - Zero downtime (background build)
   - Supabase connection string reused

---

## 🚨 Potential Issues (& Solutions)

| Problem | Fix |
|---------|-----|
| `DATABASE_URL not set` | Add to Vercel env vars (3 vars needed) |
| Connection timeout | Supabase → Settings → Network → Allow all IPs |
| `psycopg2` ImportError | Already in requirements.txt, auto-installed |
| 502 Bad Gateway | Check Vercel Logs → Python traceback |
| Data not persisting | Verify Supabase connection string is correct |
| Excel export fails | Should work (Vercel /tmp is writable) |

---

## 📞 Support Resources

- **Supabase Docs**: https://supabase.com/docs (PostgreSQL, Auth, SQL)
- **Vercel Docs**: https://vercel.com/docs (Deployment, Environment, Logs)
- **Flask Docs**: https://flask.palletsprojects.com (Python web framework)
- **psycopg2 Docs**: https://www.psycopg.org (PostgreSQL driver)

---

## 🎬 Quick Start (5-Min Version)

For impatient people:

```bash
# 1. Create GitHub repo on github.com (browser)

# 2. Push code
cd C:\Users\FedericoVedani-Soevi\Desktop\UFLOW
git init
git add -A
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USER/uflow.git
git push -u origin main

# 3. Create Supabase project (browser) → copy DATABASE_URL

# 4. Test locally
pip install -r requirements.txt
set DATABASE_URL=postgresql://...  # paste from Supabase
python app.py
# http://localhost:5000 → register as admin → see demo data

# 5. Create Vercel project (browser) → import GitHub repo
#    Add 3 env vars: DATABASE_URL, SECRET_KEY, ADMIN_EMAILS

# 6. Vercel auto-deploys → https://uflow-XXXXX.vercel.app ✅
```

---

## 🎯 Success Criteria

After 2 hours, you should have:

- ✅ Live app at https://uflow-XXXXX.vercel.app
- ✅ Supabase PostgreSQL as database
- ✅ GitHub repo as source control
- ✅ Auto-deploy on `git push`
- ✅ Users can register, login, and run simulations
- ✅ Data persists between sessions
- ✅ Admin dashboard visible for admin email

---

## 📈 Next Steps (Optional, Post-Deploy)

1. **Custom Domain**: Vercel → Domains → add yourdomain.com
2. **Slack Notifications**: GitHub → Settings → Webhooks → Slack
3. **Analytics**: Vercel → Metrics → monitor usage
4. **Backup Strategy**: Supabase → Settings → Backups → enable daily
5. **Performance**: Supabase → Logs → optimize slow queries
6. **Security**: Enable 2FA on GitHub, Supabase, Vercel accounts

---

## 📖 Reading Order

1. **This file** (now) — 2 min
2. **GUIDA_MIGRAZIONE.md** — 15 min (follow step-by-step)
3. **DIAGRAMMI_ARCHITETTURA.md** — 5 min (understand flows)
4. **ANALISI_ARCHITETTURA.md** — 10 min (deep dive, reference)

---

## 🎓 Learning Resources

After deployment, explore:

- Supabase SQL Editor: Write custom queries
- Vercel Logs: Watch app execution in real-time
- GitHub Actions: Automate tests (future)
- Flask Blueprints: Refactor routes into modules (future)

---

## 💬 Questions?

- **For Flask/Python issues**: Stack Overflow, Flask Discord
- **For Supabase issues**: Supabase Discord, Docs
- **For Vercel issues**: Vercel Community, Docs
- **For this app**: Check ANALISI_ARCHITETTURA.md for all routes/features

---

**Ready? Start with GUIDA_MIGRAZIONE.md** ⚡

Good luck! 🚀
