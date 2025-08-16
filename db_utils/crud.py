from typing import Optional
from .connection import get_connection

def get_or_create_regista(cur, nome: str, eta: Optional[int]) -> int:
    """Recupera o crea un regista e restituisce il suo ID"""
    cur.execute("SELECT id FROM registi WHERE nome=? AND eta=?", (nome, eta))
    result = cur.fetchone()
    if result:
        regista_id = result['id']
        cur.execute("UPDATE registi SET nome=?, eta=? WHERE id=?", (nome, eta, regista_id))
        return regista_id
    cur.execute("INSERT INTO registi (nome, eta) VALUES (?, ?)", (nome, eta))
    return cur.lastrowid

def get_or_create_piattaforma(cur, nome: Optional[str]) -> Optional[int]:
    """Recupera o crea una piattaforma e restituisce il suo ID"""
    if not nome:
        return None
    cur.execute("SELECT id FROM piattaforme WHERE nome=?", (nome,))
    result = cur.fetchone()
    if result:
        return result['id']
    cur.execute("INSERT INTO piattaforme (nome) VALUES (?)", (nome,))
    return cur.lastrowid

def cleanup_orphan_piattaforme(cur):
    """Rimuove piattaforme non più usate da nessun film"""
    cur.execute("""
        DELETE FROM piattaforme 
        WHERE id NOT IN (
            SELECT DISTINCT piattaforma_1 FROM movies WHERE piattaforma_1 IS NOT NULL
            UNION
            SELECT DISTINCT piattaforma_2 FROM movies WHERE piattaforma_2 IS NOT NULL
        )
    """)

def insert_or_update_film(stringa: str) -> bool:
    """
    Inserisce o aggiorna un film a partire da una stringa CSV/TSV.
    Formato: titolo, regista, eta, anno, genere, piattaforma_1[, piattaforma_2]
    """
    try:
        campi = [x.strip() for x in stringa.split(",")]
        if not (6 <= len(campi) <= 7):
            print(f"[DEBUG] Input non valido, attesi 6 o 7 campi ma trovati {len(campi)}")
            return False

        if len(campi) == 6:
            titolo, regista, eta, anno, genere, piattaforma_1 = campi
            piattaforma_2 = None
        else:
            titolo, regista, eta, anno, genere, piattaforma_1, piattaforma_2 = campi

        conn, cur = get_connection()

        regista_id = get_or_create_regista(cur, regista, int(eta) if eta else None)
        piattaforma_1_id = get_or_create_piattaforma(cur, piattaforma_1)
        piattaforma_2_id = get_or_create_piattaforma(cur, piattaforma_2)

        cur.execute("SELECT id, piattaforma_1, piattaforma_2 FROM movies WHERE titolo=? AND regista_id=?",
                    (titolo, regista_id))
        result = cur.fetchone()

        if result:
            film_id, old_p1, old_p2 = result['id'], result['piattaforma_1'], result['piattaforma_2']
            cur.execute(
                """UPDATE movies SET anno=?, genere=?, piattaforma_1=?, piattaforma_2=?, regista_id=?
                   WHERE id=?""",
                (int(anno) if anno else None, genere, piattaforma_1_id, piattaforma_2_id, regista_id, film_id)
            )
            if (old_p1 != piattaforma_1_id) or (old_p2 != piattaforma_2_id):
                cleanup_orphan_piattaforme(cur)

            print(f"[DEBUG] Film aggiornato: {titolo}")
            
        else:
            cur.execute(
                """INSERT INTO movies (titolo, anno, genere, piattaforma_1, piattaforma_2, regista_id)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (titolo, int(anno) if anno else None, genere, piattaforma_1_id, piattaforma_2_id, regista_id)
            )

            print(f"[DEBUG] Film inserito: {titolo}")

        conn.commit()
        return True

    except Exception as e:
        print(f"[DEBUG] Errore inserimento/aggiornamento: {e}")
        return False

    finally:
        try:
            cur.close()
            conn.close()
        except:
            pass
