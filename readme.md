## Application required services

Firstly, the app needs a linux distribution. (WSL is good too)

mysql server installation:
```
$sudo apt install mysql-server
```

Creating an user for mysql:
The username and password must be same with the ones used by the app's sql connector.
They can be modified in the "app.py" file.
```
$sudo mysql
mysql> CREATE USER 'dumitr'@'localhost' IDENTIFIED BY 'strongpass';
```
Granting the user all the privileges
```
mysql> GRANT ALL PRIVILEGES ON *.* TO 'dumitr'@'localhost' WITH GRANT OPTION;

mysql> FLUSH PRIVILEGES;
```
The database can be created and populated using the shell script "queries/initiaza_baza.sh" 
```
$./initiaza_baza.sh dumitr strongpass" 
```
Installing python3 with:
```
$sudo apt install python3
```
The next step is to create a virtual environment for our python app

```
$virtualenv env
```
(virtualenv can be installed using:)
```
$sudo pip3 install virtualenv 
```

To activate the env we just created we use:
```
$source env/bin/activate
```
Run this command to install the required python3 modules:
```
$pip3 install -r requirements.txt
```

Lastly, we can start the app just by using this command:
```
$python3 app.py
```

## The structure of the web app

The web app was created using the Flask python module for web development.
The python script "app.py" contains the backend functionalities and also handles the frondend part by 
calling template rendering functions. The templates consist only in HTML and jinja2.

The database was designed using SQL. In the "queries" directory we can find the SQL script "creaza_baza_proiect.sql"
in which we can see how exactly the database tables and their relations were designed.

Each and every query was made using SQL.

## The app functionallities

Up to this date, the web app consists of four types of users that have individual interfaces and specific actions. 

Customers can place/cancel/modify orders, check the status of their orders and edit their personal data.

Employees from the services department can check the available orders placed by customers, accept services
from the orders and check the orders that contain at least one service that the employee accepted. The employees can 
drop out the services they accepted any time so others employees can accept them. They also have a search tool with
for available orders by address.


Department managers can add new services for sale and see different stats related to the company orders, services
or employees. (eg: The employee who produced the most income by completing services off orders, the employee who has the most
full orders completed, The order with the most services,The orders that have a total price that exeeds the average, etc.)

Each type of user can check their personal data and change the password.

A new customer account can be created in the signup page at any time.

The app features user sessions which allows for multiple users to be connected and do different actions at the same time.
