# File name: pim.py
import kivy
kivy.require('1.9.1')

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.core.window import Window
#~ from kivy.uix.pagelayout import PageLayout

Builder.load_file('sc_buscar.kv')

Window.clearcolor = (0, 0, 0, 1)

class MyScreenManager(ScreenManager):
    def no_implementado(self):
        the_content = Label(text = "Funcionalidad no Implementada")
        the_content.color = (1,1,1,1)
        popup = Popup(title='PIM',
            content = the_content, size_hint=(None, None), size=(350, 150))
        popup.open()

class PimApp(App):
    def build(self):
        return MyScreenManager()

if __name__=="__main__":
    PimApp().run()
