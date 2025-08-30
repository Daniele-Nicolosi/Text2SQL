import csv
from db_utils.crud import insert_or_update_film

# Legge i dati dal file TSV
with open('data.tsv', newline='') as file:
    reader: csv.DictReader = csv.DictReader(file, delimiter='\t')
    
    for riga in reader:  
        """
        Crea una stringa concatenando i campi richiesti
        e la passa alla funzione insert_or_update_film
        """
        stringa: str = (
            riga['Titolo'] + ", " +
            riga['Regista'] + ", " +
            riga['Età_Autore'] + ", " +
            riga['Anno'] + ", " +
            riga['Genere'] + ", " +
            riga['Piattaforma_1'] + ", " +
            riga['Piattaforma_2']
        )
        insert_or_update_film(stringa)  # Inserisce o aggiorna il film nel DB




        
