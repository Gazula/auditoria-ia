import os
import json
from datetime import datetime
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup


class AuditoriaItem(BoxLayout):
    def __init__(self, titulo, **kwargs):
        super().__init__(orientation='vertical', spacing=5, padding=10, size_hint_y=None, height=260, **kwargs)
        self.titulo = titulo
        self.image_path = None

        self.add_widget(Label(text=titulo, size_hint_y=None, height=30, bold=True))

        toggle_layout = BoxLayout(size_hint_y=None, height=40, spacing=10)
        self.cumple_si = ToggleButton(text='Cumple', group=titulo)
        self.cumple_no = ToggleButton(text='No Cumple', group=titulo)
        toggle_layout.add_widget(self.cumple_si)
        toggle_layout.add_widget(self.cumple_no)
        self.add_widget(toggle_layout)

        self.comentario = TextInput(hint_text='Comentarios...', multiline=True, size_hint_y=None, height=80)
        self.add_widget(self.comentario)

        self.btn_imagen = Button(text='📷 Agregar imagen', size_hint_y=None, height=40)
        self.btn_imagen.bind(on_press=self.abrir_filechooser)
        self.add_widget(self.btn_imagen)

        self.img_preview = Image(size_hint_y=None, height=80)
        self.add_widget(self.img_preview)

    def abrir_filechooser(self, instance):
        content = FileChooserListView(filters=['*.png', '*.jpg', '*.jpeg'], path=os.getcwd())
        popup = Popup(title='Seleccionar imagen', content=content, size_hint=(0.9, 0.9))

        def cargar_archivo(instance, selection):
            if selection:
                self.image_path = selection[0]
                self.img_preview.source = self.image_path
                self.img_preview.reload()
            popup.dismiss()

        content.bind(on_submit=lambda instance, selection, touch: cargar_archivo(instance, selection))
        popup.open()

    def obtener_datos(self):
        estado = 'Cumple' if self.cumple_si.state == 'down' else 'No Cumple' if self.cumple_no.state == 'down' else 'No seleccionado'
        return {
            'item': self.titulo,
            'estado': estado,
            'comentario': self.comentario.text,
            'imagen': self.image_path if self.image_path else None
        }


class AuditoriaApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        self.scroll = ScrollView()
        self.items_layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.items_layout.bind(minimum_height=self.items_layout.setter('height'))

        items = [
            "Orden y Limpieza",
            "Temperatura de conservación",
            "Exhibición de productos fuera de temperatura",
            "Nivel de carga de mercadería",
            "Ausencia de productos vencidos",
            "Frescura y presentación de los productos",
            "Depósito y Cámaras (orden, limpieza y temperatura)",
            "Etiquetado de productos",
            "Fechas de retiro de góndola",
            "Riesgo de contaminación",
            "Mantenimiento",
            "Productos de limpieza"
        ]

        self.campos = []
        for item in items:
            campo = AuditoriaItem(item)
            self.campos.append(campo)
            self.items_layout.add_widget(campo)

        self.scroll.add_widget(self.items_layout)
        self.layout.add_widget(self.scroll)

        self.nombre_tienda = TextInput(hint_text='Nombre o número de tienda', size_hint_y=None, height=40)
        self.layout.add_widget(self.nombre_tienda)

        self.boton_guardar = Button(text="Guardar auditoría", size_hint_y=None, height=50)
        self.boton_guardar.bind(on_press=self.guardar_datos)
        self.layout.add_widget(self.boton_guardar)

        return self.layout

    def guardar_datos(self, instance):
        tienda = self.nombre_tienda.text.strip()
        if not tienda:
            print("Por favor ingrese el nombre o número de tienda.")
            return

        datos = []
        puntaje = 0

        for campo in self.campos:
            d = campo.obtener_datos()
            datos.append(d)
            if d["estado"] == "Cumple":
                puntaje += 1

        total_items = len(self.campos)
        porcentaje = round((puntaje / total_items) * 100, 2)

        auditoria = {
            "tienda": tienda,
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "puntaje": porcentaje,
            "total_items": total_items,
            "items_cumplidos": puntaje,
            "detalle": datos
        }

        # Crear carpeta si no existe
        os.makedirs("auditorias", exist_ok=True)

        archivo = f"auditorias/auditoria_{tienda}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(archivo, "w", encoding="utf-8") as f:
            json.dump(auditoria, f, ensure_ascii=False, indent=4)

        print(f"Auditoría guardada en: {archivo}")
        print(f"Puntaje: {porcentaje}%")

        # Reset de campos
        for campo in self.campos:
            campo.cumple_si.state = 'normal'
            campo.cumple_no.state = 'normal'
            campo.comentario.text = ''
            campo.image_path = None
            campo.img_preview.source = ''

        self.nombre_tienda.text = ''


if __name__ == '__main__':
    AuditoriaApp().run()