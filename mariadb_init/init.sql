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
    piattaforma_1_id INT,                -- Riferimento a piattaforma
    piattaforma_2_id INT,                -- Riferimento a seconda piattaforma
    regista_id INT,                      -- Riferimento a regista
    FOREIGN KEY (regista_id) REFERENCES registi(id),
    FOREIGN KEY (piattaforma_1_id) REFERENCES piattaforme(id),
    FOREIGN KEY (piattaforma_2_id) REFERENCES piattaforme(id)
);

