-- Tabella registi
CREATE TABLE registi (
    id INT AUTO_INCREMENT PRIMARY KEY,  -- ID univoco
    nome VARCHAR(100) NOT NULL,         -- Nome del regista
    eta INT                             -- Età del regista
);

-- Tabella piattaforme
CREATE TABLE piattaforme (
    id INT AUTO_INCREMENT PRIMARY KEY,  -- ID univoco
    nome VARCHAR(100) NOT NULL UNIQUE   -- Nome piattaforma, unico
);

-- Tabella movies
CREATE TABLE movies (
    id INT AUTO_INCREMENT PRIMARY KEY,  -- ID univoco film
    titolo VARCHAR(200) NOT NULL,       -- Titolo del film
    anno INT,                            -- Anno di uscita
    genere VARCHAR(100),                 -- Genere film
    piattaforma_1 INT,                   -- Riferimento a piattaforma
    piattaforma_2 INT,                   -- Riferimento a seconda piattaforma
    regista_id INT,                      -- Riferimento a regista
    FOREIGN KEY (regista_id) REFERENCES registi(id),
    FOREIGN KEY (piattaforma_1) REFERENCES piattaforme(id),
    FOREIGN KEY (piattaforma_2) REFERENCES piattaforme(id)
);

