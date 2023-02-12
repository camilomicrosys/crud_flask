from flask import Flask
from flask import render_template,request,redirect,url_for,flash
from flaskext.mysql import MySQL
from flask import send_from_directory
from datetime import datetime
import os

#creamos la aplicacion
app=Flask(__name__)
#validacion de formularios importamos flash que es para las notificaciones y creamos esta variable
app.secret_key="Camilodev2023"

#conectamos a base de datos
mysql=MySQL()
app.config['MYSQL_DATABASE_HOST']='localhost'
app.config['MYSQL_DATABASE_USER']='root'
app.config['MYSQL_DATABASE_PASSWORD']=''
app.config['MYSQL_DATABASE_DB']='flask'
mysql.init_app(app)
#creamos la ruta de carpeta uploads para hacer las referencias a eliminacion de archivos 
carpeta_uploads=os.path.join('uploads')
#metemos en la configuracion la carpeta
app.config['carpeta_uploads']=carpeta_uploads


#para mostrar imagenes en flask debemos crear una ruta con el nombre del archivo para poder referenciar en el html img sino no puede acceder al recurso
@app.route('/uploads/<nombreFoto>')
def uploads(nombreFoto):
    return send_from_directory(app.config['carpeta_uploads'],nombreFoto)

#para referenciar archivos css js  creamos una carpeta en raiz llamada static y flask alli referencia todos esos archivos
@app.route('/archivoReferenciar')
def archivoReferenciar(archivo):
     return send_from_directory(app.static_folder,archivo)

#creamos la ruta por defecto el sabe que se guardan en templates
@app.route('/')
def index():
    sql="SELECT * FROM `empleados`"
    conn=mysql.connect()
    cursor=conn.cursor()
    #aca ejecutamos el sql y le pasamos los datos e tupla o array php 
    cursor.execute(sql)
    #obtenemos la informacion del query
    empleados=cursor.fetchall()
    #imprimimos a ver si nos llegan los registros esto se ve en consola
    print(empleados)
    conn.commit()
    #los datos me vienen ((1,5,3)) arreglo de arreglo o llamos aca tuplas
    return render_template('empleados/index.html',empleados=empleados)

@app.route('/create')
def create():
    return render_template('empleados/create.html')

#recibimos la informacion del formulario visat crear.html
@app.route('/store', methods=['POST'])
#este nombre puede ser cualquiera
def storage():
    #recibimos los datos del formulario
    _nombre=request.form['nombre']
    _email=request.form['email']
    _foto=request.files['foto']
    
    #validamos formulario
    if _nombre=='' or _email=='' or _foto.filename=='':
        flash('Recuerda diligenciar todos los campos')
        return redirect(url_for('create'))
        
    
    #para que la foto sea unica ponemos hora min sec
    now=datetime.now()
    tiempo=now.strftime("%Y%H%M%S")
    #si nombre de foto no es vacio es por que si viene foto entonces la subimos y la guardamos
    if _foto.filename !='':
        nuevo_nombre_foto=tiempo+_foto.filename
        
        #guardamos la foto
        _foto.save("uploads/"+nuevo_nombre_foto)
        
   
    sql="INSERT INTO `empleados` (`id`, `nombre`, `correo`, `foto`) VALUES (NULL,%s,%s,%s)"
     #como siempre los archivos tienen tamano filename etc aca accedemos al nombre
    datos=(_nombre,_email,nuevo_nombre_foto)
    conn=mysql.connect()
    cursor=conn.cursor()
    #aca ejecutamos el sql y le pasamos los datos e tupla o array php 
    cursor.execute(sql,datos)
    conn.commit()
    return redirect('/')

#eliminar registro
@app.route('/destroy/<int:id>')
def destroy(id):
    conn=mysql.connect()
    cursor=conn.cursor()
     #Como eliminamos el usuario tambien debemos eliminar el fichero
    cursor.execute("SELECT foto FROM empleados WHERE id=%s",id)
    fila=cursor.fetchall()
    # 0 por que es una tupla arreglo de arreglos 0 el prmer elemento y 0 por que estamos solo cogiendo foto que es 1 campo
    os.remove(os.path.join(app.config['carpeta_uploads'],fila[0][0]))
    #aca ejecutamos el sql y le pasamos los datos e tupla o array php 
    cursor.execute("DELETE FROM empleados WHERE id=%s",(id))
    conn.commit()
    print("registro eliminado exitosamente")
    return redirect('/')
#editar para mostrar los datos a editar
@app.route('/editar/<int:id>')
def editar(id):
    sql="SELECT * FROM `empleados` WHERE id=%s"
    conn=mysql.connect()
    cursor=conn.cursor()
    #aca ejecutamos el sql y le pasamos los datos e tupla o array php 
    cursor.execute(sql,(id))
    #obtenemos la informacion del query
    empleados=cursor.fetchall()
    #imprimimos a ver si nos llegan los registros esto se ve en consola
    print(empleados)
    conn.commit()
    return render_template('empleados/edit.html',empleado_editar=empleados)


 #actualizadion
#recibimos la informacion del formulario visat edit.html
@app.route('/update', methods=['POST'])
def update():
    #recibimos los datos del formulario
    _nombre=request.form['nombre']
    _email=request.form['email']
    _foto=request.files['foto']
    id_empleado=request.form['idempleado']
    
        
    #actualizamos todo , menos la imagen por que puede que la imagen no la esten actualizando mas abajito validamos si se esta modificando la imagen tambien
    sql="UPDATE `empleados` SET `nombre`=%s,`correo`=%s WHERE id=%s"
     #como siempre los archivos tienen tamano filename etc aca accedemos al nombre
    datos=(_nombre,_email,id_empleado)
    conn=mysql.connect()
    cursor=conn.cursor()
    
    #creamos nuevo nombre de imagen por si viene imagen
    now=datetime.now()
    tiempo=now.strftime("%Y%H%M%S")
    #si nombre de foto no es vacio es por que si viene foto entonces la subimos y la guardamos
    if _foto.filename !='':
        nuevo_nombre_foto=tiempo+_foto.filename
        
        #guardamos la foto en las carpetas
        _foto.save("uploads/"+nuevo_nombre_foto)
        #buscamos la imagen que tienen actualmente en db la ruta y borramos esa y actualizamos con el nuevo nombre
        cursor.execute("SELECT foto FROM empleados WHERE id=%s",id_empleado)
        fila=cursor.fetchall()
        # 0 por que es una tupla arreglo de arreglos 0 el prmer elemento y 0 por que estamos solo cogiendo foto que es 1 campo
        os.remove(os.path.join(app.config['carpeta_uploads'],fila[0][0]))
        #el solo va entrar en este camino cuando venga una foto de lo contrario entra al exceute de abajo que actualiza todo menos foto
        cursor.execute("UPDATE empleados SET foto=%s WHERE id=%s",(nuevo_nombre_foto,id_empleado))
        conn.commit()  
    #aca ejecutamos el sql y le pasamos los datos e tupla o array php 
    cursor.execute(sql,datos)
    conn.commit()
    return redirect('/')
    
    

#esto debe colocarse siempre para que funcione la app
if __name__=='__main__':
    app.run(debug=True)