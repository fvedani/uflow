"""
UFLOW - Script di fix automatico dei template
Esegui con: python apply_fixes.py  (dalla cartella UFLOW)
"""
import os, sys

BASE = os.path.dirname(os.path.abspath(__file__))
TEMPLATES = os.path.join(BASE, 'templates')

errors = []
fixes_applied = 0

def patch_file(fname, replacements):
    """Applica le sostituzioni a un file template."""
    global fixes_applied, errors
    path = os.path.join(TEMPLATES, fname)
    if not os.path.exists(path):
        errors.append(f"File non trovato: {path}")
        return
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    original = content
    for old, new in replacements:
        if old in content:
            content = content.replace(old, new)
            fixes_applied += 1
            print(f"  ✅ {fname}: sostituito '{old[:60]}...' " if len(old) > 60 else f"  ✅ {fname}: sostituito '{old}'")
        else:
            print(f"  ℹ️  {fname}: pattern non trovato (già applicato?): '{old[:60]}'")
    if content != original:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  💾 {fname}: salvato")

print("=" * 55)
print("UFLOW — Applicazione fix template")
print("=" * 55)

# ──────────────────────────────────────────────
# FIX 1: landing.html — latenza stats bar
# ──────────────────────────────────────────────
print("\n[1/3] Fix landing.html — latenza stat bar...")
patch_file('landing.html', [
    ('data-target="0" data-suffix="ms"', 'data-target="100" data-suffix="ms"'),
    ('>~0<', '>~100<'),
])

# ──────────────────────────────────────────────
# FIX 2: agenti.html — updateParentOptions()
# ──────────────────────────────────────────────
print("\n[2/3] Fix agenti.html — updateParentOptions()...")

UPDATE_PARENT_FN = """
function updateParentOptions() {
  const ruolo = document.getElementById('agRuolo').value;
  const parentGroup = document.getElementById('parentGroup');
  const parentSelect = document.getElementById('agParent');

  if (ruolo === 'DIRETTORE_COMMERCIALE') {
    if (parentGroup) parentGroup.style.display = 'none';
    if (parentSelect) parentSelect.required = false;
    return;
  } else {
    if (parentGroup) parentGroup.style.display = '';
    if (parentSelect) parentSelect.required = true;
  }

  const allowedRoles = {
    'AREA_MANAGER':  ['DIRETTORE_COMMERCIALE'],
    'AGENTE':        ['AREA_MANAGER', 'DIRETTORE_COMMERCIALE'],
    'SUB_AGENTE':    ['AGENTE', 'AREA_MANAGER']
  };
  const allowed = allowedRoles[ruolo] || [];

  if (!parentSelect) return;
  Array.from(parentSelect.options).forEach(opt => {
    if (!opt.value) return;
    const optRole = opt.dataset.role || '';
    opt.style.display = allowed.includes(optRole) ? '' : 'none';
  });
  const sel = parentSelect.options[parentSelect.selectedIndex];
  if (sel && sel.style.display === 'none') parentSelect.value = '';
}
"""

agenti_path = os.path.join(TEMPLATES, 'agenti.html')
if os.path.exists(agenti_path):
    with open(agenti_path, 'r', encoding='utf-8') as f:
        content = f.read()

    if 'function updateParentOptions' not in content:
        # Insert before openModal
        if 'function openModal' in content:
            content = content.replace(
                'function openModal',
                UPDATE_PARENT_FN + '\nfunction openModal',
                1
            )
            with open(agenti_path, 'w', encoding='utf-8') as f:
                f.write(content)
            fixes_applied += 1
            print("  ✅ agenti.html: funzione updateParentOptions() aggiunta")
            print("  💾 agenti.html: salvato")
        else:
            errors.append("agenti.html: openModal non trovato, impossibile inserire updateParentOptions")
    else:
        print("  ℹ️  agenti.html: updateParentOptions già presente")
else:
    errors.append(f"File non trovato: {agenti_path}")

# ──────────────────────────────────────────────
# FIX 3: app.py — /landing sempre visibile (anche se loggati)
# ──────────────────────────────────────────────
print("\n[3/4] Fix app.py — route /landing sempre accessibile...")

app_path = os.path.join(BASE, 'app.py')
if os.path.exists(app_path):
    with open(app_path, 'r', encoding='utf-8') as f:
        app_content = f.read()

    old_landing_route = """@app.route('/landing')
def landing():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('landing.html')"""

    new_landing_route = """@app.route('/landing')
def landing():
    return render_template('landing.html')"""

    if old_landing_route in app_content:
        app_content = app_content.replace(old_landing_route, new_landing_route, 1)
        with open(app_path, 'w', encoding='utf-8') as f:
            f.write(app_content)
        fixes_applied += 1
        print("  ✅ app.py: route /landing ora sempre accessibile")
        print("  💾 app.py: salvato")
    elif new_landing_route in app_content:
        print("  ℹ️  app.py: fix già applicato")
    else:
        print("  ⚠️  app.py: pattern route /landing non trovato — verifica manualmente")
        errors.append("app.py: pattern route /landing non trovato")
else:
    errors.append(f"File non trovato: {app_path}")

# ──────────────────────────────────────────────
# FIX 4: landing.html — sezione FAQ
# ──────────────────────────────────────────────
print("\n[4/4] Fix landing.html — sezione FAQ...")

FAQ_HTML = """
<!-- ═══════════════════════════════════════ FAQ ═══════════════════════════════════════ -->
<section class="faq-section" id="faq">
  <div class="container">
    <div class="section-label">DOMANDE FREQUENTI</div>
    <h2 class="section-title">Tutto quello che devi sapere</h2>
    <p class="section-sub">Risposte rapide alle domande più comuni su UFLOW.</p>

    <div class="faq-grid">

      <div class="faq-item">
        <button class="faq-q" onclick="toggleFaq(this)">
          Come funziona il simulatore di margini?
          <span class="faq-icon">+</span>
        </button>
        <div class="faq-a">
          Inserisci il prezzo di acquisto dell'energia (luce o gas), la struttura tariffaria dell'offerta e i costi fissi associati. UFLOW calcola in tempo reale il margine unitario, il break-even e la redditività stimata del portafoglio.
        </div>
      </div>

      <div class="faq-item">
        <button class="faq-q" onclick="toggleFaq(this)">
          Quali dati servono per avviare una simulazione?
          <span class="faq-icon">+</span>
        </button>
        <div class="faq-a">
          Bastano il prezzo di acquisto (€/MWh o €/Smc), il prezzo di vendita al cliente, le componenti fisse (dispacciamento, trasporto, oneri di sistema) e le provvigioni della rete. Puoi salvare i profili fornitore per riutilizzarli rapidamente.
        </div>
      </div>

      <div class="faq-item">
        <button class="faq-q" onclick="toggleFaq(this)">
          Come vengono calcolate le provvigioni degli agenti?
          <span class="faq-icon">+</span>
        </button>
        <div class="faq-a">
          Ogni agente della rete (Direttore Commerciale, Area Manager, Agente, Sub-agente) ha una struttura provvigionale configurabile. UFLOW applica automaticamente la cascata gerarchica e mostra la provvigione netta per ogni livello, sottraendola dal margine simulato.
        </div>
      </div>

      <div class="faq-item">
        <button class="faq-q" onclick="toggleFaq(this)">
          Posso confrontare più offerte contemporaneamente?
          <span class="faq-icon">+</span>
        </button>
        <div class="faq-a">
          Sì. La sezione <strong>Confronto</strong> permette di affiancare fino a più scenari tariffari e visualizzare a colpo d'occhio quale offerta genera il margine migliore per commodity, fornitore o segmento cliente.
        </div>
      </div>

      <div class="faq-item">
        <button class="faq-q" onclick="toggleFaq(this)">
          Come si gestisce la rete agenti?
          <span class="faq-icon">+</span>
        </button>
        <div class="faq-a">
          Dalla sezione <strong>Rete Agenti</strong> puoi aggiungere, modificare o disattivare agenti, assegnare il ruolo (da Sub-agente fino a Direttore Commerciale) e definire il genitore gerarchico. Ogni agente viene automaticamente incluso nel calcolo delle provvigioni delle simulazioni.
        </div>
      </div>

      <div class="faq-item">
        <button class="faq-q" onclick="toggleFaq(this)">
          I dati inseriti sono al sicuro?
          <span class="faq-icon">+</span>
        </button>
        <div class="faq-a">
          UFLOW gira localmente sulla tua infrastruttura: nessun dato viene inviato a server esterni. L'accesso è protetto da autenticazione e il sistema di ruoli garantisce che ogni utente veda solo le informazioni di sua competenza.
        </div>
      </div>

      <div class="faq-item">
        <button class="faq-q" onclick="toggleFaq(this)">
          Posso aggiungere fornitori personalizzati?
          <span class="faq-icon">+</span>
        </button>
        <div class="faq-a">
          Assolutamente. Dalla sezione <strong>Fornitori</strong> puoi creare schede per ogni grossista o trader, inserire le condizioni di acquisto e richiamarle nelle simulazioni. In questo modo il confronto è sempre basato sui dati reali del tuo portafoglio.
        </div>
      </div>

      <div class="faq-item">
        <button class="faq-q" onclick="toggleFaq(this)">
          Il simulatore copre sia luce che gas?
          <span class="faq-icon">+</span>
        </button>
        <div class="faq-a">
          Sì. UFLOW gestisce entrambe le commodity con unità di misura distinte (MWh per l'energia elettrica, Smc/MWh per il gas naturale) e logiche di calcolo specifiche per ciascun mercato del Mercato Libero italiano.
        </div>
      </div>

    </div>
  </div>
</section>
"""

FAQ_CSS = """
/* ── FAQ ── */
.faq-section{padding:96px 0;background:var(--bg2);}
.faq-section .section-label{text-align:center;font-size:.72rem;font-weight:700;letter-spacing:.15em;color:var(--accent);text-transform:uppercase;margin-bottom:12px;}
.faq-section .section-title{text-align:center;font-size:clamp(1.6rem,3vw,2.4rem);font-weight:700;color:var(--text);margin-bottom:12px;}
.faq-section .section-sub{text-align:center;color:var(--text2);font-size:1rem;margin-bottom:56px;max-width:520px;margin-left:auto;margin-right:auto;}
.faq-grid{display:flex;flex-direction:column;gap:10px;max-width:820px;margin:0 auto;}
.faq-item{border:1px solid var(--border2);border-radius:12px;overflow:hidden;background:var(--bg3);transition:border-color .2s;}
.faq-item:hover{border-color:var(--accent);}
.faq-q{width:100%;background:none;border:none;padding:20px 24px;text-align:left;color:var(--text);font-size:.97rem;font-weight:600;cursor:pointer;display:flex;justify-content:space-between;align-items:center;gap:16px;font-family:inherit;}
.faq-icon{font-size:1.4rem;font-weight:300;color:var(--accent);flex-shrink:0;transition:transform .25s;}
.faq-q.open .faq-icon{transform:rotate(45deg);}
.faq-a{display:none;padding:0 24px 20px;color:var(--text2);font-size:.92rem;line-height:1.7;}
.faq-a strong{color:var(--accent3);}
"""

FAQ_JS = """
function toggleFaq(btn) {
  const isOpen = btn.classList.contains('open');
  document.querySelectorAll('.faq-q.open').forEach(b => {
    b.classList.remove('open');
    b.nextElementSibling.style.display = 'none';
  });
  if (!isOpen) {
    btn.classList.add('open');
    btn.nextElementSibling.style.display = 'block';
  }
}
"""

landing_path = os.path.join(TEMPLATES, 'landing.html')
if os.path.exists(landing_path):
    with open(landing_path, 'r', encoding='utf-8') as f:
        content = f.read()

    changed = False

    # Insert CSS before </style>
    if '.faq-section' not in content and '</style>' in content:
        content = content.replace('</style>', FAQ_CSS + '\n</style>', 1)
        changed = True
        print("  ✅ landing.html: CSS FAQ inserito")

    # Insert JS before </script> (last one before </body>)
    if 'toggleFaq' not in content:
        last_script = content.rfind('</script>')
        if last_script >= 0:
            content = content[:last_script] + FAQ_JS + '\n' + content[last_script:]
            changed = True
            print("  ✅ landing.html: JS FAQ inserito")

    # Insert FAQ section before footer or CTA section
    if 'faq-section' not in content:
        for anchor in ['<section class="cta-section"', '<footer', '</main>']:
            if anchor in content:
                content = content.replace(anchor, FAQ_HTML + '\n' + anchor, 1)
                changed = True
                print(f"  ✅ landing.html: sezione FAQ inserita prima di '{anchor[:30]}'")
                break

    if changed:
        with open(landing_path, 'w', encoding='utf-8') as f:
            f.write(content)
        fixes_applied += 1
        print("  💾 landing.html: salvato")
    else:
        print("  ℹ️  landing.html: FAQ già presente o anchor non trovato")
else:
    errors.append(f"File non trovato: {landing_path}")

# ──────────────────────────────────────────────
# RIEPILOGO
# ──────────────────────────────────────────────
print("\n" + "=" * 55)
print(f"Fix applicati: {fixes_applied}")
if errors:
    print(f"Errori ({len(errors)}):")
    for e in errors:
        print(f"  ❌ {e}")
else:
    print("Nessun errore.")
print("=" * 55)
print("\nRiavvia Flask per vedere le modifiche.")
