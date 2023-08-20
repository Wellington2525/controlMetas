from flask import Flask, render_template, request, redirect, url_for,session,flash
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from flask import jsonify,json
#from flask_table import Table, Col, LinkCol
import bcrypt 
import jwt
from werkzeug.security import generate_password_hash, check_password_hash 
import pyfiglet
import secrets
import csv
from flask_login import LoginManager, login_user, logout_user, login_required,UserMixin,current_user
from wtforms.validators import InputRequired, Length, ValidationError

#from config import config
from models.entities.User import User

from models.ModelUsers import ModelUser
# token = secrets.token_urlsafe(16)
# print("token=>",token)


app = Flask(__name__)
token = app.secret_key = secrets.token_urlsafe(16)
print("token=>",token)
#app.secret_key = 'B!1w8NAt1T^%kvhUI*S^'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'metas'
mysql = MySQL(app)
   


login_manager_app = LoginManager(app)
login_manager_app.session_protection = "strong"
result = pyfiglet.figlet_format("Control Metas", font="banner3-D")
print(result)

class User(UserMixin):
    def __init__(self, id):
        self.id = id
        
        
    

def validate_username(self, usernameT):
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM Users WHERE username = %s', (usernameT))
        row = cursor.fetchone()
        existing_user_username = row
        if existing_user_username:
            raise ValidationError(
                'That username already exists. Please choose a different one.')
            
            
            
@app.route('/home', methods=['GET', 'POST'])
def layout():
    msg = ''
    if 'loggedin' in session:
            # We need all the account info for the user so we can display it on the profile page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM Users WHERE username = %s', (session['username'],))
        
        account = cursor.fetchall()
        
        #print(account)
   
        
        return render_template('home.html', account=account)
    else:
             return "<h3>debe iniciar la sesion para poder entrar a la website</h3>", 404


@app.route('/user', methods=['GET'])
def crudusers():
     if 'loggedin' in session:
            # We need all the account info for the user so we can display it on the profile page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM Users WHERE username = %s', (session['username'],))
        
        account = cursor.fetchone()
        
        #print(account)
   
        
        return render_template('home.html', account=account)
     else:
        return "<h3>debe iniciar la sesion para poder entrar a la website</h3>", 404
       

@app.route('/metas' ,methods=['GET', 'POST'])
#@login_required
def Metas():
    msg=''
    
    if 'loggedin' in session:
            # We need all the account info for the user so we can display it on the profile page
        # cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # cursor.execute('SELECT * FROM Users WHERE username = %s', (session['username'],))
        # account = cursor.fetchone()
        
        conn = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        sql = ('SELECT fecha,cantidad,metaacumulada,ejecutada FROM metasdiarias')
        conn.execute(sql)
        rows = conn.fetchall()
       
    
            
        return render_template('ingresoMetas.html', row=rows)
    else:
         return "<h3>debe iniciar la sesion para poder entrar a la website</h3>", 404



@app.route('/upload', methods=['GET', 'POST'])

def upload_csv():
    if 'loggedin' in session:
        if request.method == 'POST':
            msg='Archivo ingresado'
            archivo = request.files['metas_csv']
            if archivo:
                          
                    flash('Error este archivo no tiene los formato establecido', category='success')
            else: 

             if archivo.filename == '':
                return render_template('nocsv.html',msg=msg)
             if archivo.filename.split('.')[-1].lower() != 'csv':
                return render_template('nocsv.html',msg=msg)

             if archivo:
                # Leer el contenido del archivo CSV
                csv_data = archivo.read().decode('utf-8')
               
                

                # Procesar el archivo CSV y almacenar los datos en la base de datos
                with csv.StringIO(csv_data) as csvfile:
                    csvreader = csv.DictReader(csvfile)
                 
                    for row in csvreader:
                        #fecha = row['fech']
                          
                        fecha = row['fecha']
                        cantidad =row['cantidad']
                        metaacumulada = row['metaacumulada']

                        # Realizar la conexión con la base de datos
                        conn = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                        #print('xlsx',row)

                        #Insertar los datos en la base de datos
                        query = "INSERT INTO metasdiarias (fecha, cantidad, metaacumulada) VALUES (%s, %s, %s)"
                        values = (fecha, cantidad, metaacumulada)
                        conn.execute(query, values)

                        # Cerrar la conexión
                        mysql.connection.commit()
                        conn.close()
                        conn.close()
                flash('Archivo xlsx subido exitosamente', category='success')
                return redirect(url_for('Metas'))  

        
        return redirect(url_for('Metas'))    
    else:
         return "<h3>debe iniciar la sesion para poder entrar a la website</h3>" , 404       



@login_manager_app.user_loader
def load_user(user_id):
    # Fetch user data from MySQL based on user_id and create a User object
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user_data = cursor.fetchone()
    cursor.close()
    #print('ques esto',user_data)

    if user_data:
        return User(user_data['id'])
    return None



@app.route('/', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form.get('username')
        password = request.form.get('password')
        print('normal pass',password, username)
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM Users WHERE username = %s', (username,))
        account = cursor.fetchone()
        
        if account:
            password_rs = account['password']
            #print('hast',account) 
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            msg= 'Logged in successfully !'
            
            if check_password_hash(password_rs, password):
                #flash('Error en el formato', category='success')
                session['loggedin'] = True
                session['id'] = account['id']
                session['username'] = account['username']
                msg= 'Logged in successfully !'
                
                #print('pase')
                user =  session['username'] = account['username']
                #print('user',user)
                
                #login_user(account, remember=True)
                 
                return redirect(url_for('layout'))
                
            else:
                flash('Error en el password, pls revisar', category='danger')
                msg='erro'
                
                print('error password')
        else:
            flash('Error este usuario no existe, pls revisar', category='danger')
        
    return render_template('login.html', msg=msg)
            
        
    
@app.route('/registro', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    if 'loggedin' in session:
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
        if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'nombre' in request.form:
            # Create variables for easy access
            username = request.form['username']
            password = request.form['password']
            nombre = request.form['nombre']
            
            
            _hashed_password = generate_password_hash(password)
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM Users WHERE username = %s', (username,))
            account = cursor.fetchone()
            # If account exists show error and validation checks
            if account:
                msg = 'Este registro ya existe!'
        
            else:
                # Account doesnt exists and the form data is valid, now insert new account into accounts table
                cursor.execute('INSERT INTO Users (username, password, nombre) VALUES (%s, %s,%s)', (username, _hashed_password,nombre))
                mysql.connection.commit()
                msg = 'Registro ingresado'
        elif request.method == 'POST':
            # Form is empty... (no POST data)
            msg = 'Please fill out the form!'
        # Show registration form with message (if any)
        return render_template('registroLogin.html', msg=msg)    
    else:
        return "<h3>Debe iniciar la sesion para poder entrar a la website</h3>", 404
    
# @login_manager_app.user_loader
# def load_user(id):
#     return get_by_id(id)
      

def get_by_id(self, id):
    try:
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM Users WHERE id = %s', (id,))
        row = cursor.fetchone()
        if row != None:
            print('rows',row)
            return row(row[0], row[1], None, row[2])
        else:
            return None
    except Exception as ex:
        raise Exception(ex)


@app.route('/protected')
@login_required
def protected():
    return "<h3>Página no encontrada</h3>", 404
    


def status_401(error):
    return redirect(url_for('login'))


def status_404(error):
    return "<h3>Página no encontrada</h3>", 404
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    logout_user()
    id=2

    
    return redirect(url_for('login'))










if __name__ == '__main__':
    #app.config.from_object(config['development'])
    app.debug = True
    app.register_error_handler(401, status_401)
    app.register_error_handler(404, status_404)
    app.run(host = 'localhost', port = 9000)
    