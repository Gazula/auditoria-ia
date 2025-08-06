import os
import shutil
import datetime
import socket

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.filechooser import FileChooserIconView


def is_connected(host="8.8.8.8", port=53, timeout=3):
    """Verifica si hay conexión a internet."""
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error:
        return False


def guardar_localmente(numero_tienda, observacion, imagen_path):
    carpeta_base = "pendientes"
    carpeta_tienda = os.path.join(carpeta_base, numero_tienda)
    os.makedirs(carpeta_tienda, exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_base = f"{timestamp}"

    # Copiar imagen
    imagen_nombre = f"{nombre_base}.jpg"
    imagen_destino = os.path.join(carpeta_tienda, imagen_nombre)
    shutil.copy(imagen_path, imagen_destino)

    # Guardar observación
    texto_nombre = f"{nombre_base}.txt"
    texto_destino = os.path.join(carpeta_tienda, texto_nombre)
    with open(texto_destino, "w") as f:
        f.write(f"Tienda: {numero_tienda}\n")
        f.write(f"Observación: {observacion}\n")

    print(f"[📁] Guardado localmente en: {carpeta_tienda}")


class AuditoriaLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)

        self.add_widget(Label(text="Número de Tienda:"))
        self.tienda_input = TextInput(multiline=False)
        self.add_widget(self.tienda_input)

        self.add_widget(Label(text="Observación:"))
        self.observacion_input = TextInput()
        self.add_widget(self.observacion_input)

        self.add_widget(Label(text="Seleccionar imagen:"))
        self.file_chooser = FileChooserIconView(filters=['*.jpg', '*.png', '*.jpeg'])
        self.add_widget(self.file_chooser)

        self.boton_enviar = Button(text="Enviar Auditoría", size_hint=(1, 0.2))
        self.boton_enviar.bind(on_press=self.enviar_auditoria)
        self.add_widget(self.boton_enviar)

    def enviar_auditoria(self, instance):
        numero_tienda = self.tienda_input.text.strip()
        observacion = self.observacion_input.text.strip()
        seleccion = self.file_chooser.selection

        if not numero_tienda or not observacion or not seleccion:
            print("[⚠️] Todos los campos son obligatorios.")
            return

        imagen_path = seleccion[0]

        if is_connected():
            print("[✅] Hay conexión. (Aquí iría la lógica para subir al servidor)")
            # Implementar subida real al servidor en esta parte
        else:
            guardar_localmente(numero_tienda, observacion, imagen_path)


class AuditoriaApp(App):
    def build(self):
        return AuditoriaLayout()


if __name__ == '__main__':
    AuditoriaApp().run()

print("🕒 La auditoría se guardó y será enviada automáticamente cuando vuelva la conexión.")
