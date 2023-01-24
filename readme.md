## Cerintele rularii aplicatiei

Avem nevoie de o distributie de linux. (Este bun si WSL-ul)

Pentru inceput, instalam mysql server:
```
$sudo apt install mysql-server
```

Acum trebuie sa cream un user pentru mysql:
Numele si parola userului trebuie sa se potriveasca cu cele folosite de aplicatia web.
Ele pot fi modificate in fisierul "app.py"
```
$sudo mysql
mysql> CREATE USER 'dumitr'@'localhost' IDENTIFIED BY 'strongpass';
```
Oferim userului toate privilegiile
```
mysql> GRANT ALL PRIVILEGES ON *.* TO 'dumitr'@'localhost' WITH GRANT OPTION;

mysql> FLUSH PRIVILEGES;
```
Baza de date se poate crea folosind scriptul "creaza_baza_proiect.sql" din directorul "queries/"
```
$mysql -u dumitr -p"strongpass" < "queries/creaza_baza_proiect.sql" 
```
Aplicatia ruleaza folosind python3. Pentru instalare folosim:
```
$sudo apt install python3
```
Urmatorul pas este sa cream un virtual environment pentru aplicatie.

```
$virtualenv env
```
(virtualenv se poate instala folosind:)
```
$sudo pip3 install virtualenv 
```

Activam virtual environmentul:
```
$source env/bin/activate
```
Instalam modulele de python necesare apicatiei:
```
$pip3 install -r requirements.txt
```

Ultimul pas este sa pornim aplicatia folosind:
```
$python3 app.py
```

## Structura aplicatiei

Aplicatia a fost creata folosind biblioteca de python Flask.
In fisierul app.py avem functionalitatile de backend ale aplicatiei si tot din app.py se apeleaza functii de
template rendering pentru frontend. Template-urile sunt scrise integral in HTML si jinja2.

Baza de date a fost proiectata cu limbajul SQL. In directorul "queries" se afla scriptul SQL "creaza_baza_proiect.sql"
in care putem vedea tabelele bazei de date si relatiile dintre acestea.

Toate interogarile bazei de date au fost scrise folosind limbaj SQL.

## Functionalitatile aplicatiei

Web appul dispune de 4 tipuri de useri si fiecare tip user are o interfata unica si actiuni specifice. 

Clientii pot plasa/anula/modifica comenzi, sa verifice statusul comenzilor lor (daca o comanda a fost preluata complet sau nu)
si sa isi editeze datele personale.

Angajatii din departamentul de servicii pot verifica comenzile plasate de clienti, sa preia sau sa renunte la servicii
de pe comenzi, sa vizualizeze comenzile care contin macar un serviciu preluat de acestia. Tot ei dispun de un tool de cu 
care pot cauta comenzi disponibile dupa adresa.

Managerii de departamente pot adauga servicii noi pentru vanzare si sa vada diferite statistici legate de comenzile, serviciile sau
angajatii firmei. (ex: Angajatul care a produs cel mai mult venit prin vanzarea de produse, Angajatul care are cele mai multe 
comenzi preluate integral, Comanda cu cele mai multe servicii, Comenzile cu suma peste medie etc.)

Toate tipurile de utilizatori isi pot verifica datele personale si sa isi schimbe parola.

Oricand este posibila inregistrarea unui nou cont de client cu o adresa de email noua.