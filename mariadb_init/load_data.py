import csv
from db_utils.insert_or_update import insert_or_update_film

with open('data.tsv', newline='') as file:
    reader = csv.DictReader(file, delimiter='\t')
    for riga in reader:
        stringa = riga['Titolo'] + ", " + riga['Regista'] + ", " + riga['Età_Autore'] + ", " + riga['Anno'] + ", " +  riga['Genere'] + ", " + riga['Piattaforma_1'] + ", " + riga['Piattaforma_2']
        insert_or_update_film(stringa)
        
