CREATE TABLE registi (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    eta INT
);

CREATE TABLE piattaforme (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE film (
    id INT AUTO_INCREMENT PRIMARY KEY,
    titolo VARCHAR(200) NOT NULL,
    anno INT,
    genere VARCHAR(100),
    piattaforma_1 INT,
    piattaforma_2 INT,
    regista_id INT,
    FOREIGN KEY (regista_id) REFERENCES registi(id),
    FOREIGN KEY (piattaforma_1) REFERENCES piattaforme(id),
    FOREIGN KEY (piattaforma_2) REFERENCES piattaforme(id)
);
