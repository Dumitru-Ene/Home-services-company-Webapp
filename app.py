from flask import Flask, render_template, redirect, request, session
from flask_session import Session
import mysql.connector as sql



app= Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

connectoruser="dumitr"
connectorpass="strongpass"
connectordb="ProiectDB"
connectorhost="localhost"

@app.route('/', methods=['POST', 'GET'])
def login_page():
    if request.method=='POST':
        em =request.form['email']
        pwd = request.form['password']
        try:
            m=sql.connect(host=connectorhost,user=connectoruser,passwd=connectorpass,database=connectordb)
            cursor=m.cursor()
        except:
            return ("problema la conexiunea cu baza de date")
        #cauta clienti
        c="SELECT * FROM Clienti WHERE Email='{}' AND Parola='{}'".format(em,pwd)
        cursor.execute(c)
        t=tuple(cursor.fetchall())
        if t==():
            #cauta manageri
            c="SELECT * FROM Angajati a, Departamente d WHERE a.ID_angajat = d.ID_manager AND Email='{}' AND Parola='{}'".format(em,pwd)
            cursor.execute(c)
            t2=tuple(cursor.fetchall())
            if t2==():
                # cauta angajati din departamentul de servicii
                c="SELECT * FROM Angajati a WHERE (SELECT d.ID_departament FROM Departamente d WHERE d.Denumire = 'Servicii') = a.ID_departament AND a.Email='{}' AND a.Parola='{}'".format(em,pwd)
                cursor.execute(c)
                t3=tuple(cursor.fetchall())
                if t3==():
                    # cauta in restul de angajati
                    c="SELECT * FROM Angajati WHERE Email='{}' AND Parola='{}'".format(em,pwd)
                    cursor.execute(c)
                    t4=tuple(cursor.fetchall())
                    if t4==():
                        return render_template('login_page.html',parola_proasta=True)
                    else:
                        print(t4)
                        session["Detalii_cont_curent"]=t4[0]
                        session["Tip_user"]="other"
                        return "wooow esti de la oricare alt departament decat cel de servicii, nici manager nu esti... nu prea ai ce sa faci pe aici"
                        return render_template('main_other.html')
                else:
                    print(t3)
                    session["Detalii_cont_curent"]=t3[0]
                    session["Tip_user"]="worker"
                    return redirect('/mainworker/')
                    
            else:
                print(t2)
                session["Detalii_cont_curent"]=t2[0]
                session["Tip_user"]="manager"
                

                return redirect('/mainmanager/')
        else:
            print(t)
            #(id, nume, prenume, email, parola, sex, adresa)
            session["Detalii_cont_curent"]=t[0]
            session["Tip_user"]="client"
            return redirect('/main/')
    return render_template('login_page.html',parola_proasta=False)



@app.route('/signup/', methods=['POST', 'GET'])
def signup_page():
    if request.method=="POST":
        try:
            m=m=sql.connect(host=connectorhost,user=connectoruser,passwd=connectorpass,database=connectordb)
            cursor=m.cursor()
        except:
            return ("problema la conexiunea cu baza de date")
        em=request.form["email"]
        c="SELECT * FROM Clienti where Email='{}'".format(em)
        cursor.execute(c)
        t=tuple(cursor.fetchall())
        if t!=():
                return render_template('signup_page.html',email_prost=True)

        fn=request.form["first_name"]
        ln=request.form["last_name"]
        pwd=request.form["password"]
        s=request.form["sex"]
        ad=request.form["address"]     
        c="""INSERT INTO Clienti (
        Nume,
        Prenume,
        Email,
        Parola,
        Sex,
        Adresa 
        ) VALUES ('{}','{}', '{}','{}', '{}','{}')""".format(ln,fn,em,pwd,s,ad)
        cursor.execute(c)
        try:
            m.commit()
        except:
            return "A aparut o problema la inserarea in baza de date"
        return redirect('/')
    return render_template('signup_page.html',email_prost=False)



## LOGOUT
@app.route('/main/logout')
def main_logout():
    session["Detalii_cont_curent"] = ''
    session["Tip_user"] = ''
    return redirect('/')


## pagini client normal

@app.route('/main/',methods=['POST', 'GET'])
def main_page():
    if not session.get("Detalii_cont_curent"):
        return redirect('/')
    if session["Tip_user"] != 'client':
        return redirect('/')
    return render_template('client/main.html',NUME_USER=session["Detalii_cont_curent"][2])

@app.route('/main/cont')
def main_cont():
    if not session.get("Detalii_cont_curent"):
        return redirect('/')
    if session["Tip_user"] != 'client':
        return redirect('/')
    try:
            m=m=sql.connect(host=connectorhost,user=connectoruser,passwd=connectorpass,database=connectordb)
            cursor=m.cursor()
    except:
        return ("problema la conexiunea cu baza de date")
    
   
    c="""
        SELECT s.Denumire 
        FROM Comenzi c
        INNER JOIN Comenzi_servicii cs ON c.ID_comanda = cs.ID_comanda
        INNER JOIN Servicii s ON s.ID_serviciu = cs.ID_serviciu
        WHERE c.ID_client = '{}'
        GROUP BY s.ID_serviciu
        ORDER BY COUNT(s.ID_serviciu)
        LIMIT 1
    """.format(session["Detalii_cont_curent"][0])
    cursor.execute(c)
    t=tuple(cursor.fetchall())
    if t==():
        serviciu_pref="NICIUNUL"
    else:
        serviciu_pref=t[0][0]
    return render_template ('client/cont.html',DETALII_CONT=session["Detalii_cont_curent"],SERVICIU_PREF=serviciu_pref)
## pagini legate de cont



@app.route('/main/cont/editeaza',methods=['POST', 'GET'])
def main_cont_editeaza():
    if not session.get("Detalii_cont_curent"):
        return redirect('/')
    if session["Tip_user"] != 'client':
        return redirect('/')
    if request.method=="POST":
        try:
            m=m=sql.connect(host=connectorhost,user=connectoruser,passwd=connectorpass,database=connectordb)
            cursor=m.cursor()
        except:
            return ("problema la conexiunea cu baza de date")
        em=request.form["email"]
        c="SELECT * FROM Clienti where Email='{}'".format(em)
        cursor.execute(c)
        t=tuple(cursor.fetchall())
        if t!=() and em != session["Detalii_cont_curent"][3] :
            return render_template('client/cont_editeaza.html',DETALII_CONT=session["Detalii_cont_curent"],email_prost=True)

        fn=request.form["first_name"]
        ln=request.form["last_name"]
        s=request.form["sex"]
        ad=request.form["address"]     
        c="""UPDATE Clienti SET
        Nume = "{}",
        Prenume = "{}",
        Email = "{}",
        Sex = "{}",
        Adresa = "{}" 
        WHERE ID_client = "{}"
        """.format(ln,fn,em,s,ad,session["Detalii_cont_curent"][0])
        cursor.execute(c)
        try:
            m.commit()
        except:
            return "A aparut o problema la updatarea bazei de date"
        session["Detalii_cont_curent"]=(session["Detalii_cont_curent"][0],ln,fn,em,session["Detalii_cont_curent"][4],s,ad)
        return redirect('/main/cont')
        
    
    return render_template ('client/cont_editeaza.html',DETALII_CONT=session["Detalii_cont_curent"],email_prost = False)

@app.route('/main/cont/chpass',methods=['POST', 'GET'])
def main_cont_chpass():
    if not session.get("Detalii_cont_curent"):
        return redirect('/')
    if session["Tip_user"] != 'client':
        return redirect('/')
    if request.method=="POST":
        try:
            m=m=sql.connect(host=connectorhost,user=connectoruser,passwd=connectorpass,database=connectordb)
            cursor=m.cursor()
        except:
            return ("problema la conexiunea cu baza de date")
        
        pw=request.form["password"]
        pwc=request.form["passwordconf"]
        if(pw != pwc):
            return render_template("client/cont_chpass.html",parola_proasta=True)
        c="""UPDATE Clienti SET
        Parola = "{}"
        WHERE ID_client = "{}"
        """.format(pw,session["Detalii_cont_curent"][0])
        cursor.execute(c)
        try:
            m.commit()
        except:
            return "A aparut o problema la updatarea bazei de date"
        session["Detalii_cont_curent"]=(session["Detalii_cont_curent"][0],session["Detalii_cont_curent"][1],session["Detalii_cont_curent"][2],session["Detalii_cont_curent"][3],pw,session["Detalii_cont_curent"][5],session["Detalii_cont_curent"][6])
        return redirect('/main/cont')
        
    
    return render_template ('client/cont_chpass.html',parola_proasta = False)


## pagini plasari comenzi
@app.route('/main/cumpara',methods=['POST', 'GET'])
def main_cumpara():
    if not session.get("Detalii_cont_curent"):
        return redirect('/')
    if session["Tip_user"] != 'client':
        return redirect('/')
    
    try:
        m=m=sql.connect(host=connectorhost,user=connectoruser,passwd=connectorpass,database=connectordb)
        cursor=m.cursor()
    except:
        return ("problema la conexiunea cu baza de date")

    servicii=[]
    c="""
        SELECT ID_serviciu, Denumire, Pret_serviciu FROM Servicii
    """
    cursor.execute(c)
    t=tuple(cursor.fetchall())
    print(t)
    servicii_disp=[]
    for i in t:
        servicii_disp.append(i)

    if request.method == "POST":
        print("daaaaaaaaaaa")
        print(request.form["action"])
        if request.form["action"].split(',')[0] == "comanda":
            print("s a comandat")
            suma=0
            for i in range(1,int(request.form["action"].split(',')[1])+1):
                print(request.form["serviciu"+str(i)])
                for k in servicii_disp:
                    if k[0] == int(request.form["serviciu"+str(i)]):
                        suma=suma+k[2]
                servicii.append((request.form["serviciu"+str(i)],request.form["address"+str(i)]))
            print(servicii)

            c="""
                INSERT INTO Comenzi (
                    ID_client,
                    Suma,
                    Data_comanda
                ) VALUES
                ('{}','{}',curdate())
            """.format(session["Detalii_cont_curent"][0],suma)
            cursor.execute(c)
            m.commit()
            c="""
                INSERT INTO Comenzi_servicii(
                    ID_comanda,
                    ID_serviciu,
                    Adresa_serviciu_comanda
                ) VALUES
                
            """
            for i in servicii:
                c=c+"(LAST_INSERT_ID()," + i[0] + ',"' + i[1] + '"),'
            c = c[:-1]
            cursor.execute(c)
            m.commit()
            return redirect('/main/')
        elif request.form["action"].split(',')[0] == "adauga":
            print ("s a apasat adauga servicii")
            
            if request.form["action"].split(',')[1] != '0':
                for i in range(1,int(request.form["action"].split(',')[1])+1):
                    print(request.form["serviciu"+str(i)])
                    servicii.append((request.form["serviciu"+str(i)],request.form["address"+str(i)]))
                print(servicii)
            servicii.append(("0",session["Detalii_cont_curent"][6]))
            return render_template("client/main_cumpara.html",SERVICII_DISP=servicii_disp,SERVICII=servicii)
        else:
            print ("s a apasat sterge serviciu")
            for i in range(1,int(request.form["action"].split(',')[1])+1):
                print(request.form["serviciu"+str(i)])
                servicii.append((request.form["serviciu"+str(i)],request.form["address"+str(i)]))
            del servicii[int(request.form["action"].split(',')[2])]
            print(servicii)
            return render_template("client/main_cumpara.html",SERVICII_DISP=servicii_disp,SERVICII=servicii)

    print ("abia am intrat")
    return render_template("client/main_cumpara.html",SERVICII=servicii)





@app.route('/main/comenzi',methods=["GET"])
def main_comenzi():
    if not session.get("Detalii_cont_curent"):
        return redirect('/')
    if session["Tip_user"] != 'client':
        return redirect('/')
    try:
        m=m=sql.connect(host=connectorhost,user=connectoruser,passwd=connectorpass,database=connectordb)
        cursor=m.cursor()
    except:
        return ("problema la conexiunea cu baza de date")
    
    

    c="SELECT * FROM Comenzi WHERE ID_client = {} ORDER BY Data_comanda, ID_comanda DESC".format(session["Detalii_cont_curent"][0])
    cursor.execute(c)
    comenzi=tuple(cursor.fetchall())
    if comenzi == ():
        return render_template("client/comenzi.html",DETALII_CONT=session["Detalii_cont_curent"],COMENZI=[])
    else:
        comenzi_lista=[]
        for comanda in comenzi:
            c="""
                SELECT c.ID_comanda AS id_com, COUNT(cs.ID_comanda) AS nr_serv, COUNT(acs.ID_comanda_serviciu) as nr_prel
                FROM Comenzi c 
                INNER JOIN Comenzi_servicii cs ON c.ID_Comanda =cs.ID_comanda
                LEFT JOIN Angajati_comanda_serviciu acs ON cs.ID_comanda_serviciu = acs.ID_comanda_serviciu
                WHERE c.ID_comanda = '{}'
                GROUP BY c.ID_comanda 
                HAVING COUNT(cs.ID_comanda) =  COUNT(acs.ID_comanda_serviciu)
            """.format(comanda[0])
            cursor.execute(c)
            t=tuple(cursor.fetchall())
        
            if t == ():
                final=False
            else:
                final=True
            c="SELECT s.Denumire, cs.Adresa_serviciu_comanda, s.Pret_serviciu FROM Servicii s, Comenzi_servicii cs WHERE s.ID_serviciu = cs.ID_serviciu AND ID_comanda = {}".format(comanda[0])
            cursor.execute(c)
            servicii=tuple(cursor.fetchall())
            comenzi_lista.append((comanda,servicii,final))
    
    #print(comenzi)
    #print(comenzi_lista)
    return render_template("client/comenzi.html",DETALII_CONT=session["Detalii_cont_curent"],COMENZI=comenzi_lista)


@app.route('/main/comenzi/anuleaza<int:index>',methods=["GET"])   
def main_anuleaza_comanda(index):
    if not session.get("Detalii_cont_curent"):
        return redirect('/')
    if session["Tip_user"] != 'client':
        return redirect('/')
    print(index)
    try:
        m=m=sql.connect(host=connectorhost,user=connectoruser,passwd=connectorpass,database=connectordb)
        cursor=m.cursor()
    except:
        return ("problema la conexiunea cu baza de date")
    c="SELECT * FROM Comenzi WHERE ID_comanda = {} AND ID_client = {}".format(index,session["Detalii_cont_curent"][0])
    cursor.execute(c)
    t=tuple(cursor.fetchall())
    if t==():
        return redirect('/main/comenzi')
    else:
        c="DELETE FROM Comenzi WHERE ID_comanda = {} AND ID_client = {}".format(index,session["Detalii_cont_curent"][0])
        cursor.execute(c)
        m.commit()
        c="SELECT ID_comanda_serviciu FROM Comenzi_servicii WHERE ID_comanda = {} ".format(index)
        cursor.execute(c)
        t=tuple(cursor.fetchall())
        t=t[0][0]
        c="DELETE FROM Comenzi_servicii WHERE ID_comanda = {}".format(index)
        cursor.execute(c)
        m.commit()
        c="DELETE FROM Angajati_comanda_serviciu WHERE ID_comanda_serviciu = {}".format(t)
        cursor.execute(c)
        m.commit()
    return redirect('/main/comenzi')

    
@app.route('/main/comenzi/modifica<int:index>',methods=["GET","POST"])   
def main_editeaza_comanda(index):
    if not session.get("Detalii_cont_curent"):
        return redirect('/')
    if session["Tip_user"] != 'client':
        return redirect('/')
    print(index)
    try:
        m=m=sql.connect(host=connectorhost,user=connectoruser,passwd=connectorpass,database=connectordb)
        cursor=m.cursor()
    except:
        return ("problema la conexiunea cu baza de date")

    c="SELECT * FROM Comenzi WHERE ID_comanda = {} AND ID_client = {}".format(index,session["Detalii_cont_curent"][0])
    cursor.execute(c)
    comanda=tuple(cursor.fetchall())
    if comanda==():
        return redirect('/main/comenzi')
    comanda=comanda[0]

    c="""
        SELECT ID_serviciu, Denumire, Pret_serviciu FROM Servicii
    """
    cursor.execute(c)
    t=tuple(cursor.fetchall())
    
    servicii_disp=[]
    for i in t:
        servicii_disp.append(i)

    if request.method == "POST":
        print("daaaaaaaaaaa")
        print(request.form["action"])
        if request.form["action"].split(',')[0] == "comanda":
            print("s au confirmat modificarile")
            servicii=[]
            suma=0
            for i in range(1,int(request.form["action"].split(',')[1])+1):
                print(request.form["serviciu"+str(i)])
                for k in servicii_disp:
                    if k[0] == int(request.form["serviciu"+str(i)]):
                        suma=suma+k[2]
                servicii.append((request.form["serviciu"+str(i)],request.form["address"+str(i)]))
            print(servicii)

            c="""
                UPDATE Comenzi SET Suma = "{}" WHERE ID_comanda = "{}" 
            """.format(suma,comanda[0])
            cursor.execute(c)
            m.commit()

            c="""
                DELETE FROM Angajati_comanda_serviciu WHERE ID_comanda_serviciu IN (SELECT ID_comanda_serviciu FROM Comenzi_servicii WHERE ID_comanda = {})
            """.format(comanda[0])
            cursor.execute(c)
            m.commit()

            c="""
                DELETE FROM Comenzi_servicii Where ID_comanda = {}
            """.format(comanda[0])
            cursor.execute(c)
            m.commit()
            c="""
                INSERT INTO Comenzi_servicii(
                    ID_comanda,
                    ID_serviciu,
                    Adresa_serviciu_comanda
                ) VALUES
                
            """
            for i in servicii:
                c=c +"("+ str(comanda[0]) + ',' + i[0] + ',"' + i[1] + '"),'
            c = c[:-1]
            print(c)
            cursor.execute(c)
            m.commit()
            return redirect('/main/comenzi')
        elif request.form["action"].split(',')[0] == "adauga":
            print ("s a apasat adauga servicii")
            servicii=[]
            if request.form["action"].split(',')[1] != '0':
                for i in range(1,int(request.form["action"].split(',')[1])+1):
                    print(request.form["serviciu"+str(i)])
                    servicii.append((request.form["serviciu"+str(i)],request.form["address"+str(i)]))
                print(servicii)
            servicii.append(("0",session["Detalii_cont_curent"][6]))
            return render_template("client/main_editeaza_comanda.html",SERVICII_DISP=servicii_disp,SERVICII=servicii)
        else:
            servicii=[]
            print ("s a apasat sterge serviciu")
            for i in range(1,int(request.form["action"].split(',')[1])+1):
                print(request.form["serviciu"+str(i)])
                servicii.append((request.form["serviciu"+str(i)],request.form["address"+str(i)]))
            del servicii[int(request.form["action"].split(',')[2])]
            print(servicii)
            return render_template("client/main_editeaza_comanda.html",SERVICII_DISP=servicii_disp,SERVICII=servicii)


    
    #print(comanda)
    servicii=[]
    
    
    c="""
        SELECT ID_serviciu, Adresa_serviciu_comanda FROM Comenzi_servicii WHERE ID_comanda = {}
    """.format(comanda[0])
    cursor.execute(c)
    servicii=list(cursor.fetchall())
    print(servicii)

    
    print ("abia am intrat")
    return render_template("client/main_editeaza_comanda.html",SERVICII_DISP=servicii_disp,SERVICII=servicii)
    

    
## PAGINI LUCRATOR SERVICII

@app.route('/mainworker/',methods=['POST', 'GET'])
def mainworker_page():
    if not session.get("Detalii_cont_curent"):
        return redirect('/')
    if session["Tip_user"] != 'worker':
        return redirect('/')
    return render_template('lucrator_servicii/main.html',NUME_USER=session["Detalii_cont_curent"][2])


@app.route('/mainworker/cont',methods=['POST', 'GET'])
def mainworker_cont_page():
    if not session.get("Detalii_cont_curent"):
        return redirect('/')
    if session["Tip_user"] != 'worker':
        return redirect('/')
    try:
        m=m=sql.connect(host=connectorhost,user=connectoruser,passwd=connectorpass,database=connectordb)
        cursor=m.cursor()
    except:
        return ("problema la conexiunea cu baza de date")


    c="""
        SELECT Denumire FROM Departamente WHERE ID_departament = {}
    """.format(session["Detalii_cont_curent"][5])
    cursor.execute(c)
    t=tuple(cursor.fetchall())
    if t==():
        depart="NICIUNUL"
    else:
        depart=t[0][0]
    return render_template('lucrator_servicii/cont.html',DETALII_CONT=session["Detalii_cont_curent"],DEPART=depart)


@app.route('/mainworker/cont/chpass',methods=['POST', 'GET'])
def mainworker_chpass_page():
    if not session.get("Detalii_cont_curent"):
        return redirect('/')
    if session["Tip_user"] != 'worker':
        return redirect('/')

    if request.method=="POST":
        try:
            m=m=sql.connect(host=connectorhost,user=connectoruser,passwd=connectorpass,database=connectordb)
            cursor=m.cursor()
        except:
            return ("problema la conexiunea cu baza de date")
        
        pw=request.form["password"]
        pwc=request.form["passwordconf"]
        if(pw != pwc):
            return render_template("lucrator_servicii/cont_chpass.html",parola_proasta=True)
        c="""UPDATE Angajati SET
        Parola = "{}"
        WHERE ID_angajat = "{}"
        """.format(pw,session["Detalii_cont_curent"][0])
        cursor.execute(c)
        try:
            m.commit()
        except:
            return "A aparut o problema la updatarea bazei de date"
        session["Detalii_cont_curent"]=(session["Detalii_cont_curent"][0],session["Detalii_cont_curent"][1],session["Detalii_cont_curent"][2],session["Detalii_cont_curent"][3],pw,session["Detalii_cont_curent"][5],session["Detalii_cont_curent"][6])
        return redirect('/mainworker/cont')
        
    
    return render_template ('lucrator_servicii/cont_chpass.html',parola_proasta = False)




@app.route('/mainworker/comenzinepreluate',methods=["GET","POST"])
def mainworker_comenzinepreluate():
    if not session.get("Detalii_cont_curent"):
        return redirect('/')
    if session["Tip_user"] != 'worker':
        return redirect('/')
    try:
        m=m=sql.connect(host=connectorhost,user=connectoruser,passwd=connectorpass,database=connectordb)
        cursor=m.cursor()
    except:
        return ("problema la conexiunea cu baza de date")
    

    if request.method=="POST":
        print("daaaaaaaaaaaaaaaaaaa")
        if "action" in request.form:
            print("s a preluat")
            
            id_comanda_serviciu=request.form["action"]
            print(id_comanda_serviciu)
            c="""SELECT COUNT(*) AS nr
                FROM Angajati_comanda_serviciu
                WHERE ID_comanda_serviciu = '{}' AND ID_angajat = '{}'   
            """.format(id_comanda_serviciu,session["Detalii_cont_curent"][0])
            cursor.execute(c)
            existenta=tuple(cursor.fetchall())
            print(existenta[0][0])
            if existenta[0][0]==0:
                
                c="""
                    INSERT INTO Angajati_comanda_serviciu (
                        ID_comanda_serviciu,
                        ID_angajat
                    ) VALUES(
                        '{}',
                        '{}'
                    )
                """.format(id_comanda_serviciu,session["Detalii_cont_curent"][0])
                cursor.execute(c)
                try:
                    m.commit()
                except:
                    return "A aparut o problema la inserarea in baza de date"
        elif  "renunta" in request.form:
            print("s a renuntat")
            id_comanda_serviciu=request.form["renunta"]
            print(id_comanda_serviciu)
            c="""
                DELETE FROM Angajati_comanda_serviciu WHERE ID_comanda_serviciu = {}
            """.format(id_comanda_serviciu)
            cursor.execute(c)
            try:
                m.commit()
            except:
                return "A aparut o problema la inserarea in baza de date"

    c="""SELECT cl.Nume,cl.Prenume,cl.Email,c.ID_comanda,c.Suma,c.Data_comanda,c.ID_comanda 
        FROM Clienti cl, Comenzi c
        WHERE cl.ID_client = c.ID_client ORDER BY c.Data_comanda, c.ID_comanda DESC
    """
    cursor.execute(c)
    comenzi=tuple(cursor.fetchall())
    if comenzi == ():
        return render_template("lucrator_servicii/comenzinepreluate.html",DETALII_CONT=session["Detalii_cont_curent"],COMENZI=[])
    else:
        comenzi_lista=[]
        for comanda in comenzi:
            c="""SELECT s.Pret_serviciu, s.Denumire, cs.Adresa_serviciu_comanda, a.Nume, a.Prenume, a.ID_angajat, cs.ID_comanda_serviciu
                FROM Servicii s, Comenzi_servicii cs , Angajati_comanda_serviciu acs, Angajati a
                WHERE cs.ID_comanda_serviciu = acs.ID_comanda_serviciu AND acs.ID_angajat = a.ID_angajat AND s.ID_serviciu=cs.ID_serviciu AND cs.ID_comanda = '{}'   
            """.format(comanda[6])
            cursor.execute(c)
            servicii_preluate=tuple(cursor.fetchall())
            c="""SELECT s.Pret_serviciu, s.Denumire, cs.Adresa_serviciu_comanda, cs.ID_comanda_serviciu
                FROM Servicii s INNER JOIN Comenzi_servicii cs ON s.ID_serviciu=cs.ID_serviciu LEFT JOIN Angajati_comanda_serviciu acs
                ON cs.ID_comanda_serviciu = acs.ID_comanda_serviciu
                WHERE  acs.ID_comanda_serviciu IS NULL AND cs.ID_comanda = '{}'  
            """.format(comanda[6])
           
            cursor.execute(c)
            servicii_nepreluate=tuple(cursor.fetchall())
            if servicii_nepreluate!=():
                comenzi_lista.append((comanda,servicii_preluate,servicii_nepreluate))

    #print(comenzi)
    #print(comenzi_lista)
    return render_template("lucrator_servicii/comenzinepreluate.html",DETALII_CONT=session["Detalii_cont_curent"],COMENZI=comenzi_lista)

@app.route('/mainworker/comenzipreluate',methods=["GET","POST"])
def mainworker_comenzipreluate():
    if not session.get("Detalii_cont_curent"):
        return redirect('/')
    if session["Tip_user"] != 'worker':
        return redirect('/')
    try:
        m=m=sql.connect(host=connectorhost,user=connectoruser,passwd=connectorpass,database=connectordb)
        cursor=m.cursor()
    except:
        return ("problema la conexiunea cu baza de date")
    

    if request.method=="POST":
        print("daaaaaaaaaaaaaaaaaaa")
        if "action" in request.form:
            print("s a preluat")
            
            id_comanda_serviciu=request.form["action"]
            print(id_comanda_serviciu)
            c="""SELECT COUNT(*) AS nr
                FROM Angajati_comanda_serviciu
                WHERE ID_comanda_serviciu = '{}' AND ID_angajat = '{}'   
            """.format(id_comanda_serviciu,session["Detalii_cont_curent"][0])
            cursor.execute(c)
            existenta=tuple(cursor.fetchall())
            print(existenta[0][0])
            if existenta[0][0]==0:
                
                c="""
                    INSERT INTO Angajati_comanda_serviciu (
                        ID_comanda_serviciu,
                        ID_angajat
                    ) VALUES(
                        '{}',
                        '{}'
                    )
                """.format(id_comanda_serviciu,session["Detalii_cont_curent"][0])
                cursor.execute(c)
                try:
                    m.commit()
                except:
                    return "A aparut o problema la inserarea in baza de date"
        elif  "renunta" in request.form:
            print("s a renuntat")
            id_comanda_serviciu=request.form["renunta"]
            print(id_comanda_serviciu)
            c="""
                DELETE FROM Angajati_comanda_serviciu WHERE ID_comanda_serviciu = {}
            """.format(id_comanda_serviciu)
            cursor.execute(c)
            try:
                m.commit()
            except:
                return "A aparut o problema la inserarea in baza de date"

    c="""SELECT cl.Nume, cl.Prenume, cl.Email, c.ID_comanda ,c.Suma, c.Data_comanda, c.ID_comanda 
        FROM Clienti cl INNER JOIN Comenzi c ON cl.ID_client = c.ID_client
        INNER JOIN Comenzi_servicii cs ON c.ID_comanda = cs.ID_comanda
        INNER JOIN Angajati_comanda_serviciu acs ON cs.ID_comanda_serviciu = acs.ID_comanda_serviciu
        WHERE acs.ID_angajat = '{}'
        GROUP BY cl.Nume, cl.Prenume, cl.Email, c.ID_comanda , c.Suma, c.Data_comanda, c.ID_comanda
         
    """.format(session["Detalii_cont_curent"][0])
    ## comenzile care au cel putin un serviciu preluat de angajatul logat.
    cursor.execute(c)
    comenzi=tuple(cursor.fetchall())
    if comenzi == ():
        return render_template("lucrator_servicii/comenzipreluate.html",DETALII_CONT=session["Detalii_cont_curent"],COMENZI=[])
    else:
        comenzi_lista=[]
        for comanda in comenzi:
            c="""SELECT s.Pret_serviciu, s.Denumire, cs.Adresa_serviciu_comanda, a.Nume, a.Prenume, a.ID_angajat, cs.ID_comanda_serviciu
                FROM Servicii s, Comenzi_servicii cs , Angajati_comanda_serviciu acs, Angajati a
                WHERE cs.ID_comanda_serviciu = acs.ID_comanda_serviciu AND acs.ID_angajat = a.ID_angajat AND s.ID_serviciu=cs.ID_serviciu AND cs.ID_comanda = '{}'   
            """.format(comanda[6])
            cursor.execute(c)
            servicii_preluate=tuple(cursor.fetchall())
            
            c="""SELECT s.Pret_serviciu, s.Denumire, cs.Adresa_serviciu_comanda, cs.ID_comanda_serviciu
                FROM Servicii s INNER JOIN Comenzi_servicii cs ON s.ID_serviciu=cs.ID_serviciu LEFT JOIN Angajati_comanda_serviciu acs
                ON cs.ID_comanda_serviciu = acs.ID_comanda_serviciu
                WHERE  acs.ID_comanda_serviciu IS NULL AND cs.ID_comanda = '{}'  
            """.format(comanda[6])

           
            cursor.execute(c)
            servicii_nepreluate=tuple(cursor.fetchall())
            comenzi_lista.append((comanda,servicii_preluate,servicii_nepreluate))

 
    return render_template("lucrator_servicii/comenzipreluate.html",DETALII_CONT=session["Detalii_cont_curent"],COMENZI=comenzi_lista)






@app.route('/mainworker/comenzisearch',methods=["GET","POST"])
def mainworker_cautare_comenzi():
    if not session.get("Detalii_cont_curent"):
        return redirect('/')
    if session["Tip_user"] != 'worker':
        return redirect('/')
    try:
        m=m=sql.connect(host=connectorhost,user=connectoruser,passwd=connectorpass,database=connectordb)
        cursor=m.cursor()
    except:
        return ("problema la conexiunea cu baza de date")
    
    if request.method=="POST":
        criteriu_cautare=request.form["cauta"]
        print("AICI ACIA ICIAICICIC")
        print(criteriu_cautare)
        c="""SELECT cl.Nume, cl.Prenume, cl.Email, c.ID_comanda ,c.Suma, c.Data_comanda, c.ID_comanda 
            FROM Clienti cl INNER JOIN Comenzi c ON cl.ID_client = c.ID_client
            INNER JOIN Comenzi_servicii cs ON c.ID_comanda = cs.ID_comanda
            
            WHERE UPPER(cs.Adresa_serviciu_comanda) LIKE '%{}%'
            GROUP BY cl.Nume, cl.Prenume, cl.Email, c.ID_comanda , c.Suma, c.Data_comanda, c.ID_comanda
        """.format(criteriu_cautare)
        cursor.execute(c)
        comenzi=tuple(cursor.fetchall())
        print(comenzi)
        if comenzi == ():
            return render_template("lucrator_servicii/cautarecomenzi.html",DETALII_CONT=session["Detalii_cont_curent"],COMENZI=[],NEGASIT=True)
        else:
            comenzi_lista=[]
            for comanda in comenzi:
                c="""SELECT s.Pret_serviciu, s.Denumire, cs.Adresa_serviciu_comanda, a.Nume, a.Prenume, a.ID_angajat, cs.ID_comanda_serviciu
                    FROM Servicii s, Comenzi_servicii cs , Angajati_comanda_serviciu acs, Angajati a
                    WHERE cs.ID_comanda_serviciu = acs.ID_comanda_serviciu AND acs.ID_angajat = a.ID_angajat AND s.ID_serviciu=cs.ID_serviciu AND cs.ID_comanda = '{}'   
                """.format(comanda[6])
                cursor.execute(c)
                servicii_preluate=tuple(cursor.fetchall())
            
                c="""SELECT s.Pret_serviciu, s.Denumire, cs.Adresa_serviciu_comanda, cs.ID_comanda_serviciu
                    FROM Servicii s INNER JOIN Comenzi_servicii cs ON s.ID_serviciu=cs.ID_serviciu LEFT JOIN Angajati_comanda_serviciu acs
                    ON cs.ID_comanda_serviciu = acs.ID_comanda_serviciu
                    WHERE  acs.ID_comanda_serviciu IS NULL AND cs.ID_comanda = '{}'  
                """.format(comanda[6])

            
                cursor.execute(c)
                servicii_nepreluate=tuple(cursor.fetchall())
            
                comenzi_lista.append((comanda,servicii_preluate,servicii_nepreluate))

            return render_template("lucrator_servicii/cautarecomenzi.html",DETALII_CONT=session["Detalii_cont_curent"],COMENZI=comenzi_lista,NEGASIT=False)

    
    return render_template("lucrator_servicii/cautarecomenzi.html",DETALII_CONT=session["Detalii_cont_curent"],COMENZI=[],NEGASIT=False)



## FUCNTII MANAGER



@app.route('/mainmanager/',methods=['POST', 'GET'])
def mainmanager_page():
    if not session.get("Detalii_cont_curent"):
        return redirect('/')
    if session["Tip_user"] != 'manager':
        return redirect('/')
    return render_template('manager/main.html',NUME_USER=session["Detalii_cont_curent"][2])




@app.route('/mainmanager/cont/chpass',methods=['POST', 'GET'])
def mainmanager_chpass_page():
    if not session.get("Detalii_cont_curent"):
        return redirect('/')
    if session["Tip_user"] != 'manager':
        return redirect('/')

    if request.method=="POST":
        try:
            m=m=sql.connect(host=connectorhost,user=connectoruser,passwd=connectorpass,database=connectordb)
            cursor=m.cursor()
        except:
            return ("problema la conexiunea cu baza de date")
        
        pw=request.form["password"]
        pwc=request.form["passwordconf"]
        if(pw != pwc):
            return render_template("manager/cont_chpass.html",parola_proasta=True)
        c="""UPDATE Angajati SET
        Parola = "{}"
        WHERE ID_angajat = "{}"
        """.format(pw,session["Detalii_cont_curent"][0])
        cursor.execute(c)
        try:
            m.commit()
        except:
            return "A aparut o problema la updatarea bazei de date"
        session["Detalii_cont_curent"]=(session["Detalii_cont_curent"][0],session["Detalii_cont_curent"][1],session["Detalii_cont_curent"][2],session["Detalii_cont_curent"][3],pw,session["Detalii_cont_curent"][5],session["Detalii_cont_curent"][6])
        return redirect('/mainmanager/cont')
        
    
    return render_template ('manager/cont_chpass.html',parola_proasta = False)


@app.route('/mainmanager/cont',methods=['POST', 'GET'])
def mainmanager_cont_page():
    if not session.get("Detalii_cont_curent"):
        return redirect('/')
    if session["Tip_user"] != 'manager':
        return redirect('/')
    try:
        m=m=sql.connect(host=connectorhost,user=connectoruser,passwd=connectorpass,database=connectordb)
        cursor=m.cursor()
    except:
        return ("problema la conexiunea cu baza de date")


    c="""
        SELECT Denumire FROM Departamente WHERE ID_departament = {}
    """.format(session["Detalii_cont_curent"][5])
    cursor.execute(c)
    t=tuple(cursor.fetchall())
    if t==():
        depart="NICIUNUL"
    else:
        depart=t[0][0]
    return render_template('manager/cont.html',DETALII_CONT=session["Detalii_cont_curent"],DEPART=depart)


@app.route('/mainmanager/workerstats',methods=['POST', 'GET'])
def mainmanager_workerstats_page():
    if not session.get("Detalii_cont_curent"):
        return redirect('/')
    if session["Tip_user"] != 'manager':
        return redirect('/')
    try:
        m=m=sql.connect(host=connectorhost,user=connectoruser,passwd=connectorpass,database=connectordb)
        cursor=m.cursor()
    except:
        return ("problema la conexiunea cu baza de date")

    c="""
        SELECT a.Nume,a.Prenume, a.Email, a.Salariu, d.Denumire
        FROM Angajati a INNER JOIN Departamente d ON a.ID_departament = d.ID_departament
        ORDER BY d.ID_departament, a.Nume,a.Prenume,a.ID_angajat
            
    """
    cursor.execute(c)
    t=tuple(cursor.fetchall())
    print(t)
    c="""
        SELECT COUNT(ID_comanda)
        FROM Comenzi

    """
    
    cursor.execute(c)
    tt=tuple(cursor.fetchall())
    if str(tt[0][0])!="0":

        c="""
            SELECT cv.nume ,cv.Prenume, cv.Email, cv.Salariu, cv.Denumire, cv.total
            FROM (SELECT a.Nume,a.Prenume, a.Email, a.Salariu, d.Denumire, SUM(s.Pret_serviciu) AS total
            FROM Angajati a INNER JOIN Departamente d ON a.ID_departament = d.ID_departament
            INNER JOIN Angajati_comanda_serviciu acs ON a.ID_Angajat=acs.ID_angajat
            INNER JOIN Comenzi_servicii cs on cs.ID_comanda_serviciu = acs.ID_comanda_serviciu
            INNER JOIN Servicii s on s.ID_serviciu = cs.ID_serviciu
            GROUP BY a.Nume,a.Prenume, a.Email, a.Salariu, d.Denumire
            ORDER BY total DESC) cv
            LIMIT 1
        """
        cursor.execute(c)
        angajat_suma_mare=tuple(cursor.fetchall())
        if angajat_suma_mare==():
            return render_template('manager/workerstats.html',DETALII_CONT=session["Detalii_cont_curent"],ANGAJATI=t,FARA_COMENZI=True)

        

        c="""
            SELECT cv.nume ,cv.Prenume, cv.Email, cv.Salariu, cv.Denumire, COUNT(cv.ID_angajat) as nrcomplete

            FROM
            (SELECT a.ID_angajat, a.Nume,a.Prenume, a.Email, a.Salariu, d.Denumire,cs.ID_comanda, COUNT(acs.ID_comanda_serviciu) AS preluate
            FROM Angajati a INNER JOIN Departamente d ON a.ID_departament = d.ID_departament
            INNER JOIN Angajati_comanda_serviciu acs ON a.ID_Angajat=acs.ID_angajat
            INNER JOIN Comenzi_servicii cs on cs.ID_comanda_serviciu = acs.ID_comanda_serviciu
            INNER JOIN Servicii s on s.ID_serviciu = cs.ID_serviciu
            INNER JOIN Comenzi c on cs.ID_comanda = c.ID_comanda
            GROUP BY a.ID_angajat,a.Nume,a.Prenume, a.Email, a.Salariu, d.Denumire,c.ID_comanda) cv
            
            INNER JOIN

            (SELECT c2.ID_comanda, COUNT(cs2.ID_comanda) AS nrserv
            FROM Comenzi c2 INNER JOIN Comenzi_servicii cs2 ON c2.ID_comanda = cs2.ID_comanda 
            GROUP BY cs2.ID_comanda) AS ccs2
            
            ON ccs2.ID_comanda = cv.ID_comanda
            WHERE cv.preluate = ccs2.nrserv 

            GROUP BY cv.nume ,cv.Prenume, cv.Email, cv.Salariu, cv.Denumire
            ORDER BY nrcomplete DESC
            LIMIT 1
        """
        cursor.execute(c)
        t2=tuple(cursor.fetchall())
        print(t)
        if t2==():
            return render_template('manager/workerstats.html',DETALII_CONT=session["Detalii_cont_curent"],ANGAJATI=t,FARA_COMENZI=True)

        
        return render_template('manager/workerstats.html',DETALII_CONT=session["Detalii_cont_curent"],ANGAJATI=t,ANGAJAT_SUMA_MARE=angajat_suma_mare[0],ANGAJAT_COMENZI_FULL=t2[0])

    else:

        return render_template('manager/workerstats.html',DETALII_CONT=session["Detalii_cont_curent"],ANGAJATI=t,FARA_COMENZI=True)



@app.route('/mainmanager/serviciistats',methods=['POST', 'GET'])
def mainmanager_serviciistats_page():
    if not session.get("Detalii_cont_curent"):
        return redirect('/')
    if session["Tip_user"] != 'manager':
        return redirect('/')
    try:
        m=m=sql.connect(host=connectorhost,user=connectoruser,passwd=connectorpass,database=connectordb)
        cursor=m.cursor()
    except:
        return ("problema la conexiunea cu baza de date")

    

    if request.method=="POST":
        c="""
            INSERT INTO Servicii(
                Denumire,
                Pret_serviciu
            ) VALUES ('{}','{}')
        """.format(request.form["denumire"],request.form["pret_serviciu"])
        cursor.execute(c)
        m.commit()
    
    c="""
        SELECT s.Denumire , s.Pret_serviciu*COUNT(cs.ID_serviciu) AS revenue, s.Pret_serviciu, COUNT(cs.ID_serviciu) AS orders 
        FROM Servicii s LEFT JOIN Comenzi_servicii cs ON s.ID_serviciu = cs.ID_serviciu
        GROUP BY s.ID_serviciu
        ORDER BY revenue DESC
    """
    cursor.execute(c)
    servicii=tuple(cursor.fetchall())
    
    
    
    return render_template('manager/serviciistats.html',SERVICII=servicii)





@app.route('/mainmanager/comenzistats',methods=['POST', 'GET'])
def mainmanager_comenzistats_page():
    if not session.get("Detalii_cont_curent"):
        return redirect('/')
    if session["Tip_user"] != 'manager':
        return redirect('/')
    try:
        m=m=sql.connect(host=connectorhost,user=connectoruser,passwd=connectorpass,database=connectordb)
        cursor=m.cursor()
    except:
        return ("problema la conexiunea cu baza de date")

    
    c="""SELECT cl.Nume, cl.Prenume, cl.Email, c.ID_comanda ,c.Suma, c.Data_comanda, c.ID_comanda 
            FROM Clienti cl INNER JOIN Comenzi c ON cl.ID_client = c.ID_client
            WHERE Suma >= (SELECT AVG(Suma) FROM Comenzi)
        """
    cursor.execute(c)
    comenzi=tuple(cursor.fetchall())
    print(comenzi)
    if comenzi == ():
        return render_template("manager/comenzistats.html",DETALII_CONT=session["Detalii_cont_curent"],COMENZI=[])
    else:
        c="""SELECT AVG(Suma) FROM Comenzi
        """
        cursor.execute(c)
        t=tuple(cursor.fetchall())
        medie=t[0][0]
        comenzi_lista=[]
        for comanda in comenzi:
            c="""SELECT s.Pret_serviciu, s.Denumire, cs.Adresa_serviciu_comanda, a.Nume, a.Prenume, a.ID_angajat, cs.ID_comanda_serviciu
                FROM Servicii s, Comenzi_servicii cs , Angajati_comanda_serviciu acs, Angajati a
                WHERE cs.ID_comanda_serviciu = acs.ID_comanda_serviciu AND acs.ID_angajat = a.ID_angajat AND s.ID_serviciu=cs.ID_serviciu AND cs.ID_comanda = '{}'   
            """.format(comanda[6])
            cursor.execute(c)
            servicii_preluate=tuple(cursor.fetchall())
        
            c="""SELECT s.Pret_serviciu, s.Denumire, cs.Adresa_serviciu_comanda, cs.ID_comanda_serviciu
                FROM Servicii s INNER JOIN Comenzi_servicii cs ON s.ID_serviciu=cs.ID_serviciu LEFT JOIN Angajati_comanda_serviciu acs
                ON cs.ID_comanda_serviciu = acs.ID_comanda_serviciu
                WHERE  acs.ID_comanda_serviciu IS NULL AND cs.ID_comanda = '{}'  
            """.format(comanda[6])

        
            cursor.execute(c)
            servicii_nepreluate=tuple(cursor.fetchall())
        
            comenzi_lista.append((comanda,servicii_preluate,servicii_nepreluate))

    comenzi_peste_medie=comenzi_lista

    c="""SELECT cl.Nume, cl.Prenume, cl.Email, c.ID_comanda ,c.Suma, c.Data_comanda, c.ID_comanda 
            FROM Clienti cl INNER JOIN Comenzi c ON cl.ID_client = c.ID_client
            INNER JOIN Comenzi_servicii cs ON c.ID_comanda = cs.ID_comanda
            
            GROUP BY cl.Nume, cl.Prenume, cl.Email, c.ID_comanda ,c.Suma, c.Data_comanda, c.ID_comanda
            HAVING COUNT(cs.ID_comanda) >= ( SELECT MAX(ceva.numar) FROM ( SELECT COUNT(cs.ID_comanda) as numar
                FROM Comenzi c INNER JOIN Comenzi_servicii cs ON c.ID_comanda = cs.ID_comanda
                GROUP BY cs.ID_comanda ) ceva)
        """
    cursor.execute(c)
    comenzi=tuple(cursor.fetchall())
    print(comenzi)
    if comenzi == ():
        return render_template("manager/comenzistats.html",DETALII_CONT=session["Detalii_cont_curent"],COMENZI=[])
    else:
        c="""SELECT AVG(Suma) FROM Comenzi
        """
        cursor.execute(c)
        t=tuple(cursor.fetchall())
        medie=t[0][0]
        comenzi_lista=[]
        for comanda in comenzi:
            c="""SELECT s.Pret_serviciu, s.Denumire, cs.Adresa_serviciu_comanda, a.Nume, a.Prenume, a.ID_angajat, cs.ID_comanda_serviciu
                FROM Servicii s, Comenzi_servicii cs , Angajati_comanda_serviciu acs, Angajati a
                WHERE cs.ID_comanda_serviciu = acs.ID_comanda_serviciu AND acs.ID_angajat = a.ID_angajat AND s.ID_serviciu=cs.ID_serviciu AND cs.ID_comanda = '{}'   
            """.format(comanda[6])
            cursor.execute(c)
            servicii_preluate=tuple(cursor.fetchall())
        
            c="""SELECT s.Pret_serviciu, s.Denumire, cs.Adresa_serviciu_comanda, cs.ID_comanda_serviciu
                FROM Servicii s INNER JOIN Comenzi_servicii cs ON s.ID_serviciu=cs.ID_serviciu LEFT JOIN Angajati_comanda_serviciu acs
                ON cs.ID_comanda_serviciu = acs.ID_comanda_serviciu
                WHERE  acs.ID_comanda_serviciu IS NULL AND cs.ID_comanda = '{}'  
            """.format(comanda[6])

        
            cursor.execute(c)
            servicii_nepreluate=tuple(cursor.fetchall())
        
            comenzi_lista.append((comanda,servicii_preluate,servicii_nepreluate))
    comenzi_serv_max=comenzi_lista
    return render_template('manager/comenzistats.html',COMENZI=comenzi_peste_medie,MEDIE_SUMA=medie,COMENZI_SERVICII_MAX=comenzi_serv_max)



@app.route('/mainmanager/comenziall',methods=['POST', 'GET'])
def mainmanager_comenziall_page():
    if not session.get("Detalii_cont_curent"):
        return redirect('/')
    if session["Tip_user"] != 'manager':
        return redirect('/')
    try:
        m=m=sql.connect(host=connectorhost,user=connectoruser,passwd=connectorpass,database=connectordb)
        cursor=m.cursor()
    except:
        return ("problema la conexiunea cu baza de date")

    
    c="""SELECT cl.Nume, cl.Prenume, cl.Email, c.ID_comanda ,c.Suma, c.Data_comanda, c.ID_comanda 
            FROM Clienti cl INNER JOIN Comenzi c ON cl.ID_client = c.ID_client
            ORDER BY Data_comanda, Suma, ID_comanda DESC
        """
    cursor.execute(c)
    comenzi=tuple(cursor.fetchall())
    print(comenzi)
    if comenzi == ():
        return render_template("manager/comenziall.html",DETALII_CONT=session["Detalii_cont_curent"],COMENZI=[])
    else:
        c="""SELECT AVG(Suma) FROM Comenzi
        """
        cursor.execute(c)
        t=tuple(cursor.fetchall())
        medie=t[0][0]
        comenzi_lista=[]
        for comanda in comenzi:
            c="""SELECT s.Pret_serviciu, s.Denumire, cs.Adresa_serviciu_comanda, a.Nume, a.Prenume, a.ID_angajat, cs.ID_comanda_serviciu
                FROM Servicii s, Comenzi_servicii cs , Angajati_comanda_serviciu acs, Angajati a
                WHERE cs.ID_comanda_serviciu = acs.ID_comanda_serviciu AND acs.ID_angajat = a.ID_angajat AND s.ID_serviciu=cs.ID_serviciu AND cs.ID_comanda = '{}'   
            """.format(comanda[6])
            cursor.execute(c)
            servicii_preluate=tuple(cursor.fetchall())
        
            c="""SELECT s.Pret_serviciu, s.Denumire, cs.Adresa_serviciu_comanda, cs.ID_comanda_serviciu
                FROM Servicii s INNER JOIN Comenzi_servicii cs ON s.ID_serviciu=cs.ID_serviciu LEFT JOIN Angajati_comanda_serviciu acs
                ON cs.ID_comanda_serviciu = acs.ID_comanda_serviciu
                WHERE  acs.ID_comanda_serviciu IS NULL AND cs.ID_comanda = '{}'  
            """.format(comanda[6])

        
            cursor.execute(c)
            servicii_nepreluate=tuple(cursor.fetchall())
        
            comenzi_lista.append((comanda,servicii_preluate,servicii_nepreluate))

    
    return render_template('manager/comenziall.html',COMENZI=comenzi_lista)



if __name__== "__main__":
    app.run(debug=True,port=8000)

