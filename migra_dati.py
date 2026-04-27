"""
Script di migrazione: copia i dati da SQLite (database.db) a Supabase (PostgreSQL).
Esegui UNA SOLA VOLTA: python migra_dati.py
"""
import sqlite3
import os
import sys

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Legge manualmente .env se dotenv non disponibile
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
if os.path.exists(env_path):
    with open(env_path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, val = line.split('=', 1)
                os.environ.setdefault(key.strip(), val.strip())

import psycopg2
import psycopg2.extras

DATABASE_URL = os.environ.get('DATABASE_URL', '')
SQLITE_PATH  = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.db')

TABELLE = [
    'utenti',
    'offerte',
    'fornitori',
    'piani_provvigionali',
    'portafogli',
    'clienti_portafoglio',
    'simulazioni',
]

def main():
    if not DATABASE_URL:
        print("ERRORE: DATABASE_URL non trovato nel file .env")
        sys.exit(1)

    if not os.path.exists(SQLITE_PATH):
        print(f"ERRORE: File SQLite non trovato: {SQLITE_PATH}")
        sys.exit(1)

    print(f"Connessione a SQLite: {SQLITE_PATH}")
    sqlite_conn = sqlite3.connect(SQLITE_PATH)
    sqlite_conn.row_factory = sqlite3.Row

    print(f"Connessione a Supabase...")
    pg_conn = psycopg2.connect(DATABASE_URL, cursor_factory=psycopg2.extras.RealDictCursor)
    pg_conn.autocommit = False

    try:
        for tabella in TABELLE:
            migra_tabella(sqlite_conn, pg_conn, tabella)

        pg_conn.commit()
        print("\n✅ Migrazione completata con successo!")
        print("Puoi ora usare l'app con tutti i tuoi dati.")

    except Exception as e:
        pg_conn.rollback()
        print(f"\n❌ ERRORE durante la migrazione: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    finally:
        sqlite_conn.close()
        pg_conn.close()


def migra_tabella(sqlite_conn, pg_conn, tabella):
    sqlite_cur = sqlite_conn.cursor()
    pg_cur = pg_conn.cursor()

    # Leggi righe da SQLite
    sqlite_cur.execute(f"SELECT * FROM {tabella}")
    righe = sqlite_cur.fetchall()

    if not righe:
        print(f"  {tabella}: vuota, salto")
        return

    colonne = [desc[0] for desc in sqlite_cur.description]
    n = len(righe)

    # Svuota la tabella in Supabase prima di inserire (evita duplicati)
    pg_cur.execute(f"DELETE FROM {tabella}")

    # Inserisci riga per riga con gli ID originali
    placeholders = ', '.join(['%s'] * len(colonne))
    col_names    = ', '.join(colonne)
    sql = f"INSERT INTO {tabella} ({col_names}) VALUES ({placeholders}) ON CONFLICT DO NOTHING"

    for riga in righe:
        valori = [riga[col] for col in colonne]
        pg_cur.execute(sql, valori)

    # Resetta la sequence SERIAL in PostgreSQL al valore max dell'ID
    if 'id' in colonne:
        pg_cur.execute(f"SELECT setval(pg_get_serial_sequence('{tabella}', 'id'), COALESCE(MAX(id), 1)) FROM {tabella}")

    print(f"  ✅ {tabella}: {n} righe migrate")


if __name__ == '__main__':
    main()
