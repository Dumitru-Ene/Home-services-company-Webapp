

DROP DATABASE ProiectDB;
CREATE DATABASE ProiectDB;

USE ProiectDB;

CREATE TABLE Clienti(
    ID_client int NOT NULL AUTO_INCREMENT,
    Nume varchar(50) NOT NULL,
    Prenume varchar(50) NOT NULL,
    Email varchar(100) NOT NULL,
    Parola varchar(100) NOT NULL,
    Sex char(1) NOT NULL,
    Adresa varchar(200),
    PRIMARY KEY (ID_client)
);


CREATE TABLE Comenzi(
    ID_comanda int NOT NULL AUTO_INCREMENT,
    ID_client int NOT NULL,
    Suma int NOT NULL,
    Data_comanda date NULL,
    PRIMARY KEY (ID_comanda)
);

CREATE TABLE Comenzi_servicii(
    ID_comanda_serviciu int NOT NULL AUTO_INCREMENT,
    ID_comanda int NOT NULL,
    ID_serviciu int NOT NULL,
    Adresa_serviciu_comanda varchar(200),
    PRIMARY KEY (ID_comanda_serviciu)
);

CREATE TABLE Servicii(
    ID_serviciu int NOT NULL AUTO_INCREMENT,
    Denumire varchar(50) NOT NULL,
    Pret_serviciu int NOT NULL,
    PRIMARY KEY (ID_serviciu)
);
CREATE TABLE Departamente(
    ID_departament int NOT NULL AUTO_INCREMENT,
    Denumire varchar(50) NOT NULL,
    ID_manager int NOT NULL,
    PRIMARY KEY (ID_departament)
);






CREATE TABLE Angajati(
    ID_angajat int NOT NULL AUTO_INCREMENT,
    Nume varchar(50) NOT NULL,
    Prenume varchar(50) NOT NULL,
    Email varchar(100) NOT NULL,
    Parola varchar(100) NOT NULL,
    ID_departament int,
    Salariu int NOT NULL,

    
    PRIMARY KEY (ID_angajat)

);




CREATE TABLE Angajati_comanda_serviciu(
    ID_angajat_Comanda_serviciu int NOT NULL AUTO_INCREMENT,
    ID_comanda_serviciu int NOT NULL,
    ID_angajat int NOT NULL,
    PRIMARY KEY (ID_angajat_Comanda_serviciu)
);

