USE ProiectDB;

INSERT INTO Clienti (
    Nume,
    Prenume,
    Email,
    Parola,
    Sex,
    Adresa 
) VALUES 
('Mihai','Marius', 'mariusmihai@gmail.com','1234', 'M','bucuresti, sector 2, str maracineni,43'),
('Pop','Ana','AnaPop@gmail.com','4321','F', 'bucuresti, sector 3, str mihai viteazu,13'),
('Ene','Dumitru','dumiene@gmail.com','4321','M','bucuresti, sector 6, str splaiul independentei,290');

INSERT INTO Angajati (
    Nume ,
    Prenume ,
    Email ,
    Parola ,
    ID_departament ,
    Salariu 

) VALUES
('John','Doe','asd@asd.com','1234','4','10000'),
('Dorel','Ion','dorel@ion.com','1234','4','15000'),
('Moldoveanu','Sorin','sorin@gmail.com','1234','4','55000'), 
('Olteanu','Mihai','mihai@yahoo.com','1234','1','100000'),
('Andrei','Mara','mara@gmail.com','1234','2','15000');


INSERT INTO Departamente(
    Denumire,
    ID_manager
) VALUES
('IT','10'),
('HR','11'),
('Marketing','12'),
('Servicii','3');


INSERT INTO Servicii (
    Denumire,
    Pret_serviciu
) VALUES
('Tuns Gazonul','100'),
('Tencuit','200'),
('Zugravit','200'),
('Spalat Masina','50'),
('Curatenie in Casa','250'),
('Curatare piscina','250');

