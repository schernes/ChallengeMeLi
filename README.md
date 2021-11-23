# ChallengeMeLi

## Prerrequisitos:

Importar los siguientes archivos en un IDE (en mi caso he utilizado Visual Studio Code):

      •	ChallengeMeLi.py
      •	Google.py
      •	client_secrets.json
      •	quickstart.py
      •	settings.yaml

Previo realizar la ejecución, es necesario instalar las siguientes dependencias, ingresando las mismas por consola:

      •	pip install cryptography
      •	pip install PyDrive2
      •	pip install setuptools-rust
      •	pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib


Para ver una demostración de la ejecución del Challenge, puede ingresar a este [Link](https://youtu.be/iGUSD1asboM) para ver el vide explicativo, en el cual se recorre paso a paso el código.

## Ejecutando el Código:

Una vez instaladas las dependencias, se debe ejecutar el archivo "**quickstart.py**". Con esta ejecución se abrirá una ventana emergente para validar las credenciales para acceder a Google Drive. Para ejecutar esta prueba, he creado una cuenta de Google. A continuación se detallan los datos de acceso:

   •	Usuario: **Challenge.MeLi.JS@gmail.com**
   
   •	Contraseña: **Challenge2021**

Luego del ingreso, las credenciales quedarán guardadas en el archivo **credentials_module.json**.


Es momento de poner a prueba el Challenge. Vamos a ejecutar el archivo "**ChallengeMeLi.py**". Allí se ejecutará lo requerido para el Challenge (el enunciado de este puede ser consultado en el archivo "**Challenge MeLi - Docs en Drive Públicos.pdf**"). A continuación, se detallan las acciones del código:

- En primera instancia se realizarán todos los Imports necesarios para la ejecución del programa.

- Luego, la primera acción realizada creará la base de datos (bajo el nombre **ChallengeMeLi.db3**) y se conectará a la misma. La misma función (connect) realiza también la conexión, por lo que, si encuentra que la base de datos ya existe, se limitará únicamente a conectarse a ella.

 - El próximo paso será la creación de las 2 tablas en la base de datos (la tabla **FILES** para inventariar los archivos y la tabla **PUBLIC_FILES_HISTORY** para el histórico de aquellos archivos cuya visibilidad sea modificada de pública a privada).

En caso de verificar que no es posible crear las tablas porque las mismas ya existan, se aplicará la condición de excepción y continuará la ejecución del programa.

- Luego en el código se definen todas las funciones requeridas para el programa, las cuales se ejecutarán según se cumplan determinadas condiciones.

- La primera función que se ejecutará será la función **buscaPub**. La misma la utilizaremos para buscar todos los archivos de la unidad de Drive cuya privacidad sea pública, a fin de modificar esta propiedad. Para ello se le indican una serie de parámetros de búsqueda para los archivos en el drive:

      •	Que no sean carpetas.
      •	Que no se encuentren en la papelera de reciclaje.
      •	Que el ejecutante sea el dueño de los archivos (esto excluye 
      de la búsqueda todos los archivos que no se encuentren en mi unidad de Drive).
      •	Que la visibilidad sea Pública.

Esta función validará las credenciales que definimos anteriormente para ingresar a Google Drive y realizará allí un recorrido de los archivos listando aquellos que cumplan con las condiciones dadas y modificando su privacidad (a través de la función **eliminarPermisos**). 

Luego se añadirá un registro en la tabla **PUBLIC_FILES_HISTORY** a través de la función insertHistorico por cada uno de los archivos listados. 

Por último, y en caso de haber encontrado al menos un archivo que cumpla con estas condiciones realizará el envío de un correo electrónico notificando al usuario los archivos que han sido modificados, desde la función **sendMail**. En caso de haberse cumplido esta condición, será necesario autorizar el uso de Gmail por parte de la aplicación. Luego de ello se creará el archivo **token_gmail_v1.pickle**, el cual almacenará las credenciales para futuras ejecuciones.

- En segunda instancia se ejecutará la función **recorreDrive**, la cual de forma similar a la anterior, recorrerá todos los archivos de Google Drive que cumplan con una serie de condiciones (esta segunda ejecución se debe a que, en la anterior se pudieron ver modificados algunos archivos y ahora será necesario actualizar la base de datos con los nuevos valores de cada archivo modificado):

      •	Que no sean carpetas.    
      •	Que no se encuentren en la papelera de reciclaje.   
      •	Que el ejecutante sea el dueño de los archivos (esto excluye 
      de la búsqueda todos los archivos que no se encuentren en mi unidad de Drive).
                        
Esta función tomará las propiedades relevantes de cada archivo y verificará si el mismo existe o no en la base de datos (desde la función **buscaDB**). En caso de no existir, almacenará su información en una lista que luego utilizará para hacer un insert en la tabla **FILES** (desde la función **insertDB**) al final del recorrido de todos los archivos. En caso de existir, valida si el mismo sufrió modificaciones (comparando la fecha de modificación) para lo cual realizará un update del archivo en la tabla **FILES** de la base de datos, desde la función **updateDB**. Finalmente, y si bien no se encontraba especificado en el requerimiento, se entiende que todo archivo que no se encuentre en el Drive pero sí en la base de datos, deberá eliminarse su registro de la tabla Files. Para ello se define la función **borrarArchivosDB**. Para ello se crea una **TABLA_PUENTE** que listará todos los archivos presentes en el Drive del usuario. Se eliminarán todos los archivos de la tabla **FILES** que no se encuentren en la **TABLA_PUENTE**. Luego esta última se eliminará de la base de datos.
      
- Realizadas todas las acciones, se procede a cerrar la conexión con la base de datos, dando fin a la ejecución del programa.
      
Si se desean eliminar las credenciales guardadas en esta ejecución, deberá eliminar los archivos creados **credentials_module.json** y **token_gmail_v1.pickle**. Asimismo, desde la cuenta de Google desde la cual se accedió, deberá eliminar el acceso de la aplicación **Challenge_MeLi_JS** (desde las opciones de Seguridad **-->** Aplicaciones de terceros con acceso a la cuenta, o desde la URL [https://myaccount.google.com/permissions?continue=https%3A%2F%2Fmyaccount.google.com%2Fsecurity]).
      
El repositorio de archivos de Google Drive de la cuenta ejemplo cuenta con algunos archivos que cumplen con condiciones que permiten la ejecución de las funciones creadas. Existen archivos con mismo nombre pero diferente ID, archivos dentro de carpetas, archivos compartidos por otros usuarios a fin de poder analizar su correcto funcionamiento. Para otras validaciones se recomienda realizar ejecuciones, luego realizar modificaciones de privacidad o insertar nuevos archivos. Se deja a disposición la cuenta de ejemplo para este fin. 
