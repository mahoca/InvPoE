# /usr/bin/env python3.3
# -*- coding: utf-8 -*-

__author__ = 'mahoca'

"""
:RESUMEN
:    Estoy rehaciendo el parser de nuevo una vez descubiertos los problemas delanterior codigo.
:    Ahora al leer el codigo fuente ya se queda con la linea de la url_foto. Solo queda desarrollar
:    la ultima fase para separar las propiedades del objeto. Me ayudare sabiendo que el objeto siempre
:    empieza con la linea de la url_foto.
:    Cuando haya separado el objeto con sus propiedades empezare a pensar en como guardarlo en una BD.
"""

import os, sys
import httplib2
import re
import pickle
from PyQt5 import QtCore, QtGui


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
Jewelry_list = []

nueva_lista = []    # lista de uso temporal

# declaro las variables de busqueda para encontrar las tablas en el codigo fuente
# uso re para definir el patron que voy a buscar

linea_inicio = re.compile('<table class="itemDataTable">')
linea_final = re.compile('</table>')


def abrir_web(documento):

    """
    : leemos el codigo fuente de la web usando la libreria http2lib2
    : esta libreria nos carga el codigo fuente de la web en una variable
    : de tipo bytes. Con la funcion bytes.decode obtenemos una variable 'archivo'
    : tipo string con todas las lineas del codigo fuente
    : Luego con el uso del modulo re eliminamos toda la basura y creamos una lista
    : con las lineas de codigo que tienen las tablas con la informacion que nos interesa.
    """

    instrucciones = []

    h = httplib2.Http('.cache')
    response, content = h.request(documento)

    # el valor status = 200 significa que la peticion se completo OK

    if response.status == 200:
        print('LECTURA CORRECTA')
    else:
        # aqui habra que poner algo que detecte posibles errores cuando status no sea 200

        print('ALGO FALLO')

    # decofico la variable content y la convierto en string
    # creo una lista con las lineas del archivo

    archivo = bytes.decode(content)
    lineas_archivo = re.split('\n', archivo)

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
            instrucciones.append(linea)

    return instrucciones


def guardar_archivo_bruto(documento, informacion):
    """
    :Guardo en un archivo de texto la informacion que extraigo con la funcion
    :abrir_web.
    :ESTA FUNCION NO ESTA SIENDO USADA DE MOMENTO
    """
    with open(documento, mode='w') as archivo:
        for i in informacion:
            archivo.write(i)

    return


def guardar_diccionario(documento, informacion):

    """
    :Guardo el diccionario usando pickle
    :ESTA FUNCION ESTA EN DESARROLLO DE MOMENTO.
    """
    fichero = open(documento,'wb')
    pickle.dump(informacion,fichero) # protocolo 0 = formato texto
    fichero.close()

    return


def nuevo_parser(por_linea):
    """
    :Una vez que obtengo las lineas que definen las tablas con la informacion
    :con esta funcion elimino todas las lineas que sobran quedandome solo con
    :las que definen las propiedades de cada objeto.
    :Primero busco la linea donde esta la url_foto, que es la que marca el inicio
    :de las propiedades de los objetos.
    :param por_linea:
    """
    Dcontrol = {}
    temporal_lista1 = [] # lista temporal para la primera limpieza
    temporal_lista2 = [] # lista temporal para la segunda limpieza
    patron1 = re.compile('data-large-image=(.+/>)', re.IGNORECASE)
    patron2 = re.compile('>.+?<', re.IGNORECASE)

    # defino 2 patrones:
    # patron1, para encontrar la linea de la url_foto, y que tambien me va a
    # servir para definir el inicio del objeto
    # patron2, para encontrar las propiedades del objeto

    # PRIMERA LIMPIEZA
    # ULTIMA HORA: parece que hay lineas que no se borran como es debido
    for linea in por_linea:

        objeto_cont = False
        cadena_limpi1 = patron1.findall(linea)
        if cadena_limpi1:
            objeto_cont = True
            temporal_lista1.append(cadena_limpi1)


        cadena_recur = patron2.findall(linea)
        if objeto_cont is False:
            temporal_lista1.append(cadena_recur)

    # SEGUNDA LIMPIEZA

    control_foto = False
    control_prop = False
    patron = re.compile('http://', re.IGNORECASE)
    for linea in temporal_lista1:
        cadena_info = str(linea)
        if len(linea) != 0: # ELIMINA cadena vacia
            cadena_limpi2 = patron.findall(cadena_info)
            if cadena_limpi2 or control_prop:
                control_foto = True
                temporal_lista2.append(linea)

            if control_foto:
                    control_prop = True

    #print(temporal_lista2)
    Dcontrol = crea_diccionario(temporal_lista2)

    return Dcontrol

def crea_diccionario(lista):
    """
    creo el diccionario de los objetos la clave sera el nombre, y el valor una lista con las propiedades
    de los objetos.
    """
    Dtemporal = {}
    objeto_temp = []
    valor = []
    patron = re.compile('http://', re.IGNORECASE)
    control = []
    cont = 0

    # PRIMERO CREO UNA LISTA DE CONTROL CON LA POSICION DE LAS LINEAS
    # EN LA QUE APARECE LA URL_FOTO

    for i in range(len(lista)):
        cadena_obj = str(lista[i])
        cadena_patron = patron.search(cadena_obj)
        if cadena_patron:
            control.append(i)
            #print(len(control))


    # USO LA LISTA ANTERIOR PARA DEFINIR QUE LINEAS PERTENECEN A CADA OBJETO Y ASI CREAR EL
    # DICCIONARIO.

    for a in range(0,len(control)):
        if a != len(control)-1:
            pos_fin = control[a + 1]
            intervalo = int(pos_fin - control[a])
        else:
            intervalo = int(len(lista) - control[a])

        #solo queda borrar los simbolos '<' y '>' de los elementos

        for b in range(0,intervalo):
            objeto_temp.append(lista[control[a]+b])

        clave = str(objeto_temp[1])

        objeto_temp.pop(1)
        for i in objeto_temp:
            valor.append(i)

        Dtemporal[clave] = valor

        objeto_temp = []
        valor = []

    #print("Hay ", len(Dtemporal), " objetos")
    return Dtemporal


def imprime_dic(documento):
    """
    :Funcion para imprimir el diccionario y comprobar se se creo bien.
    :ESTA FUNCION ESTA EN DESARROLLO DE MOMENTO.
    :Cuando todo este bien esta funcion no creo que se use.
    """
    fichero = open(documento, 'rb')
    diccionario = pickle.load(fichero)
    fichero.close()
    #print("ESTE DICCIONARIO TIENE : ", len(fichero), "OBJETOS")
    print(diccionario.keys())

    #for i in set(diccionario):
        #print(i, '*'*15)
        #for a in range(len(diccionario[i])):
            #print(diccionario[i][a])
        #print('*'*40)

    return

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



    Weapons_list = abrir_web(poeruta2)
    #print ("numero de lineas leidas ", len(Weapons_list))
    Dweapons = nuevo_parser(Weapons_list)
    guardar_diccionario(myruta2, Dweapons)
    imprime_dic(myruta2)

    #Currency_list = abrir_web(poeruta1)
    #print ("numero de lineas leidas ", len(Currency_list))
    #Dcurrency = nuevo_parser(Currency_list)
    #guardar_diccionario(myruta1, Dcurrency)
    #imprime_dic(myruta1)

    #Armour_list = abrir_web(poeruta3)
    #print ("numero de lineas leidas ", len(Armour_list))
    #Darmour = nuevo_parser(Armour_list)
    #guardar_diccionario(myruta3, Darmour)
    #imprime_dic(myruta3)

    #Jewelry_list = abrir_web(poeruta4)
    #print ("numero de lineas leidas ", len(Jewelry_list))
    #Djewelry = nuevo_parser(Jewelry_list)
    #guardar_diccionario(myruta4, Djewelry)
    #imprime_dic(myruta4)



    return

main()
app = QtGui.QGuiApplication(sys.argv)

widget = QtGui.QWindow()
widget.resize(300,300)
widget.setTitle('InvPoE')

widget.show()

sys.exit(app.exec_())