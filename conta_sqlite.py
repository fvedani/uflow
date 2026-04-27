import sqlite3

conn = sqlite3.connect('database.db')
tabelle = ['utenti','offerte','fornitori','piani_provvigionali','portafogli','clienti_portafoglio','simulazioni']

for t in tabelle:
    n = conn.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0]
    print(f'{t}: {n}')

conn.close()
