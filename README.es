PyFCP es una libreria de Python para Freenet 0.7 que tambien incluye una serie
de aplicaciones de consola para Freenet.

Esta version de PyFCP tiene:

    - Las siguientes aplicaciones de consola para Freenet:

	- freesitemgr: una simple y flexible herramienta para administrar freesites
	- fcpnames: herramienta para manejar la capa experimental de registro de
	            nombres, algo asi como un DNS sobre Freenet.
	- fproxyproxy: un proxy http experimental que corre sobre fproxy y traduce
		       los nombres de los sitios de manera transparente a un formato
		       legible
	- fcpget: comando para descargar un archivo de freenet
	- fcpput: comando para insertar un archivo en freenet
	- fcpgenkey: genera un par de llaves (key)
	- fcpinvertkey: genera un par de llaves SSK/USK
	- fcpredirect: inserta una redireccion de una 'key' a otra 'key' (llave).

    - Un servidor XML-RPC para accesso a freenet que puede correr por su cuenta o
      integrarse facilmente a un sitio web.

    - Paquete de python 'fcp' con las clases para accesso a freenet.

Una buena documentacion de la API (en ingles) puede obtenerse corriendo:

    $ epydoc -n "PyFCP API manual" -o html fcp

'freesitemgr' es una herramienta de consola para la insercion de freesites,
guarda configuraciones y estado de los sitios en un solo archivo de configuracion
(~/.freesitemgr, a menos que se especifique otro). Ejecutando 'freesitemgr -h' se
puede obtener una lista de opciones (en ingles) de 'freesitemgr'.

Correcciones sobre la traduccion de este documento al castellano: cacopatane@freenetproject.org
