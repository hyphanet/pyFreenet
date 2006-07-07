Requerimientos del sistema:

     - Python2.3 or superior
     - Acceso a FCP de un nodo de freenet (indistinto si esta en otra maquina o en
       (la que corremos pyFreenet).

    (Opcional)
     - Modulo 'SSLCrypto' (fuentes incluidas)
     - Librerias y cabeceras OpenSSL

Instalacion:

   1) Asegurarse de que las librerias libopenssl y libopenssl-dev esten instaladas.

    Estos paquetes incluyen las librerias y cabeceras para OpenSSL que son dependencias
    del paquete de python 'SSLCrypto' a su vez, dependencia opcional de pyFreenet.

    No hace falta tener instaladas las libopenssl[-dev] y SSLCrypto por que pyFreenet
    puede correr sin ellas, pero Freedisk va a correr sin encriptacion.

    Si no hay una necesidad de correr freenetfs (Freedisk) con encriptacion o no se va
    a hacer uso de freenetfs (Freedisk), puede saltear al paso 4 de la instalacion.

   2) Comprobar si SSLCrypto esta instalado

      Para probar si funciona SSLCrypto podemos ejecutar la siguien linea:

      $ python -c "import SSLCrypto"

      Si la ejecucion del comando no regresa nada, quiere decir que esta todo
      en orden. Por otro lado, si dice algo como 'ImportError: ...' necesitamos
      instalar bien SSLCrypto.

   3) Instalar SSLCrypto si es necesario

      (i)   Ir al directorio 'dependencies'
      (ii)  Descomprimir ambos paquetes 'Pyrex...' y 'SSLCrypto...'
      (iii) Entrar al directorio 'Pyrex-...' y, como root, ejecutar lo siguiente:

               python setup.py install

      (iv) Entrar al directorio 'SSLCrypto-...' y, como root, ejecutar lo siguiente:

               python setup.py install

   4) Para instalar pyFreenet y todas sus aplicaciones nos pararemos en el directorio
      donde descomprimimos el paquete y, como root, ejecutaremos lo siguiente:

	       python setup.py install

      Listo!

Correcciones sobre la traduccion: cacopatane@freenetproject.org
