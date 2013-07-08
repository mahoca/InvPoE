# /usr/bin/env python3.3
# -*- coding: utf-8 -*-

__author__ = 'mahoca'

"""
:RESUMEN
:    Funcion parser completada, parece que los objetos se crean bien.
:    Grabacion y lectura del diccionario usando pickle: funcion basica implementada
:    Probando Pyqt5 para crear forms y visualizar la informacion.
:    Queda mucho que estudiar asi que va a llevar tiempo.
:    - Crear UI para visualizar los objetos.
:    - Estudiar pickle y shelve para implementar mejores rutinas de lectura y grabacion
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
    : lee el codigo fuente de la web usando la libreria http2lib2
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
    :Guardo en un archivo de texto la informacion que extraigo con la funcion abrir_web.
    :ESTA FUNCION NO ESTA SIENDO USADA
    """
    with open(documento, mode='w') as archivo:
        for i in informacion:
            archivo.write(i)

    return


def guardar_diccionario(documento, informacion):

    """
    :Guardo el diccionario usando pickle
    :parametros
    :documento es la ruta del archivo a guardar
    :informacion es el diccionario que voy a guardar
    """
    fichero = open(documento,'wb')
    pickle.dump(informacion,fichero)
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

    # defino 3 patrones:
    # patron1, para encontrar la linea de la url_foto, y que tambien me va a
    # servir para definir el inicio del objeto
    # patron2, para encontrar las propiedades del objeto
    # patron3, añadido para eliminar las lineas del menu de las tablas

    # PRIMERA LIMPIEZA

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
    patron3 = re.compile('href=', re.IGNORECASE)

    for linea in temporal_lista1:

        cadena_info = str(linea)
        cadena_menu = patron3.findall(cadena_info)
        if (len(linea) != 0) and not cadena_menu: # ELIMINA cadena vacia y lineas de menu
            cadena_limpi2 = patron.findall(cadena_info)
            if cadena_limpi2 or control_prop:
                control_foto = True
                temporal_lista2.append(linea)

            if control_foto:
                    control_prop = True

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

        for b in range(0,intervalo):
            objeto_temp.append(lista[control[a]+b])

        clave_temp = str(objeto_temp[1])
        clave = clave_temp[3:-3] # elimina los simbolos de la propiedad nombre
        objeto_temp.pop(1) # borro la propiedad nombre de la lista de propiedades del objeto

        for i in objeto_temp:
            valor_temp = str(i)
            temp1 = valor_temp.replace('<','')
            temp2 = temp1.replace('>','')
            temp3 = temp2.replace('/','')

            valor.append(temp3)

        Dtemporal[clave] = valor

        objeto_temp = []
        valor = []

    return Dtemporal


def imprime_dic(documento):
    """
    :Funcion para imprimir el diccionario y comprobar se creo bien.
    :parametros
    :documento es la ruta del archivo que abro
    :debera devolver la variable diccionario <tipo> diccionario
    """
    fichero = open(documento, 'rb')
    diccionario = pickle.load(fichero)
    fichero.close()

    print("ESTE DICCIONARIO TIENE : ", len(diccionario), "OBJETOS")

    for i in set(diccionario):
        print(i, '*'*15)
        print(diccionario[i])
        print('*'*40)

    return

def main():

    # inicializo variables y diccionarios

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

    Currency_list = abrir_web(poeruta1)
    #print ("numero de lineas leidas ", len(Currency_list))
    Dcurrency = nuevo_parser(Currency_list)
    guardar_diccionario(myruta1, Dcurrency)
    imprime_dic(myruta1)

    Armour_list = abrir_web(poeruta3)
    #print ("numero de lineas leidas ", len(Armour_list))
    Darmour = nuevo_parser(Armour_list)
    guardar_diccionario(myruta3, Darmour)
    imprime_dic(myruta3)

    Jewelry_list = abrir_web(poeruta4)
    #print ("numero de lineas leidas ", len(Jewelry_list))
    Djewelry = nuevo_parser(Jewelry_list)
    guardar_diccionario(myruta4, Djewelry)
    imprime_dic(myruta4)



    return

main()
app = QtGui.QGuiApplication(sys.argv)

widget = QtGui.QWindow()
widget.resize(300,300)
widget.setTitle('InvPoE')

widget.show()

sys.exit(app.exec_())