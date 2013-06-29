__author__ = 'm3d'

import os
import httplib2
import re

a = os.getcwd()

# declaro los diccionarios

Dcurrency = {}
Dweapon = {}
Darmour = {}
Djewelry = {}

#declaro las listas

Currency_list = []
Weapons_list = []
Armour_list = []
Jewelry_list =[]

nueva_lista = []    # lista de uso temporal

# declaro las variables de busqueda para encontrar las tablas en el codigo fuente
# uso re para definir el patron que voy a buscar

linea_inicio = re.compile('<table class="itemDataTable">')
linea_final = re.compile('</table>')



def abrir_web(documento):

    # leemos el codigo fuente de la web usando la libreria http2lib2
    # esta libreria nos carga el codigo fuente de la web en una variable
    # de tipo bytes. Con la funcion bytes.decode obtenemos una variable 'archivo'
    #  tipo string con todas las lineas del codigo fuente
    # Luego con el uso del modulo re eliminamos toda la basura y creamos una lista
    # con las lineas de codigo que tienen las tablas con la informacion que nos interesa.

    instrucciones = []

    h = httplib2.Http('.cache')
    response, content = h.request(documento)

    # el metodo status = 200 significa que la peticion se completo OK

    if response.status == 200:
        print('LECTURA CORRECTA')
    else:
        # aqui habra que poner algo que detecte posibles errores cuando status no sea 200

        print('ALGO FALLO')

    # decofico la variable content y la convierto en string
    # creo una lista con las lineas del archivo

    archivo = bytes.decode(content)
    lineas_archivo = re.split('\n',archivo)

    # Luego me quedo con lo que me interesa del mismo,
    # que es el contenido de la etiqueta <table....> ... </table>
    # ** hay archivos con varias tablas

    datos = False

    for linea in lineas_archivo:
        linea = linea.rstrip("\n")

        # uso re.search para averiguar si el patron de busqueda
        # aparece en las lineas

        if linea_inicio.search(linea) or linea_final.search(linea):
            datos = not datos

        if datos:
            patron = re.compile('>.+<', re.IGNORECASE)

            # si el patron esta en la linea la añado a la lista

            if patron.findall(linea):
               instrucciones.append(linea + '\n')

            # en el archivo currency la extructura de la linea de la url_foto es distinta
            # y no carga esa linea. RESOLVER.

    return instrucciones

def guardar_archivo_bruto(documento, informacion):
    # guardo el archivo en bruto con la informacion que sale de abrir_web

   with open(documento,mode='w') as archivo:
       for i in informacion:
           archivo.write(i)

   return

def guardar_diccionario(documento, informacion):

   # guardo el diccionarioo creado

   with open(documento,mode='w') as archivo:
       for i in informacion:
           archivo.write(i)
           for a in range(len(informacion[i])):
            archivo.write(informacion[i][a])

   return

def nuevo_parser(por_linea):

    # 1 - Se que en las lineas esta la informacion
    # 2 - Se que la informacion que me interesa esta definida '>informacion<'
    #   esto es asi por la forma de definirse las etiquetas HTML.
    # 3 - El punto 2 es cierto excepto para conseguir la URL_FOTO
    # 4 - La informacion viene definida con diferentes patrones
    #   >cadena< (>\w*<), >cadena cadena< (>\w*\s\w*<), >numero< (>\d*<),
    #   >numero.numero< (>\d*.\d*<), >numero cadena numero< (>\d*\s\w*\s\d*<), etc

    #   EJEMPLO: patron = re.compile('>\w*<|>\w*\s\w*<|>\d*.\d*<|>\d*\s\w*\s\d*<', re.IGNORECASE)

    #   este patron no me parece valido por 2 cosas
    # PRIMERO debo de conocer la estructura sintactica que busco, como la informacion no
    #   la creo yo me parece un impedimento insalvable
    # SEGUNDO el comando '|' opera como un OR lo cual hace que en el momento que detecta uno de
    #   los patrones ya no siga buscando en la linea ( al menos esa es la idea que me ha quedado )

    patron = re.compile('>.+<', re.IGNORECASE)

    # este otro patron mas general busca cualquier cosa que este entre los caracteres '>' y '<'
    # en principio puede ser valido, pero deja bastante basura en las lineas

    for linea in por_linea:
        cadena_patron = patron.findall(linea)
        #ocurrencia = patron.search(linea)
        if cadena_patron:
            #print(linea)
            print(cadena_patron)




    return


def crea_diccionario(lista):

    # creo el diccionario de los objetos currency

	# Esta funcion aun esta en FASE EXPERIMENTAL
	# la clave sera el nombre, y el valor una lista con [url, almacen, descripcion]

    vacio = []
    url_imagen = []
    vacio2 = []
    nombre = []
    almacen = []
    descripcion = []


    # el reto de esta funcion es buscar la forma de eliminar el 6 del range del for
    # y calcular el numero correcto dependiendo del archivo que se abra

    for i in range(0, len(lista), 6):

        vacio.append(lista[i])
        url_imagen.append(lista[i + 1])
        vacio2.append(lista[i + 2])
        nombre.append(lista[i + 3])
        almacen.append(lista[i + 4])
        descripcion.append(lista[i + 5])

    print(len(nombre))
    for i in range(len(nombre)):
        clave = nombre[i]
        valor = [url_imagen[i], almacen[i], descripcion[i]]
        Dcurrency[clave] = valor

    for i in sorted(set(Dcurrency)):
        print('*'*10, i)
        for a in range(len(Dcurrency[i])):
            print(Dcurrency[i][a])
        print('*'*40)

    print("Hay ", len(Dcurrency), " objetos tipo Currency")


def main():

    # inicializo variables

    myruta1 = a + "/DATA/currency.mah"
    poeruta1 = 'http://www.pathofexile.com/item-data/currency'

    myruta2 = a + "/DATA/weapons.mah"
    poeruta2 = 'http://www.pathofexile.com/item-data/weapon'

    myruta3 = a + "/DATA/armour.mah"
    poeruta3 = 'http://www.pathofexile.com/item-data/armour'

    myruta4 = a + "/DATA/jewelry.mah"
    poeruta4 = 'http://www.pathofexile.com/item-data/jewelry'

    Currency_list = abrir_web(poeruta1)
    print ("numero de lineas leidas ", len(Currency_list))
    guardar_archivo_bruto(myruta1, Currency_list)
    #nuevo_parser(Currency_list)

    # VOY A TRABAJAR CON EL ARCHIVO WEAPONS
    # CONTIENE VARIAS TABLAS, LOS OBJETOS POSEEN DIFERENTE NUMERO DE PROPIEDADES
    # DIFERENTE QUIERE DECIR QUE HAY OBJETOS QUE CARECEN DE CIERTAS PROPIEDADES
    # NO QUE SU VALOR SEA 0

    Weapons_list = abrir_web(poeruta2)
    print ("numero de lineas leidas ", len(Weapons_list))
    guardar_archivo_bruto(myruta2, Weapons_list)
    nuevo_parser(Weapons_list)

    Armour_list = abrir_web(poeruta3)
    print ("numero de lineas leidas ", len(Armour_list))
    guardar_archivo_bruto(myruta3, Armour_list)
    #nuevo_parser(Armour_list)

    Jewelry_list = abrir_web(poeruta4)
    print ("numero de lineas leidas ", len(Jewelry_list))
    guardar_archivo_bruto(myruta4, Jewelry_list)
    #nuevo_parser(Jewelry_list)

    # parser(instrucciones)
    # guardar_archivo_bruto(ruta, nueva_lista)
    # crea_diccionario(nueva_lista)
    # guardar_diccionario(ruta, Dcurrency)
	
main()

