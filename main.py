#-*- coding: utf8 -*-
import kivy
kivy.require('1.9.1')

from kivy.app import App
#from kivy.lang import Builder
from kivy.storage.jsonstore import JsonStore
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.properties import ObjectProperty, StringProperty, ListProperty
from kivy.adapters.listadapter import ListAdapter
from kivy.uix.listview import ListItemButton
from kivy.uix.boxlayout import BoxLayout
from os import rename
#~ from kivy.uix.pagelayout import PageLayout

#Builder.load_file('sc_buscar.kv')

#from kivy.config import Config
#Config.set('graphics', 'width', '400')
#Config.set('graphics', 'height', '840')
#Config.set('graphics', 'resizable', '0')
#Config.set('input', 'mouse', 'mouse,disable_multitouch')

from kivy.core.window import Window
Window.clearcolor = (0, 0, 0, 1)

FICH = '-PIM.csv'
ITEM = 0
MEMO = 1
CLAVES = 2
#ultimo = ""
#abierto = ""
#archivos = []
#jstore = JsonStore("pim_store.json")
panta_inicio = "sc_lista_archivos"

class Dialogo(BoxLayout):
    def __init__(self, mensaje=''):
        super(Dialogo, self).__init__()
        #self.ids.mensaje.text = mensaje
        
class BotonDeLista(ListItemButton):
    texto = ListProperty()

class ClaveItem(object):
    def __init__(self, text='', is_selected=False):
        self.text = text
        self.is_selected = is_selected
    def deselect(self):
        self.is_selected = False

class MyScreenManager(ScreenManager):
    #ultimo = ""
    abierto = ""
    cargado = False
    modificando = False     # alta o modificando
    claves_buscando = False # para saber quien listó las claves
    dic_items = {}          # {item: 'indice registro'}
    lista = []
    lista_claves = []
    listando_claves = False
    lista_claves_cargadas = False
    jstore = ""
    registros = [] # las lineas del fichero
    items = []
    memos = []
    claves = []  # lista de claves de cada registro [[cla1,cla2],[],...]
    #indice = []
    clave = []   # claves existentes
    #jstore = JsonStore("pim_store.json")
    #i_item = ObjectProperty()
    i_buscar_item = ObjectProperty()
    b_buscar_claves = ObjectProperty()
    #lis_panta = ObjectProperty()
    titulo_lista = StringProperty()
    titulo_fichero = StringProperty()
    panta = StringProperty()
    use_kivy_settings = False

    def __init__(self, **kwargs):
        super(MyScreenManager, self).__init__(**kwargs)
        self.current = 'sc_menu_principal'
        self.jstore = JsonStore("pim_store.json")
        try:
            ultimo = self.jstore.get("pim")['ultimo']
            #self.aviso(str(ultimo))
        except:
            #self.aviso(str('no hay ultimo'))
            return
        if not self.abrir_archivo(ultimo):
            self.titulo_fichero = 'No puedo leer ' + ultimo

    def abrir_archivo(self, fich):
        try:
            F = open(fich + FICH)
        except:
            self.aviso('No puedo abrir ' + fich)
            return False
        del self.registros[:]
        try:
            r = F.readline()
            while r:
                if len(r) > 2: self.registros.append(r[:-1])
                r = F.readline()
        except:
            self.aviso('No puedo leer ' + fich)
            return False
        self.abierto = fich
        self.titulo_fichero = fich
        return True

    def alta(self):
        if not self.cargado: self.carga_listas()
        self.ids.i_item_alta.text = ""
        self.ids.i_memo_alta.text = ""
        self.ids.i_claves_alta.text = ""
        self.modificando = False
        self.current = 'sc_alta'

    def alta_clave(self, popup, cla):
        #if not cla: return
        self.aviso(cla)
        #self.clave.append(cla)
        #self.clave.sort()
        #self.ids.i_claves_alta.text += ','+cla
        #popup.dismiss()
        #self.elige_claves('registro')

    def aviso(self, txt):
        the_content = Label(text = txt)
        the_content.color = (1,1,1,1)
        popup = Popup(title='PIM',
            content=the_content, size_hint_y=.25, title_align='center')
            #content = the_content, size_hint=(None, None), size=(350, 150))
        popup.open()
        
    def dialogo(self, txt='', tema=''):
        the_content = Dialogo(txt)
        the_content.color = (1,1,1,1)
        popup = Popup(title=txt,
            content=the_content, size_hint_y=.25, title_align='center', auto_dismiss = False)
        the_content.ids.b_cancelar.bind(on_release=popup.dismiss)
        if tema == 'clave':
            the_content.ids.b_aceptar.bind(on_release=self.alta_clave(popup, the_content.ids.i_dialog.text))
        popup.open()

    def boton_lista_izq(self, texto):
        if self.titulo_lista == 'Registros encontrados':
            self.current = 'sc_menu_principal'
        elif self.titulo_lista == 'Claves':
            self.current = 'sc_buscar'
        #if texto == 'Menu': self.current = 'sc_menu_principal'

    def boton_lista_cen(self):
        if self.titulo_lista == 'Registros encontrados':
            pass
        elif self.titulo_lista == 'Claves':
            self.dialogo('Introduzca nueva clave', 'clave')

    def boton_lista_der(self, texto):
        if self.titulo_lista == 'Registros encontrados':
            self.current = 'sc_buscar'
        elif self.titulo_lista == 'Claves':
            cla_selec = [c.text for c in self.lista_claves if c.is_selected]
            if self.claves_buscando:
                self.ids.b_buscar_claves.text = ",".join(cla_selec)
                self.current = 'sc_buscar'
            else:
                self.ids.i_claves_alta.text = ",".join(cla_selec)
                self.current = 'sc_alta'

    def elige_claves(self, origen):
        if not self.listando_claves:
            self.ids.lis_panta.adapter = ListAdapter(data=[], cls=BotonDeLista, args_converter=self.args_converter_claves, selection_mode='multiple', propagate_selection_to_data=True)
            self.listando_claves = True
            #del self.lista[:]
            self.titulo_lista = 'Claves'
            self.ids.b_lista_izq.text = 'Cancelar'
            self.ids.b_lista_cen.text = 'Nueva'
            self.ids.b_lista_der.text = 'Aceptar'
            if not self.lista_claves_cargadas:
                del self.lista_claves[:]
                for c in self.clave: self.lista_claves.append(ClaveItem(text=c))
                self.lista_claves_cargadas = True
        self.marca_claves(origen)
        self.rellena(True)
        #self.titulo_lista = 'Claves'
        self.current = 'sc_lista'

    def grabar_nuevo(self):
        reg = self.ids.i_item_alta.text + \
              self.ids.i_memo_alta.text + \
              self.ids.i_claves_alta.text
        if reg == "":
            self.aviso('Registro vacío')
            return
        if reg.count(';'):
            self.aviso('No se puede usar ;')
            return
        try: F = open(self.titulo_fichero + '-NEW.csv', 'w')
        except:
            self.aviso('No puedo crear fichero')
            return
        reg = self.ids.i_item_alta.text + ';' + \
              self.ids.i_memo_alta.text.replace('\n','^') + ';' + \
              self.ids.i_claves_alta.text.replace(',',';')
        self.registros.append(reg)
        self.items.append(self.ids.i_item_alta.text)
        self.memos.append(self.ids.i_memo_alta.text)
        self.claves.append(self.ids.i_claves_alta.text.split(','))
        try:
            for r in self.registros: F.write(r + '\n')
        except:
            self.aviso('No puedo escribir fichero')
            return
        F.close()
        rename(self.titulo_fichero+'-NEW.csv', self.titulo_fichero+FICH)
        self.current = 'sc_menu_principal'
        
       #graba registro (regraba todos+nuevo)
            #graba con otro nombre
            #cambia el nombre sobreescribiendo

    def limpia_i_buscar_cadena(self):
        self.i_buscar_cadena.text = ""
        #self.aviso(jstore.get("pim")['ultimo'])
        #print self.store.get("pim")['ultimo']

    def limpia_b_buscar_claves(self):
        if self.b_buscar_claves.text != "":
            self.b_buscar_claves.text = ""
            for c in self.lista_claves: c.deselect()
            self.listando_claves = False

    def limpia_busqueda(self):
        self.limpia_i_buscar_cadena()
        self.limpia_b_buscar_claves()

    def lista_elegido(self, texto):
        if self.titulo_lista == 'Registros encontrados':
            i = self.dic_items[texto]
            self.ids.i_item.text = texto
            self.ids.i_memo.text = self.memos[i].replace('^','\n')
            self.ids.i_claves.text = ','.join(self.claves[i])
            self.ids.i_item.readonly = True
            self.ids.i_memo.readonly = True
            self.ids.i_claves.readonly = True
            self.current = 'sc_registro'
        elif self.titulo_lista == 'Claves':
            pass
        else:
            if self.abrir_archivo(texto):
            #self.store.put("pim", ultimo=fich)
                self.jstore.put("pim", ultimo=texto)
                self.current = 'sc_menu_principal'

    def marca_claves(self, origen):
        if origen == 'buscar':
            self.claves_buscando = True
            seleccionadas = self.ids.b_buscar_claves.text.split(',')
        else:
            self.claves_buscando = False
            seleccionadas = self.ids.i_claves_alta.text.split(',')
        for cl in self.lista_claves:
            cl.is_selected = True if cl.text in seleccionadas else False

#            for c in self.ids.b_buscar_claves.text.split(','):
#                for cl in self.lista_claves:
#                    cl.is_selected = True if cl.text == c else False
#        else:
#            self.claves_buscando = False
#            for c in self.ids.i_claves_alta.text.split(','):
#                for cl in self.lista_claves:
#                    cl.is_selected = True if cl.text == c else False

    def limpia(self, widg):
        self.widg.text = ""

    def panta_buscar(self):
        if self.abierto:
            if not self.cargado: self.carga_listas()
            self.ids.titulo_sc_buscar.text = 'Buscando en ' + self.titulo_fichero
            self.current = 'sc_buscar'

    def busca(self):
        #del self.indice[:]
        del self.lista[:]
        self.dic_items = {}
        Y = True
        if Y:
            for i in range(len(self.items)):
                if self.cadena_en_texto(i) and self.clave_en_claves(i):
                    self.dic_items[self.items[i]] = i
        else:
            for i in range(len(self.items)):
                if self.cadena_en_texto(i) or self.clave_en_claves(i):
                    self.dic_items[self.items[i]] = i
        self.lista = self.dic_items.keys()
        self.lista.sort()
        self.ids.lis_panta.adapter = ListAdapter(data=[], cls=BotonDeLista, args_converter=self.args_converter, selection_mode='single')
        self.titulo_lista = 'Registros encontrados'
        self.ids.b_lista_izq.text = 'Menu'
        self.ids.b_lista_der.text = 'Buscar'
        self.listando_claves = False
        self.rellena()
        self.current = 'sc_lista'

    def cadena_en_texto(self, i):
        if self.i_buscar_cadena.text:
            ambos = False
            if ambos:
                if not (self.items[i].count(self.i_buscar_cadena.text) or self.memos[i].count(self.i_buscar_cadena.text)):
                    return False
            else:
                if not self.items[i].count(self.i_buscar_cadena.text):
                    return False
        return True

    def clave_en_claves(self, i):
        #if self.b_buscar_claves.text != '<claves>':
        if self.b_buscar_claves.text != '':
            b_claves = self.b_buscar_claves.text.split(',')
            Y_claves = True
            if Y_claves:
                for c in b_claves:
                    if c not in self.claves[i]: return False
                return True
            else:
                for c in b_claves:
                    if c in self.claves[i]: return True
                return False
        return True

    def carga_listas(self):
        del self.items[:]
        del self.memos[:]
        del self.claves[:]
        del self.clave[:]
        #self.items = [i.split(';')[0] for i in self.registros]
        #self.memos = [i.split(';')[1] for i in self.registros]
        for r in self.registros:
            campos = r.split(';')
            self.items.append(campos[0])
            self.memos.append(campos[1])
            self.claves.append(campos[2:])
            for c in campos[2:]:
                if c not in self.clave: self.clave.append(c)
        #    cla = "".(r[-1])
        #self.claves = [i.split(';')[2:] for i in self.registros]
        self.clave.sort()
        self.lista_claves_cargadas = False
        #self.aviso(str(self.clave))
        self.cargado = True

    def modificar(self):
        self.ids.i_item_alta.text = self.ids.i_item.text
        self.ids.i_memo_alta.text = self.ids.i_memo.text
        self.ids.i_claves_alta.text = self.ids.i_claves.text
        self.modificando = True
        self.current = 'sc_alta'

    def preg_mod_nue(self):
        self.aviso('preg')

    def rellena(self, claves=False):
        #~ self.lis_panta.item_strings = ['wefrewr', 'klsjf lkj f']
        #~ self.lis_panta.adapter.data.clear()
        #self.titulo_lista = 'Ficheros disponibles'
        del self.ids.lis_panta.adapter.data[:]
        #self.lis_panta.adapter.data.extend(['wefrewr', 'klsjf lkj f', 'kk'])
        if claves:
            self.ids.lis_panta.adapter.data.extend(self.lista_claves)
        else:
            self.ids.lis_panta.adapter.data.extend(self.lista)
        self.ids.lis_panta._trigger_reset_populate()

    def args_converter(self, index, data_item):
        texto = data_item
        return {'texto': texto}

    def args_converter_claves(self, index, data_item):
        texto = data_item.text
        return {'texto': texto}

def leer_archivos():
    #global archivos
    archivos = ['fich1', 'c 2', 'archivo 3']

def abre_fichero(fich):
    F = open(abierto + '-pim.txt')
    return True

def lee_ultimo():
    global ultimo
    try:
        ultimo = jstore.get("pim")['ultimo']
    except:
        ultimo = ""

class PimApp(App):
    #title = 'PIM'
    #lee_ultimo()
    #if not ultimo(): leer_archivos()
    #else:
    #    if not abre_fichero(): abierto = ""
    def on_pause(self):
        return True

    def build(self):
        self.title = 'PpppIM'
        #self.icon = 'icono.png'
        return MyScreenManager()

if __name__=="__main__":
    #from kivy.utils import platform
    #if platform == 'linux':
    PimApp().run()

#CORREGIR
#

#PLAN
#nueva clave
    #buscar on_enter
    #que no pueda pulsarse fuera, a la fuerza un boton
    #reducir tamano
#pasar apertura de fichero a on_start

#IDEAS
#permitir .paste() en los textinput
#utilidades
    #comprueba si hay algún fichero pendiente de renombrar
        #si no hay origen, recuperarlo
        #si hay origen, comparar longitud
    #borrar fichero
    #copiar fichero con otro nombre
    #renombrar fichero
    #buscar líneas con caracteres raros y sustituirlos
        #listarlas
        #preguntar si sustituirlos