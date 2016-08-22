#-*- coding: utf8 -*-
import kivy
kivy.require('1.9.1')
#import platform
from kivy.utils import platform
#if platform == 'android': import android
#from kivy.utils import platform
from kivy.app import App
#from kivy.lang import Builder
from kivy.storage.jsonstore import JsonStore
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.properties import ObjectProperty, NumericProperty, StringProperty, ListProperty
from kivy.adapters.listadapter import ListAdapter
from kivy.uix.listview import ListItemButton, ListItemLabel
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from os import rename, listdir, getcwd, remove

#~ from kivy.uix.pagelayout import PageLayout

#Builder.load_file('sc_buscar.kv')

#from kivy.config import Config
#Config.set('graphics', 'width', '400')
#Config.set('graphics', 'height', '840')
#Config.set('graphics', 'resizable', '0')
#Config.set('input', 'mouse', 'mouse,disable_multitouch')

from kivy.core.window import Window
Window.clearcolor = (0, 0, 0, 1)
#Window.softinput_mode = 'resize'

FICH = '-PIM.csv'
TEMP = '-TMP.csv'
ITEM = 0
MEMO = 1
CLAVES = 2

#ultimo = ""
#abierto = ""
#archivos = []
#jstore = JsonStore("pim_store.json")
#panta_inicio = "sc_lista_archivos"

class Dialogo(BoxLayout):
    def __init__(self, mensaje=''):
        super(Dialogo, self).__init__()

class Confirmacion(BoxLayout):
    def __init__(self, mensaje=''):
        super(Confirmacion, self).__init__()
        self.ids.l_conf.text = mensaje

class BotonDeLista(ListItemButton):
    pass
    #~ texto = StringProperty()

class LabelDeLista(ListItemLabel, Button):
    pass

class ClaveItem(object):
    def __init__(self, text='', is_selected=False):
        self.text = text
        self.is_selected = is_selected
    def deselect(self):
        self.is_selected = False

class MyScreen(Screen):
    def __init__(self, **kwargs):
        self.register_event_type('on_back_pressed')
        self.register_event_type('on_menu_pressed')
        super(MyScreen, self).__init__(**kwargs)
    def on_back_pressed(self, *args):
        #mapp.root.aviso(self.name)
        mapp.root.current = 'sc_menu_principal'
    def on_menu_pressed(self, *args):
        pass

class MyScreenManager(ScreenManager):
    #ultimo = ""
    directorio = ''
    abierto = ""
    cargado = False
    modificando = False     # alta o modificando
    reg = 0
    claves_buscando = False # para saber quien listó las claves
    dic_items = {}          # {item: 'indice registro'}
    lista = []
    lista_claves = []
    listando_claves = False
    lista_claves_cargadas = False
    claves_seleccionadas = []
    eligiendo = False
    clave_nueva = False
    clave_renombrar = ""
    #pulsacion = False
    jstore = ""
    registros = [] # las lineas del fichero
    items = []
    memos = []
    claves = []  # lista de claves de cada registro [[cla1,cla2],[],...]
    #indice = []
    clave = []   # claves existentes
    num_lineas = StringProperty()
    #jstore = JsonStore("pim_store.json")
    #i_item = ObjectProperty()
    i_buscar_item = ObjectProperty()
    b_buscar_claves = ObjectProperty()
    #lis_panta = ObjectProperty()
    titulo_lista = StringProperty()
    titulo_fichero = StringProperty()
    panta = StringProperty()

    def __init__(self, **kwargs):
        super(MyScreenManager, self).__init__(**kwargs)
        self.current = 'sc_menu_principal'
        if platform == 'android': android.hide_keyboard()
        self.jstore = JsonStore("pim_store.json")
        try:
            ultimo = self.jstore.get("pim")['ultimo']
            self.directorio = self.jstore.get("pim")['directorio']
        except:
            return
        if not self.abrir_archivo(ultimo):
            self.titulo_fichero = 'No puedo leer ' + ultimo

    def abrir_archivo(self, fich):
        try:
            F = open(self.directorio + fich + FICH)
        except:
            #self.aviso('No puedo abrir ' + fich)
            return False
        del self.registros[:]
        num_lineas = 0
        try:
            r = F.readline()
            while r:
                if len(r) > 2:
                    self.registros.append(r[:-1].decode('utf-8'))
                    #self.registros.append(r[:-1])
                    num_lineas += 1
                r = F.readline()
        except:
            self.aviso('No puedo leer ' + fich + ': ' + str(sys.exc_info()[0]))
            return False
        self.abierto = fich
        self.titulo_fichero = fich
        self.num_lineas = str(num_lineas) if num_lineas else '0'
        self.cargado = False
        return True

    def abrir_otro(self):
        #self.lista = [f[:-8] for f in listdir(getcwd()) if f[-8:]=='-PIM.csv']
        self.lista = [f[:-8] for f in listdir(self.directorio) if f[-8:]=='-PIM.csv']
        self.lista.sort()
        self.ids.lis_panta.adapter = ListAdapter(data=[], cls=BotonDeLista, args_converter=self.args_converter, selection_mode='single')
        self.listando_claves = False
        self.rellena("ficheros")
        self.titulo_lista = 'Elegir archivo'
        self.ids.b_lista_izq.text = 'Menu'
        self.ids.b_lista_cen.text = ''
        self.ids.b_lista_der.text = ''
        self.ids.b_lista_over.text = 'Cancelar'
        self.current = 'sc_lista'

    def alta(self):
        if not self.cargado: self.carga_listas()
        self.ids.i_item_alta.text = ""
        self.ids.i_memo_alta.text = ""
        self.ids.i_claves_alta.text = ""
        self.modificando = False
        self.ids.i_item_alta.focus = True
        self.current = 'sc_alta'

    #def alta_clave(self, popup, cla):
        #if not cla: return
        #self.aviso(cla)
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

    def confirmacion(self, txt="", tema=""):
        def elim_1_reg(self):
            popup.dismiss()
            mapp.root.eliminar_registros(confirmado=True, modo='uno')
        def elim_n_reg(self):
            popup.dismiss()
            mapp.root.eliminar_registros(confirmado=True, modo='varios')
        cuerpo = Confirmacion(txt)
        cuerpo.color = (1,0,0,1)
        popup = Popup(title='CONFIRMACION',
            content=cuerpo, size_hint_y=.25, title_align='center',
            title_color=[1,0,0,1], auto_dismiss=False)
        cuerpo.ids.b_cancelar.bind(on_release=popup.dismiss)
        if tema == 'elim_un_reg':
            cuerpo.ids.b_aceptar.bind(on_release=elim_1_reg)
        if tema == 'elim_n_regs':
            cuerpo.ids.b_aceptar.bind(on_release=elim_n_reg)
        popup.open()

    def dialogo(self, txt='', tema=''):
        def alta_clave(self):
            if not the_content.ids.i_dialog.text: return
            mapp.root.clave.append(the_content.ids.i_dialog.text)
            mapp.root.clave.sort()
            mapp.root.lista_claves.append(ClaveItem(text=the_content.ids.i_dialog.text, is_selected=True))
            mapp.root.claves_seleccionadas.append(the_content.ids.i_dialog.text)
            if mapp.root.ids.i_claves_alta.text:
                mapp.root.ids.i_claves_alta.text += ','+the_content.ids.i_dialog.text
            else:
                mapp.root.ids.i_claves_alta.text = the_content.ids.i_dialog.text
            popup.dismiss()
            mapp.root.clave_nueva = True
            mapp.root.elige_claves('registro')
        def nuevo_fichero(self):
            popup.dismiss()
            mapp.root.fichero_nuevo(the_content.ids.i_dialog.text)
        def exportar_fichero(self):
            popup.dismiss()
            mapp.root.exportar(the_content.ids.i_dialog.text)
        def renombre_clave(self):
            popup.dismiss()
            mapp.root.clave_nuevo_nombre(the_content.ids.i_dialog.text)
        the_content = Dialogo(txt)
        the_content.color = (1,1,1,1)
        popup = Popup(title=txt,
            content=the_content, size_hint_y=.25, title_align='center', auto_dismiss=False)
        the_content.ids.b_cancelar.bind(on_release=popup.dismiss)
        if tema == 'clave':
            #~ the_content.ids.b_aceptar.bind(on_release=self.alta_clave(popup, the_content.ids.i_dialog.text))
            the_content.ids.b_aceptar.bind(on_release=alta_clave)
        elif tema == 'fichero_nuevo':
            the_content.ids.b_aceptar.bind(on_release=nuevo_fichero)
        elif tema == 'renombrar_clave':
            the_content.ids.b_aceptar.bind(on_release=renombre_clave)
        elif tema == 'fichero_exportar':
            the_content.ids.b_aceptar.bind(on_release=exportar_fichero)
        popup.open()

    def boton_lista_izq(self, texto):
        if self.titulo_lista == 'Claves':
            self.eligiendo = False
            self.current = 'sc_buscar'
        else:
            self.current = 'sc_menu_principal'
        #if texto == 'Menu': self.current = 'sc_menu_principal'

    def boton_lista_cen(self):
        if self.titulo_lista == 'Registros encontrados':
            self.exportar()
        elif self.titulo_lista == 'Claves':
            self.eligiendo = False
            self.dialogo('Introduzca nueva clave', 'clave')

    def boton_lista_der(self, texto):
        #~ self.ids.lis_panta._trigger_reset_populate()
        if self.titulo_lista == 'Registros encontrados':
            self.current = 'sc_buscar'
        elif self.titulo_lista == 'Claves':
            self.eligiendo = False
            #~ cla_selec = [c.text for c in self.ids.lis_panta.adapter.data if c.is_selected]
            self.claves_seleccionadas.sort()
            if self.claves_buscando:
                self.ids.b_buscar_claves.text = ",".join(self.claves_seleccionadas)
                self.current = 'sc_buscar'
            else:
                self.ids.i_claves_alta.text = ",".join(self.claves_seleccionadas)
                self.current = 'sc_alta'

    def boton_lista_over(self, texto):
        if texto == 'Eliminar':
            self.eliminar_registros(confirmado=False, modo='varios')
        elif texto == 'Cancelar':
            self.current = 'sc_menu_principal'

    def busca(self):
        del self.lista[:]
        #self.dic_items = {}
        self.dic_items.clear()
        cad = self.i_buscar_cadena.text.lower()
        if self.ids.sw_ignora.active:
            cad = self.traduce(cad)
            if self.ids.cb_y.active:
                for i in range(len(self.items)):
                    if self.cadena_en_texto_ignora(i,cad) and self.clave_en_claves(i):
                        self.dic_items[self.items[i]] = i
            else:
                for i in range(len(self.items)):
                    if self.cadena_en_texto_ignora(i,cad) or self.clave_en_claves(i):
                        self.dic_items[self.items[i]] = i
        else:
            if self.ids.cb_y.active:
                for i in range(len(self.items)):
                    if self.cadena_en_texto(i,cad) and self.clave_en_claves(i):
                        self.dic_items[self.items[i]] = i
            else:
                for i in range(len(self.items)):
                    if self.cadena_en_texto(i,cad) or self.clave_en_claves(i):
                        self.dic_items[self.items[i]] = i
        self.lista = self.dic_items.keys()
        self.lista.sort()
        self.ids.lis_panta.adapter = ListAdapter(data=[], cls=BotonDeLista, args_converter=self.args_converter, selection_mode='single')
        self.titulo_lista = 'Registros encontrados'
        self.ids.b_lista_izq.text = 'Menu'
        self.ids.b_lista_cen.text = 'Exportar'
        self.ids.b_lista_der.text = 'Buscar'
        self.ids.b_lista_over.text = 'Eliminar'
        self.listando_claves = False
        self.rellena("items")
        self.current = 'sc_lista'

    def cadena_en_texto(self, i, cad):
        if cad:
            if self.ids.sw_busca.active:
                if not (self.items[i].lower().count(cad) or self.memos[i].lower().count(cad)):
                    return False
            else:
                if not self.items[i].lower().count(cad):
                    return False
        return True

    def cadena_en_texto_ignora(self, i, cad):
        if cad:
            if self.ids.sw_busca.active:
                if not (self.traduce(self.items[i].lower()).count(cad) or self.traduce(self.memos[i].lower()).count(cad)):
                    return False
            else:
                if not self.traduce(self.items[i].lower()).count(cad):
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

    def clave_nuevo_nombre(self, nuevo_nombre=""):
        if not nuevo_nombre:
            self.dialogo('Nuevo nombre para '+self.clave_renombrar, 'renombrar_clave')
            return
        for i in range(len(self.registros)):
            campos = self.registros[i].split(';')
            for j in range(len(campos[2:])):
                if campos[j] == self.clave_renombrar:
                    campos[j] = nuevo_nombre
                    self.registros[i] = ';'.join(campos)
                    break
            for j in range(len(self.claves[i])):
                if self.claves[i][j] == self.clave_renombrar:
                    self.claves[i][j] = nuevo_nombre
                    break
        self.clave.append(nuevo_nombre)
        self.clave.sort()
        self.grabar(modo='renom')

    def carga_listas(self):
        del self.items[:]
        del self.memos[:]
        del self.claves[:]
        del self.clave[:]
        for r in self.registros:
            campos = r.split(';')
            self.items.append(campos[0])
            self.memos.append(campos[1])
            self.claves.append(campos[2:])
            for c in campos[2:]:
                if c not in self.clave: self.clave.append(c)
        self.clave.sort()
        self.lista_claves_cargadas = False
        self.cargado = True

    def elige_claves(self, origen=''):
        if self.eligiendo: return
        if not self.listando_claves:
            self.ids.lis_panta.adapter = ListAdapter(data=[], cls=BotonDeLista, args_converter=self.args_converter_claves, selection_mode='multiple', propagate_selection_to_data=True)
            #self.ids.lis_panta.adapter.bind(on_selection_change=self.selection_changed)
            self.listando_claves = True
            #del self.lista[:]
            self.titulo_lista = 'Claves'
            self.ids.b_lista_izq.text = 'Cancelar'
            self.ids.b_lista_cen.text = 'Nueva'
            self.ids.b_lista_der.text = 'Aceptar'
            self.ids.b_lista_over.text = 'Cancelar'
            if not self.lista_claves_cargadas:
                del self.lista_claves[:]
                for c in self.clave: self.lista_claves.append(ClaveItem(text=c))
                self.lista_claves_cargadas = True
        self.marca_claves(origen)
        self.rellena('claves')
        #self.titulo_lista = 'Claves'
        self.eligiendo = True
        self.current = 'sc_lista'
        if platform == 'android': android.hide_keyboard()

    def chequeos(self):
        reg = self.ids.i_item_alta.text + \
              self.ids.i_memo_alta.text + \
              self.ids.i_claves_alta.text
        if reg == "":
            self.aviso('Registro vacío')
            return False
        if reg.count(';'):
            self.aviso('No se puede usar ;')
            return False
        return True

    def eliminar_registros(self, confirmado=False, modo=''):
        if not confirmado:
            if modo == 'uno':
                self.confirmacion('¿Eliminar el registro?', 'elim_un_reg')
            else:
                self.confirmacion('¿Eliminar ' + str(len(self.dic_items)) + ' registros?', 'elim_n_regs')
            return
        if modo == 'uno':
            a_eliminar = [self.dic_items[self.ids.i_item.text]]
        else:
            a_eliminar = self.dic_items.values()
            a_eliminar.sort(reverse = True)
        for i in a_eliminar:
            self.registros.pop(i)
            self.items.pop(i)
            self.memos.pop(i)
            self.claves.pop(i)
        if self.graba_lista(self.abierto+TEMP, self.registros):
            rename(self.directorio+self.abierto+TEMP, self.directorio+self.abierto+FICH)
            self.aviso('Registro(s) eliminado(s)')
        else:
            self.abrir_archivo(self.abierto)
        self.current = 'sc_menu_principal'

    def existe_fichero(self, nombre):
        if nombre+FICH in listdir(self.directorio):
            self.aviso('Ya existe ese fichero')
            return True
        return False

    def exportar(self, nombre=''):
        if not nombre:
            self.dialogo('Nombre del fichero', 'fichero_exportar')
            return
        if self.existe_fichero(nombre): return
        regis = [self.registros[i] for i in self.dic_items.values()]
#        try:
            # F = open(self.directorio + nombre + FICH, 'w')
        # except:
            # self.aviso('No puedo crear fichero')
            # return
        # try:
            # for r in regis: F.write(r.encode('utf-8') + '\n')
        # except:
            # self.aviso('No puedo escribir fichero')
            # return
        # F.close()
        if self.graba_lista(nombre+FICH, regis):
            self.aviso('Exportados ' + str(len(regis)) + ' registros')

    def graba_lista(self, nombre, lista):
        try:
            F = open(self.directorio + nombre, 'w')
        except:
            self.aviso('No puedo crear fichero')
            return False
        try:
            for r in lista: F.write(r.encode('utf-8') + '\n')
        except:
            self.aviso('No puedo escribir fichero')
            remove(self.directorio + nombre)
            return False
        F.close()
        return True

    def fichero_nuevo(self, nombre=''):
        if not nombre:
            self.dialogo('Nombre del nuevo fichero', 'fichero_nuevo')
            return
        if self.existe_fichero(nombre): return
        try:
            open(self.directorio + nombre + FICH, 'w').close()
        except:
            self.aviso('No puedo crear fichero')
            return
        if self.abrir_archivo(nombre):
            self.jstore.put("pim", ultimo=nombre)
            self.num_lineas = '0'
            self.current = 'sc_menu_principal'

    def grabar(self, modo=""):
        if modo!='nuevo' and not self.modificando:
            self.aviso('No está modificando')
            return
        if modo!='renom' and not self.chequeos(): return
        try: F = open(self.directorio + self.abierto + TEMP, 'w')
        except:
            self.aviso('No puedo crear fichero')
            return
        if modo != 'renom':
            reg = self.ids.i_item_alta.text + ';' + \
                  self.ids.i_memo_alta.text.replace('\n',' ^ ') + ';' + \
                  self.ids.i_claves_alta.text.replace(',',';')
            if modo == 'nuevo':
                self.registros.append(reg)
                self.items.append(self.ids.i_item_alta.text)
                self.memos.append(self.ids.i_memo_alta.text.replace('\n',' ^ '))
                self.claves.append(self.ids.i_claves_alta.text.split(','))
            elif modo == 'modif':
                self.registros[self.reg] = reg
                self.items[self.reg] = self.ids.i_item_alta.text
                self.memos[self.reg] = self.ids.i_memo_alta.text.replace('\n',' ^ ')
                self.claves[self.reg] = self.ids.i_claves_alta.text.split(',')
        try:
            for r in self.registros: F.write(r.encode('utf-8') + '\n')
        except UnicodeEncodeError:
            try: remove(self.directorio + self.abierto+TEMP)
            except: pass
            self.aviso('Hay caracteres inválidos')
            return
        except:
            #self.aviso('No puedo escribir fichero')
            try: remove(self.directorio + self.abierto+TEMP)
            except: pass
            self.aviso(str(sys.exc_info()[0]))
            return
        F.close()
        rename(self.directorio + self.abierto+TEMP, self.directorio + self.abierto+FICH)
        #num_lineas = int(self.num_lineas) + 1
        if modo == 'nuevo': self.num_lineas = str(int(self.num_lineas) + 1)
        self.current = 'sc_menu_principal'

    def importar(self):
        self.dialogo(str(platform))

    def limpia_i_buscar_cadena(self):
        self.i_buscar_cadena.text = ""

    def limpia_b_buscar_claves(self):
        if self.b_buscar_claves.text != "":
            self.b_buscar_claves.text = ""
            for c in self.lista_claves: c.deselect()
            self.listando_claves = False

    def limpia_busqueda(self):
        self.limpia_i_buscar_cadena()
        self.limpia_b_buscar_claves()

    def lista_elegido(self, boton, texto):
        if self.titulo_lista == 'Registros encontrados':
            self.reg = self.dic_items[texto]
            self.ids.i_item.text = texto
            self.ids.i_memo.text = self.memos[self.reg].replace(' ^ ','\n')
            self.ids.i_claves.text = ','.join(self.claves[self.reg])
            self.ids.i_item.readonly = True
            self.ids.i_memo.readonly = True
            self.ids.i_claves.readonly = True
            self.current = 'sc_registro'
        elif self.titulo_lista == 'Claves':
            #~ cla_selec = [c.text for c in self.ids.lis_panta.adapter.data if c.is_selected]
            if texto in self.claves_seleccionadas:
                self.claves_seleccionadas.remove(texto)
                for c in self.ids.lis_panta.adapter.data:
                    if c.text == texto: c.is_selected = False
            else:
                self.claves_seleccionadas.append(texto)
                for c in self.ids.lis_panta.adapter.data:
                    if c.text == texto: c.is_selected = True
            #~ cla_selec = [c.text for c in self.ids.lis_panta.adapter.data if c.is_selected]
        elif self.titulo_lista == 'Elegir archivo':
            if self.abrir_archivo(texto):
#                self.jstore.put("pim", directorio='/mnt/sdcard/PIM/', ultimo=texto)
                self.jstore.put("pim", directorio=self.directorio, ultimo=texto)
                self.current = 'sc_menu_principal'
        elif self.titulo_lista == 'Archivo a importar':
            pass
        elif self.titulo_lista == 'Clave a renombrar':
            self.clave_renombrar = texto
            self.clave_nuevo_nombre("")

    def marca_claves(self, origen):
        print 'marca_claves', origen
        if origen == 'buscar':
            self.claves_buscando = True
            if self.ids.b_buscar_claves.text: self.claves_seleccionadas = self.ids.b_buscar_claves.text.split(',')
            else: self.claves_seleccionadas = []
        else:
            self.claves_buscando = False
            if not self.clave_nueva:
                if self.ids.i_claves_alta.text: self.claves_seleccionadas = self.ids.i_claves_alta.text.split(',')
                else: self.claves_seleccionadas = []
            else:
                self.clave_nueva = False
        for cl in self.lista_claves:
            cl.is_selected = True if cl.text in self.claves_seleccionadas else False

    def limpia(self, widg):
        self.widg.text = ""

    def modificar(self):
        self.ids.i_item_alta.text = self.ids.i_item.text
        self.ids.i_memo_alta.text = self.ids.i_memo.text
        self.ids.i_claves_alta.text = self.ids.i_claves.text
        self.modificando = True
        self.current = 'sc_alta'

    def panta_buscar(self):
        if self.abierto:
            if not self.cargado: self.carga_listas()
            self.ids.titulo_sc_buscar.text = 'Buscando en ' + self.titulo_fichero
            self.current = 'sc_buscar'
            self.ids.i_buscar_cadena.focus = True

    def rellena(self, tipo=""):
        #~ self.lis_panta.item_strings = ['wefrewr', 'klsjf lkj f']
        #~ self.lis_panta.adapter.data.clear()
        #self.titulo_lista = 'Ficheros disponibles'
        del self.ids.lis_panta.adapter.data[:]
        #self.lis_panta.adapter.data.extend(['wefrewr', 'klsjf lkj f', 'kk'])
        if tipo == "claves":
            #~ self.ids.lis_panta.adapter.data = self.lista_claves
            self.ids.lis_panta.adapter.cls = BotonDeLista
            self.ids.lis_panta.adapter.data.extend(self.lista_claves)
        elif tipo == "ficheros":
            self.ids.lis_panta.adapter.cls = BotonDeLista
            self.ids.lis_panta.adapter.data.extend(self.lista)
        else:
            self.ids.lis_panta.adapter.cls = LabelDeLista
            self.ids.lis_panta.adapter.data.extend(self.lista)
        self.ids.lis_panta._trigger_reset_populate()

    def args_converter(self, index, data_item):
        #~ texto = data_item
        #~ return {'texto': texto}
        return {'text': data_item}

    def args_converter_claves(self, index, data_item):
        #~ texto = data_item.text
        #~ return {'texto': texto}
        return {'text': data_item.text}

    def renombrar_clave(self):
        self.clave_renombrar = ""
        self.ids.lis_panta.adapter = ListAdapter(data=[], cls=BotonDeLista, args_converter=self.args_converter_claves)
        self.titulo_lista = 'Clave a renombrar'
        self.ids.b_lista_izq.text = 'Cancelar'
        self.ids.b_lista_cen.text = ''
        self.ids.b_lista_der.text = ''
        self.ids.b_lista_over.text = 'Cancelar'
        if not self.lista_claves_cargadas:
            del self.lista_claves[:]
            for c in self.clave: self.lista_claves.append(ClaveItem(text=c))
            self.lista_claves_cargadas = True
        self.rellena('claves')
        self.current = 'sc_lista'

    def traduce(self, s):
        s = s.encode('utf-8')
        s = s.replace('á','a').replace('é','e').replace('í','i')\
             .replace('ó','o').replace('ú','u').replace('ñ','n')\
             .replace('ç','c')
        return s.decode('utf-8')

class PimApp(App):
    title = 'PIM'
    use_kivy_settings = False
    def on_pause(self):
        return True

    def build(self):
        #self.title = 'PIM'
        #self.icon = 'icono.png'
        self.sm = MyScreenManager()
        self.bind(on_start=self.post_build_init)
        return self.sm

    def post_build_init(self, ev):
     # Map Android keys
     #if platform == 'android':
         #android.map_key(android.KEYCODE_BACK, 1000)
         #android.map_key(android.KEYCODE_MENU, 1001)
     win = self._app_window
     win.bind(on_keyboard=self._key_handler)

    def _key_handler(self, *args):
        key = args[1]
        #print key
        # 1000 is "back" on Android
        # 27 is "escape" on computers
        # 1001 is "menu" on Android
        if key in (1000, 27):
            self.sm.current_screen.dispatch("on_back_pressed")
            return True
        elif key == 1001:
            self.sm.current_screen.dispatch("on_menu_pressed")
            return True

if __name__=="__main__":
    #from kivy.utils import platform
    if platform == 'android': import android
    mapp = PimApp()
    mapp.run()

#http://davideddu.org/blog/posts/kivy-back-btn-navigation/
#CORREGIR
#

#PLAN
#nueva clave
    #reducir tamano
#orden de las fechas al reves
#pasar apertura de fichero a on_start

#IDEAS
#utilidades
    #eliminar claves vacias
    #comprueba si hay algún fichero pendiente de renombrar
        #si no hay origen, recuperarlo
        #si hay origen, comparar longitud
    #borrar fichero
    #copiar fichero con otro nombre
    #renombrar fichero
    #buscar líneas con caracteres raros y sustituirlos
        #listarlas
        #preguntar si sustituirlos