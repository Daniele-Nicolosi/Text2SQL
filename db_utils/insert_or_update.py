import mariadb

def get_or_create_regista(cursor, nome, eta):
    cursor.execute("SELECT id FROM registi WHERE nome=? AND eta=?", (nome, eta))
    result = cursor.fetchone()
    if result:
        regista_id = result[0]
        cursor.execute("UPDATE registi SET nome=?, eta=? WHERE id=?", (nome, eta, regista_id))
        return regista_id
    cursor.execute("INSERT INTO registi (nome, eta) VALUES (?, ?)", (nome, eta))
    return cursor.lastrowid

def get_or_create_piattaforma(cursor, nome):
    if not nome:
        return None
    cursor.execute("SELECT id FROM piattaforme WHERE nome=?", (nome,))
    result = cursor.fetchone()
    if result:
        return result[0]
    cursor.execute("INSERT INTO piattaforme (nome) VALUES (?)", (nome,))
    return cursor.lastrowid

def insert_or_update_film(stringa : str) -> bool:
    try:
        # Parsing input CSV
        titolo, regista, eta, anno, genere, piattaforma_1, piattaforma_2 = [x.strip() for x in stringa.split(",")]

        # Connessione al database
        conn = mariadb.connect( 
            host="mariadb",     
            port=3306,
            user="user",           
            password="password",   
            database="movies_db"
        )
        cursor = conn.cursor()

        # Recupero o creazione record associati
        regista_id = get_or_create_regista(cursor, regista, int(eta) if eta else None)
        piattaforma_1_id = get_or_create_piattaforma(cursor, piattaforma_1)
        piattaforma_2_id = get_or_create_piattaforma(cursor, piattaforma_2)

        # Verifica se il film esiste già
        cursor.execute("SELECT id FROM movies WHERE titolo=? AND regista_id=?", (titolo, regista_id))
        result = cursor.fetchone()
        
        if result:
            film_id = result[0]
            cursor.execute(
                """UPDATE movies SET anno=?, genere=?, piattaforma_1=?, piattaforma_2=?, regista_id=?
                   WHERE id=?""",
                (
                    int(anno) if anno else None,
                    genere,
                    piattaforma_1_id,
                    piattaforma_2_id,
                    regista_id,
                    film_id
                )
            )
            print(f"Aggiornato film '{titolo}'")
        else:
            cursor.execute(
                """INSERT INTO movies (titolo, anno, genere, piattaforma_1, piattaforma_2, regista_id)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    titolo,
                    int(anno) if anno else None,
                    genere,
                    piattaforma_1_id,
                    piattaforma_2_id,
                    regista_id
                )
            )
            print(f"Inserito nuovo film '{titolo}'")

        conn.commit()
        return True  # Tutto OK

    except Exception as e:
        print(f"Errore durante l'inserimento/aggiornamento: {e}")
        return False  # Qualcosa è andato storto

    finally:
        # Chiude connessione in ogni caso
        try:
            cursor.close()
            conn.close()
        except:
            pass

