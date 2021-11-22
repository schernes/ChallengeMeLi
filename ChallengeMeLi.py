from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from datetime import datetime

import base64

from email.mime.multipart import MIMEMultipart
from pydrive2.drive import GoogleDrive
from email.mime.text import MIMEText



# INICIAR SESION EN DRIVE
def login():
    directorio_credenciales = 'credentials_module.json'
    gauth = GoogleAuth()
    gauth.LoadCredentialsFile(directorio_credenciales)
    
    if gauth.access_token_expired:
        gauth.Refresh()
        gauth.LoadCredentialsFile(directorio_credenciales)
    else:
        gauth.Authorize()
    return GoogleDrive(gauth)
    
#1 Crear/Conectar a la BD
import sqlite3

conexionDB=sqlite3.connect("ChallengeMeLi.db3")

miCursor=conexionDB.cursor()

#2 Crear las tablas
try:
    miCursor.execute("CREATE TABLE FILES (FILE_ID VARCHAR(50) PRIMARY KEY, FILE_NAME VARCHAR(50), FILE_EXTENSION VARCHAR(50), OWNER VARCHAR(50), VISIBILITY VARCHAR(50), LAST_CHANGE_DATE VARCHAR(50))")
    miCursor.execute("CREATE TABLE PUBLIC_FILES_HISTORY (ID INTEGER PRIMARY KEY AUTOINCREMENT, FILE_ID VARCHAR(50), CHANGE_TO_PRIVATE_DATE DATE)")
except:
    pass

#3 Buscar archivos públicos
def buscaPub(query):
    sumaHistorico = []
    listaArchivosMod = []
    credenciales = login()
    listaPubs = credenciales.ListFile({'q': query}).GetList()
    for f in listaPubs:
        eliminar_permisos(f['id'])
        fechayHora = datetime.now()
        fechayHoraFormateada = fechayHora.strftime("%d/%m/%Y %H:%M:%S")
        historico = (f['id'],fechayHoraFormateada)
        sumaHistorico.append(historico)
        ArchivoMod = "- "+f['title']+" (ID: "+f['id']+").\n"
        listaArchivosMod.append(ArchivoMod)
        dirMail= f['owners'][0]['emailAddress']
    insertHistorico(sumaHistorico)
    cuerpoMail = ''.join(listaArchivosMod)
    if (listaArchivosMod != []):
        sendMail(cuerpoMail,dirMail)

#4 Pasar archivo a Privado
def eliminar_permisos(id_drive):
    drive = login()
    file1 = drive.CreateFile({'id':id_drive})
    permissions = file1.GetPermissions()
    file1.DeletePermission('anyoneWithLink')

#5 Agregar al histórico
def insertHistorico(x):
    miCursor.executemany("INSERT INTO PUBLIC_FILES_HISTORY VALUES(NULL,?,?)", x)

#6 Enviar Email

def sendMail(x,y):
          
    CLIENT_SECRET_FILE = 'client_secrets.json'
    API_NAME = 'gmail'
    API_VERSION = 'v1'
    SCOPES = ['https://mail.google.com/']
    
    from Google import Create_Service
    service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)
    
    emailMsg = 'Este es un mensaje automático para indicarle que la privacidad de los archivos listados a continuación ha sido modificada de pública a privada: \n\n' + x + '\n¡Muchas gracias!'
    mimeMessage = MIMEMultipart()
    mimeMessage['to'] = y
    mimeMessage['subject'] = 'Notificación: Modificación de privacidad de archivos (Challenge MeLi)'
    mimeMessage.attach(MIMEText(emailMsg, 'plain'))

    raw_string = base64.urlsafe_b64encode(mimeMessage.as_bytes()).decode()
    message = service.users().messages().send(userId='me', body={'raw': raw_string}).execute()



# 7 Recorrer archivos del drive
def recorreDrive(query):
    archivosParaInsert = []
    archivosEnDrive = []
    credenciales = login()
    archivos_drive = credenciales.ListFile({'q': query}).GetList()
    for f in archivos_drive:
        # ID Archivo
        idArchivo = f['id']
        # Nombre del archivo
        titArchivo = f['title']
        # Extensión
        if (f['mimeType'].startswith('application/vnd.google-apps.')):
            extArchivo = f['mimeType']
        else:
            extArchivo = f['fileExtension']
        # Correo del propietario
        propArchivo = f['owners'][0]['emailAddress']
        # Visibilidad
        if (f['shared']):
            visArchivo = 'Público'
        else:
            visArchivo = 'Privado'
        # Fecha de ultima modificacion
        modArchivo = f['modifiedDate']
        propiedadesArchivo = (idArchivo,titArchivo,extArchivo,propArchivo,visArchivo,modArchivo)
        propiedadesArchivoUpdate = (titArchivo,extArchivo,propArchivo,visArchivo,modArchivo,idArchivo)
        archivoExistente = (idArchivo,titArchivo)
        if (buscaDB(idArchivo)== None): #El archivo existe en la BD?
            #Si es true Hay que hacer insert
            archivosParaInsert.append(propiedadesArchivo)
            archivosEnDrive.append(archivoExistente)
        elif (modArchivo in buscaDB(idArchivo)): #si la fecha de mdificación es la misma, entonces no hay cambios
            pass
            archivosEnDrive.append(archivoExistente)
        else: #si hay, hago el update
            updateDB(propiedadesArchivoUpdate)
            archivosEnDrive.append(archivoExistente)
    #hacer el insert (si hay datos)
    if(archivosParaInsert != []):
        insertDB(archivosParaInsert)
    #delete
    borrarArchivos(archivosEnDrive)


#8 BUSCAR ARCHIVO EN LA BD
def buscaDB(x):
    miCursor.execute("SELECT FILE_ID, LAST_CHANGE_DATE FROM FILES WHERE FILE_ID = ?",[x])
    busquedaDB=miCursor.fetchone()
    return busquedaDB

#9 Insertar archivo en la BD
def insertDB(x):
    miCursor.executemany("INSERT INTO FILES VALUES(?,?,?,?,?,?)", x)

#10 Actualizar archivo en la BD
def updateDB(x):
    miCursor.execute("UPDATE FILES SET FILE_NAME=?, FILE_EXTENSION=?, OWNER=?, VISIBILITY=?, LAST_CHANGE_DATE=? WHERE FILE_ID=?", x)

#11 Borrar archivos inexistentes de la BD
def borrarArchivos(x):
    miCursor.execute("CREATE TABLE TABLA_PUENTE (ID INTEGER PRIMARY KEY AUTOINCREMENT, FILE_ID VARCHAR(50), FILE_NAME VARCHAR(50))")
    miCursor.executemany("INSERT INTO TABLA_PUENTE VALUES(NULL,?,?)", x)
    miCursor.execute("DELETE FROM FILES WHERE (NOT EXISTS (SELECT * FROM TABLA_PUENTE WHERE FILES.FILE_ID = TABLA_PUENTE.FILE_ID))")
    miCursor.execute("DROP TABLE TABLA_PUENTE")

# Ejecutar funciones
if __name__ == "__main__":
    buscaPub("mimeType != 'application/vnd.google-apps.folder' and trashed = false and 'me' in owners and visibility != 'limited'")
    recorreDrive("mimeType != 'application/vnd.google-apps.folder' and trashed = false and 'me' in owners")


# Cerrar la BD
conexionDB.commit()
conexionDB.close()
