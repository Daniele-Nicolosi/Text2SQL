from typing import Optional
from .connection import get_connection

def _get_or_create_regista(cur, nome: str, eta: Optional[int]) -> int:
    """
    Recupera o crea un regista e restituisce il suo ID
    """
    cur.execute("SELECT id FROM registi WHERE nome=? AND eta=?", (nome, eta))
    result = cur.fetchone()
    if result:
        regista_id = result['id']
        cur.execute("UPDATE registi SET nome=?, eta=? WHERE id=?", (nome, eta, regista_id))
        return regista_id
    cur.execute("INSERT INTO registi (nome, eta) VALUES (?, ?)", (nome, eta))
    return cur.lastrowid

def _get_or_create_piattaforma(cur, nome: Optional[str]) -> Optional[int]:
    """
    Recupera o crea una piattaforma e restituisce il suo ID
    """
    if not nome:
        return None
    cur.execute("SELECT id FROM piattaforme WHERE nome=?", (nome,))
    result = cur.fetchone()
    if result:
        return result['id']
    cur.execute("INSERT INTO piattaforme (nome) VALUES (?)", (nome,))
    return cur.lastrowid

def _cleanup_orphan_piattaforme(cur):
    """
    Rimuove piattaforme non più usate da nessun film
    """
    # Recupera piattaforme orfane
    cur.execute("""
        SELECT id, nome FROM piattaforme 
        WHERE id NOT IN (
            SELECT DISTINCT piattaforma_1_id FROM movies WHERE piattaforma_1_id IS NOT NULL
            UNION
            SELECT DISTINCT piattaforma_2_id FROM movies WHERE piattaforma_2_id IS NOT NULL
        )
    """)
    orphan_piattaforme = cur.fetchall()

    # Esegue la cancellazione
    cur.execute("""
        DELETE FROM piattaforme 
        WHERE id NOT IN (
            SELECT DISTINCT piattaforma_1_id FROM movies WHERE piattaforma_1_id IS NOT NULL
            UNION
            SELECT DISTINCT piattaforma_2_id FROM movies WHERE piattaforma_2_id IS NOT NULL
        )
    """)

    # Debug finale
    if orphan_piattaforme:
        for pid, nome in orphan_piattaforme:
            print(f"[DEBUG] Piattaforma eliminata: id={pid}, nome={nome}")
    else:
        print("[DEBUG] Nessuna piattaforma eliminata")


def insert_or_update_film(stringa: str) -> tuple[bool, str | None]:
    """
    Inserisce o aggiorna un film a partire da una stringa CSV/TSV.
    Restituisce (True, None) se tutto ok, (False, messaggio_errore) se fallisce.
    Formato: titolo, regista, eta, anno, genere, piattaforma_1[, piattaforma_2]
    """
    try:
        campi = [x.strip() for x in stringa.split(",")]
        if not (6 <= len(campi) <= 7):
            msg = f"Input non valido, attesi 6 o 7 campi ma trovati {len(campi)}"
            print(f"[ERRORE] {msg}")
            return False, msg
        
        for i, campo in enumerate(campi[:6]):
            if not campo:
                msg = f"Input non valido, il campo {i+1} non può essere vuoto"
                print(f"[ERRORE] {msg}")
                return False, msg

        if len(campi) == 6:
            titolo, regista, eta, anno, genere, piattaforma_1 = campi
            piattaforma_2 = None
        else:
            titolo, regista, eta, anno, genere, piattaforma_1, piattaforma_2 = campi

        conn, cur = get_connection()

        regista_id = _get_or_create_regista(cur, regista, int(eta) if eta else None)
        piattaforma_1_id = _get_or_create_piattaforma(cur, piattaforma_1)
        piattaforma_2_id = _get_or_create_piattaforma(cur, piattaforma_2)

        cur.execute("SELECT id, piattaforma_1_id, piattaforma_2_id FROM movies WHERE titolo=? AND regista_id=?",
                    (titolo, regista_id))
        result = cur.fetchone()

        if result:
            film_id, old_p1, old_p2 = result['id'], result['piattaforma_1_id'], result['piattaforma_2_id']
            cur.execute(
                """UPDATE movies SET anno=?, genere=?, piattaforma_1_id=?, piattaforma_2_id=?, regista_id=?
                   WHERE id=?""",
                (int(anno) if anno else None, genere, piattaforma_1_id, piattaforma_2_id, regista_id, film_id)
            )
            if (old_p1 != piattaforma_1_id) or (old_p2 != piattaforma_2_id):
                _cleanup_orphan_piattaforme(cur)

            print(f"[DEBUG] Film aggiornato: {titolo}")
            
        else:
            cur.execute(
                """INSERT INTO movies (titolo, anno, genere, piattaforma_1_id, piattaforma_2_id, regista_id)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (titolo, int(anno) if anno else None, genere, piattaforma_1_id, piattaforma_2_id, regista_id)
            )

            print(f"[DEBUG] Film inserito: {titolo}")

        conn.commit()
        return True, None

    except Exception as e:
        msg = f"Errore inserimento/aggiornamento: {e}"
        print(f"[ERRORE] {msg}")
        return False, msg

    finally:
        try:
            cur.close()
            conn.close()
        except:
            pass
